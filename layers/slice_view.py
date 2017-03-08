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
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
from ui.ui_slice_widget import Ui_SliceWidget
import os
from collections import OrderedDict

from common import Orientation, Layer
from .heatmaplayer import HeatmapLayer
from .vectorlayer import VectorLayer
from .volumelayer import VolumeLayer

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
        x = int(self.layers[Layer.vol1].image_item.mapFromScene(pos).x())
        y = int(self.layers[Layer.vol1].image_item.mapFromScene(pos).y())
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
            layer = HeatmapLayer(self, layer_enum, self.model, viewmanager)
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

























