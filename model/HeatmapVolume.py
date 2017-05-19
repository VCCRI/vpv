from .volume import Volume
import numpy as np
import os
import tempfile
from collections import OrderedDict
import SimpleITK as sitk
from common import read_image, timing

from lookup_tables import Lut
from read_minc import mincstats_to_numpy


class HeatmapVolume(Volume):
    def __init__(self, *args):
        self.connected_components = OrderedDict()
        super(HeatmapVolume, self).__init__(*args)
        self.lt = Lut()
        self.negative_lut = None
        self.positive_lut = None
        initial_lut = self.lt.heatmap_lut_list()[0]

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

        self.non_zero_mins = self._get_non_zero_mins()
        self.find_largest_connected_components()
        self.set_lut(initial_lut)

        self.max = self._arr_data.max()
        self.min = self._arr_data.min()

    # @property
    # def negative_lut(self):
    #     return self._negative_lut
    #
    # @negative_lut.setter
    # def negative_lut(self, lut):
    #     self._negative_lut = lut
    #
    # @property
    # def positive_lut(self):
    #     return self._negative_lut
    #
    # @positive_lut.setter
    # def positive_lut(self, lut):
    #     self._negative_lut = lut

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

    def set_lut(self, lut_name):
        self.positive_lut, self.negative_lut = self.lt.get_lut(lut_name)
        # If there are no positive or negative values, se the LUT to full transparancy
        if self.neg_levels[0] == self.neg_levels[1]:
            self.negative_lut[:] = 0
        if self.pos_levels[0] == self.pos_levels[1]:
            self.positive_lut[:] = 0

    def get_lut(self):
        return self.negative_lut, self.positive_lut

    def get_data(self, orientation, index=1):
        """
        overide the base method. return two arrays instead of one. One with negative values and the other with positives
        :param orientation:
        :param index:
        :return:
        """
        array = super(HeatmapVolume, self).get_data(orientation, index)

        neg_array = np.copy(array)
        neg_array[neg_array > 0] = 0
        pos_array = np.copy(array)
        pos_array[pos_array < 0] = 0

        return neg_array, pos_array

    def set_lower_positive_lut(self, value):
        if value > self.max:
            value = self.max - 0.1
        self.pos_levels[0] = value

    def set_upper_positive_lut(self, value):
        self.pos_levels[1] = value

    def set_lower_negative_lut(self, value):
        self.neg_levels[0] = value
        #self.neg_lut_pos[0] = value
        #self._set_negative_lut()

    def set_upper_negative_lut(self, value):
        if value < self.min:
            value = self.min + 0.1
        self.neg_levels[1] = value
        #self.neg_lut_pos[1] = value
        #self._set_negative_lut()


class DualHeatmap(HeatmapVolume):
    """
    When the dual t/p value data npz file is loaded, it is stored here
    """
    def __init__(self, *args):
        self.qvals = None  # Set in _load_data
        self.thread = None
        self.qcutoff = 0.05
        super(DualHeatmap, self).__init__(*args)
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