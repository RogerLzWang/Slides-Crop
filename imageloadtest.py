from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

class Window(QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)

        load_button = QPushButton(text = "Load Slides")
        load_button.setFixedSize(85, 40)
        load_button.clicked.connect(self.load_handler)
        slide_preview = QWidget()

        layout = QGridLayout()
        layout.addWidget(load_button)
        self.setCentralWidget(load_button)
        self.setWindowTitle("Slides Crop")
        
    def load_handler(self):
        dialog = QFileDialog()
        filenames, _ = dialog.getOpenFileNames(\
            caption = "Select one or more slide(s)", \
            filter = "Images (*.png *.jpg *.jpeg *.tif *.tiff)")

        if filenames:
            return filenames