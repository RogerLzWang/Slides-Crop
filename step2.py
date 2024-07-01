#!/usr/bin/python
################################################################################
#
#   step2.py
#   Author: Roger Wang
#   Date: 2024-06-18
#
#   Step2 is a QWidget that contains all elements of the Step2 screen.
#
################################################################################

import darkdetect
import os

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from access import *
from dialog import *
from slideviewer import *
from stepheader import *

BASEDIR = os.path.dirname(__file__)

class Step2(QWidget):
    back_clicked = pyqtSignal()
    project_edited = pyqtSignal()
    returned = pyqtSignal()

    def __init__(self, parent, project, color, resolution):
        super().__init__(parent)
        self._project = project
        self._selection_width = project.width
        self._selection_height = project.height
        self._color = color
        self._resolution = resolution

        self._layout = self._get_step_2(self._project.work_index)
        self.setLayout(self._layout)
        self._slide_viewer.setFocus()

    """
    Get the current, stored project in Step1.
    @return Project object.
    """
    def get_project(self):
        return self._project

    """
    Set the color used for displaying selecitons.
    @param color: QColor object.
    """
    def set_color(self, color):
        self._color = color
    
    """
    Set the resolution used to generate the Slides' previews.
    @param resolution: float, the resolution of the Slides' previews.
    """
    def set_resolution(self, resolution):
        self._resolution = resolution

    """
    Set the selection size.
    @param width: int, the width of the selection.
    @param height: int, the height of the selection.
    """
    def set_selection_size(self, width, height):
        self._selection_width = width
        self._selection_height = height

    """
    Return a QVBoxLayout that is the layout for step 2.
    @param index: int, the index of the current working slide.
    @return QLayout, the requeted layout.
    """
    def _get_step_2(self, index):
        self._header = StepHeader(self, self._project, 2)
        self._header.project_edited.connect(self.project_edited_handler)
        self._header.returned.connect(self.returned_handler)
        main_layout = self._get_step_2_main(index)
        footer_layout = self._get_step_2_footer(index)

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
    Return a QHBoxLayout that is the layout for the main section during step 2.
    @param index: int, the index of the current working slide.
    @return QLayout, the requeted layout.
    """
    def _get_step_2_main(self, index):
        self._slide_viewer = SlideViewer(self, self._color)
        self._slide_viewer.set_resolution(self._resolution)
        self._slide_viewer.set_selection_size(self._project.width, \
                                              self._project.height)
        self._image_index_label = QLabel()
        self._image_index_label.setObjectName("TitleLabel")
        self._image_title_label = QLabel()
        self._image_size_label = QLabel()
        self._image_selection_label = QLabel()
        self._image_selection_size_label = QLabel()
        image_selection_size_button = QPushButton(text = "Edit")
        image_selection_size_button.setCursor(\
            QCursor(Qt.CursorShape.PointingHandCursor))
        image_selection_size_button.clicked.connect(\
            self._image_selection_size_button_clicked)

        main_selection_size_layout = QHBoxLayout()
        main_selection_size_layout.addWidget(self._image_selection_size_label)
        main_selection_size_layout.addWidget(image_selection_size_button)
        main_selection_size_layout.addStretch()

        main_sublayout = QVBoxLayout()
        main_sublayout.addWidget(self._image_index_label)
        main_sublayout.addSpacing(10)
        main_sublayout.addWidget(self._image_title_label)
        main_sublayout.addSpacing(10)
        main_sublayout.addWidget(self._image_size_label)
        main_sublayout.addSpacing(10)
        main_sublayout.addWidget(self._image_selection_label)
        main_sublayout.addLayout(main_selection_size_layout)
        main_sublayout.addStretch()

        main_sublayout_widget = QWidget()
        main_sublayout_widget.setFixedWidth(300)
        main_sublayout_widget.setLayout(main_sublayout)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self._slide_viewer)
        main_layout.addWidget(main_sublayout_widget)

        self._update_step_2_main(index)
        self._slide_viewer.project_edited.connect(self.project_edited_handler)

        return main_layout

    """
    Update the layout of the main section when the displayed slide changes or 
    when the selection size changes.
    @param index: int, the index of the current working slide.
    """
    def _update_step_2_main(self, index):
        slide = self._project.slides[index - 1]
        self._slide_viewer.set_slide(slide)
        self._image_index_label.setText("%d / %d" \
                                        %(index, len(self._project.slides)))
        self._image_title_label.setText(slide.file_name)
        self._image_size_label.setText("Image: %d px x %d px" \
                                       %(slide.width, slide.height))
        self.update_selection_label()
        self.update_selection_size_label()

    """
    Return a QHBoxLayout that is the layout for the footer during step 2.
    @param index: int, the index of the current working slide.
    @return QLayout, the requeted layout.
    """
    def _get_step_2_footer(self, index):
        back_button = QPushButton(text = "Back")
        back_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        back_button.clicked.connect(self._back_button_clicked)
        self.previous_button = QPushButton()
        if darkdetect.isDark():
            self.previous_button.setIcon(QIcon(\
                os.path.join(BASEDIR, "svg", "dark", "arrow-left-circle.svg")))
        else:
            self.previous_button.setIcon(QIcon(\
                os.path.join(BASEDIR, "svg", "arrow-left-circle.svg")))
        self.previous_button.setCursor(\
            QCursor(Qt.CursorShape.PointingHandCursor))
        self.next_button = QPushButton()
        if darkdetect.isDark():
            self.next_button.setIcon(QIcon(
                os.path.join(BASEDIR, "svg", "dark", "arrow-right-circle.svg")))
        else:
            self.next_button.setIcon(QIcon(\
                os.path.join(BASEDIR, "svg", "arrow-right-circle.svg")))
        self.next_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        export_button = ExportToolButton()
        export_button.clicked.connect(self.export)
        export_button.export_all.connect(self.export_all)

        # Connecting buttons.
        self.next_button.clicked.connect(self._next_button_clicked)
        self.previous_button.clicked.connect(self._previous_button_clicked)

        footer_layout = QHBoxLayout()
        footer_layout.addStretch()
        footer_layout.addWidget(back_button)
        footer_layout.addWidget(self.previous_button)
        footer_layout.addWidget(self.next_button)
        footer_layout.addWidget(export_button)

        self._update_step_2_footer(index)

        return footer_layout
    
    """
    Update the layout of the footer section when the displayed slide changes. 
    The next or previous buttons need to be disabled accordingly.
    @param index: int, the index of the current working slide.
    """
    def _update_step_2_footer(self, index):
        # Disabling buttons if necessary.
        if index == 1:
            self.previous_button.setEnabled(False)
            if darkdetect.isDark():
                self.previous_button.setIcon(QIcon(os.path.join(\
                    BASEDIR, "svg", "dark", "arrow-left-circle-disabled.svg")))
            else:
                self.previous_button.setIcon(QIcon(os.path.join(\
                    BASEDIR, "svg", "arrow-left-circle-disabled.svg")))
        else:
            self.previous_button.setEnabled(True)
            if darkdetect.isDark():
                self.previous_button.setIcon(QIcon(os.path.join(\
                    BASEDIR, "svg", "dark", "arrow-left-circle.svg")))
            else:
                self.previous_button.setIcon(QIcon(os.path.join(\
                    BASEDIR, "svg", "arrow-left-circle.svg")))
        if index == len(self._project.slides):
            self.next_button.setEnabled(False)
            if darkdetect.isDark():
                self.next_button.setIcon(QIcon(os.path.join(\
                    BASEDIR, "svg", "dark", "arrow-right-circle-disabled.svg")))
            else:
                self.next_button.setIcon(QIcon(os.path.join(\
                    BASEDIR, "svg", "arrow-right-circle-disabled.svg")))
        else:
            self.next_button.setEnabled(True)
            if darkdetect.isDark():
                self.next_button.setIcon(QIcon(os.path.join(\
                    BASEDIR, "svg", "dark", "arrow-right-circle.svg")))
            else:
                self.next_button.setIcon(QIcon(os.path.join(\
                    BASEDIR, "svg", "arrow-right-circle.svg")))
    
    """
    Update the project title and the layouts for the main and footer sections.
    Note that this function is always called by MainWindow when returning to 
    Step2 to ensure the accuracy of the information displayed.
    """
    def update(self):
        self._slide_viewer.set_selection_size(self._selection_width, \
                                              self._selection_height)
        self._slide_viewer.set_color(self._color)
        self._slide_viewer.set_resolution(self._resolution)
        self._header.update_title()
        self._update_step_2_main(self._project.work_index)
        self._update_step_2_footer(self._project.work_index)

    """
    Update the label displaying the number of selections made.
    """
    def update_selection_label(self):
        self._image_selection_label.setText("%d / %d Selections" \
                                            %(len(self._project.slides[\
                                            self._project.work_index - 1].\
                                            selections), \
                                            self._project.selection))
    
    """
    Update the label displaying the selection size.
    """
    def update_selection_size_label(self):
        self._image_selection_size_label.setText("Selection: %d px x %d px" \
                                                 %(self._selection_width, \
                                                   self._selection_height))

    """
    Update the selection size and the label displaying this information.
    @param width: int, the new width for selections.
    @param height: int, the new height for selections.
    """
    def update_selection_size(self, width, height):
        self._selection_width = width
        self._selection_height = height
        self.update_selection_size_label()
        self._slide_viewer.set_selection_size(width, height)

    """
    Update the selection size for all existing selections and the label 
    displaying this information.
    @param width: int, the new width for selections.
    @param height: int, the new height for selections.
    """
    def update_all_selection_size(self, width, height):
        for slide in self._project.slides:
            slide.set_selection_size(width, height)
        self._selection_width = width
        self._selection_height = height
        self._slide_viewer.set_selection_size(width, height)
        self.update()
        self.project_edited.emit()

    """
    Handler for when the Export button has been clicked.
    """
    def export(self):
        dialog = QFileDialog()
        directory = dialog.getExistingDirectory(\
            caption = "Select Output Directory", \
            options = QFileDialog.Option.ShowDirsOnly)
        if directory:
            # Check if the directory can be written to.
            if Access.check_dir_write(directory):
                dialog = ExportDirectoryErrorDialog()
                dialog.exec()
                return
            
            # Setting up the dialog and the worker thread.
            self.dialog = ProgressDialog("Exporting", 1)

            self.export_thread = QThread()
            self.export_thread.finished.connect(self.export_thread.deleteLater)
            self.worker = ExportWorker([self._project.slides[\
                self._project.work_index - 1]], directory)
            self.worker.progress.connect(self.dialog.update)
            self.worker.finished.connect(self.dialog.accept)
            self.worker.finished.connect(self.export_thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.dialog.rejected.connect(self.worker.stop)
            self.worker.moveToThread(self.export_thread)
            self.export_thread.started.connect(self.worker.run)

            self.export_thread.start()
            if not self.dialog.exec():
                # If the thread is killed by the user, wait for it to finish.
                self.export_thread.terminate()
                if not self.export_thread.wait(10000):
                    self.export_thread.terminate()
                    self.export_thread.wait(10000)
                return
            
            if not self.export_thread.wait(10000):
                self.export_thread.quit()
                self.export_thread.wait(10000)
            failed = self.worker.get_failed()
            if failed:
                dialog = ExportErrorDialog(failed)
                dialog.exec()

    """
    Handler for when the Export All button has been clicked.
    """
    def export_all(self):
        dialog = QFileDialog()
        directory = dialog.getExistingDirectory(\
            caption = "Select Output Directory", \
            options = QFileDialog.Option.ShowDirsOnly)
        if directory:
            # Check if the directory can be written to.
            if Access.check_dir_write(directory):
                dialog = ExportDirectoryErrorDialog()
                dialog.exec()
                return
            
            # Setting up the dialog and the worker thread.
            self.dialog = ProgressDialog("Exporting", len(self._project.slides))

            self.export_thread = QThread()
            self.export_thread.finished.connect(self.export_thread.deleteLater)
            self.worker = ExportWorker(self._project.slides, directory)
            self.worker.progress.connect(self.dialog.update)
            self.worker.finished.connect(self.dialog.accept)
            self.worker.finished.connect(self.export_thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.dialog.rejected.connect(self.worker.stop)
            self.worker.moveToThread(self.export_thread)
            self.export_thread.started.connect(self.worker.run)

            self.export_thread.start()
            if not self.dialog.exec():
                # If the thread is killed by the user, wait for it to finish.
                self.export_thread.terminate()
                if not self.export_thread.wait(10000):
                    self.export_thread.terminate()
                    self.export_thread.wait(10000)
                return
            
            if not self.export_thread.wait(10000):
                self.export_thread.quit()
                self.export_thread.wait(10000)
            failed = self.worker.get_failed()
            if failed:
                dialog = ExportErrorDialog(failed)
                dialog.exec()

    """
    Handler for when the Back button has been clicked.
    """
    def _back_button_clicked(self):
        self.back_clicked.emit()

    """
    Handler for when the Previous button has been clicked to go back a slide.
    """
    def _previous_button_clicked(self):
        self._project.work_index -= 1
        self.update()

    """
    Handler for when the Next button has been clicked to go to the next slide.
    """
    def _next_button_clicked(self):
        self._project.work_index += 1
        self.update()

    """
    Handler for when the user wishes to change the selection size.
    This function prompts a SelectionSizeDialog to ask for changes.
    """
    def _image_selection_size_button_clicked(self):
        selection_size_dialog = SelectionSizeDialog(self._selection_width, \
                                                    self._selection_height)
        selection_size_dialog.apply_clicked.connect(self.update_selection_size)
        selection_size_dialog.applyall_clicked.connect(\
            self.update_all_selection_size)
        selection_size_dialog.exec()

    """
    Handler for when the Project has been edited.
    Notice that the label displaying the number of selections made will also be 
    updated with this function.
    """
    def project_edited_handler(self):
        self.project_edited.emit()
        self.update_selection_label()

    """
    Handler for when the return procedure is completed and the program should 
    return to the starter.
    """
    def returned_handler(self):
        self.returned.emit()

class ExportToolButton(QToolButton):
    # The Export button and Export All button is implemented as a QToolButton 
    # in order to achieve the drop-down effect.
    export_all = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        if darkdetect.isDark():
            self.setIcon(QIcon(\
                os.path.join(BASEDIR, "svg", "dark", "download.svg")))
        else:
            self.setIcon(QIcon(os.path.join(BASEDIR, "svg", "download.svg")))
        self.setText(" Export")
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)

        export_all_action = QAction("Export All", self)
        export_all_action.triggered.connect(self.export_all_triggered)

        menu = QMenu()
        menu.addAction(export_all_action)

        self.setMenu(menu)

    """
    Handler for when the user clicks "Export All".
    Note that when the "Export" is clicked, a clicked event can be accessed, so 
    no customized signal is necessary.
    """
    def export_all_triggered(self):
        self.export_all.emit()

class ExportWorker(QObject):
    # ExportWorker is a worker class for exporting slides.
    # This step is generally slow on larger images, which is why this task is 
    # separated to prevent freezing the GUI.

    progress = pyqtSignal(int)
    finished = pyqtSignal()
    
    def __init__(self, slides, directory):
        super().__init__()
        self.failed = []
        self.slides = []

        self.set_slides(slides)
        self.set_directory(directory)

        # 0: Continue processing.
        # 1: Stop.
        self.status = 0
    
    """
    Get the images that failed to export.
    @return failed: list of str, the names of the images that failed to export.
    """
    def get_failed(self):
        return self.failed

    """
    Set the slides to be exported.
    @param slides: list of Slide objects, Slides to be exported.
    """
    def set_slides(self, slides):
        self.slides = slides

    """
    Set the destination for the export.
    @param directory: str, the directory for export.
    """
    def set_directory(self, directory):
        self.directory = directory

    """
    Execute the worker.
    """
    def run(self):
        self.failed = []
        for i in range(len(self.slides)):
            if not self.status:
                self.failed += self.slides[i].save_crops(self.directory)
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
