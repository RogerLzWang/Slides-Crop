from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from indexedrectangle import *
from project import *

# The code contained in this file stems from ekhumoro's response in the post 
# https://stackoverflow.com/questions/35508711/
# how-to-enable-pan-and-zoom-in-a-qgraphicsview.
# Much of the code is taken directly. THANK YOU ekhumoro.

class SlideViewer(QGraphicsView):
    project_edited = pyqtSignal()

    def __init__(self, parent, color = QColor(255, 0, 0)):
        # Change this variable to adjust the speed of zooming.
        # This variable should always be larger than 1.
        self._scale_factor = 1.1

        super().__init__(parent)

        self._slide = None
        # mode:
        # 0: View. Users can zoom and pan with mouse activity in this mode.
        # 1: Select. Users can create selections in this mode.
        # Holding Ctrl gives temporary select mode.
        self._mode = 0

        # This is the variable for calculating the real coordinates 
        # when clicked.
        self._coordinates_transform = 1

        self._color = color
        self._selection_width = 2
        self._selection_height = 2

        # ekhumoro's variables for interacting with the basic image viewr.
        self._zoom = 0
        self._empty = True
        self._image = QGraphicsPixmapItem()
        self._image.setShapeMode(
            QGraphicsPixmapItem.ShapeMode.BoundingRectShape)
        self._scene = QGraphicsScene(self)
        self._scene.addItem(self._image)

        self._selections = []
        self._indexed_rectangles = []

        self.setScene(self._scene)
        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(128, 128, 128)))
        self.setFrameShape(QFrame.Shape.NoFrame)

    def set_slide(self, slide):
        self._slide = slide
        if self._coordinates_transform == 1:
            pixmap = QPixmap(self._slide.path)
        else:
            pixmap = QPixmap(self._slide.preview.name)
        self.set_photo(pixmap)
        self.set_selections(self._slide.selections)

    def set_mode(self, mode):
        self._mode = mode
        if mode == 0:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            if self._image.isUnderMouse():
                self.viewport().setCursor(Qt.CursorShape.OpenHandCursor)
        elif mode == 1:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            if self._image.isUnderMouse():
                self.viewport().setCursor(Qt.CursorShape.CrossCursor)

    def toggle_mode(self):
        if self._mode == 0:
            self.set_mode(1)
        elif self._mode == 1:
            self.set_mode(0)

    """
    Sets the resolution of the preview images provided.
    The resolution is then transformed to _coordinates_transform, a factor 
    multiplied when transforming coordinates for easier calculations.
    @param resolution: float, resolution of the preview (1, 0.5, 0.25, or 0.1).
    """
    def set_resolution(self, resolution):
        self._coordinates_transform = int(1 / resolution)

    def set_selection_size(self, width, height):
        self._selection_width = width
        self._selection_height = height

    def set_selections(self, selections):
        self.clear_selections()
        self._selections = selections
        for i in range(len(self._selections)):
            self.draw_selection(self._selections[i], i + 1)

    def add_selection(self, selection):
        self._selections.append(selection)
        self.draw_selection(selection, len(self._selections))

    def draw_selection(self, selection, index):
        # Adding the IndexedRectangle to the scene before importing selection 
        # is necessary.
        indexed_rectangle = IndexedRectangle(self._color)
        indexed_rectangle.object.coordinates_changed.connect(\
            self.indexed_rectangle_changed)
        indexed_rectangle.object.indexed_rectangle_removed.connect(\
            self.indexed_rectangle_remove)

        self._indexed_rectangles.append(indexed_rectangle)
        self._scene.addItem(self._indexed_rectangles[-1])
        indexed_rectangle.from_selection(selection, self._coordinates_transform)
        indexed_rectangle.set_index(index)
    
    def clear_selections(self):
        self._selections = []
        for indexed_rectangle in self._indexed_rectangles:
            self._scene.removeItem(indexed_rectangle)
        self._indexed_rectangles = []
    
    def indexed_rectangle_changed(self, index, x, y):
        x *= self._coordinates_transform
        y *= self._coordinates_transform
        self._selections[index - 1].center_coordinates = (x, y)
        self.project_edited.emit()

    def indexed_rectangle_remove(self, index):
        indexed_rectangle = self._indexed_rectangles.pop(index - 1)
        self._selections.pop(index - 1)
        self._scene.removeItem(indexed_rectangle)
        for i in range(len(self._indexed_rectangles)):
            self._indexed_rectangles[i].set_index(i + 1)
        self.project_edited.emit()

    ############################################################################
    # The functions in the following sections is written by ekhumoro.
    # THANK YOU.
    ############################################################################

    def has_photo(self):
        return not self._empty

    def reset_view(self, scale = 1):
        rect = QRectF(self._image.pixmap().rect())
        if not rect.isNull():
            # Weirdly, calling setSceneRect() on QGraphicsView doesn't change 
            # the rect of the QGraphicsScene. Therefore, both calls below are 
            # necessary.
            self.setSceneRect(rect)
            self._scene.setSceneRect(rect)

            if (scale := max(1, scale)) == 1:
                self._zoom = 0
            if self.has_photo():                
                unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height()) * scale
                self.scale(factor, factor)

    def set_photo(self, pixmap = None):
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            self._image.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self._image.setPixmap(QPixmap())
        if not self.has_photo():
            self._zoom = 0
        self.reset_view(self._scale_factor ** self._zoom)

    def zoom(self, step):
        zoom = max(0, self._zoom + (step := int(step)))
        if zoom != self._zoom:
            self._zoom = zoom
            if self._zoom > 0:
                if step > 0:
                    factor = self._scale_factor ** step
                else:
                    factor = 1 / self._scale_factor ** abs(step)
                self.scale(factor, factor)
            else:
                self.reset_view()

    ############################################################################
    # The following section contains overridden functions to customize features.
    ############################################################################

    def event(self, event):
        # Implementing ZoomNativeGesture for MacOS (two finger pinch-to-zoom).
        if isinstance(event, QNativeGestureEvent):
            if self._mode == 0:
                if event.gestureType() == \
                    Qt.NativeGestureType.ZoomNativeGesture or \
                    event.gestureType() == \
                    Qt.NativeGestureType.SmartZoomNativeGesture:
                    delta = event.value()
                    self.zoom(delta and delta // abs(delta))
        return QGraphicsView.event(self, event)

    def enterEvent(self, event):
        # Change the cursor to the cross cursor when in select mode and 
        # the cursor enters the image in the SlideViewer.
        # This function is important. Without it, the cursor shape will not 
        # change without user clicking on the app first after entering Step2.
        self.setFocus()  
        if self._mode == 1 and self._image.isUnderMouse():
            self.viewport().setCursor(Qt.CursorShape.CrossCursor)
        else:
            super().enterEvent(event)

    def keyPressEvent(self, event):
        # Pressing the control key enters the select mode.
        if event.key() == Qt.Key.Key_Control:
            self.set_mode(1)

    def keyReleaseEvent(self, event):
        # Releasing the control key returns to view mode.
        if event.key() == Qt.Key.Key_Control:
            self.set_mode(0)

    def mousePressEvent(self, event):
        if self._mode == 1 and self._image.isUnderMouse():   
            # Adding a selection to the slide.
            point = self.mapToScene(event.pos()).toPoint()
            selection = SlideSelection()
            selection.center_coordinates = (point.x() * \
                                            self._coordinates_transform, \
                                            point.y() * \
                                            self._coordinates_transform)
            selection.width = self._selection_width
            selection.height = self._selection_height
            self.add_selection(selection)
            self.project_edited.emit()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # The original mouseReleaseEvent will cause the cursor shape to be 
        # changed back to the arrow.
        # Therefore, we are only calling the overridden function when in 
        # view mode.
        if self._mode == 0:
            super().mouseReleaseEvent(event)
    
    def mouseMoveEvent(self, event):
        if self._mode == 1:
            # The cross cursor is not shown if the mouse leaves the image.
            if self._image.isUnderMouse():
                self.viewport().setCursor(Qt.CursorShape.CrossCursor)
            else:
                self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
        else:       
            # Similar to mouseReleaseEvent, mouseMoveEvent also changes the 
            # cursor shape.         
            super().mouseMoveEvent(event)

    def resizeEvent(self, event):
        # This function is also written by ekhumoro. THANK YOU.
        super().resizeEvent(event)
        self.reset_view()

    def wheelEvent(self, event):
        # This function is also written by ekhumoro. THANK YOU.
        if self._mode == 0:
            delta = event.angleDelta().y()
            self.zoom(delta and delta // abs(delta))

    def toggleDragMode(self):
        # This function is also written by ekhumoro. THANK YOU.
        if self.dragMode() == QGraphicsView.DragMode.ScrollHandDrag:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
        elif not self._image.pixmap().isNull():
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)