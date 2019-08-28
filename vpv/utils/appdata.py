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

import appdirs
import yaml
from os.path import expanduser
import os
import collections
from vpv import common
import logging

VPV_APPDATA_VERSION = 2.2
ANNOTATION_CRICLE_RADIUS_DEFAULT = 40


class AppData(object):
    def __init__(self):
        self.using_appdata = True # Set to false if we weren't able to find a sirectory to save the appdata
        appname = 'vpv'
        appdata_dir = appdirs.user_data_dir(appname)

        if not os.path.isdir(appdata_dir):
            try:
                os.mkdir(appdata_dir)
            except WindowsError:
                #Can't find the AppData directory. So just make one in home directory
                appdata_dir = os.path.join(expanduser("~"), '.' + appname)
                if not os.path.isdir(appdata_dir):
                    os.mkdir(appdata_dir)

        self.app_data_file = os.path.join(appdata_dir, 'vpv.yaml')

        if os.path.isfile(self.app_data_file):

            self.app_data = common.load_yaml(self.app_data_file)
            if not self.app_data:
                logging('Warning: could not load app data file')
                self.app_data = {}
        else:
            self.app_data = {}

        # Appdata versioning was not always in place. If a we find some appdata without a version, reset the data
        # Also reset the data if we find a previous version

        # This breaks for JIm on v2.02. Complains about NoneType not having a get(). Catch attribute error
        try:
            if self.app_data.get('version') is None or self.app_data['version'] < VPV_APPDATA_VERSION:
                print("resetting appdata")
                self.app_data = {}
        except AttributeError:
            self.app_data = {}

        if self.app_data == {}:
            self.app_data['version'] = VPV_APPDATA_VERSION

        if 'recent_files' not in self.app_data:
            self.app_data['recent_files'] = collections.deque(maxlen=10)

    def set_flips(self, flip_options: dict):
        self.app_data['flips'] = flip_options

    def get_flips(self):
        flips = self.app_data.get('flips')

        if not flips:
            self.app_data['flips'] = {'axial':    {'x': False, 'z': False, 'y': False},
                                      'coronal':  {'x': False, 'z': False, 'y': False},
                                      'sagittal': {'x': False, 'z': False, 'y': False},
                                      'impc_view': False}

        return self.app_data['flips']

    @property
    def annotation_circle_radius(self):
        return self.app_data.get('annotation_cricle_radius', ANNOTATION_CRICLE_RADIUS_DEFAULT)

    @annotation_circle_radius.setter
    def annotation_circle_radius(self, radius):
        self.app_data['annotation_cricle_radius'] = radius

    @property
    def annotation_centre(self):
        return self.app_data.get('annotation_centre')

    @annotation_centre.setter
    def annotation_centre(self, centre):
        self.app_data['annotation_centre'] = centre

    @property
    def annotation_stage(self):
        return self.app_data.get('annotation_stage')

    @annotation_stage.setter
    def annotation_stage(self, stage):
       self.app_data['annotation_stage'] = stage

    @property
    def annotator_id(self):
        return self.app_data.get('annotator_id')

    @annotator_id.setter
    def annotator_id(self, id_):
        self.app_data['annotator_id'] = id_

    @property
    def last_screen_shot_dir(self):
        if not self.app_data.get('last_screenshot_dir'):
            self.app_data['last_screenshot_dir'] = expanduser("~")
        return self.app_data['last_screenshot_dir']

    @last_screen_shot_dir.setter
    def last_screen_shot_dir(self, dir_):
        self.app_data['last_screenshot_dir'] = dir_

    def write_app_data(self):
        with open(self.app_data_file, 'w') as fh:
            fh.write(yaml.dump(self.app_data))

    def get_last_dir_browsed(self):
        if not self.app_data.get('last_dir_browsed'):
            self.app_data['last_dir_browsed'] = expanduser("~")
        return self.app_data['last_dir_browsed']

    def set_last_dir_browsed(self, path):
        self.app_data['last_dir_browsed'] = path

    def add_used_volume(self, volpath):
        if volpath not in self.app_data['recent_files']:
            self.app_data['recent_files'].append(volpath)

    def get_recent_files(self):
        return self.app_data['recent_files']

    def set_include_filter_patterns(self, patterns):
        self.app_data['include_patterns'] = patterns

    def get_include_filter_patterns(self):
        if not self.app_data.get('include_patterns'):
            return []
        else:
            return self.app_data.get('include_patterns')

    def set_exclude_filter_patterns(self, patterns):
        self.app_data['exclude_patterns'] = patterns

    def get_exclude_filter_patterns(self):
        if not self.app_data.get('exclude_patterns'):
            return []
        else:
            return self.app_data.get('exclude_patterns')

    def clear_recent(self):
        self.app_data['recent_files'].clear()
