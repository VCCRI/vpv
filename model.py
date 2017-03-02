# Copyright 2016 Medical Research Council Harwell.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# @author Neil Horner <n.horner@har.mrc.ac.uk>

"""
TODO: don't duplicate the full array for each _get_* function
"""
import numpy as np
import os
import tempfile
from PIL import Image
from PyQt4 import QtCore, Qt
from collections import OrderedDict
from scipy import ndimage
from scipy.misc import imresize
import json
from lib.addict import Dict
import SimpleITK as sitk
from common import Orientation, Stage, read_image

from lib import nrrd
from lookup_tables import Lut
from read_minc import minc_to_numpy, mincstats_to_numpy


class LoadVirtualStackWorker(QtCore.QThread):
    progress_signal = QtCore.pyqtSignal([str])

    def __init__(self, file_paths):
        QtCore.QThread.__init__(self)
        self.file_paths = file_paths
        self.memmap_result = None  # Populated at end of run()

    def sitk_load(self, p):
        return read_image(p)

    def pil_load(self, p):
        im = Image.open(p)
        return np.array(im)

    def run(self):
        size = len(self.file_paths)
        # SimpleITK reads in 2D bmps as 3D. So use PIL instead
        if self.file_paths[0].lower().endswith('.bmp'):
            reader = self.pil_load
        else:
            reader = self.sitk_load

        arr = reader(self.file_paths[0])
        dtype = arr.dtype
        zyx = list(arr.shape)
        zyx.insert(0, len(self.file_paths))
        t = tempfile.TemporaryFile()
        m = np.memmap(t, dtype=dtype, mode='w+', shape=tuple(zyx))
        for i, path in enumerate(sorted(self.file_paths)):
            img_arr = reader(path)
            m[i] = img_arr
            self.progress_signal.emit("Loading virtual stack.. {}%".format(str(100.0/size * i)))
        self.memmap_result = m


class Annotation(object):
    """
    Records a single manual annotation
    """
    def __init__(self, x, y, z, dims, stage):
        self.x = x
        self.y = y
        self.z = z
        self.dims = dims  # x,y,z
        self.x_percent, self.y_percent, self.z_percent = self.set_percentages(dims)
        self.stage = stage

    def __getitem__(self, index):
        if index == 0:  # First row of column (dimensions)
            return "{}, {}, {}".format(self.x, self.y, self.z)  # Convert enum member to string for table
        else: # The terms and stages columns
            return self.indexes[index - 1]

    def set_percentages(self, dims):
        xp = 100.0 / dims[0] * self.x
        yp = 100.0 / dims[1] * self.y
        zp = 100.0 / dims[2] * self.z
        return xp, yp, zp


class MpAnnotation(Annotation):
    def __init__(self, x, y, z, mp_term, dims, stage):
        super(MpAnnotation, self).__init__(x, y, z, dims, stage)
        self.mp_term = str(mp_term)
        self.indexes = [self.mp_term, '', self.stage.value]
        self.type = 'mp'


class MaPatoAnnotation(Annotation):
    def __init__(self, x, y, z, ma_term, pato_term, dims, stage):
        super(MaPatoAnnotation, self).__init__(x, y, z, dims, stage)
        self.emap_term = str(ma_term)
        self.pato_term = str(pato_term)
        self.indexes = [self.emap_term, self.pato_term, self.stage.value]
        self.type = 'ma'


class VolumeAnnotations(object):
    """
    Associated with a volume class
    Holds positions and MP terms associated with manual annotations
    """

    def __init__(self, dims):
        self.annotations = []
        self.col_count = 4
        self.dims = dims

    def add_mapato(self, x, y, z, ma, pato, stage):
        """
        Add an emap/pato type annotaiotn unless exact is already present
        """
        for a in self.annotations:
            new_params = (x, y, z, ma, pato)
            old_parmas = (a.x, a.y, a.z, pato)
            if new_params == old_parmas:
                return
        ann = MaPatoAnnotation(x, y, z, ma, pato, self.dims, stage)
        self.annotations.append(ann)

    def add_mp(self,  x, y, z, mp, stage):
        """
        Add a n MP type annotation unless excat already present
        """
        for a in self.annotations:
            new_params = (x, y, z, mp)
            old_parmas = (a.x, a.y, a.z, mp)
            if new_params == old_parmas:
                return
        ann = MpAnnotation(x, y, z, mp, self.dims, stage)
        self.annotations.append(ann)

    def remove(self, row):
        del self.annotations[row]

    def __getitem__(self, index):
        return self.annotations[index]

    def __len__(self):
        return len(self.annotations)


class DataModel(QtCore.QObject):
    """
    The model for our app
    """
    data_changed_signal = QtCore.pyqtSignal()
    updating_started_signal = QtCore.pyqtSignal()
    updating_msg_signal = QtCore.pyqtSignal(str)
    updating_finished_signal = QtCore.pyqtSignal()

    def update_msg_slot(self, msg):
        """
        Gets update messages from the different volume classes which are then propagated to the main window to display
        a progress message

        Parameters
        ----------
        msg: str
            progress message
        """
        self.update_msg_signal.emit(msg)

    def __init__(self):
        super(DataModel, self).__init__()
        self.id_counter = 0
        self._volumes = {}
        self._data = {}
        self._vectors = {}

    def change_vol_name(self, old_name, new_name):
        # Only work on image volumes for now
        if self._volumes.get(old_name):
            # Change the dictionary key entry
            self._volumes[new_name] = self._volumes.pop(old_name)
            # Change the id on the object
            self._volumes[new_name].name = new_name

    def set_interpolation(self, onoff):
        for vol in self._volumes.values():
            vol.set_interpolation(onoff)

    def clear_data(self):
        for key in self._volumes.keys():
            self._volumes[key].destroy()
        for key in self._data.keys():
            self._data[key].destroy()
        self._volumes = {}
        self._data = {}

    def volume_id_list(self):
        return sorted([id_ for id_ in self._volumes])

    def data_id_list(self):
        return sorted([id_ for id_ in self._data])

    def vector_id_list(self):
        return sorted([id_ for id_ in self._vectors])

    def all_volumes(self):
        return [vol for vol in self._volumes.values()]

    def getvol(self, id_):
        # bodge. should merge vols and data, as they have unique ids

        if id_ == 'None':
            return 'None'
        try:
            vol = self._volumes[id_]
        except KeyError:
            pass
        try:
            vol = self._data[id_]
        except KeyError:
            pass
        try:
            vol = self._vectors[id_]
        except KeyError:
            pass  # Need to do something else here, like logging
        return vol

    def getdata(self, id_):
        if id_ == 'None':
            return 'None'
        return self._data[id_]

    def load_image_series(self, series_paths, memory_map):
        volpath = str(series_paths[0])
        n = os.path.basename(volpath)
        unique_name = self.create_unique_name(n)
        vol = ImageSeriesVolume(series_paths, self, 'series', memory_map)
        vol.name = unique_name
        self._volumes[vol.name] = vol
        self.id_counter += 1

    def load_annotation(self, ann_path):
        """
        Load an annotation from a json file. Apply annotations to volumes with the corresponding basename minus
        extension

        Parameters
        ----------
        ann_path: str
            path to annotation file
        Returns
        -------
        None: if successful,
        str: Error message if not succesfull
        """
        file_id = os.path.splitext(os.path.basename(ann_path))[0]
        vol = self._volumes.get(file_id)
        if vol:
            with open(ann_path) as fh:
                ann_dict = Dict(json.load(fh))
                for a in ann_dict.values():
                    # check that diemsions stored in annotation file are same os the loaded volume
                    xyz_in_file = a.volume_dimensions_xyz
                    # reverese as numpy works in zyx
                    vol_dims = list(reversed(vol.get_shape()))
                    if vol_dims != xyz_in_file:
                        return """Error loading annotations\nAnnotations dimensions are {}.
                        Loaded volume dimensions are {}""".format(
                            ",".join([str(x) for x in xyz_in_file]),
                            ",".join([str(x) for x in vol_dims]))

                    if a.annotation_type == 'mp':
                        vol.annotations.add_mp(a.x, a.y, a.z, a.mp_term, Stage(a.stage))
                    elif a.annotation_type == 'emap':
                        vol.annotations.add_mapato(a.x, a.y, a.z, a.emap_term, a.pato_term, Stage(a.stage))
        else:
            return "Could not load annotation: {}. Not able to find loaded volume with same id".format(file_id)
        return None

    def add_volume(self, volpath, data_type, memory_map, lower_threshold=None):
        """
        Load a volume into a subclass of a Volume object
        Parameters
        ----------
        volpath
        data_type
        memory_map
        lower_threshold: float
            A value used to threshold low values. Currently only used for heatmap objects

        Returns
        -------

        """

        if data_type != 'virtual_stack':
            volpath = str(volpath)
            n = os.path.basename(volpath)
            unique_name = self.create_unique_name(n)
        else:
            n = os.path.basename(os.path.split(volpath[0])[0])
            unique_name = self.create_unique_name(n)

        if data_type == 'data':
            vol = DataVolume(volpath, self, 'data')
            if lower_threshold:
                vol.set_upper_negative_lut(-lower_threshold)
                vol.set_lower_positive_lut(lower_threshold)
            vol.name = unique_name
            self._data[vol.name] = vol
        elif data_type == 'vol':
            vol = ImageVolume(volpath, self, 'volume', memory_map)
            vol.name = unique_name
            self._volumes[vol.name] = vol
        elif data_type == 'virtual_stack':
            vol = VirtualStackVolume(volpath, self, 'virtual_stack', memory_map)
            vol.name = unique_name
            self._volumes[vol.name] = vol
        elif data_type == 'dual':
            vol = DualData(volpath, self, 'dual')
            vol.name = unique_name
            self._data[vol.name] = vol
        elif data_type == 'vector':
            vol = VectorVolume(volpath, self, 'vector')
            vol.name = unique_name
            self._vectors[vol.name] = vol

        self.id_counter += 1
        self.data_changed_signal.emit()

    def create_unique_name(self, name):
        """
        Create a unique name for each volume. If it already exists, append a digit in a bracket to it
        :param name:
        :return:
        """
        name = os.path.splitext(name)[0]
        if name not in self._volumes and name not in self._data and name not in self._vectors:
            return name
        else:
            for i in range(1, 100):
                new_name = '{}({})'.format(name, i)
                if new_name not in self._volumes and new_name not in self._data:
                    return new_name


class Volume(Qt.QObject):
    axial_slice_signal = QtCore.pyqtSignal(str, name='axial_signal')

    def __init__(self, vol, model, datatype,  memory_map=False):
        super(Volume, self).__init__()
        self.data_type = datatype
        self.name = None
        self.model = model
        self._arr_data = self._load_data(vol, memory_map)
        self.voxel_size = 28  # Temp hard coding
        self.interpolate = False
        # Set to False if Volume to be destroyed. We can't just delete this object as there are reference to
        # it in Slices.Layers and possibly others
        self.active = True
        self.int_order = 3
        self.min = float(self._arr_data.min())
        self.max = float(self._arr_data.max())

    def get_shape(self):
        return self._arr_data.shape

    def get_axial_slot(self):
        print('get_axial_slot')

    def pixel_axial(self, z, y, x):
        """
        get pixel intensity. due to way pyqtgraph orders the axes, we have to flip the z axis
        """
        y = self._arr_data.shape[1] - y
        return self._arr_data[z, y, x], (z, y, x)

    def pixel_sagittal(self, z, y, x):
        """
        get pixel intensity. due to way pyqtgraph orders the axes, we have to flip the y axis
        """
        return self._arr_data[z, y, x], (z, y, x)

    def pixel_coronal(self, z, y, x):
        """
        get pixel intensity. due to way pyqtgraph orders the axes, we have to flip the y axis
        """
        return self._arr_data[z, y, x], (z, y, x)

    def intensity_range(self):
        return self.min, self.max

    def _load_data(self, path, memmap=False):
        """
        Open data and convert
        todo: error handling
        :param path:
        :return:
        """
        ext = os.path.splitext(path)[1].lower()
        if ext == '.mnc':
            return minc_to_numpy(path)

        vol = read_image(path)
        if memmap:
            temp = tempfile.TemporaryFile()
            m = np.memmap(temp, dtype=vol.dtype, mode='w+', shape=vol.shape)
            m[:] = vol[:]
            return m
        else:
            return vol

    def get_data(self, orientation, index=0):
        """
        Return a 2d slice of image data of the specified axis. If index=None, midpoint is returned
        :param orientation:
        :param index:
        :return:
        """
        if orientation == Orientation.sagittal:
            return self._get_sagittal(index)
        if orientation == Orientation.coronal:
            return self._get_coronal(index)
        if orientation == Orientation.axial:
            return self._get_axial(index)

    def dimension_length(self, orientation):
        """
        Temp bodge. return the number of slices in this dimension
        :param orientation:
        :return:
        """
        if orientation == Orientation.sagittal:
            return self._arr_data[0, 0, :].size
        if orientation == Orientation.coronal:
            return self._arr_data[0, :, 0].size
        if orientation == Orientation.axial:
            return self._arr_data[:, 0, 0].size

    def set_voxel_size(self, size):
        """
        Set the voxel size in real world dimensions
        :param size:
        :return:
        """
        self.voxel_size = size

    def _get_coronal(self, index):
        slice_ = np.flipud(np.rot90(self._arr_data[:, index, :], 1))
        if self.interpolate:
            return self._interpolate(slice_)
        return slice_

    def _get_sagittal(self, index):

        slice_ = np.rot90(self._arr_data[:, :, index], 1)
        if self.interpolate:
            return np.flipud(self._interpolate(slice_))
        return np.flipud(slice_)

    def _get_axial(self, index):
        slice_ = np.rot90(self._arr_data[index, :, :], 3)
        if self.interpolate:
            return self._interpolate(slice_)
        return slice_

    def set_lower_level(self, level):
        #print 'l', level
        self.levels[0] = level

    def set_upper_level(self, level):
        #print 'u', level
        self.levels[1] = level

    def destroy(self):
        self._arr_data = None
        self.active = False

    def set_interpolation(self, state):
        self.interpolate = state

    def _interpolate(self, slice_):
        return imresize(ndimage.zoom(slice_, 2, order=4), 0.5, interp='bicubic')
        #return ndimage.gaussian_filter(slice_, sigma=0.7, order=0)


class ImageVolume(Volume):
    def __init__(self, *args):
        super(ImageVolume, self).__init__(*args)

        # We have annotations only on ImageVolumes
        self.annotations = VolumeAnnotations(list(reversed(list(self.get_shape()))))
        self.levels = [float(self._arr_data.min()), float(self._arr_data.max())]

    # def add_annotation(self, x, y, z, ma, pato):
    #     self.annotations.add(x, y, z, ma, pato)


class VirtualStackVolume(ImageVolume):
    def __init__(self, *args):
        super(VirtualStackVolume, self).__init__(*args)

    def _load_data(self, file_paths, memap=True):
        """

        Parameters
        ----------
        file_paths

        Raises
        ------
        ValueError
            If an image in the stack is of the icorrect dimensions

        """
        # self.worker = LoadVirtualStackWorker(file_paths)
        # self.model.updating_started_signal.emit()
        # self.worker.progress_signal.connect(self.model.updating_msg_signal)
        # self.worker.finished.connect(self.loading_finsihed)
        # self.worker.start()

    # def loading_finsihed(self):
    #     self.model.updating_finished_signal.emit()
    #     return self.worker.memmap_result

        def sitk_load(p):
            return read_image(str(p))

        def pil_load(p):
            im = Image.open(p)
            return np.array(im)

        # SimpleITK reads in 2D bmps as 3D. So use PIL instead
        if file_paths[0].lower().endswith('.bmp'):
            reader = pil_load
        else:
            reader = sitk_load

        arr = reader(file_paths[0])
        dtype = arr.dtype
        zyx = list(arr.shape)
        zyx.insert(0, len(file_paths))
        t = tempfile.TemporaryFile()
        m = np.memmap(t, dtype=str(dtype), mode='w+', shape=tuple(zyx))
        for i, path in enumerate(sorted(file_paths)):
            img_arr = reader(path)
            m[i] = img_arr
        return m


class ImageSeriesVolume(Volume):
    """
    Contains a series of images
    """
    def __init__(self, *args):
        self.images = []
        super(ImageSeriesVolume, self).__init__(*args)
        self.levels = [float(self._arr_data.min()), float(self._arr_data.max())]

    def _load_data(self, paths, memmap=False):
        """
        :param path:
            multiple paths
        :param memmap:
        :return:
        """
        for path in paths:
            array = super(ImageSeriesVolume, self)._load_data(path, memmap)
            self.images.append(array)
        return self.images[0]

    def set_image(self, idx):
        self._arr_data = self.images[idx]

    def num_images(self):
        return len(self.images)


class DataVolume(Volume):
    def __init__(self, *args):
        self.connected_components = OrderedDict()
        super(DataVolume, self).__init__(*args)
        self.lt = Lut()
        neg_lower = float(self._arr_data.min())

        # Fix problem when we have no negative values
        if float(self._arr_data.min()) >= 0:
            neg_upper = 0
        else:
            neg_upper = float(self._arr_data[self._arr_data < 0].max())
        self.neg_levels = [neg_lower, neg_upper]

        pos_upper = self._arr_data.max()
        # Fix problem when we have no positve values
        if self._arr_data.max() <= 0:
            pos_lower = 0
        else:
            pos_lower = self._arr_data[self._arr_data > 0].min()
        self.pos_levels = [float(pos_lower), float(pos_upper)]
        self.neg_lut = self._set_negative_lut()
        self.pos_lut = self._set_positive_lut()

        self.non_zero_mins = self._get_non_zero_mins()
        self.find_largest_connected_components()

    def _get_non_zero_mins(self):
        """
        return the minimum non-zero positive value an dthe maximum non-zero negative value
        used to set the minimum T-statistic values in the view manager sliders
        :return:
        """

        if self._arr_data.min() >= 0:
            neg = 0
        else:
            neg = self._arr_data[self._arr_data < 0].max()
        if self._arr_data.max() <= 0:
            pos = 0
        else:
            pos = self._arr_data[self._arr_data > 0].min()
        self.mins = (neg, pos)
        return self.mins

    def max(self):
        return self._arr_data.max()

    def min(self):
        return self._arr_data.min()

    def positive_min(self):
        return self._arr_data[self._arr_data > 0].min()

    def negative_min(self):
        return self._arr_data[self._arr_data < 0].max()

    def _load_data(self, path, memmap=False):
        """
        override Volume method to cast to 16bit float to speed things up
        """
        if os.path.splitext(path)[1].lower() == '.mnc':

            arr = mincstats_to_numpy(path)
            return arr
        else:
            arr = read_image(path).astype(np.float16)
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

    @timing
    def find_largest_connected_components(self):
        """
        Look for the top n conencted comonets for easy finding
        :return:
        """
        self.connected_components = OrderedDict()
        img = sitk.GetImageFromArray(self._arr_data.astype(np.float32)) # Create this on the fly as it would take up lots of space
        lower_threshold = self.neg_levels[1]
        upper_threshold = self.pos_levels[0]
        binary_img = sitk.BinaryThreshold(img, lower_threshold, upper_threshold, 0, 1)
        conn = sitk.RelabelComponent(sitk.ConnectedComponent(binary_img))
        ls = sitk.LabelStatisticsImageFilter()
        ls.Execute(img, conn)
        number_of_labels = ls.GetNumberOfLabels()
        # Now get the top 50  coordinates of the connected components
        n = 50
        if n > number_of_labels:
            n = number_of_labels
        for i in range(1, n):
            bbox = ls.GetBoundingBox(i)  # x,x,y,y, z,z
            size = ls.GetCount(i)
            if size < 4:
                break
            mean = ls.GetMean(i)

            bbox_zyx = [bbox[4], bbox[5], bbox[2], bbox[3], bbox[0], bbox[1]]
            self.connected_components[size, mean] = bbox_zyx

    def _set_negative_lut(self):
        if self.neg_levels[0] == self.neg_levels[1]:  # There are no negative values
            return self.lt.transparent()
        else:
            return self.lt.hotblue()

    def _set_positive_lut(self):
        if self.pos_levels[0] == self.pos_levels[1]: # There are no positive values
            return self.lt.transparent()
        else:
            return self.lt.hotred()

    def get_data(self, orientation, index=1):
        """
        overide the base method. return two arrays instead of one. One with negative values and the other with positives
        :param orientation:
        :param index:
        :return:
        """
        array = super(DataVolume, self).get_data(orientation, index)

        neg_array = np.copy(array)
        neg_array[neg_array > 0] = 0
        pos_array = np.copy(array)
        pos_array[pos_array < 0] = 0

        return neg_array, pos_array

    def set_lower_positive_lut(self, value):
        self.pos_levels[0] = value

    def set_upper_positive_lut(self, value):
        self.pos_levels[1] = value

    def set_lower_negative_lut(self, value):
        self.neg_levels[0] = value
        #self.neg_lut_pos[0] = value
        #self._set_negative_lut()

    def set_upper_negative_lut(self, value):
        self.neg_levels[1] = value
        #self.neg_lut_pos[1] = value
        #self._set_negative_lut()


class DualData(DataVolume):
    """
    When the dual t/p value data npz file is loaded, it is stored here
    """
    def __init__(self, *args):
        self.qvals = None  # Set in _load_data
        self.thread = None
        self.qcutoff = 0.05
        super(DualData, self).__init__(*args)
        self.TVAL_VOPY = np.copy(self._arr_data)
        self.set_qval_cutoff(self.qcutoff)

    @staticmethod
    def memory_map_array(array):
        """
        Create a copy of the tscores in a memory map. This should never be modified
        """
        t = tempfile.TemporaryFile()
        m = np.memmap(t, dtype=array.dtype, mode='w+', shape=array.shape)
        m[:] = array[:]
        return m

    def _load_data(self, path, memmap=False):
        """
        Override
        """
        data = np.load(path)
        try:
            qvals = data['qvals'][0].astype(np.float16)
            tvals = data['tvals'][0].astype(np.float16)
        except KeyError:
            print("Cant access data in LAMA file")
        else:
            self.qvals = qvals
            return tvals

    # TODO: this needs to be put on a seperate thread as it slows down the gui
    def set_qval_cutoff(self, qval):
        """
        Set the qval filter cutoff. Filter out tscores according
        :param qval:
        :return:
        """
        self.qcutoff = qval
        self._arr_data = self.TVAL_VOPY.copy()
        self._arr_data[self.qvals > self.qcutoff] = 0
        # Reset the min and max values on the newly filtered data
        self.min = float(self._arr_data.min())
        self.max = float(self._arr_data.max())
        img = sitk.GetImageFromArray(self._arr_data.astype(np.float32))
        self.find_largest_connected_components(img)

    def get_qval_cutoff(self):
        return self.qcutoff


class VectorVolume(object):
    """
    Holds deformation vector field volume.
    Does not inherit from Volume as it's so different
    """
    def __init__(self,  vol, model, datatype):
        self.model = model
        self.datatype = datatype
        self._arr_data = self._load_data(vol)
        self.shape = self._arr_data.shape
        self.scale = 1
        self.subsampling = 5

    def _load_data(self, vol, memap=False):
        return read_image(vol)

    def get_coronal(self, index):
        #slice_ = np.rot90(self._arr_data[:, index, :], 1)
        slice_ = np.fliplr(self._arr_data[:, index, :])
        return slice_

    def get_sagittal(self, index):
        slice_ = self._arr_data[:, :, index]
        #slice_ = np.rot90(self._arr_data[:, :, index], 1)
        return slice_

    def get_axial(self, index):
        slice_ = np.flipud(self._arr_data[index, :, :])
        return slice_

    def dimension_length(self, orientation):
        """
        Temp bodge. return the number of slices in this dimension
        :param orientation:
        :return:
        """
        if orientation == Orientation.sagittal:
            return self._arr_data[0, 0, :, 0].size
        if orientation == Orientation.coronal:
            return self._arr_data[0, :, 0, 0].size
        if orientation == Orientation.axial:
            return self._arr_data[:, 0, 0, 0].size


