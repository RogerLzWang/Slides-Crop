import json
import math
import os
import tempfile

from PIL import Image

Image.MAX_IMAGE_PIXELS = None

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

    def save_json(self, path):
        slides = []
        for slide in self.slides:
            temp_slide = {
                "path": slide.path,
            }
            selections = []

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

        project = {
            "name": self.name,
            "work_index": self.work_index,
            "selection": self.selection,
            "width": self.width,
            "height": self.height,
            "slides": slides
        }

        with open(path, "w") as file: 
            json.dump(project, file, indent = 4)

        self.saved = True
        self.path = path
        
    def load_json(self, path, resolution):
        self.path = path
        self.saved = True
        self.slides = []
        with open(path, "r") as file:
            project = json.load(file)
        
        self.name = project["name"]
        self.work_index = project["work_index"]
        self.selection = project["selection"]
        self.width = project["width"]
        self.height = project["height"]

        for slide in project["slides"]:
            temp_slide = Slide(slide_path = slide["path"])
            for selection in slide["selections"]:
                temp_selection = SlideSelection()
                temp_selection.center_coordinates = (selection["center_x"], 
                                                     selection["center_y"])
                temp_selection.width = selection["width"]
                temp_selection.height = selection["height"]
                temp_slide.selections.append(temp_selection)

            temp_slide.generate_previews(resolution)
            self.slides.append(temp_slide)

# Each Slide corresponds to an image of a slide.
class Slide():
    def __init__(self, slide_path, resolution = 0.5):
        self.file_name = os.path.basename(slide_path)

        self.path = slide_path
        self.folder_path = os.path.dirname(slide_path)

        # selections should be a list of SlideSelection objects.
        self.selections = []

        self.width = 0
        self.height = 0

        # Temporary preview files.
        self.preview = None

        self.generate_previews(resolution)

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

    def generate_previews(self, resolution):
        original = Image.open(self.path)
        self.width, self.height = original.size

        if resolution != 1:
            # Calculating the dimensions of the preview images.
            preview_size = (math.ceil(self.width * resolution), \
                            math.ceil(self.height * resolution))
            # Resizing the image.
            preview = original.resize(preview_size)
            # Creating temporary files to store the preview images.
            self.preview = tempfile.NamedTemporaryFile()
            # Saving the preview images in the temporary files.
            preview.save(self.preview, format = "PNG")

    def check_path(self, path):
        pass

    def get_crop_names(self):
        names = []
        name_prefix = self.file_name[:self.file_name.rfind(".")]
        for i in range(len(self.selections)):
            names.append(name_prefix + "_" + str(i + 1) + ".tif")
        
        return names

    def save_crops(self, path):
        names = self.get_crop_names()
        image = Image.open(self.path)

        for i in range(len(self.selections)):
            temp_path = os.path.join(path, names[i])

            x = self.selections[i].center_coordinates[0]
            y = self.selections[i].center_coordinates[1]
            width = self.selections[i].width
            height = self.selections[i].height

            left = x - width // 2
            right = x + math.ceil(width / 2)
            top = y - height // 2
            bottom = y + math.ceil(height / 2)

            temp_image = image.crop([left, top, right, bottom])
            temp_image.save(temp_path)

class SlideSelection():
    # SlideSelection contains information about a selected area on a slide.
    
    def __init__(self):
        self.center_coordinates = (0, 0)
        self.width = 0
        self.height = 0
