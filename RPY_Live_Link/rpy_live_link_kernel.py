# -*- coding: utf-8 -*-
"""Kernel-side script execution for RPY Live Link in Abaqus/CAE 2021."""

from __future__ import print_function

import io
import os
import time
import traceback


PLUGIN_VERSION = '1.1.0'
_state = None


def _normalise_path(file_path):
    if file_path is None:
        return ''
    return os.path.abspath(os.path.expanduser(str(file_path).strip()))


def _log_path_for(file_path):
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    return os.path.join(
        os.path.dirname(file_path),
        base_name + '.rpy_live_link.log',
    )


def _log(state, message):
    line = '[%s] %s' % (time.strftime('%Y-%m-%d %H:%M:%S'), message)
    log_path = state.get('log_path', '')
    if log_path:
        try:
            with io.open(log_path, 'a', encoding='utf-8') as log_handle:
                log_handle.write(line + u'\n')
        except Exception:
            pass
    print('RPY Live Link: ' + line)


def _execution_namespace(file_path):
    namespace = {
        '__name__': '__main__',
        '__file__': file_path,
    }

    try:
        from abaqus import mdb, session
        namespace['mdb'] = mdb
        namespace['session'] = session
    except Exception:
        pass

    try:
        import abaqusConstants
        for name in dir(abaqusConstants):
            if not name.startswith('_'):
                namespace[name] = getattr(abaqusConstants, name)
    except Exception:
        pass

    # Full replay files may contain cliCommand("..."). This adapter executes
    # those kernel command blocks in the same namespace.
    def cli_command(command_text):
        command_code = compile(
            command_text,
            file_path + '::<cliCommand>',
            'exec',
        )
        exec(command_code, namespace, namespace)

    namespace['cliCommand'] = cli_command
    return namespace


def _execute_file(file_path):
    # Abaqus 2021 uses Python 2.7. Compile bytes so a coding declaration in
    # the RPY file is interpreted correctly.
    with io.open(file_path, 'rb') as script_handle:
        source = script_handle.read()

    code_object = compile(source, file_path, 'exec')
    namespace = _execution_namespace(file_path)
    exec(code_object, namespace, namespace)


def _execute_and_record(state, signature=None, raise_on_error=False):
    state['busy'] = True
    try:
        _execute_file(state['file_path'])
        state['last_signature'] = signature
        state['last_error'] = None
        state['success_count'] += 1
        _log(
            state,
            'Reload successful (count=%d).' % state['success_count'],
        )
        return True
    except Exception as error:
        state['last_signature'] = signature
        state['last_error'] = str(error)
        state['error_count'] += 1
        _log(state, 'Reload failed: ' + str(error))
        _log(state, traceback.format_exc())
        if raise_on_error:
            raise
        return False
    finally:
        state['busy'] = False


def configure_watch(file_path, delay=0.50, run_now=True):
    """Configure main-thread execution; GUI-side code performs file polling."""
    global _state

    normalised_path = _normalise_path(file_path)
    if not normalised_path:
        raise ValueError('Select an RPY or PY file.')
    if not os.path.isfile(normalised_path):
        raise ValueError('File does not exist: ' + normalised_path)
    extension = os.path.splitext(normalised_path)[1].lower()
    if extension not in ('.rpy', '.py'):
        raise ValueError('Only .rpy and .py files are supported.')

    try:
        delay_value = float(delay)
    except Exception:
        delay_value = 0.50
    delay_value = max(0.20, min(delay_value, 10.0))

    _state = {
        'enabled': True,
        'file_path': normalised_path,
        'log_path': _log_path_for(normalised_path),
        'delay': delay_value,
        'last_signature': None,
        'last_error': None,
        'success_count': 0,
        'error_count': 0,
        'busy': False,
    }

    _log(_state, 'Monitoring configured for ' + normalised_path)
    if bool(run_now):
        _execute_and_record(_state, signature='initial', raise_on_error=False)

    print('RPY Live Link %s is ON.' % PLUGIN_VERSION)
    print('Watching: ' + normalised_path)
    print('Log: ' + _state['log_path'])
    return normalised_path


def execute_if_enabled(file_path, signature=None):
    """Execute a GUI-detected stable save on Abaqus's main kernel thread."""
    current_state = _state
    if current_state is None or not current_state.get('enabled'):
        return False

    normalised_path = _normalise_path(file_path)
    if normalised_path.lower() != current_state['file_path'].lower():
        return False
    if not os.path.isfile(normalised_path):
        current_state['last_error'] = 'File does not exist: ' + normalised_path
        _log(current_state, current_state['last_error'])
        return False

    return _execute_and_record(
        current_state,
        signature=signature,
        raise_on_error=False,
    )


def stop_watch():
    """Disable execution; the lightweight GUI timer may remain registered."""
    global _state
    if _state is None:
        print('RPY Live Link: watcher is not configured.')
        return True

    _state['enabled'] = False
    _log(_state, 'Monitoring stopped.')
    print('RPY Live Link: OFF')
    return True


def run_once(file_path):
    """Execute one RPY/PY file immediately without monitoring."""
    normalised_path = _normalise_path(file_path)
    if not os.path.isfile(normalised_path):
        raise ValueError('File does not exist: ' + normalised_path)
    _execute_file(normalised_path)
    print('RPY Live Link: one-time execution successful.')
    return normalised_path


def status():
    """Print current status to the Abaqus message area."""
    if _state is None:
        print('RPY Live Link: NOT CONFIGURED')
        return 'NOT CONFIGURED'

    status_text = 'ON' if _state.get('enabled') else 'OFF'
    print('RPY Live Link: ' + status_text)
    print('Watching: ' + _state['file_path'])
    print('Reloads: %d successful, %d failed' % (
        _state['success_count'],
        _state['error_count'],
    ))
    if _state.get('last_error'):
        print('Last error: ' + _state['last_error'])
    print('Log: ' + _state['log_path'])
    return status_text
