# -*- coding: utf-8 -*-
"""GUI dialog for selecting and opening a live-linked RPY/PY file."""

from abaqusGui import *
import os
import subprocess


class RpyLiveLinkDB(AFXDataDialog):

    [
        ID_BROWSE,
        ID_OPEN_EDITOR,
    ] = range(AFXDataDialog.ID_LAST, AFXDataDialog.ID_LAST + 2)

    def __init__(self, form):
        AFXDataDialog.__init__(
            self,
            form,
            'RPY Live Link',
            self.OK | self.APPLY | self.CANCEL,
            DIALOG_ACTIONS_SEPARATOR,
        )

        self.form = form
        self.file_selector = None

        file_group = FXGroupBox(
            self,
            'Replay or Python file',
            LAYOUT_FILL_X | FRAME_GROOVE,
        )
        file_row = FXHorizontalFrame(file_group, LAYOUT_FILL_X)
        AFXTextField(
            file_row,
            52,
            'File:',
            form.filePathKw,
            0,
            LAYOUT_FILL_X,
        )
        FXButton(file_row, 'Browse...', None, self, self.ID_BROWSE)
        FXButton(
            file_row,
            'Open in Notepad',
            None,
            self,
            self.ID_OPEN_EDITOR,
        )

        options_group = FXGroupBox(
            self,
            'Live update options',
            LAYOUT_FILL_X | FRAME_GROOVE,
        )
        FXCheckButton(
            options_group,
            'Execute once immediately when monitoring starts',
            form.runNowKw,
            0,
        )
        AFXTextField(
            options_group,
            8,
            'Save debounce (seconds):',
            form.delayKw,
            0,
        )

        instructions = (
            'How to use:\n'
            '1. Select an .rpy or .py file.\n'
            '2. Click Open in Notepad to edit it.\n'
            '3. Click Apply or OK to start monitoring.\n'
            '4. Every complete file save is executed in the current CAE session.\n\n'
            'Warning: the selected script has full access to the current model. '
            'A script that deletes parts, meshes, loads, or files can do so again '
            'after every save.'
        )
        FXLabel(
            self,
            instructions,
            None,
            JUSTIFY_LEFT | LAYOUT_FILL_X,
        )

        FXMAPFUNC(
            self,
            SEL_COMMAND,
            self.ID_BROWSE,
            RpyLiveLinkDB.onCmdBrowse,
        )
        FXMAPFUNC(
            self,
            SEL_COMMAND,
            self.ID_OPEN_EDITOR,
            RpyLiveLinkDB.onCmdOpenEditor,
        )

    def onCmdBrowse(self, sender, selector, pointer):
        patterns = (
            'Abaqus replay files (*.rpy)\n'
            'Python scripts (*.py)\n'
            'All files (*)'
        )
        if self.file_selector is None:
            self.file_selector = AFXFileSelectorDialog(
                self,
                'Select an Abaqus replay or Python file',
                self.form.filePathKw,
                None,
                AFXSELECTFILE_EXISTING,
                patterns,
            )
            self.file_selector.create()
        self.file_selector.showModal()
        return 1

    def onCmdOpenEditor(self, sender, selector, pointer):
        file_path = str(self.form.filePathKw.getValue()).strip()
        if not file_path or not os.path.isfile(file_path):
            showAFXErrorDialog(
                self,
                'Select an existing .rpy or .py file first.',
            )
            return 1

        try:
            subprocess.Popen(['notepad.exe', file_path])
        except Exception as error:
            showAFXErrorDialog(
                self,
                'Could not open Notepad:\n' + str(error),
            )
        return 1
