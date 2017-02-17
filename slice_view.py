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
This module is involved in the display of a single orthogonal view.

"""
from __future__ import division
from PyQt4 import QtGui, QtCore, Qt
import pyqtgraph as pg
from ui.ui_slice_widget import Ui_SliceWidget
from lookup_tables import Lut
import numpy as np
import math
import os
from collections import OrderedDict

from common import Orientation, Layer

DEFAULT_SCALE_BAR_SIZE = 1000.00
DEFAULT_VOXEL_SIZE = 14.0


class ViewBox(pg.ViewBox):
    """
    Subclass the PyQtGraph Viewbox to alter mouse interaction functionality
    """
    wheel_scroll_signal = QtCore.pyqtSignal(bool, name='wheel_scroll')

    def __init__(self):
        super(ViewBox, self).__init__()

    def wheelEvent(self, ev, axis=None):
        d = ev.delta()
        if d > 0:
            self.wheel_scroll_signal.emit(True)
        elif d < 0:
            self.wheel_scroll_signal.emit(False)
        ev.accept()


class InformationOverlay(QtGui.QWidget):
    def __init__(self, parent=None):
        super(InformationOverlay, self).__init__(parent)

        palette = QtGui.QPalette(self.palette())
        palette.setColor(palette.Background, QtCore.Qt.transparent)

        self.setPalette(palette)
        self.vbox = QtGui.QVBoxLayout()
        self.vol_label = QtGui.QLabel()
        self.vol_label.setStyleSheet("font: 13pt; color: white")
        self.vol2_label = QtGui.QLabel()
        self.vol2_label.setStyleSheet("font: 13pt; color: white")
        self.data_label = QtGui.QLabel()
        self.data_label.setStyleSheet("font: 13pt; color: white")
        self.vector_label = QtGui.QLabel()
        self.vector_label.setStyleSheet("font: 13pt;")
        self.vbox.addWidget(self.vol_label)
        self.vbox.addWidget(self.vol2_label)
        self.vbox.addWidget(self.data_label)
        self.vbox.addWidget(self.vector_label)
        self.setLayout(self.vbox)
        self.adjustSize()

    def set_volume_label(self, text):
        if text == 'None':
            text = ''
        self.vol_label.setText(text)
        self.adjustSize()

    def set_volume2_label(self, text):
        if text == 'None':
            text = ''
        self.vol2_label.setText(text)
        self.adjustSize()

    def set_data_label(self, text):
        if text == 'None':
            text = ''
        self.data_label.setText(text)
        self.adjustSize()

    def set_vector_label(self, text):
        if text == 'None':
            text = ''
        self.vector_label.setText(text)
        self.adjustSize()


class RoiOverlay(object):
    def __init__(self, parent):
        self.parent = parent
        self.roi_item = None
        self.animate_count = 10
        self.box_timer = None

    def set(self, x, y, w, h):
        if self.roi_item:
            self.parent.viewbox.removeItem(self.roi_item)
        self.roi_item = QtGui.QGraphicsRectItem(x, y, w, h)
        self.roi_item.setPen(pg.mkPen({'color': [255, 255, 0], 'width': 1}))
        self.parent.viewbox.addItem(self.roi_item)

    def clear(self):
        if self.roi_item:
            self.parent.viewbox.removeItem(self.roi_item)


class AnnotationOverlay(object):
    def __init__(self, parent):
        self.parent = parent
        self.annotation_item = None
        self.x = None
        self.y = None
        self.index = None
        self.color = None
        self.size = None

    def set_size(self, radius):
        if self.index:
            self.size = radius
            self.set(self.x, self.y, self.index, self.color, self.size)

    def update(self, index):
        if self.index:
            if index == self.index:
                self.set(self.x, self.y, self.index, self.color, self.size)

    def set(self, x, y, index, color, size):
        self.index = index
        self.color = color
        self.size = size
        self.x = x
        self.y = y
        x1 = x - (size / 2)
        y1 = y - (size / 2)
        if self.annotation_item:
            self.parent.viewbox.removeItem(self.annotation_item)
        self.annotation_item = QtGui.QGraphicsEllipseItem(x1, y1, size, size)
        self.annotation_item.setPen(pg.mkPen({'color': color, 'width': 1}))
        self.parent.viewbox.addItem(self.annotation_item)

    def clear(self):
        if self.annotation_item:
            self.parent.viewbox.removeItem(self.annotation_item)


class ScaleBar(pg.ScaleBar):
    def __init__(self):
        color = QtGui.QColor(255, 255, 255)
        pen = QtGui.QPen(color)
        brush = QtGui.QBrush(color)
        self.scalebar_size = DEFAULT_SCALE_BAR_SIZE
        super(ScaleBar, self).__init__(size=self.scalebar_size, suffix='um', width=7, pen=pen, brush=brush)
        self.voxel_size = DEFAULT_VOXEL_SIZE
        font = QtGui.QFont('Arial', 16, QtGui.QFont.Bold)
        self.text.setFont(font)
        self.set_scalebar_size(self.scalebar_size)

    def set_voxel_size(self, voxel_size):
        self.voxel_size = voxel_size
        self.updateBar()

    def set_color(self, qcolor):
        self.bar.setBrush(QtGui.QBrush(qcolor))
        self.bar.setPen(QtGui.QPen(qcolor))
        self.updateBar()

    def set_scalebar_size(self, size):
        self.scalebar_size = size
        if size >= 1000:
            suffix = 'mm'
            size = size / 1000
        else:
            suffix = 'um'
        # self.text.setText(pg.fn.siFormat(size, suffix=suffix))
        self.text.setText('')
        self.updateBar()

    def updateBar(self):
        view = self.parentItem()
        if view is None:
            return
        p1 = view.mapFromViewToItem(self, QtCore.QPointF(0, 0))
        p2 = view.mapFromViewToItem(self, QtCore.QPointF(self.scalebar_size, 0))
        w = (p2-p1).x() / self.voxel_size
        self.bar.setRect(QtCore.QRectF(-w, 0, w, self._width))
        self.text.setPos(-w/2., 0)


class SliceWidget(QtGui.QWidget, Ui_SliceWidget):
    """
    The qt widget that displays a signle ortohogoal view.
    Has attribute layers: {z_index: Layer}
    """
    mouse_shift = QtCore.pyqtSignal(int, int, int, Orientation, name='mouse_shift')
    mouse_pressed_signal = QtCore.pyqtSignal(int, int, int, Orientation, str, name='mouse_pressed')
    crosshair_visible_signal = QtCore.pyqtSignal(bool)
    volume_position_signal = QtCore.pyqtSignal(int, int, int)
    volume_pixel_signal = QtCore.pyqtSignal(float)
    data_pixel_signal = QtCore.pyqtSignal(float)
    object_counter = 0
    manage_views_signal = QtCore.pyqtSignal(int)
    voxel_clicked_signal = QtCore.pyqtSignal(tuple, Orientation, tuple)  # vols, orientation, (x, y)
    orthoview_link_signal = QtCore.pyqtSignal(str, QtCore.QPoint)
    scale_changed_signal = QtCore.pyqtSignal(Orientation, int, list)
    resized_signal = QtCore.pyqtSignal()
    slice_index_changed_signal = QtCore.pyqtSignal(Orientation, int, int)
    move_to_next_vol_signal = QtCore.pyqtSignal(int, bool)  # Slice id, reverse order

    def __init__(self, orientation, model, border_color):
        super(SliceWidget, self).__init__()
        self.ui = Ui_SliceWidget()
        # Bug in Windows - https://groups.google.com/forum/#!msg/pyqtgraph/O7E2sWaEWDg/7KPVeiO6qooJ
        if os.name == 'nt':
            pg.functions.USE_WEAVE = False
        else:
            pg.functions.USE_WEAVE = True

        self.scalebar = None
        self.ui.setupUi(self)
        self.ui.labelSliceNumber.setFixedWidth(30)

        self.orientation = orientation
        self.model = model
        self.slice_color = border_color
        self.id = SliceWidget.object_counter
        SliceWidget.object_counter += 1

        self.overlay = InformationOverlay(self)
        self.overlay.show()

        self.link_orthoganal_views = False

        # ViewBox. Holds the pg.ImageItems
        self.viewbox = ViewBox()
        self.viewbox.wheel_scroll_signal.connect(self.wheel_scroll)
        self.ui.graphicsView.centralWidget.addItem(self.viewbox)
        self.viewbox.setAspectLocked()

        # testing
        self.viewbox.sigRangeChangedManually.connect(self.range_changed)

        self.ui.graphicsView.setAntialiasing(True)
        # self.ui.graphicsView.useOpenGL(True)  # Slows things down and seems to mess up antialiasing
        self.viewbox.enableAutoRange()

        self.viewbox.scene().sigMouseMoved.connect(self.mouse_moved)
        self.viewbox.scene().sigMouseClicked.connect(self.mouse_pressed)
        self.shift_pressed = False

        # Reduce the padding/border between slice views
        self.ui.graphicsView.ci.layout.setContentsMargins(0, 0, 0, 0)
        self.ui.graphicsView.ci.layout.setSpacing(1)

        self.setStyleSheet('QWidget#controlsWidget{{ background-color: {} }}'.format(border_color))

        self.current_slice_idx = 0
        self.layers = OrderedDict()

        self.viewbox.setAspectLocked(True)

        # Slice control signals ########################################################################################
        self.ui.sliderSlice.valueChanged.connect(self.on_change_slice)
        self.ui.sliderSlice.sliderPressed.connect(self.slice_slider_pressed)
        self.ui.sliderSlice.sliderReleased.connect(self.slice_slider_released)

        self.ui.pushButtonScrollLeft.pressed.connect(self.left_scroll_button_pressed)
        self.ui.pushButtonScrollLeft.released.connect(self.scroll_button_released)

        self.ui.pushButtonScrollRight.pressed.connect(self.right_scroll_button_pressed)
        self.ui.pushButtonScrollRight.released.connect(self.scroll_button_released)

        self.button_scrolling = False
        ################################################################################################################
        self.ui.pushButtonManageVolumes.clicked.connect(self.on_manage_views)

        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.hLine.setZValue(10)
        self.vLine.setZValue(10)
        self.vLine.setOpacity(0.0)
        self.hLine.setOpacity(0.0)
        cross_hair_pen = pg.mkPen(color=(229, 255, 0))
        self.vLine.setPen(cross_hair_pen)
        self.hLine.setPen(cross_hair_pen)

        self.viewbox.addItem(self.vLine)
        self.viewbox.addItem(self.hLine)

        self.setMouseTracking(1)

        self.roi = RoiOverlay(self)
        self.annotation = AnnotationOverlay(self)

        self.ui.seriesSlider.hide()

        self.show()

    def set_scalebar_color(self, qcolor):
        self.scalebar.set_color(qcolor)

    def annotation_radius_changed(self, radius):
        self.annotation.set_size(radius)

    def resizeEvent(self, int_):
        """
        Overide the widget resize event. Updates the scale bar. Does not work unless I stick a sleep in there.
        TODO: Work out how to hook into an event after the size of the widget has been set
        """
        return
        QtCore.QTimer.singleShot(2000, lambda: self.resized_signal.emit())

    def show_scale_bar(self, visible):
        if visible:
            self.scalebar.show()
            self.scalebar.updateBar()
        else:
            self.scalebar.hide()

    def set_voxel_size(self, size):
        if not self.scalebar:
            return
        self.scalebar.set_voxel_size(size)

    def set_scalebar_size(self, size):
        if not self.scalebar:
            return
        self.scalebar.set_scalebar_size(size)

    def set_roi(self, x, y, w, h):
        self.roi.set(x, y, w, h)

    def set_annotation(self, x, y, color, size):
        self.annotation.set(x, y, self.current_slice_idx, color, size)

    def range_changed(self):
        self.scale_changed_signal.emit(self.orientation, self.id,  self.viewbox.viewRange())
        QtCore.QTimer.singleShot(1000, lambda: self.scalebar.updateBar())

    def set_zoom(self, range_x=None, range_y=None):
        if range_x:
            self.viewbox.setXRange(range_x[0], range_x[1], padding=False)
        if range_y:
            self.viewbox.setYRange(range_y[0], range_y[1], padding=False)
        QtCore.QTimer.singleShot(1000, lambda: self.scalebar.updateBar())

    def set_data_label_visibility(self, visible):
        self.overlay.setVisible(visible)

    def mouse_pressed(self, event):
        self.setFocus()
        pos = event._scenePos
        x = self.layers[Layer.vol1].image_item.mapFromScene(pos).x()
        y = self.layers[Layer.vol1].image_item.mapFromScene(pos).y()
        if x < 0 or y < 0:
            return
        self.mouse_pressed_signal.emit(self.current_slice_idx, x, y, self.orientation, self.layers[Layer.vol1].vol.name)

    def mouse_moved(self, pos):
        """
        On mouse move, get mouse position, volume and data levels and do synchronised slicing between views
        :param pos:
        :return:
        """
 
        self.setFocus()
        x = self.layers[Layer.vol1].image_item.mapFromScene(pos).x()
        y = self.layers[Layer.vol1].image_item.mapFromScene(pos).y()
        if x < 0 or y < 0:
            return
        if self.layers[Layer.vol1].vol:
            try:
                pix, pos = self.get_pixel(Layer.vol1, self.current_slice_idx, y, x)
                self.volume_position_signal.emit(int(pos[0]), int(pos[1]), int(pos[2]))
            except IndexError:  # mouse placed outside the image can yield non-existent indices
                pass
            else:
                self.volume_pixel_signal.emit(round(float(pix), 2))

        if self.layers[Layer.heatmap].vol:
            try:
                pix, _ = self.get_pixel(Layer.heatmap, self.current_slice_idx, y, x)
            except IndexError:
                pass
            else:
                self.data_pixel_signal.emit(round(float(pix), 6))

        if self.link_orthoganal_views:
            self.mouse_shift.emit(self.current_slice_idx, x, y, self.orientation)

    def get_pixel(self, layer_index, z, y, x):
        pos = []
        try:
            if self.orientation == Orientation.axial:
                pix_intensity, pos = self.layers[layer_index].vol.pixel_axial(self.current_slice_idx, y, x)
            if self.orientation == Orientation.sagittal:
                pix_intensity, pos = self.layers[layer_index].vol.pixel_sagittal(y, x, self.current_slice_idx)
            if self.orientation == Orientation.coronal:
                pix_intensity, pos = self.layers[layer_index].vol.pixel_coronal(y, self.current_slice_idx, x)
            return pix_intensity, pos,
        except AttributeError:
            print(self.layers[layer_index].vol)

    def clear_layers(self):
        for layer in self.layers.items():
            layer[1].clear()  # Why is layer a tuple?
            layer[1].clear()

    def register_layer(self, layer_enum, viewmanager):
        """
        Create a new Layer object and add to layers
        """
        if layer_enum == Layer.vol1:  # the bottom layer is always an image volume
            layer = VolumeLayer(self, layer_enum, self.model, viewmanager)
            self.viewbox.addItem(layer.image_item)
            self.scalebar = ScaleBar()
            self.scalebar.setParentItem(self.viewbox)
            self.scalebar.anchor((1, 1), (1, 1), offset=(-60, -60))
            self.scalebar.hide()
            layer.volume_label_signal.connect(self.overlay.set_volume_label)

        elif layer_enum == Layer.vol2:
            layer = VolumeLayer(self, layer_enum, self.model, viewmanager)
            self.viewbox.addItem(layer.image_item)
            layer.volume_label_signal.connect(self.overlay.set_volume2_label)

        elif layer_enum == Layer.heatmap:
            layer = DataLayer(self, layer_enum, self.model, viewmanager)
            layer.volume_label_signal.connect(self.overlay.set_data_label)
            for image_item in layer.image_items:
                self.viewbox.addItem(image_item)

        elif layer_enum == Layer.vectors:
            layer = VectorLayer(self.viewbox, self, self.model)

        self.layers[layer_enum] = layer

    def all_layers(self):
        return [layer for layer in self.layers.values()]

    def refresh_layers(self):
        for layer in self.all_layers():
            if layer.vol:
                layer.reload()

    def slice_slider_released(self):
        """
        switch off interpolation while scolling to make it smoother
        """
        #self.model.interpolate = True

        # Reset the interpolated slice as sliding through the faster non-interpolated slices
        pass
        #self.refresh_layers()

    def slice_slider_pressed(self):
        """
        Swith interpolation back on after scrolling
        :return:
        """
        return
        self.model.interpolate = False

    def left_scroll_button_pressed(self):
        # Switch of interpolation while scrolling

        self.model.interpolate = True
        self.button_scrolling = True
        self.left_scroll_timer = QtCore.QTimer()
        self.left_scroll_timer.timeout.connect(self.button_scroll_left)
        self.left_scrolls = 0
        self.left_scroll_timer.start(150)

    def button_scroll_left(self):
        self.left_scrolls += 1
        if self.left_scrolls > 4:
            # speed up after a few slices
            self.left_scroll_timer.setInterval(40)
        self.set_slice(self.current_slice_idx - 1)
        self.emit_index_changed(self.current_slice_idx - 1)
        if not self.button_scrolling:
            self.left_scroll_timer.stop()
            # Switch interpolation back on for the static image and refresh
            #self.model.interpolate = True
            self.refresh_layers()

    def scroll_button_released(self):
        self.button_scrolling = False

    def right_scroll_button_pressed(self):
        # Switch of interpolation while scrolling
        #self.model.interpolate = False
        self.button_scrolling = True
        self.right_scroll_timer = QtCore.QTimer()
        self.right_scroll_timer.timeout.connect(self.button_scroll_right)
        self.right_scrolls = 0
        self.right_scroll_timer.start(150)

    def button_scroll_right(self):
        self.right_scrolls += 1
        if self.right_scrolls > 4:
            # speed up after a few slices
            self.right_scroll_timer.setInterval(40)
        self.set_slice(self.current_slice_idx + 1)
        self.emit_index_changed(self.current_slice_idx + 1)
        if not self.button_scrolling:
            self.right_scroll_timer.stop()
            # Switch interpolation back on for the static image and refresh
            #self.model.interpolate = True
            self.refresh_layers()

    def emit_index_changed(self, idx):
        self.slice_index_changed_signal.emit(self.orientation, self.id, idx)

    def wheel_scroll(self, forward):
        if forward:
            self.set_slice(self.current_slice_idx + 1)
            self.emit_index_changed(self.current_slice_idx + 1)
        else:
            self.set_slice(self.current_slice_idx - 1)
            self.emit_index_changed(self.current_slice_idx - 1)

    def on_manage_views(self):
        self.manage_views_signal.emit(self.id)

    def set_slice(self, index, reverse=False, crosshair_xy=None):
        """
        Used when setting slice from external module.
        Parameters
        ----------
        index: int
            the slice to show
        reverse: bool
            Due to the way pyqtgraph indexes the volumes, for some orientations we need to count from the other side of the volume
        crosshair_xy: tuple
            xy coordinates of the cross hair
        """
        if reverse:
            index = self.layers[Layer.vol1].vol.dimension_length(self.orientation) - index

        self.ui.sliderSlice.setValue(index)
        self._set_slice(index, crosshair_xy)

    def _set_slice(self, index, crosshair_xy=None):
        """
        :param index: int, slice to view
        :param reverse: bool, count from reverse
        """

        self.roi.clear()
        self.annotation.clear()
        self.ui.labelSliceNumber.setText(str(index))

        if index < 0:
            return
        for layer in self.all_layers():
            if layer.vol:
                layer.set_slice(index)

        self.current_slice_idx = index

        if crosshair_xy:
            self.vLine.setPos(crosshair_xy[0])
            self.hLine.setPos(crosshair_xy[1])
        self.annotation.update(self.current_slice_idx)

    def move_slice(self, num_slices):
        """
        Shift slices relative to current view.
        :param num_slices. signed int
        """
        # clear any non-persistent rois

        self._set_slice(self.current_slice_idx + num_slices)

    def set_orientation(self, orientation):

        self.orientation = orientation  # Covert str from combobox to enum member
        # Get the range and midslice of the new orientation
        new_orientation_len = self.layers[Layer.vol1].vol.dimension_length(self.orientation)
        self.current_slice_idx = int(new_orientation_len/2)

        for layer in self.all_layers():
            if layer.vol:
                layer.update()

        self.ui.sliderSlice.blockSignals(True)
        self.ui.sliderSlice.setRange(0, new_orientation_len)
        self.ui.sliderSlice.setValue(self.current_slice_idx)
        self.ui.sliderSlice.blockSignals(False)
        self.viewbox.autoRange()

    def set_slice_slider(self, range, index):
        self.ui.sliderSlice.setRange(0, range)
        self.ui.sliderSlice.setValue(int(index))

    def show_controls(self, show):
        self.ui.controlsWidget.setVisible(show)

    def show_index_slider(self, show):
        self.ui.controlsWidget.setVisible(show)

    # def opacity_change(self, value):
    #     opacity = 1.0 / value
    #     if value == 10:
    #         opacity = 0

    def on_change_slice(self, index):
        self._set_slice(int(index))

    def update_view(self):
        """
        Reload each layers' imageItem after properties set. If it has a volume set
        """
        for view in list(self.layers.values())[0:3]:
            if view.vol:
                view.update()

    ### Key events #####################################################################################################

    def left_key_pressed(self):
        if not self.button_scrolling:
            self.left_scroll_button_pressed()

    def right_key_pressed(self):
        if not self.button_scrolling:
            self.right_scroll_button_pressed()

    def hide_crosshair(self):
        self.hLine.setOpacity(0.0)
        self.vLine.setOpacity(0.0)

    def show_crosshair(self):
        self.hLine.setOpacity(1.0)
        self.vLine.setOpacity(1.0)

    def keyPressEvent(self, event):

        if event.key() == QtCore.Qt.Key_Shift:
            self.crosshair_visible_signal.emit(True)
            self.link_orthoganal_views = True
        elif event.key() == QtCore.Qt.Key_Left:
            self.left_key_pressed()
        elif event.key() == QtCore.Qt.Key_Right:
            self.right_key_pressed()
        elif event.key() == QtCore.Qt.Key_S:
            self.set_orientation(Orientation.sagittal)
        elif event.key() == QtCore.Qt.Key_C:
            self.set_orientation(Orientation.coronal)
        elif event.key() == QtCore.Qt.Key_A:
            self.set_orientation(Orientation.axial)
        elif event.key() == QtCore.Qt.Key_PageUp or event.key() == QtCore.Qt.Key_Up:
            self.move_to_next_vol_signal.emit(self.id, True)
        elif event.key() == QtCore.Qt.Key_PageDown or event.key() ==QtCore.Qt.Key_Down:
            self.move_to_next_vol_signal.emit(self.id, False)

        # Propagate unused signals to parent widget
        else:
            event.ignore()

    def move_to_next_volume(self, reverse=False):
        vol_ids = self.model.volume_id_list()
        if len(vol_ids) < 2:
            return
        current_vol_idx = vol_ids.index(self.layers[Layer.vol1].vol.name)
        if not self.layers[Layer.vol1].vol.name or self.layers[Layer.vol1].vol.name == 'None':
            return
        if reverse:
            if current_vol_idx - 1 < 0:
                new_index = len(vol_ids) - 1
            else:
                new_index = current_vol_idx - 1
        else:
            if current_vol_idx + 1 >= len(vol_ids):
                new_index = 0
            else:
                new_index = current_vol_idx + 1
        new_vol_name = vol_ids[new_index]
        self.layers[Layer.vol1].set_volume(new_vol_name)

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return
        if event.key() == QtCore.Qt.Key_Shift:
            self.crosshair_visible_signal.emit(False)
            self.link_orthoganal_views = False  # show intersecting slices on other views when mouse is moved
        elif event.key() == QtCore.Qt.Key_Left:
            self.scroll_button_released()
        elif event.key() == QtCore.Qt.Key_Right:
            self.scroll_button_released()
        # Propagate unused signals to parent widget
        # else:
        #     event.ignore()

    def mousePressEvent(self, e):
        """
        Find the position that was clicked and emit them along with any stats data volumes in the layers
        """
        xy = self.viewbox.mapFromItemToView(self.viewbox, QtCore.QPointF(e.pos().x(), e.pos().y()))
        clickpos = (xy.x(), xy.y(), self.current_slice_idx)
        datavols = tuple(l.vol for l in self.layers.values() if l.vol and l.vol.data_type == 'stats')
        self.voxel_clicked_signal.emit(datavols, self.orientation, clickpos)

    # def mouseMoveEvent(self, e):
    #     xy = self.viewbox.mapFromItemToView(self.viewbox, QtCore.QPointF(e.pos().x(), e.pos().y()))
    #     # if self.link_orthoganal_views:
    #     #     self.orthoview_link_signal.emit(self.orientation, xy)


class LayerBase(Qt.QObject):
    """
    Represents a layer of an orthogonal view.
    """
    volume_label_signal = QtCore.pyqtSignal(str)

    def __init__(self, parent, layer_type, model, viewmanager):
        super(LayerBase, self).__init__()
        self.viewmanager = viewmanager # This is not ideal. Maybe should think about a Qt signal mapper
        # If it's a data volume, dont add slider, add number box to filter q-values
        self.model = model
        self.parent = parent
        self.image_items = []
        self.vol = None  # When setting to "None" in the view manager we get problems. Needs rewriting
        self.layer_type = layer_type # this should be unique
        self.lt = Lut()

    def clear(self):
        self.vol = None
        #clear the image item with an empty array

        self.image_item.setImage(np.zeros((2,2)))

    def get_imageItem(self): # Delete?
        return self.image_item

    def update(self, auto_levels=False):
        """
        Sets the orientation and centres the image at the mid-slice
        :param orientation:
        :param auto_levels:
        :return:
        """
        if self.vol and self.vol != 'None':
            self.image_item.setLevels(self.vol.levels, update=False)
            self.image_item.setLookupTable(self.lut[0])
            self.reload()

            self.volume_label_signal.emit(self.vol.name)
        else:
            self.volume_label_signal.emit("")

    def reload(self):
        """
        reload the current image. For example when the orientation has changed
        """
        self.image_item.setImage(self.vol.get_data(self.parent.orientation, self.parent.current_slice_idx),
                                 autoLevels=False)

    def set_volume(self, volname, initial=False):
        """
        :param vol, Volume object from model.py
        """
        if volname == "None":
            self.vol = None
            self.image_item.setImage(opacity=0.0)
            return

        self.vol = self.model.getvol(volname)

        self.set_series_slider()

        orientation = self.parent.orientation
        self.name = self.vol.name
        self.image_item.setZValue(self.layer_type.value)

        dim_len = self.vol.dimension_length(orientation)

        # Try setting the new volume to the slice index of the current volume. If out of bounds, set to midslice
        if self.parent.current_slice_idx + 1 > dim_len or initial:
            slice_indx = dim_len / 2
        else:
            slice_indx = self.parent.current_slice_idx
        slice_ = self.vol.get_data(orientation, int(slice_indx))
        self.parent.set_slice_slider(dim_len, slice_indx)

        self.image_item.setImage(slice_, autoLevels=False, opacity=1.0)

        # This fixes problem with linked zooming
        self.parent.viewbox.autoRange()
        self.parent.scalebar.updateBar()

    def set_slice(self, index):
        if self.vol:
            self.image_item.setImage(self.vol.get_data(self.parent.orientation, index - 1), autoLevels=False)

    def set_series_slider(self):
        if self.vol.data_type == 'series':
            num_vols_in_series = len(self.vol.images)
            self.parent.ui.seriesSlider.setRange(0, num_vols_in_series - 1)
            self.parent.ui.seriesSlider.valueChanged.connect(self.series_slider_changed)
            self.parent.ui.seriesSlider.show()
            self.parent.ui.labelImageSeriesNumber.show()
        else:
            self.parent.ui.seriesSlider.hide()
            self.parent.ui.labelImageSeriesNumber.hide()

    def series_slider_changed(self, idx):
        self.vol.set_image(idx)
        self.parent.ui.labelImageSeriesNumber.setText(str(idx))
        self.reload()


class VolumeLayer(LayerBase):

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


class DataLayer(LayerBase):
    def __init__(self, *args):
        super(DataLayer, self).__init__(*args)
        self.neg_image_item = pg.ImageItem(autoLevels=False)
        self.neg_image_item.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)
        self.neg_image_item.setLookupTable(self.lt.hotblue())
        self.image_items.append(self.neg_image_item)

        self.pos_image_item = pg.ImageItem(autoLevels=False)
        self.pos_image_item.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)
        self.pos_image_item.setLookupTable(self.lt.hotred())
        self.image_items.append(self.pos_image_item)

    def update(self, auto_levels=False):
        """
        :param orientation:
        :param auto_levels:
        :return:
        """
        if self.vol and self.vol != 'None':
            self.neg_image_item.setLookupTable(self.vol.neg_lut)
            self.pos_image_item.setLookupTable(self.vol.pos_lut)
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
            for i, image_item in enumerate(self.image_items):
                image_item.setImage(opacity=0.0)
            self.vol = None
            return

        self.vol = self.model.getvol(volname)
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
        self.neg_image_item.setLookupTable(self.vol.neg_lut)
        self.pos_image_item.setLookupTable(self.vol.pos_lut)
        for i, image_item in enumerate(self.image_items):
            if self.vol == "None":
                # self.vol = None
                # The only way I found to hide removed image was to set transparent
                image_item.setImage(opacity=0.0)
            else:
                image_item.setZValue(z)
                image_item.setImage(slice_[i], autoLevels=True, opacity=1.0)
                z += 1

    def set_slice(self, index):
        if self.vol and self.vol != "None":
            slices = self.vol.get_data(self.parent.orientation, index - 1)
            for i, ii in enumerate(self.image_items):
                ii.setImage(slices[i], autoLevels=False)

    def update_qvalue_cutoff(self, value):
        if self.vol:
            # This takes a while, so let's have a progress indicator
            self.vol.set_qval_cutoff(value)

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


class VectorLayer(object):
    def __init__(self, viewbox, parent, model):
        # Create dummy vectors
        self.model = model
        self.parent = parent
        self.orientation = self.parent.orientation
        self.slice_change_function = None
        self.arrows = []
        self.viewbox = viewbox
        self.def_field = None
        self.drawn = False
        self.item = None
        self.arrow_angle = 50
        self.plt = pg.PlotItem()
        self.plt.hideAxis('left')
        self.plt.hideAxis('right')
        self.plt.hideAxis('bottom')
        self.plt.hideAxis('top')
        self.vol = None
        self.arrow_color = "22E300"
        self.vec_mag_min = 0.0
        self.vec_mag_max = 5.0

    def set_magnitude_cutoff(self, min_, max_):
        self.vec_mag_min = min_
        self.vec_mag_max = max_
        self.set_slice(self.current_index)

    def register_slice_change_function(self):
        if self.orientation == Orientation.coronal:
            return self.vol.get_coronal
        elif self.orientation == Orientation.sagittal:
            return self.vol.get_sagittal
        elif self.orientation == Orientation.axial:
            return self.vol.get_axial

    def set_volume(self, volname):
        if volname == "None":
            self.vol = None
            if self.item:
                self.viewbox.removeItem(self.item)
            return

        self.parent.overlay.set_vector_label(volname)

        self.vol = self.model.getvol(volname)
        orientation = self.parent.orientation
        self.slice_change_function = self.register_slice_change_function()
        self.name = self.vol.name
        dim_len = self.vol.dimension_length(orientation)
        self.current_index = dim_len / 2
        midslice = self.slice_change_function(dim_len / 2)
        self.shape = midslice.shape

        self.plt.hideAxis('left')
        self.plt.hideAxis('right')
        self.plt.hideAxis('bottom')
        self.plt.hideAxis('top')
        self.plt.hideButtons()
        self.plt.setRange(xRange=(0, self.shape[0]), yRange=(0, self.shape[1]))
        # self.plt.yRange(shape[2])
        self.viewbox.addItem(self.plt)

        self.set_orientation()

        self.set_slice(dim_len / 2)

    def set_orientation(self):
        """
        set which 2 axes to take from the 3D vector.
        """
        if self.parent.orientation == Orientation.axial:
            self.vector_axes = (1, 0)
        elif self.parent.orientation == Orientation.coronal:
            self.vector_axes = (0, 2)
        elif self.parent.orientation == Orientation.sagittal:
            self.vector_axes = (1, 2)

    def set_slice(self, index=None):
        # if not self.vol:
        #     if self.item:
        #         self.viewbox.removeItem(self.item)
        #     print 'not vol'
        #     return

        if index < 0:
            return
        if not index:
            index = self.current_index
        else:
            self.current_index = index - 1

        c = self.vol.subsampling
        scale = self.vol.scale

        if self.item:
            self.viewbox.removeItem(self.item)

        # Get the slice and 2D vectors for this orientation
        slice_ = self.slice_change_function(index)

        # Get the 2d vector for this plane
        slice_2d_vec = slice_.take(self.vector_axes, axis=2)

        x_points = []
        y_points = []
        connect = []

        for y in range(0, slice_.shape[0] - c, c):
            for x in range(0, slice_.shape[1] -c, c):

                try:

                    subsmapled_box = slice_2d_vec[y: y+c, x: x+c, :]
                except IndexError:
                    print("fell off")
                else:
                    x1 = x + (c/2)
                    y1 = y + (c/2)

                    x_magnitude, y_magnitude = np.mean(subsmapled_box, axis=(0, 1))
                    magnitude = np.linalg.norm((x_magnitude, y_magnitude))
                    if magnitude < self.vec_mag_min:
                        continue
                    if self.orientation == Orientation.axial:
                        x_magnitude, y_magnitude = self.rotate_vector((x_magnitude, y_magnitude), -90.0)

                    x_points.append(x1)
                    y_points.append(y1)
                    connect.append(1)

                    # Draw a line to end of arrow
                    x2 = x1 + (x_magnitude * scale)
                    y2 = y1 + (y_magnitude * scale)

                    x_points.append(x2)
                    y_points.append(y2)
                    connect.append(1)

                    arrow_Xs, arrow_ys = self.draw_arrow_head(x2, x1, y2, y1)

                    x_points.append(arrow_Xs[0])
                    y_points.append(arrow_ys[0])
                    connect.append(0)

                    x_points.append(arrow_Xs[1])
                    y_points.append(arrow_ys[1])
                    connect.append(1)

                    # Back to arrow tip
                    x_points.append(x2)
                    y_points.append(y2)
                    connect.append(0)

        path = pg.arrayToQPath(np.array(x_points), np.array(y_points), np.array(connect))
        self.item = QtGui.QGraphicsPathItem(path)
        self.item.setPen(pg.mkPen({'color': self.arrow_color, 'width': 1}))
        self.viewbox.addItem(self.item)

    def rotate_vector(self, vector, theta):
        x_temp = np.copy(vector[0])
        theta = math.radians(theta)
        x = vector[0] * math.cos(theta) - vector[1] * math.sin(theta)
        y = x_temp * math.sin(theta) + vector[1] * math.cos(theta)
        return x, y

    def draw_arrow_head(self, tipX, tailX, tipY, tailY):
        """
        This is the function that needs speeding up
        :param tipX:
        :param tailX:
        :param tipY:
        :param tailY:
        :return:
        """
        arrowLength = 1
        dx = tipX - tailX
        dy = tipY - tailY

        theta = math.atan2(dy, dx)

        rad = math.radians(20)
        x = tipX - arrowLength * math.cos(theta + rad)
        y = tipY - arrowLength * math.sin(theta + rad)


        phi2 = math.radians(-20)
        x2 = tipX - arrowLength * math.cos(theta + phi2)
        y2 = tipY - arrowLength * math.sin(theta + phi2)

        arrowYs = []
        arrowYs.append(y)
        arrowYs.append(y2)

        arrowXs = []
        arrowXs.append(x)
        arrowXs.append(x2)

        return arrowXs, arrowYs

    def set_subsampling(self, value):
        self.vol.subsampling = int(value)
        self.update()

    def set_scale(self, value):
        self.vol.scale = int(value)
        self.update()

    def set_arrow_color(self, color):
        self.arrow_color = color

    def clear(self):
        pass

    def update(self):
        self.set_orientation()
        self.set_slice(self.current_index)

    def reload(self):
        pass


















