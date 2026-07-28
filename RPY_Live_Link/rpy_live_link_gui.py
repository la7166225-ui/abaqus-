# -*- coding: utf-8 -*-
"""GUI-side save detection using the Abaqus/FOX main event loop."""

from __future__ import print_function

from abaqusGui import *
import io
import os
import time


class RpyLiveLinkMonitor(FXObject):

    ID_TIMEOUT = FXObject.ID_LAST

    def __init__(self):
        FXObject.__init__(self)
        self.active = False
        self.file_path = ''
        self.delay = 0.50
        self.poll_milliseconds = 200
        self.last_signature = None
        self.pending_signature = None
        self.pending_since = None
        self.timer = None

        FXMAPFUNC(
            self,
            SEL_TIMEOUT,
            self.ID_TIMEOUT,
            RpyLiveLinkMonitor.onTimeout,
        )

    def _signature(self):
        try:
            stat_result = os.stat(self.file_path)
            return (stat_result.st_mtime, stat_result.st_size)
        except OSError:
            return None

    def _log_gui_error(self, message):
        if not self.file_path:
            return
        base_name = os.path.splitext(os.path.basename(self.file_path))[0]
        log_path = os.path.join(
            os.path.dirname(self.file_path),
            base_name + '.rpy_live_link.log',
        )
        line = '[%s] GUI monitor error: %s\n' % (
            time.strftime('%Y-%m-%d %H:%M:%S'),
            message,
        )
        try:
            with io.open(log_path, 'a', encoding='utf-8') as log_handle:
                log_handle.write(line)
        except Exception:
            pass

    def _schedule(self):
        if not self.active:
            return
        self.timer = getAFXApp().addTimeout(
            self.poll_milliseconds,
            self,
            self.ID_TIMEOUT,
        )

    def configure(self, file_path, delay):
        self.active = False
        if self.timer is not None:
            try:
                getAFXApp().removeTimeout(self.timer)
            except Exception:
                pass
            self.timer = None

        self.file_path = os.path.abspath(str(file_path).strip())
        try:
            self.delay = max(0.20, min(float(delay), 10.0))
        except Exception:
            self.delay = 0.50

        self.last_signature = self._signature()
        self.pending_signature = None
        self.pending_since = None
        self.active = True
        self._schedule()

    def onTimeout(self, sender, selector, pointer):
        self.timer = None
        try:
            if not self.active:
                return 1

            current_signature = self._signature()
            if current_signature == self.last_signature:
                self.pending_signature = None
                self.pending_since = None
                return 1

            if current_signature is None:
                return 1

            if current_signature != self.pending_signature:
                self.pending_signature = current_signature
                self.pending_since = time.time()
                return 1

            if time.time() - self.pending_since < self.delay:
                return 1

            if getAFXApp().isLocked():
                return 1

            command = (
                'import rpy_live_link_kernel; '
                'rpy_live_link_kernel.execute_if_enabled('
                'file_path=%r, signature=%r)'
                % (self.file_path, current_signature)
            )

            # sendCommand runs the script in Abaqus's main kernel command
            # path. This avoids modifying mdb/session from a Python worker
            # thread, which can block in Abaqus/CAE 2021.
            sendCommand(command)
            self.last_signature = current_signature
            self.pending_signature = None
            self.pending_since = None
        except Exception as error:
            self.last_signature = self._signature()
            self.pending_signature = None
            self.pending_since = None
            self._log_gui_error(str(error))
        finally:
            self._schedule()
        return 1


_monitor = RpyLiveLinkMonitor()


def configure_monitor(file_path, delay=0.50):
    _monitor.configure(file_path, delay)
    return True
