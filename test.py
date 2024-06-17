import sys

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
"""
app = QApplication(sys.argv)

test = QWidget()

test1 = QHBoxLayout()
test2 = QVBoxLayout()
test3 = QGridLayout()

test4 = QPushButton()
test3.addWidget(test4)

test1.addLayout(test2)
test1.addLayout(test3)

test.setLayout(test1)

print(test.layout().itemAt(1).itemAt(0).widget())
"""
"""
class Test1():
    def __init__(self, project):
        self._project = project

class Test2():
    def __init__(self, project):
        self._project = project

class Project():
    def __init__(self):
        self.test_a = "1"
        self.test_b = "2"

project = Project()
project_1 = Test1(project)
project_1._project.test_a = "3"
project_2 = Test2(project_1)
project_2._project._project.test_b = "4"
print(project.test_a)
print(project.test_b)
"""

#class Test(QGraphicsObject):
#    def __init__(self, parent):
#        super().__init__(parent)

test1 = QColor(255, 0, 0)
#test2 = Test(test1)
#print(test2.parentItem())
test1.setAlpha(32)
test2 = QPen(test1)
test1.setAlpha(128)
test3 = QPen(test1)

print(test2.color().alpha())
print(test3.color().alpha())