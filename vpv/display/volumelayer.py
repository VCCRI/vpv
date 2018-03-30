from PyQt5 import QtGui
import pyqtgraph as pg
from .layer import Layer


class VolumeLayer(Layer):

    def __init__(self, *args):
        super(VolumeLayer, self).__init__(*args)
        self.image_item = pg.ImageItem(autoLevels=False)
        self.image_item.setCompositionMode(QtGui.QPainter.CompositionMode_Plus)
        self.image_items.append(self.image_item)
        self.lut = self.lt.get_lut('grey')

    def set_lut(self, lutname):
        self.lut = self.lt.get_lut(lutname)
        if lutname == 'anatomy_labels':
            self.set_blend_mode_over()
        else:
            self.set_blend_mode_plus()
        self.update()

    def set_scale(self, scale):
        self.image_item.setScale(scale)

    def set_blend_mode_plus(self):
        """
        Set to blend for normal volumes
        :return:
        """
        self.image_item.setCompositionMode(QtGui.QPainter.CompositionMode_Plus)

    def set_blend_mode_over(self):
        """
        Set to overlay for labelmaps
        :return:
        """
        self.image_item.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)