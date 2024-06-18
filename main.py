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

import sys

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from mainwindow import *

if __name__ == "__main__":
    # Removing the image size limit.
    QImageReader.setAllocationLimit(0)

    app = QApplication(sys.argv)
    app.setApplicationName("Slides Crop")
    app.setApplicationDisplayName("Slides Crop")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Jonathan A. Epstein Lab")
    icon = QIcon("Slides Crop.icns")
    app.setWindowIcon(icon)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())