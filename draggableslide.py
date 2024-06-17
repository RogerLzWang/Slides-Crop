from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

class DraggableSlide(QWidget):
    order_changed = pyqtSignal()
    slide_removed = pyqtSignal(int)

    def __init__(self, parent = None, image_width = 100, \
                 image_height = 100):
        super(DraggableSlide, self).__init__()
        self.setParent(parent)
        self._slide = None
        self.drag_start_pos = None

        # Setting the width and height of the image.
        self.image_width = image_width
        self.image_height = image_height

        # Creating the two necessary widgets.
        self._image = QLabel()
        self._image.setFixedSize(self.image_width, self.image_height)
        self._image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._text = QLabel()
        self._text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Creating the layout of this widget.
        self._layout = QVBoxLayout()
        self._layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self._image, alignment = \
                               Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self._text, alignment = \
                               Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self._layout)
    
    def set_slide(self, slide):
        self._slide = slide
        if self._slide.preview:
            self._image.setPixmap(QPixmap(slide.preview.name).scaled(\
                self.image_width, self.image_height, \
                Qt.AspectRatioMode.KeepAspectRatio, \
                Qt.TransformationMode.SmoothTransformation))
        else:
            self._image.setPixmap(QPixmap(slide.path).scaled(\
                self.image_width, self.image_height, \
                Qt.AspectRatioMode.KeepAspectRatio, \
                Qt.TransformationMode.SmoothTransformation))
        self._text.setText(slide.file_name)

    def get_slide(self):
        return self._slide

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            # This will give us the start position when a drag is triggered.
            self.drag_start_pos = event.pos()
            self.raise_()
        super(DraggableSlide, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drag_start_pos is not None:
            # If clicked, the widget will move along with the mouse.
            self.move(self.pos() + event.pos() - self.drag_start_pos)
        super(DraggableSlide, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.drag_start_pos = None

        parent_layout = self.parent().layout()

        all_images = [parent_layout.itemAt(i).widget() \
                      for i in range(parent_layout.count())]

        # Sort the list of widgets by their x position.
        order = sorted(all_images, key = lambda i: i.pos().x())
        
        # Remove each item from the layout and insert in new order.
        for index, widget in enumerate(order):
            parent_layout.takeAt(index)
            parent_layout.insertWidget(index, widget)

        self.order_changed.emit()
        
        super(DraggableSlide, self).mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        index = self.parent().layout().indexOf(self)
        self.slide_removed.emit(index)
        self.setParent(None)
