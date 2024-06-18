#!/usr/bin/python
################################################################################
#
#   indexedrectangle.py
#   Author: Roger Wang
#   Date: 2024-06-17
#
#   IndexedRectangle (along with the IndexedRectangleObject carried) is used 
#   to represent selections within the SlideViewer during Step2.
#   The selection is added by clicking in selection mode.
#   The selection can be moved by clicking and dragging in view mode.
#   The selection can be removed by right-clicking in view mode.
#
#   IndexedRectangle (inherited from QGraphicsRectItem) is a QGraphcisItem. 
#   Therefore, having the QGraphicsObject included is necessary to use 
#   signals and slots.
#
################################################################################

import math

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

class IndexedRectangle(QGraphicsRectItem):
    def __init__(self, color = QColor(255, 0, 0)):
        super().__init__()
        # Item needs to be movable and selectable with geometry changes tracked.
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        # The cursor should change to the size all cursor (four arrows) when 
        # hovered over.
        # Note that when the user is in select mode, interaction with 
        # IndexedRectangle is not possible.
        # Therefore, we do not need to consider that case here.
        self.setCursor(Qt.CursorShape.SizeAllCursor)

        # Adding the IndexedRectangleObject to enable the use of signals.
        self.object = IndexedRectangleObject(self)

        self._index = 0
        self._center_coordinates = (0, 0)
        self._width = 0
        self._height = 0

        # Setting transparencies for the number, border, and background.
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

        # The number is added as a QLabel. A QGraphicsProxyWidget is therefore 
        # needed to add the QWidget to the QGraphicsItem.
        self._label = QLabel()
        self._label.setCursor(Qt.CursorShape.SizeAllCursor)
        self._proxy = QGraphicsProxyWidget(self)

    """
    Initialize IndexedRectangle from a SlideSelection object.
    @param selection: SlideSelection object.
    @param coordinates_transform: int/float, the factor used to transform 
        coordinates when using a preview image.
    """
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

        # Adjusting the position so that the selection area doesn't move 
        # out of the boundary.
        # Note that under this coordinate system, a SlideSelection that is 
        # larger than the image will also have its top left corner at (0, 0).
        x = max(x, 0)
        y = max(y, 0)
        x = min(x, self.scene().width() - math.ceil(self._width / 2))
        y = min(y, self.scene().height() - math.ceil(self._height / 2))
        self.moveBy(x, y)

    """
    Returns the index (number) of this IndexedRectangle.
    Note that unless never initialized, this should not return 0.
    @return int, the index of this IndexedRectangle.
    """
    def get_index(self):
        return self._index

    """
    Set the index of the IndexedRectangle and update the QLabel.
    @param index: int, the new index of this IndexedRectangle.
    """
    def set_index(self, index):
        self._index = index
        if self._label:
            self._label.setText(str(self._index))

    """
    A private function called when drawing the object so that the font size is 
    adjusted.
    """
    def _adjust_label(self):
        # Resize the label to fill the rectangle.
        self._label.resize(int(self._width), int(self._height))
        
        # Adjust the size of the font.
        font_size = 0.5 * min(self._width, self._height)
        self._font.setPointSizeF(font_size)
        self._label.setFont(self._font)
    
    ############################################################################
    # The following section contains overridden functions to customize features.
    ############################################################################
    
    def paint(self, painter, option, a):
        # Disable the state label so that selected outline doesn't appear.
        option.state = QStyle.StateFlag.State_None
        return super(IndexedRectangle, self).paint(painter, option)

    def itemChange(self, change, value):
        # When the rectangle is being dragged, make sure it doesn't go out of 
        # the scene (image).
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
            
        # Emitting coordinates_changed signal from child object when the change 
        # is over.
        elif change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            if self._index:
                point = self.mapToScene(self.rect().center())
                self.object.coordinates_changed.emit(self._index, point.x(), \
                                                     point.y())
        
        return super().itemChange(change, value)

class IndexedRectangleObject(QGraphicsObject):
    # Implementing QGraphicsObject.
    # This object is to be embedded in an IndexedRectangle, which is a 
    # QGraphicsItem.
    # Doing this allows the use of signals and slots through the 
    # QGraphicsObject.
    coordinates_changed = pyqtSignal(int, float, float)
    removed = pyqtSignal(int)

    def __init__(self, parent):
        super().__init__(parent)
        self.paint = self.parentItem().paint

    ############################################################################
    # The following section contains overridden functions to customize features.
    ############################################################################

    def contextMenuEvent(self, event):
        # Right-clicking on the IndexedRectangle causes the selection to be 
        # removed.
        self.removed.emit(self.parentItem().get_index())
    
    def boundingRect(self):
        # Return the boundingRect of the parent IndexedRectangle.
        return self.parentItem().boundingRect()