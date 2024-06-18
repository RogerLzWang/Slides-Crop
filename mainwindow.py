#!/usr/bin/python
################################################################################
#
#   mainwindow.py
#   Author: Roger Wang
#   Date: 2024-06-18
#
#   The MainWindow (inherited from QMainWindow) for Slides Crop.
#   The MainWindow manages the change of the program from Starter, where 
#   the user can choose to create a project or open an existing project, to 
#   Step1, where users add, remove, or change the order of slides, to Step2, 
#   where users make selections and export the cropped images.
#
################################################################################

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from project import *
from starter import *
from step1 import *
from step2 import *

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setMinimumSize(1080, 640)
        self.resize(1080, 720)
        self.setUnifiedTitleAndToolBarOnMac(True)

        # The centralWidget is a QStackedWidget.
        # Starter, Step1, and Step2 are all QWidgets that occupy the entire 
        # window. Different widgets are initialized if necessary and set as 
        # the current widget when necessary to realize the step change.
        self._central_widget = QStackedWidget()
        self.setCentralWidget(self._central_widget)

        self._project = None

        # Placeholder variables for the 3 QWidgets.
        self._starter = None
        self._step_1 = None
        self._step_2 = None

        self._resolution = 0.5
        self._color = QColor(255, 0, 0)

        # Starter is shown when the program initiates.
        self.goto_starter()

    """
    Prepares Starter and set Starter as the current widget.
    """
    def goto_starter(self):
        # Creating Starter if not already initialized.
        if not self._starter:
            self._starter = Starter(self, self._resolution, self._color)
            self._starter.continue_clicked.connect(\
                self.starter_continue_handler)
            self._central_widget.addWidget(self._starter)
        self._project = None
        self._central_widget.setCurrentWidget(self._starter)

        # No project can be open when Starter is showing.
        # Opened projects are closed when returning to Starter.
        # Therefore, going to Starter automatically sets the window as 
        # unmodified.
        self.setWindowModified(False)
        
    """
    Handler for continuing from Starter to Step1.
    @param project: Project object.
    """
    def starter_continue_handler(self, project):
        self._project = project

        # A new project is created so that the project is automatically unsaved.
        if not project.saved:
            self.project_edited_handler()

        # Get settings.
        self._resolution = self._starter.get_resolution()
        self._color = self._starter.get_color()
        self.goto_step_1()

    """
    Prepares Step1 and set Step1 as the current widget.
    """
    def goto_step_1(self):
        # Creating Step1 if not already initialized.
        if not self._step_1:
            self._step_1 = Step1(self, self._project, self._resolution)
            self._step_1.project_edited.connect(self.project_edited_handler)
            self._step_1.continue_clicked.connect(self.goto_step_2)
            self._step_1.returned.connect(self.goto_starter)
            self._central_widget.addWidget(self._step_1)
        self._step_1.update()
        self._central_widget.setCurrentWidget(self._step_1)

    """
    Prepares Step2 and set Step2 as the current widget.
    """
    def goto_step_2(self):
        # If no slides have been added, prompt an error dialog and remain in 
        # Step1.
        if not len(self._project.slides):
            dialog = NoSlideErrorDialog()
            dialog.exec()
            return
        
        # Creating Starter if not already initialized.
        if not self._step_2:
            self._step_2 = Step2(self, self._project, self._color, \
                                 self._resolution)
            self._step_2.project_edited.connect(self.project_edited_handler)
            self._step_2.back_clicked.connect(self.goto_step_1)
            self._step_2.returned.connect(self.goto_starter)
            self._central_widget.addWidget(self._step_2)
        else:
            self._step_2.update()
        self._central_widget.setCurrentWidget(self._step_2)

    """
    Sets the window as modified and changing the saved attribute of Project 
    when modifications have been made.
    """
    def project_edited_handler(self):
        self.setWindowModified(True)
        self._project.saved = False

    """
    Upon a closeEvent, check if the project has been saved.
    """
    def closeEvent(self, event):
        if not self._project or self._project.saved:
            # Close the program directly if no project is opened or if no 
            # modifications have been made.
            super().closeEvent(event)
        else:
            # If the project is not saved, prompt a dialog to save.
            close_dialog = CloseSaveDialog(self._project)
            if close_dialog.exec():
                super().closeEvent(event)
            else:
                # The user has selected cancel and the program shouldn't be 
                # closed.
                event.ignore()

class CloseSaveDialog(QDialog):
    # This dialog shows when the user clicks on the close button on the window 
    # but the project has not been saved.

    def __init__(self, project):
        super().__init__()
        self._project = project
        self.setWindowTitle("Close")

        label = QLabel(text = \
                       "Would you like to save the project before closing?")

        save_button = QPushButton(text = "Save")
        save_button.clicked.connect(self.save_clicked)
        nosave_button = QPushButton(text = "Don't Save")
        nosave_button.clicked.connect(self.accept)
        cancel_button = QPushButton(text = "Cancel")
        cancel_button.clicked.connect(self.reject)

        label_layout = QHBoxLayout()
        label_layout.addWidget(label)
        label_layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(nosave_button)
        button_layout.addWidget(cancel_button)

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addLayout(label_layout)
        layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)

    """
    Handler for when user clicks "Save" on the dialog.
    This function is necessary as the user might click "Cancel" while the file 
    dialog shows. In this case, we do not close the application to avoid 
    unwanted loss of data.
    """
    def save_clicked(self):
        if self.save_project():
            self.accept()

    """
    Saving the project. Prompts a file dialog if no path is in the project.
    @return True (project saved successfully) / False (project not saved).
    """
    def save_project(self):
        if self._project.path:
            self._project.save_json(self._project.path)
            self.window().setWindowModified(False)
            return True
        else:
            filename, _ = QFileDialog.getSaveFileName(\
                caption = "Create a project file", \
                filter = "SCP File (*.scp)", directory = self._project.name + \
                ".scp")
            if filename:
                self._project.save_json(filename)
                self.window().setWindowModified(False)
                return True
            return False
        
class NoSlideErrorDialog(QDialog):
    # This dialog shows when the user attempts to proceed to Step2 without 
    # adding any slides.
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Error")

        label = QLabel(text = \
                       "Please add at least one slide before proceeding!")

        ok_button = QPushButton(text = "Ok")
        ok_button.clicked.connect(self.accept)
        label_layout = QHBoxLayout()
        label_layout.addWidget(label)
        label_layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(ok_button)

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addLayout(label_layout)
        layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)