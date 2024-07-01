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

from access import *
from dialog import *
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
        if self._project:
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
        else:
            self._step_1.set_resolution(self._resolution)
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
            self._step_2.set_color(self._color)
            self._step_2.set_resolution(self._resolution)
            self._step_2.set_selection_size(self._project.width, \
                                            self._project.height)
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
