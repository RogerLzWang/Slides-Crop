from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

class StepHeader(QWidget):
    project_edited = pyqtSignal()
    returned = pyqtSignal()

    def __init__(self, parent, project, step):
        super().__init__(parent)
        self._project = project
        self._step = step
        self._layout = self._get_step_header()
        self.setLayout(self._layout)
    
    def set_project(self, project):
        self._project = project

    """
    Return a QHBoxLayout that is the layout for the headers.
    """
    def _get_step_header(self):
        #
        return_button = QPushButton(text = "<")
        return_button.clicked.connect(self.return_button_clicked)
        self.title_label = QLabel()
        self.update_title()
        subtitle_label = QLabel()
        settings_button = QPushButton(text = "Settings")
        settings_button.clicked.connect(self.settings_button_clicked)
        save_button = QPushButton(text = "Save")
        save_button.clicked.connect(self.save_button_clicked)
        saveas_button = QPushButton(text = "Save As")
        saveas_button.clicked.connect(self.saveas_button_clicked)

        if self._step == 1:
            subtitle_label.setText("Step 1: Add images of slides.")
        elif self._step == 2:
            subtitle_label.setText("Step 2: Make selections on slide images.")

        header_title_layout = QVBoxLayout()
        header_title_layout.addWidget(self.title_label)
        header_title_layout.addWidget(subtitle_label)

        header_layout = QHBoxLayout()
        header_layout.addWidget(return_button)
        header_layout.addLayout(header_title_layout)
        header_layout.addStretch()
        header_layout.addWidget(settings_button)
        header_layout.addWidget(save_button)
        header_layout.addWidget(saveas_button)

        return header_layout

    def return_button_clicked(self):
        if not self._project.saved:
            return_dialog = CloseSaveDialog(self._project)
            return_dialog.project_saved.connect(self.project_saved_handler)
            if return_dialog.exec():
                self.returned.emit()
        else:
            self.returned.emit()

    def settings_button_clicked(self):
        project_edit_dialog = ProjectEditDialog(self._project)
        project_edit_dialog.project_edited.connect(self.project_edited_handler)
        project_edit_dialog.exec()

    def save_button_clicked(self):
        if self._project.path:
            self._project.save_json(self._project.path)
            self.window().setWindowModified(False)
        else:
            self.saveas_button_clicked()

    def saveas_button_clicked(self):
        filename, _ = QFileDialog.getSaveFileName(\
            caption = "Create a project file", \
            filter = "SCP File (*.scp)", directory = self._project.name + \
            ".scp")
        if filename:
            self._project.save_json(filename)
            self.window().setWindowModified(False)

    def project_saved_handler(self):
        self.window().setWindowModified(False)

    def project_edited_handler(self):
        self.project_edited.emit()
        self.update_title()

    def update_title(self):
        self.title_label.setText(self._project.name)

class ProjectEditDialog(QDialog):
    project_edited = pyqtSignal()

    def __init__(self, project):
        super().__init__()
        self.setWindowTitle("Edit Project")
        self._project = project

        name_label = QLabel(text = "Project Name: ")
        self.name_lineedit = QLineEdit()
        self.name_lineedit.setText(self._project.name)

        index_label = QLabel(text = "Selections Per Slide: ")
        self.index_spinbox = QSpinBox()
        self.index_spinbox.setMinimum(1)
        self.index_spinbox.setMaximum(128)
        self.index_spinbox.setValue(self._project.selection)

        size_label_1 = QLabel(text = "Default Selection Size: ")

        self.width_lineedit = QLineEdit()
        self.width_lineedit.setFixedWidth(60)
        self.width_lineedit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.width_lineedit.setValidator(QIntValidator(2, 100000))
        self.width_lineedit.setText(str(self._project.width))

        size_label_2 = QLabel(text = "px  x")

        self.height_lineedit = QLineEdit()
        self.height_lineedit.setFixedWidth(60)
        self.height_lineedit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.height_lineedit.setValidator(QIntValidator(2, 100000))
        self.height_lineedit.setText(str(self._project.height))

        size_label_3 = QLabel(text = "px")
        
        apply_button = QPushButton(text = "Apply")
        apply_button.clicked.connect(self.accept)
        cancel_button = QPushButton(text = "Cancel")
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

        self.setLayout(layout)

    def accept(self):
        self._project.name = self.name_lineedit.text()
        self._project.selection = self.index_spinbox.value()
        self._project.width = int(self.width_lineedit.text())
        self._project.height = int(self.height_lineedit.text())
        self.project_edited.emit()
        super().accept()

class CloseSaveDialog(QDialog):
    project_saved = pyqtSignal()

    def __init__(self, project):
        super().__init__()
        self.setWindowTitle("Close Project")
        self._project = project

        label = QLabel(text = \
                       "Would you like to save the project before returning?")

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
                self._project.save_json(filename)
                self.project_saved.emit()
                self.accept()