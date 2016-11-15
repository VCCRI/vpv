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


import pyqtgraph as pg
from PyQt4 import QtCore

## Not working yet
class SliceOverlay(pg.GraphicsObject, pg.GraphicsWidgetAnchor):
    """
    Displays a rectangular bar to indicate the relative scale of objects on the view.
    """
    def __init__(self, brush=None, pen=None):
        pg.GraphicsObject.__init__(self)
        pg.GraphicsWidgetAnchor.__init__(self)
        self.setFlag(self.ItemHasNoContents)
        self.setAcceptedMouseButtons(QtCore.Qt.NoButton)

        self.id = 'Temp'
        self.text = pg.TextItem(self.id, color=(255, 255, 255), anchor=(0.5, 1))
        self.text.setParentItem(self)

    def parentChanged(self):
        view = self.parentItem()
        if view is None:
            return
        view.sigRangeChanged.connect(self.updateBar)
        self.updateBar()

    def add_id(self, id):
        print 'add'
        self.text.setText("Title of the volume", color=(255, 255, 255))
        self.text.setPos(400/2, 0)

    def id_visible(self, visible):
        if visible:
            self.text.hide()
        else:
            self.text.show()



        # self.text.setText(fn.siFormat(bar_size_mm, suffix=suffix), color=(255, 255, 255))
        # self.text.setPos(-view_box_width/2, 0)



