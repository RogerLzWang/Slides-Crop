#!/usr/bin/python
################################################################################
#
#   project.py
#   Author: Roger Wang
#   Date: 2024-06-18
#
#   Project and all associated classes to contain information of a project.
#   A Project contains a list of Slides, while a Slide contains a list of 
#   SlideSelections.
#
################################################################################

import json
import math
import os

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

class Project():
    def __init__(self):
        self.name = ""
        self.path = ""
        self.saved = False

        # slides should be a list of Slide objects.
        self.slides = []

        # work_index should be an integer specifying which slide is looked at.
        self.work_index = 1

        # selection should be an integer that serves as a guide for each slide.
        self.selection = 6

        # width and height contain the default size for all selections.
        self.width = 0
        self.height = 0

    """
    Save the project into a JSON format file.
    Note that in practice, the project file always have SCP extensions.
    @param path: str, the path to the project file.
    """
    def save_json(self, path):
        slides = []

        # Iterate slides.
        for slide in self.slides:
            temp_slide = {
                "path": slide.path,
            }
            selections = []

            # Iterate selections.
            for selection in slide.selections:
                temp_selection = {
                    "center_x": selection.center_coordinates[0],
                    "center_y": selection.center_coordinates[1],
                    "width": selection.width,
                    "height": selection.height,
                }
                selections.append(temp_selection)
            temp_slide.update({"selections": selections})
            slides.append(temp_slide)

        # Adding information about the project.
        project = {
            "name": self.name,
            "work_index": self.work_index,
            "selection": self.selection,
            "width": self.width,
            "height": self.height,
            "slides": slides
        }

        # Saving.
        with open(path, "w") as file: 
            json.dump(project, file, indent = 4)

        self.saved = True
        self.path = path
        
    """
    Load and initialize the Project from a JSON format file.
    Note that the previews are not generated in this function, as fake paths 
    can potentially exist in a JSON file. Use ProjectVerifier to make sure that 
    the project is safe before proceeding.
    Note that in practice, the project file always have SCP extensions.
    @param path: str, the path to the project file.
    """
    def load_json(self, path):
        self.path = path
        self.saved = True
        self.slides = []

        # Loading project file.
        with open(path, "r") as file:
            project = json.load(file)
        
        self.name = project["name"]
        self.work_index = project["work_index"]
        self.selection = project["selection"]
        self.width = project["width"]
        self.height = project["height"]

        # Iterate slides.
        for slide in project["slides"]:
            temp_slide = Slide(slide_path = slide["path"])

            # Iterate selections.
            for selection in slide["selections"]:
                temp_selection = SlideSelection()
                temp_selection.center_coordinates = (selection["center_x"], 
                                                     selection["center_y"])
                temp_selection.width = selection["width"]
                temp_selection.height = selection["height"]
                temp_slide.selections.append(temp_selection)

            self.slides.append(temp_slide)

    """
    Generate previews for all the slides in the Project.
    @param resolution: float, the resolution of the preview file generated.
    """
    def generate_previews(self, resolution):
        for slide in self.slides:
            slide.generate_preview(resolution)

class Slide():
    # Each Slide corresponds to an image of a slide.

    def __init__(self, slide_path):
        self.file_name = os.path.basename(slide_path)

        self.path = slide_path
        self.folder_path = os.path.dirname(slide_path)

        # selections should be a list of SlideSelection objects.
        self.selections = []

        self.width = 0
        self.height = 0

        # Path of the temporary preview file.
        self.preview = None
        self.icon = None

    """
    Check if any selection will be over the boundary of the slide for an 
    arbitrary new selection size.
    @param width: int, the new width for selection areas.
    @param height: int, the new height for selection areas.
    @return True (all selections are safe) / False (overflow exists).
    """
    def check_selection_size(self, width, height):
        # Calculate the new length in each direction from the center.
        left = width // 2
        right = math.ceil(width / 2)
        top = height // 2
        bottom = math.ceil(height / 2)

        # Iterate through each selection point to check.
        for selection in self.selections:
            x = selection.center_coordinates[0]
            y = selection.center_coordinates[1]
            if x - left < 0:
                return False
            if x + right > self.width:
                return False
            if y - top < 0:
                return False
            if y + bottom > self.height:
                return False

        return True
    
    """
    Update the width and height of all selections.
    @param width: int, the new width.
    @param height: int, the new height.
    """
    def set_selection_size(self, width, height):
        for i in range(len(self.selections)):
            self.selections[i].width = width
            self.selections[i].height = height

            # Check if the center coordinates need to be changed.
            x = self.selections[i].center_coordinates[0]
            y = self.selections[i].center_coordinates[1]
            x = max(x, math.ceil(width / 2))
            y = max(y, math.ceil(height / 2))
            x = min(x, self.width - math.ceil(width / 2))
            y = min(y, self.height - math.ceil(height / 2))

    """
    Generate a preview temp file and store its path with the given resolution.
    @param preview_res: float, the resolution of the preview files generated.
    @param icon_width: int, the width of the QPixmap used during Step1.
    @param icon_height: int, the height of the QPixmap used during Step1.
    """
    def generate_preview(self, preview_res, icon_width = 100, \
                         icon_height = 100):
        # For some reason, using QPixmap here clogs the main thread.
        original = QImage(self.path)
        self.width = original.width()
        self.height = original.height()

        if preview_res != 1:
            # Resizing the image.
            self.preview = original.scaled(\
                math.ceil(self.width * preview_res), \
                math.ceil(self.height * preview_res), \
                Qt.AspectRatioMode.KeepAspectRatio, \
                Qt.TransformationMode.SmoothTransformation)
        else:
            self.preview = original

        self.icon = original.scaled(icon_width, icon_height, \
            Qt.AspectRatioMode.KeepAspectRatio, \
            Qt.TransformationMode.SmoothTransformation)
        
        # Finally, convert the QImages back to QPixmap, losing some efficiency.
        self.preview = QPixmap.fromImage(self.preview)
        self.icon = QPixmap.fromImage(self.icon)
        
    """
    Get a list of the names of the cropped image files for this Slide.
    @return list of str, the list of file names.
    """
    def get_crop_names(self):
        names = []
        name_prefix = self.file_name[:self.file_name.rfind(".")]
        for i in range(len(self.selections)):
            names.append(name_prefix + "_" + str(i + 1) + ".tif")
        
        return names

    """
    Save all cropped image selections to a given path.
    NOte that get_crop_names is called in this function.
    @param path: str, the path to the directory for the files to be saved in.
    @return failed: list, the files that failed to export.
    """
    def save_crops(self, path):
        failed = []
        names = self.get_crop_names()
        original = QImage(self.path)

        for i in range(len(self.selections)):
            temp_path = os.path.join(path, names[i])

            x = self.selections[i].center_coordinates[0]
            y = self.selections[i].center_coordinates[1]
            width = int(self.selections[i].width)
            height = int(self.selections[i].height)

            left = int(x - width // 2)
            top = int(y - height // 2)

            temp_image = original.copy(QRect(left, top, width, height))

            try:
                # Removing any existing file with os is always safer.
                # In some cases, Pillow will cause even the GUI to freeze.
                if os.path.exists(temp_path) and os.path.isfile(temp_path):
                    os.remove(temp_path)
                temp_image.save(temp_path)
            except Exception as e:
                failed.append(os.path.basename(names[i]))

        return failed

class SlideSelection():
    # SlideSelection contains information about a selected area on a slide.
    
    def __init__(self):
        self.center_coordinates = (0, 0)
        self.width = 0
        self.height = 0
