import math

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

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
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

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

    # Implementing ZoomNativeGesture for MacOS (two finger pinch-to-zoom).
    def event(self, event):
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
        self.setFocus()  
        if self._mode == 1 and self._image.isUnderMouse():
            self.viewport().setCursor(Qt.CursorShape.CrossCursor)
        else:
            super().enterEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Control:
            self.set_mode(1)

    def keyReleaseEvent(self, event):
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
        if self._mode == 0:
            super().mouseReleaseEvent(event)
    
    def mouseMoveEvent(self, event):
        if self._mode == 1:
            if self._image.isUnderMouse():
                self.viewport().setCursor(Qt.CursorShape.CrossCursor)
            else:
                self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
        else:                
            super().mouseMoveEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.reset_view()

    def wheelEvent(self, event):
        if self._mode == 0:
            delta = event.angleDelta().y()
            self.zoom(delta and delta // abs(delta))

    def toggleDragMode(self):
        if self.dragMode() == QGraphicsView.DragMode.ScrollHandDrag:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
        elif not self._image.pixmap().isNull():
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

class IndexedRectangle(QGraphicsRectItem):
    def __init__(self, color = QColor(255, 0, 0)):
        super().__init__()
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setCursor(Qt.CursorShape.SizeAllCursor)

        self.object = IndexedRectangleObject(self)

        self._index = 0
        self._center_coordinates = (0, 0)
        self._width = 0
        self._height = 0

        color.setAlpha(128)
        self._border_pen = QPen(color)
        color.setAlpha(32)
        self._background_brush = QBrush(color)
        self.setPen(self._border_pen)
        self.setBrush(self._background_brush)

        self._font = QFont()

        color.setAlpha(128)
        self._text_color = color
        self._palette = QPalette()
        self._palette.setColor(QPalette.ColorRole.WindowText, self._text_color)
        self._palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0, 0))

        self._label = QLabel()
        self._label.setCursor(Qt.CursorShape.SizeAllCursor)
        self._proxy = QGraphicsProxyWidget(self)

    def from_selection(self, selection, coordinates_transform):
        self._center_coordinates = selection.center_coordinates
        self._width = selection.width
        self._height = selection.height

        # Checking that the x and y coordinates don't cause the selection 
        # to overflow.
        x = self._center_coordinates[0] - self._width // 2
        y = self._center_coordinates[1] - self._height // 2

        # Transforming coordinates based on preview.
        self._width /= coordinates_transform
        self._height /= coordinates_transform
        x /= coordinates_transform
        y /= coordinates_transform
        self._border_pen.setWidthF(1 / coordinates_transform)

        # Initially set the rectangle and the proxy widget at (0, 0).
        # Otherwise the coordinate system becomes problematic.
        self.setRect(0, 0, self._width, self._height)
        self._label.setText(str(self._index))
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setPalette(self._palette)
        self._label.setFont(self._font)
        self._adjust_label()
        self._proxy.setWidget(self._label)
        self._proxy.setPos(0, 0)

        x = max(x, 0)
        y = max(y, 0)
        x = min(x, self.scene().width() - math.ceil(self._width / 2))
        y = min(y, self.scene().height() - math.ceil(self._height / 2))
        self.moveBy(x, y)

    def get_index(self):
        return self._index

    def set_border_color(self, color):
        self._border_pen = QPen(color)

    def set_background_color(self, color):
        self._background_brush = QBrush(color)
    
    def set_text_color(self, color):
        self._text_color = color

    def set_index(self, index):
        self._index = index
        if self._label:
            self._label.setText(str(self._index))

    # Disable the state label so that selected outline doesn't appear.
    def paint(self, painter, option, a):
        option.state = QStyle.StateFlag.State_None
        return super(IndexedRectangle, self).paint(painter, option)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and \
            self.scene():
            bounding_rect = self.boundingRect().translated(value)
            scene_rect = self.scene().sceneRect()

            if not scene_rect.contains(bounding_rect):
                if bounding_rect.right() > scene_rect.right():
                    bounding_rect.moveRight(scene_rect.right())
                if bounding_rect.x() < 0:
                    bounding_rect.moveLeft(0)
                if bounding_rect.bottom() > scene_rect.bottom():
                    bounding_rect.moveBottom(scene_rect.bottom())
                if bounding_rect.y() < 0:
                    bounding_rect.moveTop(0)
                return bounding_rect.topLeft()
            
        # Emitting coordinates_changed signal from child object.
        elif change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            if self._index:
                point = self.mapToScene(self.rect().center())
                self.object.coordinates_changed.emit(self._index, point.x(), \
                                                     point.y())
        
        return super().itemChange(change, value)

    def _adjust_label(self):
        # Resize the label to fill the rectangle.
        self._label.resize(int(self._width), int(self._height))
        
        # Adjust the size of the font.
        font_size = 0.5 * min(self._width, self._height)
        self._font.setPointSizeF(font_size)
        self._label.setFont(self._font)

# Implementing QGraphicsObject.
# This object is to be embedded in an IndexedRectangle, which is a 
# QGraphicsItem.
# Doing this allows the use of signals and slots through the QGraphicsObject.
class IndexedRectangleObject(QGraphicsObject):
    coordinates_changed = pyqtSignal(int, float, float)
    indexed_rectangle_removed = pyqtSignal(int)

    def __init__(self, parent):
        super().__init__(parent)
        self.paint = self.parentItem().paint

    def contextMenuEvent(self, event):
        self.indexed_rectangle_removed.emit(self.parentItem().get_index())
    
    def boundingRect(self):
        return self.parentItem().boundingRect()