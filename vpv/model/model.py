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
from PyQt5 import QtCore
import json
from vpv.lib.addict import Dict
from vpv.common import Stage, AnnotationOption, read_image, info_dialog
from vpv.annotations.impc_xml import load_xml
from vpv.annotations.annotations_model import centre_stage_options

from .ImageVolume import ImageVolume
from .HeatmapVolume import HeatmapVolume
from .VectorVolume import VectorVolume
from .ImageSeriesVolume import ImageSeriesVolume
from .VirtualStackVolume import VirtualStackVolume


class LoadVirtualStackWorker(QtCore.QThread):
    progress_signal = QtCore.pyqtSignal([str])

    def __init__(self, file_paths):
        QtCore.QThread.__init__(self)
        self.file_paths = file_paths
        self.memmap_result = None  # Populated at end of run()

    def sitk_load(self, p):
        read_image(p, convert_to_ras=True)

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
        self._volumes = {}
        self._data = {}

    def volume_id_list(self):
        return sorted([id_ for id_ in self._volumes])

    def data_id_list(self):
        return sorted([id_ for id_ in self._data])

    def vector_id_list(self):
        return sorted([id_ for id_ in self._vectors])

        for key in self._data.keys():
            self._data[key].destroy()

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
        Load annotations from an IMPC xml file.

        Parameters
        ----------
        ann_path: str
            path to xml annotation file

        Returns
        -------

        """
        #  def add_impc_annotation(self, x, y, z, impc_param, name, options, default_option, stage, order, is_mandatory, dims):
        centerID, pipeline, project, doe, ex_id, spec_id, proc_id, \
        simple_and_series_params, procedure_metadata = load_xml(ann_path)

        file_id = os.path.splitext(os.path.basename(ann_path))[0]
        vol = self._volumes.get(file_id)

        if vol:
            # Get the dict that contains the available options for a given center/stage
            default_opts = centre_stage_options.opts
            stage = self.get_stage_from_proc_id(simple_and_series_params, centerID)

            # Get all the simpleParameter entries form the xml file
            for xml_param, xml_data in simple_and_series_params.items():
                option = xml_data['option']
                xyz = xml_data.get('xyz')
                if xyz:
                    x, y, z = [int(i) for i in xyz]
                else:
                    x = y = z = None
                dims = vol.shape_xyz()

                # Some of the data neded to crate an annotation object is not recorded in the XML output
                # So we need to load that from the center annotation options file
                for center, default_data in default_opts['centers'].items():
                    if default_data['short_name'] == centerID:
                        params = default_data['stages'][stage]['parameters']

                        for param_id, default_param_info in params.items():
                            if param_id == xml_param:
                                name = default_param_info['name']
                                options = default_opts['available_options'][default_param_info['options']]# available options for this parameter
                                order = default_param_info['options']
                                is_mandatory = default_param_info['mandatory']

                                vol.annotations.add_impc_annotation(x, y, z, xml_param, name, options, option, stage,
                                                            order, is_mandatory, dims)

        else:
            return "Could not load annotation: {}. Not able to find loaded volume with same id".format(file_id)
        return None

    def get_stage_from_proc_id(self, parameters: dict, center_id: dict):
        """
        There is nowhere in the IMPC xml to log what stage we are using.
        We must infer that from the procedures we are using.
        If centre is Harwell return e14.5 instead of e15.5

        Returns
        -------
        str: stage identifier
        center_id: the one letter centre code.
        """
        param_id, _ = list(parameters.items())[0]
        if 'EMO' in param_id:
            if center_id.lower() == 'h':
                return 'e14.5'
            return 'e15.5'
        elif 'EMP' in param_id:
            return 'e18.5'  # Not sure this is correct. Look up. For now only using E15.5

    def load_annotation_old_json_method(self, ann_path):
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
                    if a['option'] == 'imageOnly':
                        continue  # just leave the defult in there
                    # check that diemsions stored in annotation file are same os the loaded volume
                    xyz_in_file = tuple(a.volume_dimensions_xyz)
                    # reverese as numpy works in zyx
                    vol_dims = vol.shape_xyz()
                    if vol_dims != xyz_in_file:
                        return """Error loading annotations\nAnnotations dimensions are {}.
                        Loaded volume dimensions are {}""".format(
                            ",".join([str(x) for x in xyz_in_file]),
                            ",".join([str(x) for x in vol_dims]))

                    option = AnnotationOption(a.option)
                    stage = Stage(a.stage)

                    if a.annotation_type == 'mp': # can get rif of ths?
                        vol.annotations.add_mp(a.x, a.y, a.z, a.mp_term, stage)
                    elif a.annotation_type == 'emapa':
                        vol.annotations.add_impc_annotation(a.x, a.y, a.z, a.emapa_term, option, stage)
        else:
            return "Could not load annotation: {}. Not able to find loaded volume with same id".format(file_id)
        return None

    def add_volume(self, volpath, data_type, memory_map, fdr_thresholds=False):
        """
        Load a volume into a subclass of a Volume object
        Parameters
        ----------
        volpath: str
        data_type: str
        memory_map: bool
        fdr_thresholds: fdict
            q -> t statistic mappings
                {0.01: 3.4,
                0.05:, 3.1}
        """

        if data_type != 'virtual_stack':
            volpath = str(volpath)
            n = os.path.basename(volpath)
            unique_name = self.create_unique_name(n)
        else:
            n = os.path.basename(os.path.split(volpath[0])[0])
            unique_name = self.create_unique_name(n)

        if data_type == 'heatmap':
            vol = HeatmapVolume(volpath, self, 'heatmap')
            if fdr_thresholds or fdr_thresholds is None:
                vol.fdr_thresholds = fdr_thresholds
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



