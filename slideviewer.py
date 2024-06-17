from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from imageviewer import *
from project import *

class SlideViewer(QWidget):
    project_edited = pyqtSignal()

    def __init__(self, parent, color):
        super().__init__(parent)

        self._image_viewer = ImageViewer(self, color)
        self._image_viewer.selection_made.connect(self.selection_made)
        self._image_viewer.selection_removed.connect(\
            self.project_edited_handler)
        self._image_viewer.selection_moved.connect(self.project_edited_handler)

        self._slide = None
        self._pixmap = None

        self._layout = self._get_layout()
        self.setLayout(self._layout)

        # This is the variable for calculating the real coordinates 
        # when clicked.
        self._coordinates_transform = 1

        self._selection_width = 0
        self._selection_height = 0

    def set_resolution(self, resolution):
        self._coordinates_transform = int(1 / resolution)
        self._image_viewer._coordinates_transform = self._coordinates_transform

    def _get_layout(self):
        layout = QHBoxLayout()
        layout.addWidget(self._image_viewer)

        return layout

    def set_slide(self, slide):
        self._slide = slide
        if self._coordinates_transform == 1:
            self._pixmap = QPixmap(self._slide.path)
        else:
            self._pixmap = QPixmap(self._slide.preview.name)
        self._image_viewer.setPhoto(self._pixmap)
        self._image_viewer.set_selections(self._slide.selections)

    def set_selection_size(self, width, height):
        self._selection_width = width
        self._selection_height = height

    def redraw_selections(self):
        self._image_viewer.set_selections(self._slide.selections)

    def selection_made(self, point):
        selection = SlideSelection()
        selection.center_coordinates = (point.x() * \
                                        self._coordinates_transform, \
                                        point.y() * \
                                        self._coordinates_transform)
        selection.width = self._selection_width
        selection.height = self._selection_height
        self._image_viewer.add_selection(selection)
        self.project_edited.emit()
    
    def project_edited_handler(self):
        self.project_edited.emit()