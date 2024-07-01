#!/usr/bin/python
################################################################################
#
#   step1.py
#   Author: Roger Wang
#   Date: 2024-06-18
#
#   Step1 is a QWidget that contains all elements of the Step1 screen.
#
################################################################################

import darkdetect
import os

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from stepheader import *
from slidequeue import *

BASEDIR = os.path.dirname(__file__)

class Step1(QWidget):
    continue_clicked = pyqtSignal()
    project_edited = pyqtSignal()
    returned = pyqtSignal()

    def __init__(self, parent, project, resolution):
        super().__init__(parent)
        self._project = project
        self._slide_queue = None
        self._resolution = resolution

        self._layout = self._get_step_1()
        self.setLayout(self._layout)
        self._slide_queue.setFocus()

    """
    Get the current, stored project in Step1.
    @return Project object.
    """
    def get_project(self):
        return self._project
        
    """
    Set the resolution used to generate the Slides' previews.
    @param resolution: float, the resolution of the Slides' previews.
    """
    def set_resolution(self, resolution):
        self._resolution = resolution

    """
    Update the project title and the slides.
    Note that this function is always called by MainWindow when returning to 
    Step1 to ensure the accuracy of the information displayed.
    """
    def update(self):
        self._header.update_title()
        self._slide_queue.clear_slides()
        self._slide_queue.add_slides(self._project.slides)
    
    """
    Return a QVBoxLayout that is the layout for step 1.
    @return QLayout, the requeted layout.
    """
    def _get_step_1(self):
        self._header = StepHeader(self, self._project, 1)
        self._header.project_edited.connect(self.project_edited_emit)
        self._header.returned.connect(self.returned_handler)
        main_layout = self._get_step_1_main()
        footer_layout = self._get_step_1_footer()

        main = QWidget()
        main.setLayout(main_layout)
        footer = QWidget()
        footer.setLayout(footer_layout)

        layout = QVBoxLayout()
        layout.addWidget(self._header)
        layout.addWidget(main)
        layout.addWidget(footer)

        return layout

    """
    Return a QHBoxLayout that is the layout for the main section during step 1.
    @return QLayout, the requeted layout.
    """
    def _get_step_1_main(self):
        self._slide_queue = SlideQueue(self._project)
        self._slide_queue.project_edited.connect(self.project_edited_emit)
        self._slide_queue.add_slides(self._project.slides)

        add_button = QPushButton(text = " Add Slides")
        if darkdetect.isDark():
            add_button.setIcon(QIcon(os.path.join(BASEDIR, "svg", "dark", \
                                                  "plus.svg")))
        else:
            add_button.setIcon(QIcon(os.path.join(BASEDIR, "svg", "plus.svg")))
        add_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        add_button.clicked.connect(self.add_button_clicked)

        add_layout = QHBoxLayout()
        add_layout.addStretch()
        add_layout.addWidget(add_button)
        add_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self._slide_queue)
        main_layout.addLayout(add_layout)
        
        return main_layout
    
    """
    Return a QHBoxLayout that is the layout for the footer during step 1.
    @return QLayout, the requeted layout.
    """
    def _get_step_1_footer(self):
        continue_button = QPushButton(text = "Next")
        continue_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        continue_button.clicked.connect(self.continue_button_clicked)

        footer_layout = QHBoxLayout()
        footer_layout.addStretch()
        footer_layout.addWidget(continue_button)

        return footer_layout

    """
    Handler for when the user clicks the "Add Slides" button.
    """
    def add_button_clicked(self):
        dialog = QFileDialog()
        filenames, _ = dialog.getOpenFileNames(\
            caption = "Select one or more slide(s)", \
            filter = "Images (*.png *.jpg *.jpeg *.tif *.tiff)")

        if filenames:
            # Setting up the dialog and the worker thread.
            self.dialog = ProgressDialog("Loading", len(filenames))

            self.add_thread = QThread()
            self.add_thread.finished.connect(self.add_thread.deleteLater)
            self.worker = AddWorker(filenames, self._resolution)
            self.worker.progress.connect(self.dialog.update)
            self.worker.finished.connect(self.dialog.accept)
            self.worker.finished.connect(self.add_thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.dialog.rejected.connect(self.worker.stop)
            self.worker.moveToThread(self.add_thread)
            self.add_thread.started.connect(self.worker.run)

            self.add_thread.start()

            if self.dialog.exec():
                if not self.add_thread.wait(10000):
                    self.add_thread.quit()
                    self.add_thread.wait(10000)
                self._slide_queue.add_slides(self.worker.slides)
                self._project.slides += self.worker.slides
                self.project_edited.emit()
            else:
                # If the thread is killed by the user, wait for it to finish.
                self.add_thread.terminate()
                if not self.add_thread.wait(10000):
                    self.add_thread.terminate()
                    self.add_thread.wait(10000)

    """
    Handler for when the user clicks the "Continue" button.
    """
    def continue_button_clicked(self):
        self._project.slides = self._slide_queue.get_slides()
        self.continue_clicked.emit()

    """
    Handler for when the Project has been modified.
    """
    def project_edited_emit(self):
        self.project_edited.emit()

    """
    Handler for when the return procedure is completed and the program should 
    return to the starter.
    """
    def returned_handler(self):
        self.returned.emit()

class AddWorker(QObject):
    # AddWorker is a worker class for adding slides and generating previews.
    # This step is generally slow on larger images, which is why this task is 
    # separated to prevent freezing the GUI.

    progress = pyqtSignal(int)
    finished = pyqtSignal()
    
    def __init__(self, filenames, resolution):
        super().__init__()
        self.slides = []
        self.set_files(filenames)
        self._resolution = resolution
    
        # 0: Continue processing.
        # 1: Stop.
        self.status = 0
    
    """
    Set the files to be executed.
    @param filenames: list, string of paths to files to be processed.
    """
    def set_files(self, filenames):
        self.filenames = filenames

    """
    Execute the worker.
    """
    def run(self):
        self.slides = []
        for i in range(len(self.filenames)):
            if not self.status:
                self.slides.append(Slide(self.filenames[i]))
                self.slides[-1].generate_preview(self._resolution)
                self.progress.emit(i + 1)
            else:
                self.progress.emit(i + 1)
                continue
        self.finished.emit()

    """
    Stops the worker.
    """
    def stop(self):
        self.status = 1
