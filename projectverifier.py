#!/usr/bin/python
################################################################################
#
#   projectverifier.py
#   Author: Roger Wang
#   Date: 2024-06-18
#
#   ProjectVerifier is a helper class that checks a loaded project so that all 
#   image paths are valid. If invalid paths are found, a QDialog will first be 
#   prompted to ask the user if the missing Slides should be located or removed.
#
#   Clicking "Cancel" at this step cancels the Project load entirely.
#   Clicking "Remove" at this step removes all unfound Slides.
#   Clicking "Locate" at this step will prompt QFileDialogs that ask the user 
#   to locate the files.
#
#   Clicking "Cancel" on the QFileDialog removes that specific Slide.
#   In addition, a friendly feature is added where if the user locates one 
#   Slide, the directory of that Slide is immediately checked to see if other 
#   missing Slides can be found. If so, they will be located automatically.
#
################################################################################

import os

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from dialog import *
from project import *

class ProjectVerifier():
    def __init__(self, project):
        self._project = project
        self._unfounds = []

        # _to_remove is a temporary list of indices.
        # Notice that when trying to locate files, recursion is used to make 
        # sure that the user is asked to locate each unfound file exactly once.
        # During this process, if the user presses cancel on the file dialog, 
        # the index of that Slide should still be removed from _unfounds but 
        # added here so that it is scheduled for removal without interfering 
        # with the order of the Slides list in the Project.
        self._to_remove = []
    
    """
    Verify the path to Slides of a Project. Prompt dialog to ask for actions if 
    unfound images exist, and locate, remove, or cancel the load.
    @return True (Project is now safe and loading should continue) / False 
    (Project loading should be canceled).
    """
    def verify(self):
        # Reset variables.
        self._unfounds = []
        self._to_remove = []

        # Iterating through Slides to check that all paths exist.
        for i in range(len(self._project.slides)):
            if not os.path.exists(self._project.slides[i].path):
                self._unfounds.append(i)

        # Return True immediately if all images were found.
        if not self._unfounds:
            return True
        
        # Extracting the names of the unfound files to be preseted to the user.
        unfound_names = [self._project.slides[index].file_name \
                         for index in self._unfounds]
        
        dialog = UnfoundItemActionDialog(unfound_names)
        dialog.locate_clicked.connect(self._locate_clicked_handler)
        dialog.remove_clicked.connect(self._remove_clicked_handler)

        if not dialog.exec():
            return False
        
        # Reset the work index just to be safe.
        self._project.saved = False
        self._project.work_index = 1
        return True

    """
    Handler for if user chooses to locate the missing images.
    """
    def _locate_clicked_handler(self):
        while self._unfounds:
            self._locate_first_unfound()
        
        # Remove the Slides that the user did not relocate.
        self._remove_slides(self._to_remove)
    
    """
    Ask the user to locate the first unfound image.
    """
    def _locate_first_unfound(self):
        index = self._unfounds.pop(0)
        original = self._project.slides[index].file_name

        # Currently, macOS doesn't support having captions or default file 
        # names in its native file dialog. Therefore, the native dialog is not 
        # used here.
        filename, _ = QFileDialog.getOpenFileName(\
            caption = "Locate " + original, filter = \
            "Images (*.png *.jpg *.jpeg *.tif *.tiff)", directory = original, 
            options = QFileDialog.Option.DontUseNativeDialog)
        
        if not filename:
            self._to_remove.append(index)
        else:
            self._project.slides[index].path = filename
            self._project.slides[index].file_name = os.path.basename(filename)
            self._project.slides[index].folder_path = os.path.dirname(filename)
            self._fix_selections(self._project.slides[index])

            # Checking to see if other unfound items can be found in this 
            # directory. If so, also locate them.
            for i in range(len(self._unfounds)):

                # Since found indices are popped from the list, it is 
                # possible for the list to grow shorter.
                if i >= len(self._unfounds):
                    break

                if self._project.slides[self._unfounds[i]].file_name in \
                    os.listdir(os.path.dirname(filename)):
                    temp_index = self._unfounds.pop(i)
                    self._project.slides[temp_index].folder_path = \
                        os.path.dirname(filename)
                    self._project.slides[temp_index].path = os.path.join(\
                        self._project.slides[temp_index].folder_path, \
                        self._project.slides[temp_index].file_name)

                    self._fix_selections(self._project.slides[temp_index])

    """
    Checks that the selections in the given Slide are within the boundary.
    If not, fix and change the coordinates.
    @param slide: Slide object.
    """
    def _fix_selections(self, slide):
        original = QImage(slide.path)
        image_width = original.width()
        image_height = original.height()

        for selection in slide.selections:
            # Calculating the position of the selection rectangle.
            x = selection.center_coordinates[0]
            y = selection.center_coordinates[1]
            selection_width = selection.width
            selection_height = selection.height

            left = x - selection_width // 2
            right = x + math.ceil(selection_width / 2)
            top = y - selection_height // 2
            bottom = y + math.ceil(selection_height / 2)
        
            # Adjusting coordinates if necessary.
            if right > image_width:
                selection.center_coordinates = (image_width - \
                    selection_width // 2, selection.center_coordinates[1])
                left = selection.center_coordinates[0] - selection_width // 2
            if left < 0:
                selection.center_coordinates = (selection_width // 2, \
                    selection.center_coordinates[1])
            if bottom > image_height:
                selection.center_coordinates = (\
                    selection.center_coordinates[0], \
                    image_height - selection_height // 2)
                top = selection.center_coordinates[1] - selection_height // 2
            if top < 0:
                selection.center_coordinates = (\
                    selection.center_coordinates[0], selection_height // 2)

    """
    Handler for when the user clicks the "Remove" button.
    """
    def _remove_clicked_handler(self):
        self._remove_slides(self._unfounds)

    """
    Remove slides with a given list of indices.
    @param index_list: list of int, the indices of the Slides to be removed.
    """
    def _remove_slides(self, index_list):
        for i in range(len(index_list) - 1, -1, -1):
            self._project.slides.pop(index_list[i])
        