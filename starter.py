#!/usr/bin/python
################################################################################
#
#   starter.py
#   Author: Roger Wang
#   Date: 2024-06-18
#
#   Starter is a QWidget that contains all elements of the Starter screen.
#
################################################################################

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from project import *
from projectverifier import *

class Starter(QWidget):
    continue_clicked = pyqtSignal(Project)

    def __init__(self, parent, resolution, color):
        super().__init__(parent)
        self._project = None
        self._resolution = resolution
        self._color = color

        self._layout = self._get_starter()
        self.setLayout(self._layout)

    """
    Get the loaded project.
    @return Project object.
    """
    def get_project(self):
        return self._project

    """
    Get the current resolution setting.
    @return float, the current resolution setting.
    """
    def get_resolution(self):
        return self._resolution

    """
    Get the current color for displaying the selections during Step2.
    @return QColor.
    """
    def get_color(self):
        return self._color

    """
    Return a QVBoxLayout that is the start up screen.
    @return QLayout, the requeted layout.
    """
    def _get_starter(self):
        # Getting sublayouts.
        starter_header_layout = self._get_starter_header()
        starter_main_layout = self._get_starter_main()

        starter_footer = QLabel(text = "Roger Wang")

        starter_layout = QVBoxLayout()
        starter_layout.addLayout(starter_header_layout)
        starter_layout.addLayout(starter_main_layout)
        starter_layout.addWidget(starter_footer)

        return starter_layout

    """
    Return a QHBoxLayout that is the header section during start up.
    @return QLayout, the requeted layout.
    """
    def _get_starter_header(self):
        logo = QPixmap()
        logo_label = QLabel()
        logo_label.setPixmap(logo)
        subtitle = QLabel(text = "Welcome!")
        settings_button = QPushButton(text = "Settings")
        settings_button.clicked.connect(self.settings_button_clicked)
        info_button = QPushButton(text = "Information")

        header_layout = QHBoxLayout()
        header_layout.addWidget(logo_label)
        header_layout.addWidget(subtitle)
        header_layout.addStretch()
        header_layout.addWidget(settings_button)
        header_layout.addWidget(info_button)

        return header_layout

    """
    Return a QHBoxLayout that is the main section during start up.
    @return QLayout, the requeted layout.
    """
    def _get_starter_main(self):
        # Widgets and layouts for the "New Project" section.
        new_title_label = QLabel(text = "New Project")
        new_subtitle_label = QLabel(text = \
            "Create a new project and import your slide images.")
        new_name_label = QLabel(text = "Project Name: ")
        self.new_name_lineedit = QLineEdit()
        new_index_label = QLabel(text = "Selections Per Slide: ")
        self.new_index_spinbox = QSpinBox()
        self.new_index_spinbox.setMinimum(1)
        self.new_index_spinbox.setMaximum(128)
        self.new_index_spinbox.setValue(6)
        new_size_label = QLabel(text = "Default Selection Size: ")
        self.new_size_width_lineedit = QLineEdit()
        self.new_size_width_lineedit.setFixedWidth(60)
        self.new_size_width_lineedit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.new_size_width_lineedit.setValidator(QIntValidator(2, 100000))
        self.new_size_width_lineedit.setText("4000")
        new_size_sublabel_1 = QLabel(text = "px  x")
        self.new_size_height_lineedit = QLineEdit()
        self.new_size_height_lineedit.setFixedWidth(60)
        self.new_size_height_lineedit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.new_size_height_lineedit.setValidator(QIntValidator(2, 100000))
        self.new_size_height_lineedit.setText("4000")
        new_size_sublabel_2 = QLabel(text = "px")
        new_button = QPushButton(text = "Create")
        new_button.clicked.connect(self.new_button_clicked)

        new_title_layout = QHBoxLayout()
        new_title_layout.addStretch()
        new_title_layout.addWidget(new_title_label)
        new_title_layout.addStretch()

        new_name_layout = QHBoxLayout()
        new_name_layout.addWidget(new_name_label)
        new_name_layout.addWidget(self.new_name_lineedit)

        new_index_layout = QHBoxLayout()
        new_index_layout.addWidget(new_index_label)
        new_index_layout.addWidget(self.new_index_spinbox)
        new_index_layout.addStretch()

        new_size_layout = QHBoxLayout()
        new_size_layout.addWidget(new_size_label)
        new_size_layout.addWidget(self.new_size_width_lineedit)
        new_size_layout.addWidget(new_size_sublabel_1)
        new_size_layout.addWidget(self.new_size_height_lineedit)
        new_size_layout.addWidget(new_size_sublabel_2)
        new_size_layout.addStretch()

        new_button_layout = QHBoxLayout()
        new_button_layout.addStretch()
        new_button_layout.addWidget(new_button)
        new_button_layout.addStretch()

        new_layout = QVBoxLayout()
        new_layout.addLayout(new_title_layout)
        new_layout.addWidget(new_subtitle_label)
        new_layout.addLayout(new_name_layout)
        new_layout.addLayout(new_index_layout)
        new_layout.addLayout(new_size_layout)
        new_layout.addLayout(new_button_layout)
        new_layout.addStretch()

        # Widgets and layouts for the "Open Project" section.

        open_title_label = QLabel(text = "Open Project")
        open_subtitle_label = QLabel(text = "Open an existing project.")
        open_button = QPushButton(text = "Select")
        open_button.clicked.connect(self.open_button_clicked)

        open_title_layout = QHBoxLayout()
        open_title_layout.addStretch()
        open_title_layout.addWidget(open_title_label)
        open_title_layout.addStretch()

        open_button_layout = QHBoxLayout()
        open_button_layout.addStretch()
        open_button_layout.addWidget(open_button)
        open_button_layout.addStretch()

        open_layout = QVBoxLayout()
        open_layout.addLayout(open_title_layout)
        open_layout.addWidget(open_subtitle_label)
        open_layout.addLayout(open_button_layout)
        open_layout.addStretch()

        # Building the main layout.

        main_layout = QHBoxLayout()
        main_layout.addSpacing(50)
        main_layout.addLayout(new_layout)
        main_layout.addSpacing(50)
        main_layout.addLayout(open_layout)
        main_layout.addSpacing(50)
        main_layout.setStretch(1, 1)
        main_layout.setStretch(3, 1)

        return main_layout

    """
    Handler for when the user clicks the button that creates a new project.
    """
    def new_button_clicked(self):
        # Checking that the project name is not empty.
        if not self.new_name_lineedit.text():
            dialog = NoNameErrorDialog()
            dialog.exec()
            return
        
        if not self._project:
            self._project = Project()
        self._project.name = self.new_name_lineedit.text()
        self._project.path = ""
        self._project.saved = False
        self._project.slides = []
        self._project.work_index = 1
        self._project.selection = self.new_index_spinbox.value()
        self._project.width = int(self.new_size_width_lineedit.text())
        self._project.height = int(self.new_size_height_lineedit.text())

        self.continue_clicked.emit(self._project)

    """
    Handler for when the user clicks the button that opens an existing project.
    """
    def open_button_clicked(self):
        dialog = QFileDialog()
        filename, _ = dialog.getOpenFileName(\
            caption = "Select a project file", \
            filter = "SCP File (*.scp)")

        if filename:
            if not self._project:
                self._project = Project()
            self._project.load_json(filename)

            # Verifying that all paths in the Project exist.
            verifier = ProjectVerifier(self._project)
            if verifier.verify():
                self._project.generate_previews(self._resolution)
                self.continue_clicked.emit(self._project)

    """
    Handler for when the user on the button that changes the program's settings.
    """
    def settings_button_clicked(self):
        settings_edit_dialog = SettingsEditDialog(self._resolution, \
                                                  self._color)
        settings_edit_dialog.settings_changed.connect(\
            self.settings_changed_handler)
        settings_edit_dialog.exec()

    """
    Handler for when the program's settings are changed.
    """ 
    def settings_changed_handler(self, resolution, color):
        self._resolution = resolution
        self._color = color

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
        self.color_button.setAutoFillBackground(True)
        self.color_button.setFixedWidth(50)
        self.color_button.clicked.connect(self.color_button_clicked)
        self.color_button.setStyleSheet("background-color: rgb(%d, %d, %d)" \
                                        %(self._color.red(), \
                                          self._color.green(), \
                                          self._color.blue()))

        apply_button = QPushButton(text = "Apply")
        apply_button.clicked.connect(self.accept)
        apply_button.setDefault(True)
        cancel_button = QPushButton(text = "Cancel")
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