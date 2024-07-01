#!/usr/bin/python
################################################################################
#
#   main.py
#   Author: Roger Wang
#   Date: 2024-06-17
#
#   Main (program entrance) to Slides Crop. Welcome!
#
################################################################################

import darkdetect
import os
import platform
import sys

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from mainwindow import *

BASEDIR = os.path.dirname(__file__)

if __name__ == "__main__":
    QLocale.setDefault(QLocale(QLocale.Language.English))
    
    # Removing the image size limit.
    QImageReader.setAllocationLimit(0)

    app = QApplication(sys.argv)
    app.setApplicationName("Slides Crop")
    app.setApplicationDisplayName("Slides Crop")
    app.setApplicationVersion("1.1.2")
    app.setOrganizationName("Jonathan A. Epstein Lab")
    if platform.system() == "Darwin":
        icon = QIcon(os.path.join(BASEDIR, "icon", "Slides Crop.icns"))
    else:
        icon = QIcon(os.path.join(BASEDIR, "icon", "Slides Crop.ico"))
    app.setWindowIcon(icon)

    # Using darkdetect to check if the system is currently in dark mode.
    if darkdetect.isDark():
        stylesheet_file = os.path.join(BASEDIR, "qss", "style_dark.qss")
        chevron_down_path = os.path.join(BASEDIR, "svg", "dark", \
                                         "chevron-down.svg")
        chevron_up_path = os.path.join(BASEDIR, "svg", "dark", \
                                       "chevron-up.svg")
    else:
        stylesheet_file = os.path.join(BASEDIR, "qss", "style.qss")
        chevron_down_path = os.path.join(BASEDIR, "svg", \
                                         "chevron-down.svg")
        chevron_up_path = os.path.join(BASEDIR, "svg", \
                                       "chevron-up.svg") 

    # The Windows back slash is never used in QSS.
    chevron_down_path = chevron_down_path.replace("\\", "/")
    chevron_up_path = chevron_up_path.replace("\\", "/")

    # Setting stylesheet.
    with open(stylesheet_file, "r") as stylesheet:
        stylesheet_str = stylesheet.read()

        # Since QSS is incompatible with adding relative paths, we replace the 
        # paths for all images loaded in the QSS here.
        stylesheet_str = stylesheet_str.replace("QSSPATH_CHEVRONUP", \
                                                chevron_up_path)
        stylesheet_str = stylesheet_str.replace("QSSPATH_CHEVRONDOWN", \
                                                chevron_down_path)
        app.setStyleSheet(stylesheet_str)
    
    window = MainWindow()
    window.show()

    sys.exit(app.exec())