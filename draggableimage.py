
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

class DraggableImage(QLabel):
    def __init__(self, imgPath = None, parent = None):
        super(DraggableImage, self).__init__()

        width = 100
        height = 100

        self.setParent(parent)
        self.setFixedSize(width, height)
        self.setPixmap(QPixmap(imgPath).scaled(width, height, \
            Qt.AspectRatioMode.KeepAspectRatio, \
            Qt.TransformationMode.SmoothTransformation))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drag_start_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            # This will give us the start position when a drag is triggered.
            self.drag_start_pos = event.pos()
            self.raise_()
        super(DraggableImage, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drag_start_pos is not None:
            # If clicked, the widget will move along with the mouse.
            self.move(self.pos() + event.pos() - self.drag_start_pos)
        super(DraggableImage, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.drag_start_pos = None

        parent_layout = self.parent().mainLayout

        all_images = [parent_layout.itemAt(i).widget() for i in range(parent_layout.count())]

        # Sort the list of widgets by their x position.
        order = sorted(all_images, key=lambda i : i.pos().x())
        
        # Remove each item from the layout and insert in new order.
        for idx, widget in enumerate(order):
            parent_layout.takeAt(idx)
            parent_layout.insertWidget(idx, widget)
            
        super(DraggableImage, self).mouseReleaseEvent(event)
