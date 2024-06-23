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

import darkdetect
import os
import webbrowser

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtSvgWidgets import *

from project import *
from projectverifier import *

BASEDIR = os.path.dirname(__file__)

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
        starter_footer_layout = self._get_starter_footer()

        starter_header = QWidget()
        starter_header.setLayout(starter_header_layout)

        starter_footer = QWidget()
        starter_footer.setLayout(starter_footer_layout)

        starter_layout = QVBoxLayout()
        starter_layout.addWidget(starter_header)
        starter_layout.addStretch(2)
        starter_layout.addLayout(starter_main_layout)
        starter_layout.addStretch(4)
        starter_layout.addWidget(starter_footer)

        return starter_layout

    """
    Return a QHBoxLayout that is the header section during start up.
    @return QLayout, the requeted layout.
    """
    def _get_starter_header(self):
        if darkdetect.isDark():
            logo = QSvgWidget(os.path.join(BASEDIR, "svg", "dark", \
                                           "slides-crop.svg"))
        else:
            logo = QSvgWidget(os.path.join(BASEDIR, "svg", "slides-crop.svg"))
        logo.setFixedSize(50, 50)
        title_label = QLabel(text = "Slides Crop")
        title_label.setObjectName("TitleLabel")
        subtitle_label = QLabel(\
            text = "Slide image cropping tool for histology analysis.")
        settings_button = QPushButton()
        if darkdetect.isDark():
            settings_button.setIcon(QIcon(os.path.join(BASEDIR, "svg", "dark", \
                                                       "gear.svg")))
        else:
            settings_button.setIcon(QIcon(os.path.join(BASEDIR, "svg", \
                                                       "gear.svg")))
        settings_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        settings_button.clicked.connect(self.settings_button_clicked)
        info_button = QPushButton()
        if darkdetect.isDark():
            info_button.setIcon(QIcon(os.path.join(BASEDIR, "svg", "dark", \
                                                   "info-circle.svg")))
        else:
            info_button.setIcon(QIcon(os.path.join(BASEDIR, "svg", \
                                                   "info-circle.svg")))
        info_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        info_button.clicked.connect(self.info_button_clicked)

        header_title_layout = QVBoxLayout()
        header_title_layout.setSpacing(5)
        header_title_layout.setContentsMargins(0, 0, 0, 0)
        header_title_layout.addStretch()
        header_title_layout.addWidget(title_label)
        header_title_layout.addWidget(subtitle_label)
        header_title_layout.addStretch()

        header_layout = QHBoxLayout()
        header_layout.addWidget(logo)
        header_layout.addLayout(header_title_layout)
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
        if darkdetect.isDark():
            new_title_logo = QSvgWidget(os.path.join(BASEDIR, "svg", "dark", \
                                                     "file-earmark.svg"))
        else:
            new_title_logo = QSvgWidget(os.path.join(BASEDIR, "svg", \
                                                     "file-earmark.svg"))
        new_title_logo.setFixedSize(40, 40)
        new_title_label = QLabel(text = "New Project")
        new_title_label.setObjectName("TitleLabel")
        new_subtitle_label = QLabel(text = \
            "Create a new project and import your slide images.")
        new_line = QFrame()
        new_line.setObjectName("Line")
        new_line.setFrameShape(QFrame.Shape.HLine)
        new_line.setFixedHeight(2)
        new_name_label = QLabel(text = "Project Name: ")
        self.new_name_lineedit = QLineEdit()
        self.new_name_lineedit.setContextMenuPolicy(\
            Qt.ContextMenuPolicy.NoContextMenu)
        new_index_label = QLabel(text = "Selections Per Slide: ")
        self.new_index_spinbox = QSpinBox()
        self.new_index_spinbox.setCursor(Qt.CursorShape.PointingHandCursor)
        self.new_index_spinbox.setContextMenuPolicy(\
            Qt.ContextMenuPolicy.NoContextMenu)
        self.new_index_spinbox.setMinimum(1)
        self.new_index_spinbox.setMaximum(128)
        self.new_index_spinbox.setValue(6)
        new_size_label = QLabel(text = "Default Selection Size: ")
        self.new_size_width_lineedit = QLineEdit()
        self.new_size_width_lineedit.setContextMenuPolicy(\
            Qt.ContextMenuPolicy.NoContextMenu)
        self.new_size_width_lineedit.setFixedWidth(60)
        self.new_size_width_lineedit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.new_size_width_lineedit.setValidator(QIntValidator(2, 100000))
        self.new_size_width_lineedit.setText("4000")
        new_size_sublabel_1 = QLabel(text = "px  x")
        self.new_size_height_lineedit = QLineEdit()
        self.new_size_height_lineedit.setContextMenuPolicy(\
            Qt.ContextMenuPolicy.NoContextMenu)
        self.new_size_height_lineedit.setFixedWidth(60)
        self.new_size_height_lineedit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.new_size_height_lineedit.setValidator(QIntValidator(2, 100000))
        self.new_size_height_lineedit.setText("4000")
        new_size_sublabel_2 = QLabel(text = "px")
        new_button = QPushButton(text = "Create")
        new_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        new_button.clicked.connect(self.new_button_clicked)

        new_title_sublayout = QVBoxLayout()
        new_title_sublayout.setSpacing(5)
        new_title_sublayout.setContentsMargins(0, 0, 0, 0)
        new_title_sublayout.addStretch()
        new_title_sublayout.addWidget(new_title_label)
        new_title_sublayout.addWidget(new_subtitle_label)
        new_title_sublayout.addStretch()

        new_title_layout = QHBoxLayout()
        new_title_layout.addWidget(new_title_logo)
        new_title_layout.addLayout(new_title_sublayout)
        new_title_layout.addStretch()

        new_name_layout = QHBoxLayout()
        new_name_layout.addSpacing(5)
        new_name_layout.addWidget(new_name_label)
        new_name_layout.addWidget(self.new_name_lineedit)

        new_index_layout = QHBoxLayout()
        new_index_layout.addSpacing(5)
        new_index_layout.addWidget(new_index_label)
        new_index_layout.addWidget(self.new_index_spinbox)
        new_index_layout.addStretch()

        new_size_layout = QHBoxLayout()
        new_size_layout.addSpacing(5)
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
        new_layout.addSpacing(5)
        new_layout.addWidget(new_line)
        new_layout.addSpacing(20)
        new_layout.addLayout(new_name_layout)
        new_layout.addSpacing(10)
        new_layout.addLayout(new_index_layout)
        new_layout.addSpacing(10)
        new_layout.addLayout(new_size_layout)
        new_layout.addSpacing(20)
        new_layout.addLayout(new_button_layout)
        new_layout.addStretch()

        # Widgets and layouts for the "Open Project" section.

        if darkdetect.isDark():
            open_title_logo = QSvgWidget(os.path.join(BASEDIR, "svg", "dark", \
                                                      "folder2.svg"))
        else:
            open_title_logo = QSvgWidget(os.path.join(BASEDIR, "svg", \
                                                      "folder2.svg"))
        open_title_logo.setFixedSize(40, 40)
        open_title_label = QLabel(text = "Open Project")
        open_title_label.setObjectName("TitleLabel")
        open_subtitle_label = QLabel(text = "Open an existing project.")
        open_line = QFrame()
        open_line.setObjectName("Line")
        open_line.setFrameShape(QFrame.Shape.HLine)
        open_line.setFixedHeight(2)
        open_button = QPushButton(text = "Open")
        open_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        open_button.clicked.connect(self.open_button_clicked)

        open_title_sublayout = QVBoxLayout()
        open_title_sublayout.setSpacing(5)
        open_title_sublayout.setContentsMargins(0, 0, 0, 0)
        open_title_sublayout.addStretch()
        open_title_sublayout.addWidget(open_title_label)
        open_title_sublayout.addWidget(open_subtitle_label)
        open_title_sublayout.addStretch()

        open_title_layout = QHBoxLayout()
        open_title_layout.addWidget(open_title_logo)
        open_title_layout.addLayout(open_title_sublayout)
        open_title_layout.addStretch()

        open_button_layout = QHBoxLayout()
        open_button_layout.addStretch()
        open_button_layout.addWidget(open_button)
        open_button_layout.addStretch()

        open_layout = QVBoxLayout()
        open_layout.addLayout(open_title_layout)
        open_layout.addSpacing(5)
        open_layout.addWidget(open_line)
        open_layout.addSpacing(20)
        open_layout.addLayout(open_button_layout)
        open_layout.addStretch(10000)

        # Building the main layout.

        main_layout = QHBoxLayout()
        main_layout.addStretch(2)
        main_layout.addLayout(new_layout)
        main_layout.addStretch(3)
        main_layout.addLayout(open_layout)
        main_layout.addStretch(2)
        main_layout.setStretch(1, 8)
        main_layout.setStretch(3, 8)

        return main_layout

    """
    Return a QHBoxLayout that is the footer section during start up.
    @return QLayout, the requeted layout.
    """
    def _get_starter_footer(self):
        copyright_label = QLabel(text = "© 2024 Lizhou Roger Wang " + \
                                 "<rogerlzwang@gmail.com> " + \
                                 "at the Jonathan A. Epstein Lab.")
        
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()
        footer_layout.addWidget(copyright_label)
        footer_layout.addStretch()

        return footer_layout

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
    Handler for when the user clicks the button that changes the settings.
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

    """
    Handler for when the user clicks the button that shows the application's 
    information.
    """
    def info_button_clicked(self):
        info_dialog = InfoDialog()
        info_dialog.exec()

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
        text_1 = "Version: 1.0.0"
        text_2 = "Originally Published: 2024-06-22"
        text_3 = "Last Updated: 2024-06-22"
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