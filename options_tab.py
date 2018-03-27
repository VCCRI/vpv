import numpy as np
from PyQt5 import QtGui, QtCore
from ui.ui_options_tab import Ui_options
from common import Orientation
from appdata import AppData
from common import info_dialog


"""
A widget that allows the setting of some global options. The widget is added as a tab on the data manager
tab widget
"""


class OptionsTab(QtGui.QWidget):
    flip_signal = QtCore.pyqtSignal(Orientation, str, bool)
    impc_view_signal = QtCore.pyqtSignal(bool)
    save_options_signal = QtCore.pyqtSignal()

    def __init__(self, mainwindow, appdata: AppData):
        super(OptionsTab, self).__init__(mainwindow)
        self.ui = Ui_options()
        self.ui.setupUi(self)

        self.ui.checkBoxAxialFlipx.clicked.connect(self.on_axial_flipx)
        self.ui.checkBoxAxialFlipZ.clicked.connect(self.on_axial_flipz)

        self.ui.checkBoxCoronalFlipX.clicked.connect(self.on_coronal_flipx)
        self.ui.checkBoxCoronalFlipZ.clicked.connect(self.on_coronal_flipz)

        self.ui.checkBoxSagittalFlipX.clicked.connect(self.on_sagittal_flipx)
        self.ui.checkBoxSagittalFlipZ.clicked.connect(self.on_sagittal_flipz)

        self.ui.checkBoxImpcView.clicked.connect(self.on_impc_view)

        self.appdata = appdata

    def set_orientations(self):
        """
        Load the orientation-specific flip state stored in the appdata
        """
        if not self.appdata:
            return

        self.flips = self.appdata.get_flips()

        axial= self.flips['axial']
        coronal = self.flips['coronal']
        sagittal = self.flips['sagittal']

        self.ui.checkBoxAxialFlipx.setChecked(axial['x'])

        self.ui.checkBoxAxialFlipY.setChecked(axial['y'])

        self.ui.checkBoxAxialFlipZ.setChecked(axial['z'])

        self.ui.checkBoxCoronalFlipX.setChecked(coronal['x'])

        self.ui.checkBoxCoronalFlipY.setChecked(coronal['y'])

        self.ui.checkBoxCoronalFlipZ.setChecked(coronal['z'])

        self.ui.checkBoxSagittalFlipX.setChecked(sagittal['x'])

        self.ui.checkBoxSagittalFlipY.setChecked(sagittal['y'])

        self.ui.checkBoxSagittalFlipZ.setChecked(sagittal['z'])

        self.ui.checkBoxImpcView.setChecked(self.flips['impc_view'])
        self.on_impc_view(self.flips['impc_view'])

    def on_impc_view(self, checked: bool):
        self.impc_view_signal.emit(checked)
        self.flips['impc_view'] = checked

    def on_axial_flipx(self, checked: bool):
        self.flip_signal.emit(Orientation.axial, 'x', checked)
        self.flips['axial']['x'] = checked

    def on_axial_flipy(self, checked: bool):
        self.flip_signal.emit(Orientation.axial, 'y', checked)
        self.flips['axial']['y'] = checked

    def on_axial_flipz(self, checked: bool):
        self.flip_signal.emit(Orientation.axial, 'z', checked)
        self.flips['axial']['z'] = checked

    def on_coronal_flipx(self, checked: bool):
        self.flip_signal.emit(Orientation.coronal, 'x', checked)
        self.flips['coronal']['x'] = checked

    def on_coronal_flipy(self, checked: bool):
        self.flip_signal.emit(Orientation.coronal, 'y', checked)
        self.flips['coronal']['y'] = checked

    def on_coronal_flipz(self, checked: bool):
        self.flip_signal.emit(Orientation.coronal, 'z', checked)
        self.flips['coronal']['z'] = checked

    def on_sagittal_flipx(self, checked: bool):
        self.flip_signal.emit(Orientation.sagittal, 'x', checked)
        self.flips['sagittal']['x'] = checked

    def on_sagittal_flipy(self, checked: bool):
        self.flip_signal.emit(Orientation.sagittal, 'y', checked)
        self.flips['sagittal']['y'] = checked

    def on_sagittal_flipz(self, checked: bool):
        self.flip_signal.emit(Orientation.sagittal, 'z', checked)
        self.flips['sagittal']['z'] = checked
