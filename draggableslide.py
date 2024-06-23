#!/usr/bin/python
################################################################################
#
#   draggableslide.py
#   Author: Roger Wang
#   Date: 2024-06-16
#
#   DraggableSlide is the QWidget added to the SlideQueue in Step1.
#   A slide can be added via button or removed by right-click.
#   The order of slides can be changed by dragging and dropping.
#   Note that the change of order is handeled in this class, not SlideQueue.
#
################################################################################

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
    
    """
    Set the Slide object represented by this DraggableSlide.
    @param slide: Slide.
    """
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

    """
    Returns the Slide object represented by this DraggableSlide.
    """
    def get_slide(self):
        return self._slide

    ############################################################################
    # The following section contains overridden functions to customize features.
    ############################################################################

    def enterEvent(self, event):
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def leaveEvent(self, event):
        self.setCursor(Qt.CursorShape.ArrowCursor)
    
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
        # Upon release, reorder may have happened due to dragged slides.
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.drag_start_pos = None

        parent_layout = self.parent().layout()
        images = [parent_layout.itemAt(i).widget() \
                  for i in range(parent_layout.count())]
                
        # First, sort all the images into their corresponding rows.
        image_rows = [[] for _ in range(parent_layout.rows)]
        for image in images:
            for i in range(parent_layout.rows - 1, -1, -1):
                if image.pos().y() + image.height() / 2 \
                    >= parent_layout.rows_y[i]:
                    image_rows[i].append(image)
                    break
                elif i == 0:
                    image_rows[0].append(image)
        
        # Next, sort all the rows by the x position of images in that row.
        for i in range(len(image_rows)):
            image_rows[i] = sorted(image_rows[i], key = lambda i: i.pos().x())

        # Finally, remove each item from the layout and insert in new order.
        for i in range(parent_layout.count()):
            parent_layout.itemAt(0).widget().setParent(None)
        for i in range(len(image_rows)):
            for j in range(len(image_rows[i])):
                parent_layout.addWidget(image_rows[i][j])

        self.order_changed.emit()
        
        super(DraggableSlide, self).mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        # The slide is removed when right-clicked.
        index = self.parent().layout().indexOf(self)
        self.slide_removed.emit(index)
        self.setParent(None)