from PyQt4 import QtGui, QtCore
from enum import Enum
import SimpleITK as sitk
import tempfile
import gzip
from os.path import splitext
import numpy as np

RAS_DIRECTIONS = (-1.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 1.0)
LPS_DIRECTIONS = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)

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

class AnnotationOption(Enum):
    unobserved = "unobserved"
    normal = 'normal'
    abnormal = 'abnormal'
    image_only = 'imageOnly'

class Orientation(Enum):
    sagittal = 1
    coronal = 2
    axial = 3

class Stage(Enum):
    e9_5 = 'E9.5'
    e12_5 = 'E12.5'
    e14_5 = 'E14.5'
    e15_5 = 'E15.5'
    e18_5 = 'E18.5'


class Layer(Enum):
    """
    Map layer names to z-index
    """
    vol1 = 0
    vol2 = 1
    heatmap = 2
    vectors = 3


class ImageReader(object):
    def __init__(self, img_path):
        if img_path.endswith('.gz'):
            # Get the image file extension
            ex = splitext(splitext(img_path)[0])[1]
            tmp = tempfile.NamedTemporaryFile(suffix=ex)
            with gzip.open(img_path, 'rb') as infile:
                data = infile.read()
            with open(tmp.name, 'wb') as outfile:
                outfile.write(data)
            img_path = tmp.name
        self.img = sitk.ReadImage(img_path)
        self.space = self._convert_direction(self.img.GetDirection())
        self.vol = sitk.GetArrayFromImage(
            self.img)

    def _convert_direction(self, directions):
        """
        Convert the coordinate system in the sitk object to human readable
        Returns
        -------

        """
        dir_map = {
            (-1.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 1.0): 'RAS'}
        return dir_map.get(directions)



def read_image(img_path, convert_to_ras=False):
    if img_path.endswith('.gz'):
        # Get the image file extension
        ex = splitext(splitext(img_path)[0])[1]
        tmp = tempfile.NamedTemporaryFile(suffix=ex)
        with gzip.open(img_path, 'rb') as infile:
            data = infile.read()
        with open(tmp.name, 'wb') as outfile:
            outfile.write(data)
        img_path = tmp.name
    img = sitk.ReadImage(img_path)
    direction = img.GetDirection()
    arr = sitk.GetArrayFromImage(img)  # Leave this fix out for now until I make optin available to chose orientation
    # if convert_to_ras: # testing to get orientation the same as in IEV by default
    #     #convert to RAS (testing)
    #     arr = np.flip(arr, 0)
        # arr = np.flip(arr, 2)
    return arr


def timing(f):
    import time
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print('%s function took %0.3f ms' % (f.__name__, (time2 - time1) * 1000.0))
        return ret
    return wrap

# class infoDialogTimed(QtGui.QMessageBox):
#     def __init__(self, timeout, message):
#         super(infoDialogTimed, self).__init__(self, timeout, message)
#         self.timeout = timeout
#         timeoutMessage = "Closing in {} seconds".format(timeout)
#         #self.setText('\n'.join((message, timeoutMessage)))
#
#     def showEvent(self, event):
#         QtCore.QTimer().singleShot(self.timeout*1000, self.close)
#         super(infoDialogTimed, self).showEvent(event)