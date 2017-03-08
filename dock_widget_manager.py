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

from PyQt4 import QtGui
from lookup_tables import Lut
from ui.ui_manager import Ui_ManageViews


class ManagerDockWidget(QtGui.QDockWidget):

    def __init__(self, model, mainwindow, appdata, data_manager, annotations_manager, console):
        super(ManagerDockWidget, self).__init__(mainwindow)
        lut = Lut()
        self.appdata = appdata
        self.data_manager = data_manager
        self.annotations = annotations_manager
        self.console = console
        self.hotred = lut._hot_red_blue()[0]
        self.hotblue = lut._hot_red_blue()[1]
        self.ui = Ui_ManageViews()
        self.ui.setupUi(self)
        self.setStyleSheet("font-size: 12px")
        self.setFeatures(QtGui.QDockWidget.AllDockWidgetFeatures)
        self.model = model
        self.mainwindow = mainwindow
        self.volume_ids = None
        self.luts = Lut()

        self.current_view_id = 0
        self.current_view = None

        self.link_views = True

        self.ui.tabWidget.addTab(self.data_manager, 'Data')

        self.annotations.annotation_recent_dir_signal.connect(self.appdata.set_last_dir_browsed)
        self.ui.tabWidget.addTab(self.annotations, 'Annotations')
        self.ui.tabWidget.currentChanged.connect(self.tab_changed)
        self.ui.tabWidget.addTab(self.console, 'Console')

    def tab_changed(self, indx):
        """
        When changing to annotations tab, make sure all views are linked
        """
        self.data_manager.link_views = True
        self.annotations.tab_changed(indx)

    def switch_tab(self, idx):
        self.ui.tabWidget.setCurrentIndex(idx)

    def mouse_pressed(self, view_index, x, y, orientation, vol_id):   # delete
        # Only do annotations when annotation tab is visible
        # if self.ui.tabWidget.isTabEnabled(2):
        self.annotations.mouse_pressed_annotate(view_index, x, y, orientation, vol_id)

    def volume_changed(self, vol_name):
        """
        When volume is changed from the combobox
        """
        self.data.modify_layer(0, 'set_volume', str(vol_name))

    def volume2_changed(self, vol_name):
        """
        When volume is changed from the combobox
        """
        self.data.modify_layer(1, 'set_volume', str(vol_name))

    def update(self):

        self.mainwindow.manager_layout.addWidget(self, 0)
        self.show()

        self.data.update()
        self.annotations.update()
