from PyQt4 import QtGui
from enum import Enum
import SimpleITK as sitk
import tempfile
import gzip
from os.path import splitext


ZIP_EXTENSIONS = ['']

def error_dialog(parent, title, msg):
       dialog = QtGui.QMessageBox.warning(parent, title, msg, QtGui.QMessageBox.Cancel)


def info_dialog(parent, title, msg):
    dialog = QtGui.QMessageBox.information(parent, title, msg, QtGui.QMessageBox.Ok)


class ImType(Enum):
    VOLUME = 'Volume'
    HEATMAP = 'Heatmap data'
    LAMA_DATA = 'LAMA data'
    VECTORS = "Vectors"
    ANNOTATIONS = "Annotations"
    IMAGE_SERIES = "Image series"
    IMPC_ANALYSIS = "IMPC analysis"

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


def read_image(img_path):
    print('isfhisdjf', img_path)
    if img_path.endswith('.gz'):
        print('dkfjskd')
        # Get the image file extension
        ex = splitext(splitext(img_path)[0])[1]
        tmp = tempfile.NamedTemporaryFile(suffix=ex)
        with gzip.open(img_path, 'rb') as infile:
            data = infile.read()
        with open(tmp.name, 'wb') as outfile:
            outfile.write(data)
        img_path = tmp.name
    img = sitk.ReadImage(img_path)
    arr = sitk.GetArrayFromImage(img)
    return arr
