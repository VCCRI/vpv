from PyQt4 import QtGui
from enum import Enum

def error_dialog(parent, title, msg):
       dialog = QtGui.QMessageBox.warning(parent, title, msg, QtGui.QMessageBox.Cancel)


def info_dialog(parent, title, msg):
    dialog = QtGui.QMessageBox.information(parent, title, msg, QtGui.QMessageBox.Ok)



class Orientation(Enum):
    sagittal = 1
    coronal = 2
    axial = 3


class Stage(Enum):
    e9_5 = 'E9.5'
    e12_5 = 'E12.5'
    e14_5 = 'E14.5-E15.5'
    e18_5 = 'E18.5'


class Layer(Enum):
    """
    Map layer names to z-index
    """
    vol1 = 0
    vol2 = 1
    heatmap = 2
    vectors = 3
