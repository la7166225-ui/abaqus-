# -*- coding: utf-8 -*-
"""Abaqus/CAE GUI registration for RPY Live Link."""

from abaqusGui import *
from abaqusConstants import ALL
import os


class RpyLiveLinkForm(AFXForm):

    def __init__(self, owner):
        AFXForm.__init__(self, owner)

        self.cmd = AFXGuiCommand(
            mode=self,
            method='configure_watch',
            objectName='rpy_live_link_kernel',
            registerQuery=False,
        )

        default_file = r'F:\temp\Cube_parametric.rpy'
        if not os.path.isfile(default_file):
            default_file = os.path.join(os.getcwd(), 'abaqus.rpy')

        self.filePathKw = AFXStringKeyword(
            self.cmd,
            'file_path',
            True,
            default_file,
        )
        self.delayKw = AFXFloatKeyword(
            self.cmd,
            'delay',
            True,
            0.50,
        )
        self.runNowKw = AFXBoolKeyword(
            self.cmd,
            'run_now',
            AFXBoolKeyword.TRUE_FALSE,
            True,
            True,
        )

    def getFirstDialog(self):
        import rpy_live_linkDB
        return rpy_live_linkDB.RpyLiveLinkDB(self)

    def doCustomChecks(self):
        file_path = str(self.filePathKw.getValue()).strip()
        if not os.path.isfile(file_path):
            showAFXErrorDialog(
                self.getCurrentDialog(),
                'Select an existing .rpy or .py file.',
            )
            return False
        if os.path.splitext(file_path)[1].lower() not in ('.rpy', '.py'):
            showAFXErrorDialog(
                self.getCurrentDialog(),
                'Only .rpy and .py files are supported.',
            )
            return False
        import rpy_live_link_gui
        rpy_live_link_gui.configure_monitor(
            file_path,
            self.delayKw.getValue(),
        )
        return True

    def okToCancel(self):
        return False


toolset = getAFXApp().getAFXMainWindow().getPluginToolset()

toolset.registerGuiMenuButton(
    buttonText='RPY Live Link|Configure / Start...',
    object=RpyLiveLinkForm(toolset),
    messageId=AFXMode.ID_ACTIVATE,
    icon=None,
    kernelInitString='import rpy_live_link_kernel',
    applicableModules=ALL,
    version='1.1.0',
    author='OpenAI Codex',
    description='Watch an RPY/PY file and execute stable saves on the CAE kernel.',
    helpUrl='',
)

toolset.registerKernelMenuButton(
    buttonText='RPY Live Link|Stop',
    moduleName='rpy_live_link_kernel',
    functionName='stop_watch()',
    icon=None,
    applicableModules=ALL,
    version='1.1.0',
    author='OpenAI Codex',
    description='Stop the current RPY Live Link watcher.',
    helpUrl='',
)

toolset.registerKernelMenuButton(
    buttonText='RPY Live Link|Status',
    moduleName='rpy_live_link_kernel',
    functionName='status()',
    icon=None,
    applicableModules=ALL,
    version='1.1.0',
    author='OpenAI Codex',
    description='Print RPY Live Link status and the last execution result.',
    helpUrl='',
)
