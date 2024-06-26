#!/usr/bin/python
################################################################################
#
#   stepheader.py
#   Author: Roger Wang
#   Date: 2024-06-18
#
#   StepHeader is a QWidget that is the toolbar/banner used by both Step1 and 
#   Step2. It displays the project's name and the description of the current 
#   step. Buttons for returning to the Starter, editing project settings, and 
#   saving the project are also provided.
#
################################################################################

import darkdetect
import os

from access import *
from dialog import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

BASEDIR = os.path.dirname(__file__)

class StepHeader(QWidget):
    project_edited = pyqtSignal()
    returned = pyqtSignal()

    def __init__(self, parent, project, step):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, \
                           QSizePolicy.Policy.Fixed)
        self._project = project
        self._step = step
        self._layout = self._get_step_header()
        self.setLayout(self._layout)
    
    """
    Sets the project for the StepHeader.
    @param project: Project object.
    """
    def set_project(self, project):
        self._project = project

    """
    Return a QHBoxLayout that is the layout for the headers.
    @return QLayout, the requeted layout.
    """
    def _get_step_header(self):
        # Creating all necessary QWidgets.
        return_button = QPushButton()
        return_button.setObjectName("ReturnButton")
        if darkdetect.isDark():
            return_button.setIcon(QIcon(os.path.join(BASEDIR, "svg", "dark", \
                                                     "box-arrow-left.svg")))
        else:
            return_button.setIcon(QIcon(os.path.join(BASEDIR, "svg", \
                                                     "box-arrow-left.svg")))
        return_button.setFixedSize(40, 50)
        return_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        return_button.clicked.connect(self.return_button_clicked)
        self.title_label = QLabel()
        self.title_label.setObjectName("TitleLabel")
        self.update_title()
        subtitle_label = QLabel()
        settings_button = QPushButton()
        if darkdetect.isDark():
            settings_button.setIcon(QIcon(os.path.join(BASEDIR, "svg", "dark", \
                                                       "gear.svg")))
        else:
            settings_button.setIcon(QIcon(os.path.join(BASEDIR, "svg", \
                                                       "gear.svg")))
        settings_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        settings_button.clicked.connect(self.settings_button_clicked)
        save_button = QPushButton(text = " Save")
        if darkdetect.isDark():
            save_button.setIcon(QIcon(os.path.join(BASEDIR, "svg", "dark", \
                                                   "floppy.svg")))
        else:
            save_button.setIcon(QIcon(os.path.join(BASEDIR, "svg", \
                                                   "floppy.svg")))
        save_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        save_button.clicked.connect(self.save_button_clicked)
        saveas_button = QPushButton(text = " Save As")
        if darkdetect.isDark():
            saveas_button.setIcon(QIcon(os.path.join(BASEDIR, "svg", "dark", \
                                                     "floppy.svg")))
        else:
            saveas_button.setIcon(QIcon(os.path.join(BASEDIR, "svg", \
                                                     "floppy.svg")))
        saveas_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        saveas_button.clicked.connect(self.saveas_button_clicked)

        # The text on the subtitle changes based on the current step.
        if self._step == 1:
            subtitle_label.setText("Step 1: Add images of slides.")
        elif self._step == 2:
            subtitle_label.setText("Step 2: Make selections on slide images.")

        # Creating layouts.
        header_title_layout = QVBoxLayout()
        header_title_layout.setSpacing(5)
        header_title_layout.setContentsMargins(0, 0, 0, 0)
        header_title_layout.addStretch()
        header_title_layout.addWidget(self.title_label)
        header_title_layout.addWidget(subtitle_label)
        header_title_layout.addStretch()

        header_layout = QHBoxLayout()
        header_layout.addWidget(return_button)
        header_layout.addLayout(header_title_layout)
        header_layout.addStretch()
        header_layout.addWidget(settings_button)
        header_layout.addWidget(save_button)
        header_layout.addWidget(saveas_button)

        return header_layout

    """
    Updates the title label in case the name of the project has changed.
    """
    def update_title(self):
        self.title_label.setText(self._project.name)

    """
    Handler for when the return button has been clicked.
    """
    def return_button_clicked(self):
        if not self._project.saved:
            return_dialog = ReturnSaveDialog(self._project)
            return_dialog.project_saved.connect(self.project_saved_handler)
            if return_dialog.exec():
                self.returned.emit()
        else:
            self.returned.emit()

    """
    Handler for when the user has clicked the "Settings" button.
    """
    def settings_button_clicked(self):
        project_edit_dialog = ProjectEditDialog(self._project)
        project_edit_dialog.project_edited.connect(self.project_edited_handler)
        project_edit_dialog.exec()

    """
    Handler for when the user has clicked the "Save" button.
    """
    def save_button_clicked(self):
        if self._project.path:
            if Access.check_new_file_write(self._project.path):
                dialog = PermissionErrorDialog()
                dialog.exec()
                return False
            self._project.save_json(self._project.path)
            self.window().setWindowModified(False)
        else:
            self.saveas_button_clicked()

    """
    Handler for when the user has clicked the "Save As" button.
    """
    def saveas_button_clicked(self):
        filename, _ = QFileDialog.getSaveFileName(\
            caption = "Create a project file", \
            filter = "SCP File (*.scp)", directory = self._project.name + \
            ".scp")
        if filename:
            if Access.check_new_file_write(filename):
                dialog = PermissionErrorDialog()
                dialog.exec()
                return False
            self._project.save_json(filename)
            self.window().setWindowModified(False)

    """
    Handler for when the Project has been saved.
    """
    def project_saved_handler(self):
        self.window().setWindowModified(False)

    """
    Handler for when the Project has been edited.
    Notice that the label displaying the Project;s name will also be updated 
    with this function.
    """
    def project_edited_handler(self):
        self.project_edited.emit()
        self.update_title()
