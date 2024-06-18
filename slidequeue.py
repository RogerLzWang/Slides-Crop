#!/usr/bin/python
################################################################################
#
#   slidequeue.py
#   Author: Roger Wang
#   Date: 2024-06-18
#
#   SlideQueue is the QScrollArea added to Step1 to display the Slides added by 
#   the user and allows for the Slides to be reordered or removed.
#   Slides are reordered by clicking and dragging.
#   A Slide is removed by right-clicking on it.
#   Each Slide is added as a DraggableSlide into the SlideQueue. SlideQueue 
#   utilizes a custom FlowLayout to allow automatic wrapping based on the 
#   width of the window and dragging and dropping with respect to the row and 
#   column positions.
#
################################################################################

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from draggableslide import *
from flowlayout import *
from project import *

class SlideQueue(QScrollArea):
    project_edited = pyqtSignal()

    def __init__(self, project):
        super().__init__()

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self._project = project
        self.setWidgetResizable(True)
        self._widget = QWidget()
        self._layout = FlowLayout(self._widget)

        self.setWidget(self._widget)
    
    """
    Add a single Slide to the end of the queue.
    @param slide: Slide object, the Slide to be added to the queue.
    """
    def add_slide(self, slide):
        # Creating a DraggableSlide.
        draggable_slide = DraggableSlide(parent = self._widget)
        draggable_slide.order_changed.connect(self.update_slides)
        draggable_slide.slide_removed.connect(self.remove_slide)
        draggable_slide.set_slide(slide)
        self._layout.addWidget(draggable_slide)
    
    """
    Add a list of Slides to the end of the queue.
    @param slides_list: list of Slides, the list of Slides to be added.
    """
    def add_slides(self, slides_list):
        for slide in slides_list:
            self.add_slide(slide)

    """
    Get a list of slides in the current order of the queue.
    @return slides_list: list, the list of Slide objects.
    """
    def get_slides(self):
        slides_list = []
        for i in range(self._layout.count()):
            slides_list.append(self._layout.itemAt(i).widget().get_slide())

        return slides_list
    
    """
    Get the Slides in the current SlideQueue and compare if it has been updated 
    from the Slides contained in the Project. If so, emit the project_edited 
    signal.
    """
    def update_slides(self):
        temp_slides = self._project.slides
        self._project.slides = self.get_slides()

        # Checking if the order has been changed. If so, emit updated signal.
        # First, simply check if the length of Slides are different.
        if len(temp_slides) != len(self._project.slides):
            self.project_edited.emit()
            return
        
        # If the lengths are the same, check each Slide and emit signal.
        for i in range(len(temp_slides)):
            if temp_slides[i].path != self._project.slides[i].path:
                self.project_edited.emit()
                return

    """
    Remove a Slide from the list contained in the Project at the given index.
    Note that removing the Slide from the SlideQueue is completed by the 
    DraggableSlide itself.
    @param index: int, the index of the Slide removed.
    """
    def remove_slide(self, index):
        self._project.slides.pop(index)
        self.project_edited.emit()

    """
    Remove a Slide from the list contained in the Project at the given index.
    Note that removing the Slide from the SlideQueue is completed by the 
    DraggableSlide itself.
    @param index: int, the index of the Slide removed.
    """
    def clear_slides(self):
        for i in range(self._layout.count()):
            self._layout.itemAt(0).widget().setParent(None)
