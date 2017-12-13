
import numpy as np
import os
import tempfile
from PyQt4 import QtCore, Qt
from scipy import ndimage
from scipy.misc import imresize
from common import Orientation, read_image, ImageReader
from read_minc import minc_to_numpy


class Volume(Qt.QObject):
    """
    Basically a wrapper around a numpy 3D array
    The classes that inherit from this add functionality specific to those volume type
    """
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
        # The coordinate spacing of the input volume
        self.space = None

    def get_shape_zyx(self):
        return self._arr_data.shape

    def get_shape_xyz(self):
        return tuple(reversed(self._arr_data.shape))

    def get_axial_slot(self):
        print('get_axial_slot')

    def pixel_axial(self, z, y, x, flip=False):
        """
        get pixel intensity. due to way pyqtgraph orders the axes, we have to flip the z axis
        """
        vox = self.get_data(Orientation.axial, z, flip, (x, y))
        return vox
    # y = self._arr_data.shape[1] - y
        # return self._arr_data[z, y, x], (z, y, x)

    def pixel_sagittal(self, z, y, x, flip=False):
        """
        get pixel intensity. due to way pyqtgraph orders the axes, we have to flip the y axis
        """
        vox = self.get_data(Orientation.sagittal, x, flip, (y, z))
        return vox

    def pixel_coronal(self, z, y, x, flip=False):
        """
        get pixel intensity. due to way pyqtgraph orders the axes, we have to flip the y axis
        """
        vox = self.get_data(Orientation.coronal, y, flip, (x, z))
        return vox

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

        ir = ImageReader(path)
        vol = ir.vol
        self.space = ir.space
        if memmap:
            temp = tempfile.TemporaryFile()
            m = np.memmap(temp, dtype=vol.dtype, mode='w+', shape=vol.shape)
            m[:] = vol[:]
            return m
        else:
            return vol

    def get_data(self, orientation, index=0, flip=False, xy=None):
        """
        Get a 2D slice given the index and orthogonal orientation. Optioanlly return the slice flipped in x
        Parameters
        ----------
        orientation: Orientation
        index: int
            the slice to returb
        flip: bool
            to flip in x or not

        Returns
        -------
        np.ndarry 2D

        """
        if orientation == Orientation.sagittal:
            return self._get_sagittal(index, flip, xy)
        if orientation == Orientation.coronal:
            return self._get_coronal(index, flip, xy)
        if orientation == Orientation.axial:
            return self._get_axial(index, flip, xy)

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

    def _get_coronal(self, index, flip, xy=None):
        index = self._arr_data.shape[1] - index  # Go in reverse so we go from front to back
        slice_ = np.flipud(np.rot90(self._arr_data[:, index, :], 1))
        if flip:
            slice_ = np.flipud(slice_)
        if xy:
            y, x = xy
            slice_ = slice_[y, x]
        return slice_

    # Testing. Adding reverse option to try and get same view sequence as IEV. Need to flip now
    def _get_sagittal(self, index, flip, xy=None):
        slice_ = np.rot90(self._arr_data[:, :, index], 1)
        if flip:
            slice_ = np.flipud(slice_)
        if xy:
            y, x = xy
            slice_ = slice_[y, x]
        return slice_

    def _get_axial(self, index, flip, xy=None):
        index = self._arr_data.shape[0] - index  # Go in reverse so we go from head to tail
        slice_ = np.rot90(self._arr_data[index, :, :], 3)
        if flip:
            slice_ = np.flipud(slice_)
        if xy:
            y, x = xy
            slice_ = slice_[y, x]
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
