#!/usr/bin/env python3

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


# I distribute VPV as an installer with a bundled version of WinPython
# In at least one case, the paths are not correctly set. So the following hack attempts to set correct paths


WINPYTHON_DIR = 'WinPython-64bit-3.4.4.2Zero'
PYTHON_DIR = 'python-3.4.4.amd64'

import os
import sys
from os.path import join
p = sys.path

import PyQt4
if os.name == 'nt':
    # check where vpv has been installed
    vpv_installation_dir = os.path.dirname(os.path.realpath(__file__))
    winpython_path = os.path.join(vpv_installation_dir, WINPYTHON_DIR, PYTHON_DIR)
    if os.path.isdir(winpython_path):
        dll_path = os.path.join(winpython_path, 'DLLs')
        lib_path = os.path.join(winpython_path, 'Lib')
        site_packages_path = os.path.join(lib_path, 'site-packages')
        sys.path.insert(0, dll_path)
        sys.path.insert(0, lib_path)
        sys.path.insert(0, site_packages_path)
    else:
        print('cannot find winpython folder: {}'.format(winpython_path))

import main_window
import numpy as np
from dock_widget_manager import ManagerDockWidget
import importer
from PyQt4 import QtGui, QtCore
from model.model import DataModel
from appdata import AppData
from stats import StatsWidget
import common
from common import Orientation, Layer
from layers.slice_widget import SliceWidget
from data_manager import ManageData
from annotations.annotations_widget import Annotations

try:
    from console import Console
    console_imported = True
except ImportError:
    print('cannot import qtconsole, so diabling console widget tab')
    console_imported = False
except Exception:  # I thnk it might not be an ImportError? look into it
    print('cannot import qtconsole, so diabling console widget tab')
    console_imported = False



from gradient_editor import GradientEditor
import zipfile
from lib import addict
import tempfile
import csv


class Vpv(QtCore.QObject):
    data_processing_finished_signal = QtCore.pyqtSignal()
    crosshair_visible_signal = QtCore.pyqtSignal()
    crosshair_invisible_signal = QtCore.pyqtSignal()

    def __init__(self):
        super(Vpv, self).__init__()
        self.voxel_size = 28.0
        self.view_scale_basrs = False
        self.view_id_counter = 0
        self.appdata = AppData()
        self.mainwindow = main_window.Main(self, self.appdata)
        # self.mainwindow.showFullScreen()
        self.model = DataModel()
        self.model.updating_started_signal.connect(self.updating_started)
        self.model.updating_finished_signal.connect(self.updating_finished)
        self.model.updating_msg_signal.connect(self.display_update_msg)
        self.views = {}
        # layers and views now created in manage_views
        self.data_manager = ManageData(self, self.model, self.mainwindow)
        self.data_manager.gradient_editor_signal.connect(self.gradient_editor)

        self.annotations_manager = Annotations(self, self.mainwindow)
        self.annotations_manager.annotation_highlight_signal.connect(self.highlight_annotation)
        self.annotations_manager.annotation_radius_signal.connect(self.annotation_radius_changed)

        # Sometimes QT console is a pain to install. If not availale do not make console tab
        if console_imported:
            self.console = Console(self.mainwindow, self)
        else:
            self.console = None


        self.dock_widget = ManagerDockWidget(self.model, self.mainwindow, self.appdata, self.data_manager,
                                             self.annotations_manager, self.console)
        self.dock_widget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)

        # Create the initial 3 orthogonal views
        inital_views = [
            [Orientation.sagittal, 'red', 0, 1],
            [Orientation.coronal, 'blue', 0, 2],
            [Orientation.axial, 'green', 0, 3],
            [Orientation.sagittal, 'orange', 1, 1, True],
            [Orientation.coronal, 'grey', 1, 2, True],
            [Orientation.axial, 'cyan', 1, 3, True]
            # ['sagittal', 'yellow', 1, 1, True],
            # ['axial', 'pink', 1, 3, True],
            # ['coronal', 'cyan', 1, 2, True]
        ]

        for v in inital_views:
            self.setup_views(*v)
        self.current_view = self.views[0]

        self.crosshair_visible = False

        # self.view_manager.data_processing_signal.connect(self.mainwindow.data_processing_slot)
        # self.view_manager.data_processing_finished_signal.connect(self.data_processing_finished_slot)

        self.data_manager.roi_signal.connect(self.set_to_centre_of_roi)

        self.add_layer(Layer.vol1)
        self.add_layer(Layer.vol2)
        self.add_layer(Layer.heatmap)
        self.add_layer(Layer.vectors)

        self.any_data_loaded = False
        self.crosshair_permanent = False
        self.gradient_editor_widget = None

    def current_annotation_volume(self):
        """
        Get the volume currently visible in the annotation view
        
        Returns 
        -------
        model.ImageVolume instance
        """

        return self.current_view.layers[Layer.vol1].vol

    def on_console_enter_pressesd(self):
        print('command update')
        self.update_slice_views()

    def take_screen_shot(self):
        sshot = QtGui.QPixmap.grabWidget(self.mainwindow.ui.centralwidget, )
        QtGui.QApplication.clipboard().setPixmap(sshot)
        common.info_dialog(self.mainwindow, 'Message', "Screenshot copied to clipboard")

    def volume_changed(self, vol_name):
        self.data_manager.volume_changed(vol_name)

    def set_current_view(self, slice_id):
        self.current_view = self.views[slice_id]

    def highlight_annotation(self, x, y, z, color, radius):
        for view in self.views.values():
            if view.orientation == Orientation.axial:
                y = self.current_view.layers[Layer.vol1].vol.dimension_length(Orientation.coronal) - y
                view.set_slice(z)
                view.set_annotation(x, y, color, radius)
            if view.orientation == Orientation.coronal:
                view.set_slice(y)
                view.set_annotation(x, z, color, radius)
            if view.orientation == Orientation.sagittal:
                view.set_slice(x)
                view.set_annotation(y, z, color, radius)

    def current_orientation(self):
        return self.current_view.orientation

    def annotation_radius_changed(self, radius):
        for view in self.views.values():
            view.annotation_radius_changed(radius)

    def tab_changed(self, indx: int):
        """
        When changing to annotations tab, make sure all views are linked
        """
        self.data_manager.link_views = True
        self.annotations_manager.tab_changed(indx)

    def add_layer(self, z_position: int):  # move
        for view in self.views.values():
            view.register_layer(z_position, self)

    def updating_started(self):
        self.updating_dlg = QtGui.QMessageBox()

    def updating_finished(self):
        self.updating_dlg.close()

    def display_update_msg(self, msg: str):
        self.updating_dlg.setText(msg)

    def set_view_controls_visibility(self, visible):
        for view in self.views.values():
            view.show_index_slider(visible)

    def show_color_scale_bars(self, visible):

        self.data_manager.show_color_scale_bars(visible)

    def show_scale_bars(self, visible):
        for view in self.views.values():
            view.update()
            view.show_scale_bar(visible)

    def update_slice_views(self):

        for view in self.views.values():
            view.update_view()

    def setup_views(self, orientation, color, row, column, hidden=False):
        """
        Create all the orthogonal views and setup the signals and slots
        """
        view = self.add_view(self.view_id_counter, orientation, color, row, column)
        view.mouse_shift.connect(self.mouse_shift)
        view.mouse_pressed_signal.connect(self.dock_widget.mouse_pressed)
        view.crosshair_visible_signal.connect(self.crosshair_visible_slot)
        view.scale_changed_signal.connect(self.zoom_changed)
        view.slice_index_changed_signal.connect(self.index_changed)
        view.move_to_next_vol_signal.connect(self.move_to_next_vol)
        self.data_manager.scale_bar_color_signal.connect(view.set_scalebar_color)
        self.crosshair_visible_signal.connect(view.show_crosshair)
        self.crosshair_invisible_signal.connect(view.hide_crosshair)
        self.view_id_counter += 1
        self.mainwindow.add_slice_view(view, row, column)
        view.setHidden(hidden)

    def gradient_editor(self):
        # Activeated 6 times on one click so bogdge for now
        self.ge = GradientEditor(self)
        self.ge.sigFinished.connect(self.set_heatmap_luts)
        self.ge.show()
        print('gradient in vpv')

    def set_heatmap_luts(self, luts):
        for view in self.views.values():
            if view.layers[Layer.heatmap].vol:
                view.layers[Layer.heatmap].vol.pos_lut = luts[0]
                #view.layers[Layer.heatmap].vol.neg_lut = luts[1]
                view.layers[Layer.heatmap].update()


    def move_to_next_vol(self, view_id, reverse=False):
        if self.data_manager.link_views:
            for view in self.views.values():
                view.move_to_next_volume(reverse)
        else:
            self.views[view_id].move_to_next_volume(reverse)
        self.data_manager.switch_selected_view(view_id)

    def recalc_connected_components(self):
        self.current_view.layers[Layer.heatmap].vol.find_largest_connected_components()
        self.data_manager.update_connected_components(self.current_view.layers[Layer.heatmap].vol.name)

    def add_view(self, id_, orientation, color, row, column):  # move to vpv
        """
        Setup the controls for each layer)
        :param id, int
        :param orientation: str,
        :param color: str, jsut a color word at the moment eg: red
        :return SliceWidget
        """
        view = SliceWidget(orientation, self.model, color)
        view.volume_pixel_signal.connect(self.mainwindow.set_volume_pix_intensity)
        view.data_pixel_signal.connect(self.mainwindow.set_data_pix_intensity)
        view.volume_position_signal.connect(self.mainwindow.set_mouse_position)
        view.manage_views_signal.connect(self.update_manager)
        self.views[id_] = view
        return view

    def toggle_dock_widget_visibility(self):
        if self.dock_widget.isVisible():
            self.dock_widget.hide()
        else:
            self.update_manager()

    def update_manager(self, slice_id=0):  # called from data_manager:update_manager
        """
        update the slice manager with data from a slice view
        :param slice_id: Id of the SliceWidget that this current widget was activated from
        """
        self.current_view = self.views[slice_id]
        self.data_manager.switch_selected_view(slice_id)
        self.mainwindow.show_manager(self.dock_widget)
        self.mainwindow.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dock_widget)
        self.dock_widget.show()

    def remove_views(self, row, column):
        self.mainwindow.remove_view(row, column)

    def set_to_centre_of_roi(self, zindices, yindices, xindices):

        z = [int(x) for x in zindices]
        y = [int(x) for x in yindices]
        x = [int(x) for x in xindices]

        xslice = int(np.mean(x))
        yslice = int(np.mean(y))
        zslice = int(np.mean(z))

        # Set the slice views to the centre of the ROI
        for view in self.views.values():
            if view.orientation == Orientation.axial:
                view._set_slice(zslice)
            if view.orientation == Orientation.coronal:
                view._set_slice(yslice)
            if view.orientation == Orientation.sagittal:
                view._set_slice(xslice)

        # Send a 2D ROI to each view
        for view in self.views.values():
            if view.orientation == Orientation.axial:
                dim_len = view.layers[Layer.vol1].vol.dimension_length(Orientation.coronal)
                w = x[1] - x[0]
                h = y[0] - y[1]
                y1 = dim_len - y[0]
                view.set_roi(x[0], y1, w, h)
            if view.orientation == Orientation.coronal:
                w = x[1] - x[0]
                h = z[0] - z[1]
                view.set_roi(x[0], z[1], w, h)
            if view.orientation == Orientation.sagittal:
                w = y[1] - y[0]
                h = z[0] - z[1]
                view.set_roi(y[0], z[1], w, h)

    def index_changed(self, orientation, id_, idx):
        orientation = str(orientation)
        if not self.data_manager.link_views:
            return
        for view in self.views.values():
            if view.id == id_:  # The view that emiited the signal
                continue
            if orientation == view.orientation: # For now, only zoom views with the same orientation
                view.set_slice(idx)

    def zoom_changed(self, orientation, id_, ranges):
        """
        Called when a slice view zooms in.
        Parameters
        ----------
        orientation: string
            orientation of the calling slice view
        id: int
            id of the calling slice view
        scale: list
            [[xstart, xend], [ystart, yend]]
        """
        if not self.data_manager.link_views:
            return
        for view in self.views.values():
            if view.id == id_:  # The view that emiited the signal
                continue
            if orientation == view.orientation: # For now, only zoom views with the same orientation
                view.set_zoom(ranges[0], ranges[1])

    def crosshair_visible_slot(self, visible):
        if visible:
            self.crosshair_visible_signal.emit()
        elif not self.crosshair_permanent:
            self.crosshair_invisible_signal.emit()

    def set_crosshair_permanent(self, is_visible_always):
        self.crosshair_permanent = is_visible_always
        self.crosshair_invisible_signal.emit()

    def data_labels_visible(self, visible):
        for view in self.views.values():
            view.set_data_label_visibility(visible)

    def data_processing_finished_slot(self):
        self.data_processing_finished_signal.emit()

    def mouse_shift(self, own_index, x, y, orientation):
        """
        Gets mouse moved signal

        Parameters
        ----------
        own_index: int
            the current slice of the calling view
        x: int
            the x position of the mouse
        y: int
            the y position of the mouse
        orientation: str
            the orientation of the calling view
        """
        for view in self.views.values():
            # TODO: make this better
            if orientation == Orientation.sagittal:
                if view.orientation == Orientation.axial:
                    try:
                        x1 = view.layers[Layer.vol1].vol.dimension_length(Orientation.coronal) - x
                    except:
                        pass
                    view.set_slice(y, crosshair_xy=(own_index, x1))
                elif view.orientation == Orientation.coronal:
                    view.set_slice(x, crosshair_xy=(own_index, y))
                elif view.orientation == Orientation.sagittal:
                    view.set_slice(own_index, crosshair_xy=(x, y))

            elif orientation == Orientation.axial:
                if view.orientation == Orientation.sagittal:
                    y1 = view.layers[Layer.vol1].vol.dimension_length(Orientation.coronal) - y
                    view.set_slice(x, crosshair_xy=(y1, own_index))
                elif view.orientation == Orientation.coronal:
                    view.set_slice(y, True, crosshair_xy=(x, own_index))
                elif view.orientation == Orientation.axial:
                    view.set_slice(own_index, crosshair_xy=(x, y))

            elif orientation ==Orientation.coronal:
                if view.orientation ==  Orientation.axial:
                    oi = view.layers[Layer.vol1].vol.dimension_length(Orientation.coronal) - own_index
                    view.set_slice(y, crosshair_xy=(x, oi))
                elif view.orientation == Orientation.sagittal:
                    view.set_slice(x, crosshair_xy=(own_index, y))
                elif view.orientation == Orientation.coronal:
                    view.set_slice(own_index, crosshair_xy=(x, y))

    def stats(self):
        """
        Show the stats dialog
        """
        sw = StatsWidget(self.mainwindow, self.model)
        #sw.set_available_data(self.model.data_id_list())
        sw.show()

    def control_visiblity(self, visible):
        for slice_ in self.slice_widgets.values():
            slice_.show_controls(visible)

    def scale_bar_visible(self, visible):
        pass
        for slice_ in self.slice_widgets.values():
            slice_.scale_bar_visible(visible)

    def load_data_slot(self, dragged_files=None):
        """
        Gets signal from main window
        :return:
        """
        last_dir = self.appdata.get_last_dir_browsed()
        # Convert QStrings to unicode in case they contain special characters
        files = [x for x in dragged_files]
        importer.Import(self.mainwindow, self.importer_callback, self.virtual_stack_callback, last_dir, self.appdata,
                        files)

    def clear_views(self):
        self.model.clear_data()
        for view in self.views.values():
            view.clear_layers()
        self.data.clear()
        self.annotations_manager.clear()
        self.any_data_loaded = False
        self.update()

    def virtual_stack_callback(self, file_paths, last_dir):
        if len(file_paths) > 0:
            self.appdata.set_last_dir_browsed(last_dir)
            try:
                self.model.add_volume(file_paths, 'virtual_stack', memory_map=True)
            except ValueError:
                QtGui.QMessageBox.warning(self.mainwindow, 'Loading error',
                    "Virtual stack could not be loaded\nAre all images the same dimension?", QtGui.QMessageBox.Ok)
            else:
                self.appdata.set_last_dir_browsed(last_dir)
                if self.dock_widget.isVisible():
                    self.dock_widget.update()
                if not self.any_data_loaded:
                    #  Load up one of the volumes just loaded into the bottom layer
                    self.add_initial_volume()
                    self.any_data_loaded = True

    def add_initial_volume(self):  # move to vpv.py
        """
        Called when loading in volumes for the first time, to get a volume displayed without havong to manually set it
        """
        try:
            init_vol = self.model.volume_id_list()[0]
            for view in self.views.values():
                view.layers[Layer.vol1].set_volume(init_vol, initial=True)
                view.layers[Layer.vol1].update()  # This should make sure 16bit images are scaled correctly at loading?

        except IndexError:  # No Volume objects have been loaded
            print('No volumes oaded')
        try:  # See if we have any Data objects loaded
            init_vol = self.model.data_id_list()[0]
            for view in self.views.values():
                view.layers[Layer.heatmap].set_volume(init_vol, initial=True)
        except IndexError:  # No Volume objects have been loaded
            pass

    def importer_callback(self, volumes, datafiles, annotations, dual_datafiles, vector_files, image_series,
                          impc_analysis, last_dir, memory_map=False):
        """
        Recieves a list of files to open from the Importer widget

        Parameters
        ----------
        dual_datafiles: str
            path to config file for loading paired tval/pval files
        :return:
        """
        if len(impc_analysis) > 0:
            self.load_impc_analysis(impc_analysis[0])
        if len(volumes) > 0:
            self.load_volumes(volumes, 'vol', memory_map)
        if len(datafiles) > 0:
            self.load_volumes(datafiles, 'data', memory_map)
        if len(dual_datafiles) > 0:
            self.load_volumes(dual_datafiles, 'dual', memory_map)
        if len(vector_files) > 0:
            self.load_volumes(vector_files, 'vector', memory_map)
        if len(image_series) > 0:
            self.model.load_image_series(image_series, memory_map)
            if not self.any_data_loaded:
                self.add_initial_volume()
        # Now load the annotations. Only load if there is a corresponding volume with the same id
        if len(annotations) > 0:
            for ann in annotations:
                error = self.model.load_annotation(ann)
                if error:
                    common.error_dialog(self.mainwindow, 'Annotations not loaded', error)
            # Switch to annotations tab
            #self.dock_widget.switch_tab(1)
            #self.dock_widget.tab_changed(1)

        self.appdata.set_last_dir_browsed(last_dir)

        if self.dock_widget.isVisible():
            self.data_manager.update()
            self.annotations_manager.update()

    def load_volumes(self, file_list, data_type, memory_map=False, lower_thresholds=False):
        """
        Load some volumes from a list of paths.
        Parameters
        ----------
        file_list: list
            list of paths to volumes
        data_type: str
            vol data etc
        memory_map: bool
            wheter to memory map after reading
        lower_thresholds: list
            optional lower thresholds to apply to the list of volumes. Ussually for data volumes

        """
        non_loaded = []
        for i, vol_path in enumerate(file_list):
            try:
                if lower_thresholds:
                    self.model.add_volume(vol_path, data_type, memory_map, lower_thresholds[i])
                else:
                    self.model.add_volume(vol_path, data_type, memory_map)
                self.appdata.add_used_volume(vol_path)
                if not self.any_data_loaded:
                    #  Load up one of the volumes just loaded into the bottom layer
                    self.add_initial_volume()
                    self.any_data_loaded = True
            except (IOError, RuntimeError) as e:  # RT error Raised by SimpleITK
                print(e)
                non_loaded.append(vol_path)
        if len(non_loaded) > 0:
            dialog = QtGui.QMessageBox.warning(self.mainwindow, 'Volumes not loaded', '\n'.join(non_loaded),
                                               QtGui.QMessageBox.Cancel)

    def load_impc_analysis(self, impc_zip_file):
        """
        Load a zip file containing the results of the IMPC automated analysis (TCP pipeline)
        Parameters
        ----------
        impc_zip_file: str
            path tho analysis results zip
        """
        zf = zipfile.ZipFile(impc_zip_file)
        names = zf.namelist()

        file_names = addict.Dict(
            {'intensity_tstats_file': None,
             'jacobians_tstats_file': None,
             'qvals_intensity_file': None,
             'qvals_jacobians_file': None,
             'popavg_file': None}
        )

        files_remaining = []
        for name in names:
            name_lc = name.lower()
            if 'intensities-tstats' in name_lc:
                file_names.intensity_tstats_file = name
            elif 'jacobians-tstats' in name_lc:
                file_names.jacobians_tstats_file = name
            elif 'qvals-intensities' in name_lc:
                file_names.qvals_intensity_file = name
            elif 'qvals-jacobians' in name_lc:
                file_names.qvals_jacobians_file = name
            elif 'popavg' in name_lc:
                file_names.popavg_file = name
            else:
               files_remaining.append(name)

        if all(value for value in file_names.values()):
            td = tempfile.TemporaryDirectory()
            zf.extractall(td.name)
            popavg = join(td.name, file_names.popavg_file)
            self.load_volumes([popavg], 'vol')
            inten_tstat = join(td.name, file_names.intensity_tstats_file)
            jac_tstat = join(td.name, file_names.jacobians_tstats_file)

            # get the trhesholds from the csv files
            qval_int_csv = join(td.name, file_names.qvals_intensity_file)
            intensity_t_thresh = self.extract_threshold_value_from_csv(qval_int_csv, 0.05)
            qval_jac_csv = join(td.name, file_names.qvals_jacobians_file)
            jacobian_t_thresh = self.extract_threshold_value_from_csv(qval_jac_csv, 0.05)
            print('jacobian threshold at p=0.005 is {}'.format(jacobian_t_thresh))
            print('intensity threshold at p=0.005 is {}'.format(intensity_t_thresh))

            # Load the population average and stats
            self.load_volumes([inten_tstat, jac_tstat], 'data', memory_map=False,
                              lower_thresholds= [intensity_t_thresh, jacobian_t_thresh])

            # Load any other volumes in the zip. Probably will be mutants
            mutants = [join(td.name, x) for x in files_remaining if x.endswith('nrrd')]
            self.load_volumes(mutants, 'vol', memory_map=False)

        else:
            # Make this a dialog?
            failed = []
            for f in file_names:
                if not f:
                    failed.append(f)
            print('IMPC analysis data failed to load. The following files could not be found in the zip')
            print(failed)

    @staticmethod
    def extract_threshold_value_from_csv(stats_info_csv, p_value):
        """
        Given a csv path containing the stats summary from the TCP pipeline and a p-value cutoff,
        return the corresponding t-stat threshold

        Parameters
        ----------
        stats_info_csv: str
            path to csv
        p_value: float
            the p-value threshold at which the corresponding t-score should be set to invisible
        Returns
        -------
            t_score_threshold: float
            0 if t-threshold cannot be extracted from csv file
        """
        with open(stats_info_csv, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            reader.__next__()  # remove header
            t = 0
            for line in reader:
                try:
                    p = float(line[0])
                except ValueError:
                    print("There is a problem with the stats info file. Cannot read the pvalue '{}'from file {}".format(
                        line[0], stats_info_csv
                    ))
                    return 'max'
                if p == p_value:
                    try:
                        t = float(line[3])
                    except ValueError: # NAs have been noticed here
                        print("There is a problem with the stats info file. Cannot read the pvalue '{}'from file {}".format(
                            line[3], stats_info_csv
                            ))
                        return 'max'
        return t


    def activate_view_manager(self, view_widget_id):
        """
        :param sliceid: int ,
        :return:
        """
        self.dock_widget.show(view_widget_id)

    def close(self):
        print('Bye')
        self.appdata.write_app_data()

    def on_view_new_screen(self):

        # Work out how to maximize on anotehr screen
        # dtw = QtGui.QDesktopWidget()
        # current_screen = dtw.screenNumber(self.mainwindow)
        # print 'scree', dtw.screenGeometry(3)

        pass
        # self.mainwindow2 = main_window.Main(self, self.app_data)
        # self.mainwindow2.setWindowTitle('Harwell vol viewer (2)')
        #
        # self.slice_sag2 = SliceWidget('sagittal', self.model, 'yellow')
        # self.slice_axi2 = SliceWidget('axial', self.model, 'magenta')
        # self.slice_cor2 = SliceWidget('coronal', self.model, 'orange')
        #
        # self.slice_cor2.manage_views_signal.connect(self.activate_view_manager)
        # self.slice_axi2.manage_views_signal.connect(self.activate_view_manager)
        # self.slice_sag2.manage_views_signal.connect(self.activate_view_manager)
        #
        # self.slice_widgets2 = [self.slice_sag2, self.slice_cor2, self.slice_axi2]
        #
        # self.mainwindow2.add_slice_views(self.slice_widgets2)
        # self.model.register_slice_widgets(self.slice_widgets2)


def update_check():
    pass

if __name__ == '__main__':



    app = QtGui.QApplication(sys.argv)
    ex = Vpv()
    if len(sys.argv) > 1:
        test_files = []
        test_files = [sys.argv[1]]
        ex.load_volumes(test_files, 'vol')
    if len(sys.argv) > 2:
        test_files = []
        test_files = [sys.argv[2]]
        ex.load_volumes(test_files, 'data')
    sys.exit(app.exec_())
