from PyQt5.QtWidgets import QMessageBox
from enum import Enum
import SimpleITK as sitk
import tempfile
import gzip
from os.path import splitext, dirname, realpath, join
import yaml



RAS_DIRECTIONS = (-1.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 1.0)
LPS_DIRECTIONS = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)

ZIP_EXTENSIONS = ['']

_this_dir = dirname(realpath(__file__))
resources_dir = join(_this_dir, 'resources')
style_sheet_path = join(resources_dir, 'stylesheet.qss')
generic_anatomy_label_map_path = join(resources_dir, 'generic_anatomy.csv')

ANNOTATIONS_PROC_VERSION = "IMPC_EMO_002"


def get_stage_from_proc_id(proc_id: str, center_id: dict):
    """
    There is nowhere in the IMPC xml to log what stage we are using.
    We must infer that from the procedures we are using.
    If centre is Harwell return e14.5 instead of e15.5

    Parameters
    ----------
    proc_id: the IMPC procedure ID
    center_id: the one letter centre code.

    Returns
    -------
    str: stage identifier
    """

    if 'EMO' in proc_id:
        if center_id.lower() == 'h':
            return 'e14.5'
        return 'e15.5'
    elif 'EMP' in proc_id:
        return 'e18.5'  # Not sure this is correct. Look up. For now only using E15.5

def load_yaml(path):
    with open(path, 'r') as fh:
        yaml_data = yaml.load(fh)
    return yaml_data

def info_dialog(parent, title, msg):
    QMessageBox.information(parent, title, msg, QMessageBox.Ok)


def error_dialog(parent, title, msg):
    QMessageBox.warning(parent, title, msg, QMessageBox.Ok)


def question_dialog(parent, title, question):
    return QMessageBox.question(parent, title, question)


class ImType(Enum):
    VOLUME = 'Volume'
    HEATMAP = 'Heatmap data'
    LAMA_DATA = 'LAMA data'
    VECTORS = "Vectors"
    ANNOTATIONS = "Annotations"
    IMAGE_SERIES = "Image series"
    IMPC_ANALYSIS = "IMPC analysis"


class AnnotationOption(Enum):
    present = 'present'
    absent = 'absent'
    abnormal = 'abnormal'
    unobservable = "unobservable"
    ambiguous = 'ambiguous'
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


class Layers(Enum):
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
        # if img_path.endswith('nrrd'):
        #     self.vol = nrrd.read(img_path)[0]
        #     self.space = None
        # else:
        self.img = sitk.ReadImage(img_path)
        self.space = self.img.GetDirection()
        self.vol = sitk.GetArrayFromImage(self.img)
        import numpy as np
        # PyqtGraph displays the views on their sides.
        # This transormation puts them the right way up and effectively flips the views so that
        # Axial is the last dimension and sagittal the first
        # self.vol = np.rot90(self.vol, axes=(0, 2), k=1)


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