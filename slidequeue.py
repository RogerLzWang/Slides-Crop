from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from draggableslide import *
from project import *

class SlideQueue(QScrollArea):
    project_edited = pyqtSignal()

    def __init__(self, project):
        super(SlideQueue, self).__init__()

        self._project = project
        self._layout = QHBoxLayout()
        self._layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        self._widget = QWidget()
        self._widget.setLayout(self._layout)

        self.setWidget(self._widget)
    
    def add_slides(self, slides_list):
        for slide in slides_list:
            self.set_slide(slide)
            self._project.slides.append(slide)

    def set_slides(self, slides_list):
        for slide in slides_list:
            self.set_slide(slide)

    def set_slide(self, slide):
        draggable_slide = DraggableSlide(parent = self._widget)
        draggable_slide.order_changed.connect(self.update_slides)
        draggable_slide.slide_removed.connect(self.remove_slide)
        draggable_slide.set_slide(slide)
        self._layout.addWidget(draggable_slide)
    
    """
    Get a list of slides in the current order of the queue.
    @return slides_list: list, the list of Slide objects.
    """
    def get_slides(self):
        slides_list = []
        for i in range(self._layout.count()):
            slides_list.append(self._layout.itemAt(i).widget().get_slide())

        return slides_list
    
    def update_slides(self):
        temp_slides = self._project.slides
        self._project.slides = self.get_slides()

        # Checking if the order has been changed. If so, update saved statuses.
        if len(temp_slides) != len(self._project.slides):
            self.project_edited_emit()
            return
        
        for i in range(len(temp_slides)):
            if temp_slides[i].path != self._project.slides[i].path:
                self.project_edited_emit()
                return

    def remove_slide(self, index):
        self._project.slides.pop(index)
        self.project_edited_emit()

    def clear_slides(self):
        for i in range(self._layout.count()):
            self._layout.itemAt(0).widget().setParent(None)

    def project_edited_emit(self):
        self.project_edited.emit()