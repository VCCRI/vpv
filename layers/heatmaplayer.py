from PyQt5 import QtGui
import pyqtgraph as pg
import numpy as np
from common import Layer
from .layer import LayerBase


class HeatmapLayer(LayerBase):
    def __init__(self, *args):
        super(HeatmapLayer, self).__init__(*args)
        self.neg_image_item = pg.ImageItem(autoLevels=False)
        self.neg_image_item.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)
        self.neg_image_item.setLookupTable(self.lt._hot_red_blue()[1])
        self.image_items.append(self.neg_image_item)

        self.pos_image_item = pg.ImageItem(autoLevels=False)
        self.pos_image_item.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)
        self.pos_image_item.setLookupTable(self.lt._hot_red_blue()[0])
        self.image_items.append(self.pos_image_item)

    def update(self, auto_levels=False):
        """
        :param orientation:
        :param auto_levels:
        :return:
        """
        if self.vol and self.vol != 'None':
            self.neg_image_item.setLookupTable(self.vol.negative_lut)
            self.pos_image_item.setLookupTable(self.vol.positive_lut)
            self.neg_image_item.setLevels(self.vol.neg_levels, update=False)
            self.pos_image_item.setLevels(self.vol.pos_levels, update=False)
            self.reload()

    def reload(self):
        """
        what?
        :return:
        """
        if self.vol:
            slices = self.vol.get_data(self.parent.orientation, self.parent.current_slice_idx)
            for i, ii in enumerate(self.image_items):
                ii.setImage(slices[i], autoLevels=False)

    def set_volume(self, volname):
        """
        :param vol, Volume object from model.py
        """
        if volname == "None":
            self.volume_label_signal.emit("None")
            for i, image_item in enumerate(self.image_items):
                image_item.setImage(opacity=0.0)
            self.vol = None
            return

        self.volume_label_signal.emit(volname)

        self.vol = self.model.getvol(volname) # this is the problem

        orientation = self.parent.orientation


        self.parent.overlay.set_data_label(volname)
        dim_len = self.vol.dimension_length(orientation)

        # If there is a volume image, use the same slice index
        if not self.parent.layers[Layer.vol1].vol:
            # A slice for 'data' is a list of negative and positive values. Get the midslice
            slice_ = self.vol.get_data(orientation, dim_len / 2)
            #self.parent.set_slice_slider(self.dim_len, self.dim_len / 2)
        else:
            # Get the parent current index slice
            slice_ = self.vol.get_data(orientation, self.parent.current_slice_idx)
        #self.vol.levels = self.image_item.getLevels()
        z = self.layer_type.value

        self.neg_image_item.setLookupTable(self.vol.negative_lut)
        self.pos_image_item.setLookupTable(self.vol.positive_lut)
        self.set_slice(self.parent.current_slice_idx)

        # for i, image_item in enumerate(self.image_items):
        #     if self.vol == "None":
        #         # self.vol = None
        #         # The only way I found to hide removed image was to set transparent
        #         image_item.setImage(opacity=0.0)
        #     else:
        #         image_item.setZValue(z)
        #         image_item.setImage(slice_[i], autoLevels=True, opacity=1.0)
        #         z += 1
        self.update()

    def set_slice(self, index, flip=None):
        flip = self.parent.flipped_x
        if self.vol and self.vol != "None":
            slices = self.vol.get_data(self.parent.orientation, index - 1, flip=flip)
            for i, ii in enumerate(self.image_items):
                ii.setImage(slices[i], autoLevels=False)

    def set_t_threshold(self, t):
        if self.vol:
            # This takes a while, so let's have a progress indicator
            self.vol.set_t_threshold(t)

    def clear(self):
        """
        Override as we have multiple imageitems for
        :return:
        """
        self.vol = None
        #clear the image item with an empty array

        self.image_items[0].setImage(np.zeros((2, 2)))
        self.image_items[1].setImage(np.zeros((2, 2)))
        self.item = None
