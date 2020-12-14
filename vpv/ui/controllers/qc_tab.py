from pathlib import Path

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QDialog, QMessageBox, QFileDialog

import pandas as pd
import yaml
import addict

from vpv.ui.views.ui_qctab import Ui_QC
from vpv.common import info_dialog, question_dialog, Layers
from lama.common import get_file_paths
from lama.paths import get_specimen_dirs


SUBFOLDERS_TO_IGNORE = ['resolution_images', 'pyramid_images']

class QC(QtGui.QWidget):

    load_specimen_signal = QtCore.pyqtSignal(list, str)
    clear_data_signal = QtCore.pyqtSignal()

    def __init__(self, vpv, mainwindow):
        super(QC, self).__init__(mainwindow)
        self.ui = Ui_QC()
        self.ui.setupUi(self)
        self.vpv = vpv

        self.ui.pushButtonOpenDir.clicked.connect(self.open_dir_slot)
        self.ui.pushButtonSaveQC.clicked.connect(self.save_qc)
        self.ui.pushButtonNextSpecimen.clicked.connect(self.next_specimen)
        self.ui.listWidgetQcSpecimens.currentRowChanged.connect(self.load_specimen)

        self.mainwindow = mainwindow
        self.specimen_index = 0

        self.qc_results_file = None
        self.is_active = False

        self.qc = []  # Containing SpecimenPaths objects

    def label_clicked_slot(self, label_num):

        if not self.is_active:
            return

        s: set = self.qc[self.specimen_index].qc_flagged
        if label_num in s:
            s.add(label_num)
        else:
            s.remove(label_num)
        self.update_flagged_list()

    def update_flagged_list(self):
        self.ui.listWidgetQcFlagged.clear()
        spec_qc = self.qc[self.specimen_index]
        self.ui.listWidgetQcFlagged.addItems(spec_qc.qc_flagged)

    def update_specimen_list(self):
        self.ui.listWidgetQcSpecimens.clear()
        for s in self.qc:
            self.ui.listWidgetQcSpecimens.addItem(s.outroot.parent.name)

    def next_specimen(self):
        new_index = self.specimen_index + 1
        self.load_specimen(new_index)

    def load_specimen(self, idx):
        spec_qc = self.qc[idx]
        spec_dir = spec_qc.outroot.parent
        self.load_specimen_into_viewer(spec_dir)
        self.specimen_index = idx
        self.update_flagged_list()

    def open_dir_slot(self):
        dir_ = QFileDialog.getExistingDirectory(None, "Select root directory containing lama runs")
        root = Path(dir_)
        if self.qc: # Any qc in memory
            doit = question_dialog(self.mainwindow, 'Load QC?', 'This will delete any previously made qc flags')
            if not doit:
                return

        # First check for presence of QC file
        self.qc_results_file = root / 'vpv_qc.yaml'

        if self.qc_results_file.is_file():
            info_dialog(self.mainwindow, 'QC file found', 'Continuing previous QC')
        else:
            info_dialog(self.mainwindow, 'QC file NOT found', 'Creating new QC file') # Do it on next save
        self.load_qc(root)
        self.update_specimen_list()
        self.load_specimen(0)

    def save_qc(self, file_):
        # Convert the list of SpecimenDataPath objects to a yaml
        results = {}
        with open(file_, 'r') as fh:
            for s in self.qc:
                results[s.outroot] = {'qc_flagged': s.qc_flagged }
        yaml.dump(results, fh)

    def load_qc(self, root):
        print('loading qc')
        if self.qc_results_file and self.qc_results_file.is_file():
            with open(self.qc_results_file, 'r') as fh:
                qc_info = addict.Dict(yaml.load(fh))
        else:
            qc_info = {}

        self.qc = get_specimen_dirs(root)

        # For each Lama specimen object, assign previously qc-flagged labels
        for s in self.qc:
            s.setup() # Lets get rid of setup method
            if s.outroot in qc_info:
                s.qc_flagged = list(qc_info['qc_flagged'])
            else:
                s.qc_flagged = set()

    def load_specimen_into_viewer(self, spec_dir: Path, rev=True, title=None):

        invert_yaml = next(spec_dir.glob('**/inverted_transforms/invert.yaml'))
        with open(invert_yaml, 'r') as fh:
            invert_order = yaml.load(fh)['inversion_order']

        if not rev:
            vol_dir = next(spec_dir.rglob('**/reg*/*rigid*'))
            try:
                lab_dir = next(spec_dir.rglob('**/inverted_labels/similarity'))
            except StopIteration:
                lab_dir = next(spec_dir.rglob('**/inverted_labels/affine'))
        else:
            # Labels progated by reverse registration
            last_dir = invert_order[-1]
            vol_dir = spec_dir / 'inputs/'  # Change this to rigid for the next run
            lab_dir = next(spec_dir.rglob(f'**/inverted_labels/{last_dir}'))

        vol = get_file_paths(vol_dir, ignore_folders=SUBFOLDERS_TO_IGNORE)[0]
        lab = get_file_paths(lab_dir, ignore_folders=SUBFOLDERS_TO_IGNORE)[0]

        # Remove previous data so we don't run out of memory
        # self.clear_data_signal.emit()
        vpv_ids = self.vpv.load_volumes([vol, lab], 'vol')

        # Vpv deals with images with the same name by appending parenthetical digits. We need to know the ids it will assign
        # if we are to get a handle once loaded
        # img_ids = self.vpv.img_ids()

        num_top_views = 3

        # Set the top row of views
        for i in range(num_top_views):
            vol_id = vpv_ids[0]
            # label_id = top_labels[i].stem
            label_id = vpv_ids[1]
            # if label_id == vol_id:
            #     label_id = f'{label_id}(1)'
            self.vpv.views[i].layers[Layers.vol1].set_volume(vol_id)
            self.vpv.views[i].layers[Layers.vol2].set_volume(label_id)

        if not title:
            title = spec_dir.name
        self.vpv.mainwindow.setWindowTitle(title)

        self.vpv.data_manager.show2Rows(False)

        # Set orientation
        # ex.data_manager.on_orientation('sagittal')

        # Set colormap
        self.vpv.data_manager.on_vol2_lut_changed('anatomy_labels')

        # opacity
        self.vpv.data_manager.modify_layer(Layers.vol2, 'set_opacity', 0.6)

        self.vpv.data_manager.update()



