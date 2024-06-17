from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from stepheader import *
from slidequeue import *

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

    def get_project(self):
        return self._project
    
    """
    Return a QVBoxLayout that is the layout for step 1.
    """
    def _get_step_1(self):
        self._header = StepHeader(self, self._project, 1)
        self._header.project_edited.connect(self.project_edited_emit)
        self._header.returned.connect(self.returned_handler)
        main_layout = self._get_step_1_main()
        footer_layout = self._get_step_1_footer()

        layout = QVBoxLayout()
        layout.addWidget(self._header)
        layout.addLayout(main_layout)
        layout.addLayout(footer_layout)

        return layout

    """
    Return a QHBoxLayout that is the layout for the main section during step 1.
    """
    def _get_step_1_main(self):
        self._slide_queue = SlideQueue(self._project)
        self._slide_queue.project_edited.connect(self.project_edited_emit)
        self._slide_queue.set_slides(self._project.slides)

        add_button = QPushButton(text = "Add Slides")
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
    """
    def _get_step_1_footer(self):
        continue_button = QPushButton(text = "Next")
        continue_button.clicked.connect(self.continue_button_clicked)

        footer_layout = QHBoxLayout()
        footer_layout.addStretch()
        footer_layout.addWidget(continue_button)

        return footer_layout

    def add_button_clicked(self):
        dialog = QFileDialog()
        filenames, _ = dialog.getOpenFileNames(\
            caption = "Select one or more slide(s)", \
            filter = "Images (*.png *.jpg *.jpeg *.tif *.tiff)")

        if filenames:
            slides = []
            for filename in filenames:
                slides.append(Slide(filename, self._resolution))
            self._slide_queue.add_slides(slides)
            self.project_edited.emit()

    def continue_button_clicked(self):
        self._project.slides = self._slide_queue.get_slides()
        self.continue_clicked.emit()

    def project_edited_emit(self):
        self.project_edited.emit()

    def returned_handler(self):
        self.returned.emit()
    
    def update(self):
        self._header.update_title()
        self._slide_queue.clear_slides()
        self._slide_queue.set_slides(self._project.slides)