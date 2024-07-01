#!/usr/bin/python
################################################################################
#
#   dialog.py
#   Author: Roger Wang
#   Date: 2024-06-25
#
#   Collection of all the QDialogs needed in the application.
#
################################################################################

import darkdetect
import os
import webbrowser

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtSvgWidgets import *

from access import *

BASEDIR = os.path.dirname(__file__)

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
        save_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        save_button.clicked.connect(self.save_clicked)
        nosave_button = QPushButton(text = "Don't Save")
        nosave_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        nosave_button.clicked.connect(self.accept)
        cancel_button = QPushButton(text = "Cancel")
        cancel_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
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
        layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

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
                if Access.check_new_file_write(filename):
                    dialog = PermissionErrorDialog()
                    dialog.exec()
                    return False
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
        ok_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
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
        layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        self.setLayout(layout)

class PermissionErrorDialog(QDialog):
    # This dialog shows when the program fails to save to a given path.
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Error")

        label = QLabel(text = \
                       "Failed to write to given path! Project not saved.")

        ok_button = QPushButton(text = "Ok")
        ok_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
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
        layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        self.setLayout(layout)

class UnfoundItemActionDialog(QDialog):
    # This dialog is prompted when any of the Project's Slides are not found.
    # The dialog asks the user whether or not the Slides should be relocated, 
    # removed, or cancel loading the project altogether.

    locate_clicked = pyqtSignal()
    remove_clicked = pyqtSignal()
    
    def __init__(self, unfounds):
        super().__init__()
        self.setWindowTitle("Error")

        # Creating the text to be displayed.
        text = "The following %d slide images are not found:\n" %len(unfounds)
        for unfound in unfounds:
            text += unfound
            text += "\n"
        text += "Would you like to locate the images or "
        text += "remove them from the project?"

        label = QLabel(text = text)

        locate_button = QPushButton(text = "Locate")
        locate_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        locate_button.clicked.connect(self._locate_clicked_handler)
        remove_button = QPushButton(text = "Remove")
        remove_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        remove_button.clicked.connect(self._remove_clicked_handler)
        cancel_button = QPushButton(text = "Cancel")
        cancel_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cancel_button.clicked.connect(self.reject)

        label_layout = QHBoxLayout()
        label_layout.addWidget(label)
        label_layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(locate_button)
        button_layout.addWidget(remove_button)
        button_layout.addWidget(cancel_button)

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addLayout(label_layout)
        layout.addStretch()
        layout.addLayout(button_layout)
        layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        self.setLayout(layout)

    """
    Handler for if the user clicks the "Locate" button.
    """
    def _locate_clicked_handler(self):
        self.locate_clicked.emit()
        self.accept()
    
    """
    Handler for if the user clicks the "Remove" button.
    """
    def _remove_clicked_handler(self):
        self.remove_clicked.emit()
        self.accept()

class SettingsEditDialog(QDialog):
    settings_changed = pyqtSignal(float, QColor)

    def __init__(self, resolution, color):
        super().__init__()
        self.setWindowTitle("Settings")
        self._color = color

        # Preview resolution section.
        preview_label = QLabel(text = "Preview At: ")
        self.preview_100_button = QRadioButton(text = "100%")
        self.preview_50_button = QRadioButton(text = "50%")
        self.preview_25_button = QRadioButton(text = "25%")
        self.preview_10_button = QRadioButton(text = "10%")
        if resolution == 1:
            self.preview_100_button.setChecked(True)
        elif resolution == 0.5:
            self.preview_50_button.setChecked(True)
        elif resolution == 0.25:
            self.preview_25_button.setChecked(True)
        elif resolution == 0.1:
            self.preview_10_button.setChecked(True)
        self.preview_buttongroup = QButtonGroup()
        self.preview_buttongroup.addButton(self.preview_100_button)
        self.preview_buttongroup.addButton(self.preview_50_button)
        self.preview_buttongroup.addButton(self.preview_25_button)
        self.preview_buttongroup.addButton(self.preview_10_button)

        # Color section.
        color_label = QLabel(text = "Selection Color: ")
        self.color_button = QPushButton()
        self.color_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.color_button.setAutoFillBackground(True)
        self.color_button.setFixedWidth(50)
        self.color_button.clicked.connect(self.color_button_clicked)
        self.color_button.setStyleSheet("background-color: rgb(%d, %d, %d)" \
                                        %(self._color.red(), \
                                          self._color.green(), \
                                          self._color.blue()))

        apply_button = QPushButton(text = "Apply")
        apply_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        apply_button.clicked.connect(self.accept)
        apply_button.setDefault(True)
        cancel_button = QPushButton(text = "Cancel")
        cancel_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cancel_button.clicked.connect(self.reject)

        preview_layout = QHBoxLayout()
        preview_layout.addWidget(preview_label)
        preview_layout.addWidget(self.preview_100_button)
        preview_layout.addWidget(self.preview_50_button)
        preview_layout.addWidget(self.preview_25_button)
        preview_layout.addWidget(self.preview_10_button)
        preview_layout.addStretch()

        color_layout = QHBoxLayout()
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_button)
        color_layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(apply_button)
        button_layout.addWidget(cancel_button)

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addLayout(preview_layout)
        layout.addLayout(color_layout)
        layout.addStretch()
        layout.addLayout(button_layout)
        layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        self.setLayout(layout)

    """
    Handler for when the color change button is clicked.
    """ 
    def color_button_clicked(self):
        # Prompts a new dialog that gets the user's customized color.
        color = QColorDialog.getColor()
        if color.isValid():
            self._color = color
            self.color_button.setStyleSheet("background-color: rgb(%d, %d, %d)"\
                                            %(self._color.red(), \
                                            self._color.green(), \
                                            self._color.blue()))
    
    ############################################################################
    # The following section contains overridden functions to customize features.
    ############################################################################

    def accept(self):
        # New settings are emitted as a signal when the dialog is accepted.
        if self.preview_100_button.isChecked():
            self.settings_changed.emit(1, self._color)
        elif self.preview_50_button.isChecked():
            self.settings_changed.emit(0.5, self._color)
        elif self.preview_25_button.isChecked():
            self.settings_changed.emit(0.25, self._color)
        elif self.preview_10_button.isChecked():
            self.settings_changed.emit(0.1, self._color)
        super().accept()
    
class NoNameErrorDialog(QDialog):
    # This dialog shows when the user attempts to create a Project with no name.
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Error")

        label = QLabel(text = \
                       "The project's name cannot be empty!")

        ok_button = QPushButton(text = "Ok")
        ok_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
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
        layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        self.setLayout(layout)

class InfoDialog(QDialog):
    # This dialog shows when the user clicks on the information button.

    def __init__(self):
        super().__init__()

        self.setWindowTitle("About")

        if darkdetect.isDark():
            logo = QSvgWidget(os.path.join(BASEDIR, "svg", "dark", \
                                           "slides-crop.svg"))
        else:
            logo = QSvgWidget(os.path.join(BASEDIR, "svg", "slides-crop.svg"))
        logo.setFixedSize(50, 50)

        lab_logo = QPixmap(os.path.join(BASEDIR, "png", "epstein-lab.png"))
        lab_logo = lab_logo.scaled(50, 50)
        lab_label = QLabel()
        lab_label.setPixmap(lab_logo)
        lab_label.setFixedSize(50, 50)

        title = "Slides Crop"
        text_1 = "Version: 1.1.1"
        text_2 = "Originally Published: 2024-06-22"
        text_3 = "Last Updated: 2024-06-30"
        text_4 = "Author: Lizhou Roger Wang"
        text_5 = "Contact: rogerlzwang@gmail.com"
        text_6 = "Jonathan A. Epstein Lab @ Penn Medicine"

        title = QLabel(text = title)
        title.setObjectName("TitleLabel")
        label_1 = QLabel(text = text_1)
        label_2 = QLabel(text = text_2)
        label_3 = QLabel(text = text_3)
        label_4 = QLabel(text = text_4)
        label_5 = QLabel(text = text_5)
        label_6 = QLabel(text = text_6)

        line = QFrame()
        line.setObjectName("Line")
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFixedHeight(1)

        # Buttons for hyperlinks.
        github_button = QPushButton()
        github_button.setObjectName("LogoButton")
        github_button.setFixedSize(20, 20)
        github_button.setCursor(Qt.CursorShape.PointingHandCursor)
        github_button.clicked.connect(self.github_button_clicked)
        x_button = QPushButton()
        x_button.setObjectName("LogoButton")
        x_button.setFixedSize(20, 20)
        x_button.setCursor(Qt.CursorShape.PointingHandCursor)
        x_button.clicked.connect(self.x_button_clicked)
        x_lab_button = QPushButton()
        x_lab_button.setObjectName("LogoButton")
        x_lab_button.setFixedSize(20, 20)
        x_lab_button.setCursor(Qt.CursorShape.PointingHandCursor)
        x_lab_button.clicked.connect(self.x_lab_button_clicked)
        if darkdetect.isDark():
            github_button.setIcon(QIcon(os.path.join(BASEDIR, "svg", "dark", \
                                                     "github.svg")))
            x_button.setIcon(QIcon(os.path.join(BASEDIR, "svg", "dark", \
                                                "x.svg")))
            x_lab_button.setIcon(QIcon(os.path.join(BASEDIR, "svg", "dark", \
                                                    "x-lab.svg")))
        else:
            github_button.setIcon(QIcon(os.path.join(BASEDIR, "svg", \
                                                     "github.svg")))
            x_button.setIcon(QIcon(os.path.join(BASEDIR, "svg", "x.svg")))
            x_lab_button.setIcon(QIcon(os.path.join(BASEDIR, "svg", \
                                                    "x-lab.svg")))
        github_button.setIconSize(QSize(20, 20))
        x_button.setIconSize(QSize(20, 20))
        x_lab_button.setIconSize(QSize(20, 20))

        logo_layout = QHBoxLayout()
        logo_layout.addStretch()
        logo_layout.addWidget(logo)
        logo_layout.addSpacing(10)
        logo_layout.addWidget(lab_label)
        logo_layout.addStretch()

        title_layout = QHBoxLayout()
        title_layout.addStretch()
        title_layout.addWidget(title)
        title_layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(github_button)
        button_layout.addSpacing(10)
        button_layout.addWidget(x_button)
        button_layout.addSpacing(10)
        button_layout.addWidget(x_lab_button)
        button_layout.addStretch()
        

        layout = QVBoxLayout()
        layout.addLayout(logo_layout)
        layout.addSpacing(10)
        layout.addLayout(title_layout)
        layout.addSpacing(10)
        layout.addWidget(label_1)
        layout.addWidget(label_2)
        layout.addWidget(label_3)
        layout.addSpacing(10)
        layout.addWidget(label_4)
        layout.addWidget(label_5)
        layout.addSpacing(10)
        layout.addWidget(label_6)
        layout.addSpacing(5)
        layout.addWidget(line)
        layout.addSpacing(5)
        layout.addLayout(button_layout)

        layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        self.setLayout(layout)

    """
    Handler for when the GitHub button is clicked.
    """
    def github_button_clicked(self):
        webbrowser.open("https://github.com/RogerLzWang")

    """
    Handler for when the X button is clicked.
    """
    def x_button_clicked(self):
        webbrowser.open("https://x.com/RogerLzWang")

    """
    Handler for when the X (lab) button is clicked.
    """
    def x_lab_button_clicked(self):
        webbrowser.open("https://x.com/JonEpsteinLab")

class SelectionSizeDialog(QDialog):
    # The SelectionSizeDialog prompts when the user wishes to change the 
    # selection size, either for the next selection made or to change the size 
    # of all previous selections.
    apply_clicked = pyqtSignal(int, int)
    applyall_clicked = pyqtSignal(int, int)

    def __init__(self, width, height):
        super().__init__()
        self.setWindowTitle("Selection Size")

        self.width_lineedit = QLineEdit()
        self.width_lineedit.setContextMenuPolicy(\
            Qt.ContextMenuPolicy.NoContextMenu)
        self.width_lineedit.setFixedWidth(60)
        self.width_lineedit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.width_lineedit.setValidator(QIntValidator(2, 100000))
        self.width_lineedit.setText(str(width))

        label_1 = QLabel(text = "px  x")

        self.height_lineedit = QLineEdit()
        self.height_lineedit.setContextMenuPolicy(\
            Qt.ContextMenuPolicy.NoContextMenu)
        self.height_lineedit.setFixedWidth(60)
        self.height_lineedit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.height_lineedit.setValidator(QIntValidator(2, 100000))
        self.height_lineedit.setText(str(height))

        label_2 = QLabel(text = "px")
        
        cancel_button = QPushButton(text = "Cancel")
        cancel_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cancel_button.clicked.connect(self.reject)
        apply_button = QPushButton(text = "Apply")
        apply_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        apply_button.clicked.connect(self.apply_clicked_handler)
        apply_button.setDefault(True)
        applyall_button = QPushButton(text = "Apply to All")
        applyall_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        applyall_button.clicked.connect(self.applyall_clicked_handler)

        size_layout = QHBoxLayout()
        size_layout.addWidget(self.width_lineedit)
        size_layout.addWidget(label_1)
        size_layout.addWidget(self.height_lineedit)
        size_layout.addWidget(label_2)
        size_layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addWidget(cancel_button)
        button_layout.addStretch()
        button_layout.addWidget(apply_button)
        button_layout.addWidget(applyall_button)

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addLayout(size_layout)
        layout.addStretch()
        layout.addLayout(button_layout)
        layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        self.setLayout(layout)

    """
    Handler for when the user clicks "Apply".
    """
    def apply_clicked_handler(self):
        self.apply_clicked.emit(int(self.width_lineedit.text()), \
                                int(self.height_lineedit.text()))
        self.close()
        
    """
    Handler for when the user clicks "Apply All".
    """
    def applyall_clicked_handler(self):
        self.applyall_clicked.emit(int(self.width_lineedit.text()), \
                                   int(self.height_lineedit.text()))
        self.close()

class ExportDirectoryErrorDialog(QDialog):
    # This dialog shows when the export directory chosen by the user cannot be 
    # written to.
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Error")

        label = QLabel(text = \
                       "Failed to write to the given directory! " + \
                       "No files exported.")

        ok_button = QPushButton(text = "Ok")
        ok_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
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
        layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        self.setLayout(layout)

class ExportErrorDialog(QDialog):
    # This dialog shows when some exports have failed.
    def __init__(self, failed):
        super().__init__()
        self.setWindowTitle("Error")

        text = "The following files have failed to export:"

        for item in failed:
            text += "\n"
            text += item

        label = QLabel(text = text)

        ok_button = QPushButton(text = "Ok")
        ok_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
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
        layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        self.setLayout(layout)

class ProjectEditDialog(QDialog):
    # The ProjectEditDialog is prompted when the user clicks the "Settings" 
    # button during Step1 or Step2.

    project_edited = pyqtSignal()

    def __init__(self, project):
        super().__init__()
        self.setWindowTitle("Edit Project")
        self._project = project

        name_label = QLabel(text = "Project Name: ")
        self.name_lineedit = QLineEdit()
        self.name_lineedit.setContextMenuPolicy(\
            Qt.ContextMenuPolicy.NoContextMenu)
        self.name_lineedit.setText(self._project.name)

        index_label = QLabel(text = "Selections Per Slide: ")
        self.index_spinbox = QSpinBox()
        self.index_spinbox.setCursor(Qt.CursorShape.PointingHandCursor)
        self.index_spinbox.setContextMenuPolicy(\
            Qt.ContextMenuPolicy.NoContextMenu)
        self.index_spinbox.setMinimum(1)
        self.index_spinbox.setMaximum(128)
        self.index_spinbox.setValue(self._project.selection)

        size_label_1 = QLabel(text = "Default Selection Size: ")

        self.width_lineedit = QLineEdit()
        self.width_lineedit.setContextMenuPolicy(\
            Qt.ContextMenuPolicy.NoContextMenu)
        self.width_lineedit.setFixedWidth(60)
        self.width_lineedit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.width_lineedit.setValidator(QIntValidator(2, 100000))
        self.width_lineedit.setText(str(self._project.width))

        size_label_2 = QLabel(text = "px  x")

        self.height_lineedit = QLineEdit()
        self.height_lineedit.setContextMenuPolicy(\
            Qt.ContextMenuPolicy.NoContextMenu)
        self.height_lineedit.setFixedWidth(60)
        self.height_lineedit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.height_lineedit.setValidator(QIntValidator(2, 100000))
        self.height_lineedit.setText(str(self._project.height))

        size_label_3 = QLabel(text = "px")
        
        apply_button = QPushButton(text = "Apply")
        apply_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        apply_button.clicked.connect(self.accept)
        cancel_button = QPushButton(text = "Cancel")
        cancel_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cancel_button.clicked.connect(self.reject)

        name_layout = QHBoxLayout()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_lineedit)
        name_layout.addStretch()

        index_layout = QHBoxLayout()
        index_layout.addWidget(index_label)
        index_layout.addWidget(self.index_spinbox)
        index_layout.addStretch()

        size_layout = QHBoxLayout()
        size_layout.addWidget(size_label_1)
        size_layout.addWidget(self.width_lineedit)
        size_layout.addWidget(size_label_2)
        size_layout.addWidget(self.height_lineedit)
        size_layout.addWidget(size_label_3)
        size_layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(apply_button)
        button_layout.addWidget(cancel_button)

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addLayout(name_layout)
        layout.addLayout(index_layout)
        layout.addLayout(size_layout)
        layout.addStretch()
        layout.addLayout(button_layout)
        layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        self.setLayout(layout)

    ############################################################################
    # The following section contains overridden functions to customize features.
    ############################################################################

    def accept(self):
        # When the dialog is accepted, update all settings in the Project 
        # before closing.
        self._project.name = self.name_lineedit.text()
        self._project.selection = self.index_spinbox.value()
        self._project.width = int(self.width_lineedit.text())
        self._project.height = int(self.height_lineedit.text())
        self.project_edited.emit()
        super().accept()

class ReturnSaveDialog(QDialog):
    # The ReturnSaveDialog is prompted when the user clicks the return button 
    # but unsaved changes are present.

    project_saved = pyqtSignal()

    def __init__(self, project):
        super().__init__()
        self.setWindowTitle("Close Project")
        self._project = project

        label = QLabel(text = \
                       "Would you like to save the project before returning?")

        save_button = QPushButton(text = "Save")
        save_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        save_button.clicked.connect(self.save_clicked)
        nosave_button = QPushButton(text = "Don't Save")
        nosave_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        nosave_button.clicked.connect(self.accept)
        cancel_button = QPushButton(text = "Cancel")
        cancel_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
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
        layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        self.setLayout(layout)

    """
    Handler for when the user clicks "Save".
    If no path has been set for the project, prompt a QFileDialog to determine 
    the path of the project.
    """
    def save_clicked(self):
        if self._project.path:
            self._project.save_json(self._project.path)
            self.project_saved.emit()
            self.accept()
        else:
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
                self.project_saved.emit()
                self.accept()

class ProgressDialog(QDialog):
    # ProgressDialog is a generic dialog for displaying a task with a 
    # progress bar. Using this with QThread is necessary.

    def __init__(self, title, total):
        super().__init__()
        self.setWindowTitle(title)

        self.current = 0
        self.total = total

        self._progress_bar = QProgressBar()
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setMaximum(total)
        self._progress_bar.setFixedWidth(300)

        self._label = QLabel()
        self.update(0)

        cancel_button = QPushButton(text = "Cancel")
        cancel_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cancel_button.clicked.connect(self.reject)

        progress_layout = QHBoxLayout()
        progress_layout.addWidget(self._progress_bar)

        label_layout = QHBoxLayout()
        label_layout.addStretch()
        label_layout.addWidget(self._label)
        label_layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)

        layout = QVBoxLayout()
        layout.addLayout(progress_layout)
        layout.addLayout(label_layout)
        layout.addLayout(button_layout)
        layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        self.setLayout(layout)

    """
    Updates the current progress.
    @param current: int, index of the latest finished item.
    """
    def update(self, current):
        self.current = current
        self._progress_bar.setValue(current)

        self._label.setText(str(self.current) + " / " + str(self.total))
