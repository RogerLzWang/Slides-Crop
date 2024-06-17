from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import *

from project import *
from starter import *
from step1 import *
from step2 import *

# During step 1, all images that need to be processed are selected and loaded.
# During step 2, the selection boxes for each image is determined.
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setMinimumSize(1080, 640)
        self.resize(1080, 720)
        self.setUnifiedTitleAndToolBarOnMac(True)

        self._central_widget = QStackedWidget()
        self.setCentralWidget(self._central_widget)

        self._starter = None
        self._project = None
        self._step_1 = None
        self._step_2 = None

        self._resolution = 0.5
        self._color = QColor(255, 0, 0)

        self.goto_starter()

    def goto_starter(self):
        if not self._starter:
            self._starter = Starter(self, self._resolution, self._color)
            self._starter.continue_clicked.connect(\
                self.starter_continue_handler)
            self._central_widget.addWidget(self._starter)
        self._project = None
        self.setWindowModified(False)
        self._central_widget.setCurrentWidget(self._starter)

    def starter_continue_handler(self, project):
        self._project = project
        if not project.saved:
            self.project_edited_handler()
        self._resolution = self._starter.get_resolution()
        self._color = self._starter.get_color()
        self.goto_step_1()

    def goto_step_1(self):
        if not self._step_1:
            self._step_1 = Step1(self, self._project, self._resolution)
            self._step_1.project_edited.connect(self.project_edited_handler)
            self._step_1.continue_clicked.connect(self.goto_step_2)
            self._step_1.returned.connect(self.goto_starter)
            self._central_widget.addWidget(self._step_1)
        self._step_1.update()
        self._central_widget.setCurrentWidget(self._step_1)

    def goto_step_2(self):
        if not len(self._project.slides):
            dialog = NoSlideErrorDialog()
            dialog.exec()
            return
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
    
    def project_edited_handler(self):
        self.setWindowModified(True)
        self._project.saved = False

    def closeEvent(self, event):
        if not self._project or self._project.saved:
            super().closeEvent(event)
        else:
            close_dialog = CloseSaveDialog(self._project)
            if close_dialog.exec():
                super().closeEvent(event)
            else:
                event.ignore()

class CloseSaveDialog(QDialog):
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

    def save_clicked(self):
        if self.save_project():
            self.accept()

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