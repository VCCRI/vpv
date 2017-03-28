
import os
import copy
from PyQt4 import QtGui, QtCore
from ui.ui_annotations import Ui_Annotations
import json
import csv
import common
from common import Orientation, Stage, Layer
from lib.addict import Dict


E145_PATO_TERMS_FILE = 'ontologies/e14.5/pato_terms.csv'
E145_EMAP_TERMS_FILE = 'ontologies/e14.5/emap_terms.csv'

E155_OPTIONS_FILE = 'ontologies/e15.5/options.csv'
# E155_EMAP_TERMS_FILE = 'ontologies/e15.5/emap_terms.csv'
E155_EMAP_TERMS_FILE = 'ontologies/e15.5/VPV_e15_5_terms.yaml'
E185_PATO_TERMS_FILE = 'ontologies/e18.5/pato_terms.csv'
E185_EMAP_TERMS_FILE = 'ontologies/e18.5/emap_terms.csv'

E125_PATO_TERMS_FILE = 'ontologies/e12.5/pato_terms.csv'
E125_EMAP_TERMS_FILE = 'ontologies/e12.5/emap_terms.csv'



class VolumeAnnotationsTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super(VolumeAnnotationsTableModel, self).__init__(parent)
        self.ann_data = None  # model.volume.VolumeAnnotations
        self.header_data = ['x:y:z', 'EMAPA', 'option', 'stage']

    def set_data(self, annotations_model):
        self.ann_data = annotations_model

    def rowCount(self, parent):
        if self.ann_data:
            return len(self.ann_data)
        else:
            return 0

    def columnCount(self, parent):
        if self.ann_data:
            return self.ann_data.col_count
        else:
            return 0

    def data(self, index, role):
        if self.ann_data:
            if not index.isValid():
                return None
            elif role != QtCore.Qt.DisplayRole:
                return None
            return self.ann_data[index.row()][index.column()]

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header_data[col]
        return None


class Annotations(QtGui.QWidget):
    annotation_highlight_signal = QtCore.pyqtSignal(int, int, int, list, int)
    annotation_radius_signal = QtCore.pyqtSignal(int)
    annotation_recent_dir_signal = QtCore.pyqtSignal(str)

    def __init__(self, controller,  manager):
        super(Annotations, self).__init__(manager)
        self.controller = controller
        self.ui = Ui_Annotations()
        self.ui.setupUi(self)
        self.appdata = self.controller.appdata

        self.terms = Dict()
        self.terms[Stage.e12_5]['pato'] = self.parse_options(E125_PATO_TERMS_FILE)
        self.terms[Stage.e12_5]['emap'] = self.parse_emap(E125_EMAP_TERMS_FILE)

        self.terms[Stage.e14_5]['option'] = self.parse_options(E145_PATO_TERMS_FILE)
        self.terms[Stage.e14_5]['emap'] = self.parse_emap(E145_EMAP_TERMS_FILE)

        self.terms[Stage.e15_5]['option'] = self.parse_options(E155_OPTIONS_FILE)
        # self.terms[Stage.e15_5]['emap'] = self.parse_emap(E155_EMAP_TERMS_FILE)
        self.terms[Stage.e15_5]['emap'] = self.parse_emap_yaml(E155_EMAP_TERMS_FILE)

        self.terms[Stage.e18_5]['pato'] = self.parse_options(E185_PATO_TERMS_FILE)
        self.terms[Stage.e18_5]['emap'] = self.parse_emap(E185_EMAP_TERMS_FILE)

        # Set E145 terms as the default
        self.ui.radioButtonE145.setChecked(True)
        self.activate_stage()

        self.annotations_table = VolumeAnnotationsTableModel(self)
        self.ui.tableViewAvailableAnnotations.setModel(self.annotations_table)
        self.ui.tableViewAvailableAnnotations.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.ui.tableViewAvailableAnnotations.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        self.ui.comboBoxAnnotationsVolumes.activated['QString'].connect(self.volume_changed)
        self.ui.pushButtonAddAnnotation.clicked.connect(self.add_annotation)
        self.ui.pushButtonRemoveAnnotation.clicked.connect(self.remove_annotation)
        self.ui.tableViewAvailableAnnotations.clicked.connect(self.annotation_row_selected)
        self.ui.treeWidgetAvailableTerms.clicked.connect(self.resize_table)


        self.ui.radioButtonE125.toggled.connect(self.activate_stage)
        self.ui.radioButtonE145.toggled.connect(self.activate_stage)
        self.ui.radioButtonE185.toggled.connect(self.activate_stage)

        self.ui.pushButtonSaveAnnotations.clicked.connect(self.save_annotations)
        self.ui.spinBoxAnnotationCircleSize.valueChanged.connect(self.annotation_radius_changed)
        self.annotation_radius = 10
        self.annotation_type = 'emap'
        self.annotating = False
        self.populate_available_terms()

    def clear(self):
        self.ui.comboBoxAnnotationsVolumes.clear()

    def populate_available_terms(self):
        terms = self.terms[Stage.e15_5]['emap']

        header = QtGui.QTreeWidgetItem(['category', 'term', 'option'])
        self.ui.treeWidgetAvailableTerms.setHeaderItem(header)
        for category in terms:
            parent = QtGui.QTreeWidgetItem(self.ui.treeWidgetAvailableTerms)
            parent.setText(0, category)
            parent.setFlags(parent.flags())
            for i, term in enumerate(terms[category]):
                child = QtGui.QTreeWidgetItem(parent)
                child.setText(1, term)
                parent.addChild(child)
                box_item = QtGui.QTreeWidgetItem(child)
                box = QtGui.QComboBox()
                box.addItems(['normal', 'abnormal', 'unobserved'])
                self.ui.treeWidgetAvailableTerms.setItemWidget(child, 2, box)

    def annotation_radius_changed(self, radius):
        self.annotation_radius = radius
        self.annotation_radius_signal.emit(radius)

    def parse_options(self, pato_file):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        pato_path = os.path.join(script_dir, pato_file)
        options = []
        try:
            with open(pato_path, 'r') as fh:
                csv_reader = csv.reader(fh)
                for row in csv_reader:
                    options.append(row[0])
        except OSError:
            return None
        return options

    def parse_emap(self, emap_file):
        """
        This may not be used soon. Moving to yaml file loading
        Parameters
        ----------
        emap_file

        Returns
        -------

        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        emap_path = os.path.join(script_dir, emap_file)
        emap_info = {}
        try:
            with open(emap_path, 'r') as fh:
                csv_reader = csv.reader(fh)
                header = csv_reader.__next__()
                for row in csv_reader:
                    emap_id, emap_term= row
                    entry = {'emap_term': emap_term, 'emap_id': emap_id}   # [1:-1] stripping quotes
                    emap_info[emap_term] = entry
        except OSError:
            return None
        return emap_info

    def parse_emap_yaml(self, emap_file):
        import yaml
        from collections import defaultdict
        script_dir = os.path.dirname(os.path.abspath(__file__))
        emap_path = os.path.join(script_dir, emap_file)
        outdict = Dict()
        try:
            with open(emap_path, 'r') as fh:
                emap_terms = yaml.load(fh)
                for category, terms in emap_terms.items():
                    for term in terms:
                        outdict[category][term] = 'emap id here'
        except OSError:
            print('could not open the annotations yaml file {}'.format(emap_path))
            raise
        return outdict


    def save_annotations(self):

        success = True
        saved_files = []

        default_dir = self.appdata.get_last_dir_browsed()[0]
        if not os.path.isdir(default_dir):
            default_dir = os.path.expanduser("~")

        out_dir = str(QtGui.QFileDialog.getExistingDirectory(
            self,
            'Select directory to save annotations',
            default_dir,
            QtGui.QFileDialog.ShowDirsOnly))

        for vol in self.controller.model.all_volumes():
            annotations_dict = Dict()
            ann = vol.annotations
            vol_id = vol.name
            for i,  a in enumerate(ann.annotations):
                annotations_dict[i]['annotation_type'] = 'emapa'
                annotations_dict[i]['emapa_term'] = a.emap_term
                annotations_dict[i]['emapa_id'] = self.terms[a.stage]['emap'][a.emap_term]['emap_id']
                annotations_dict[i]['option'] = a.pato_term
                annotations_dict[i]['x'] = a.x
                annotations_dict[i]['y'] = a.y
                annotations_dict[i]['z'] = a.z
                annotations_dict[i]['x_percent'] = a.x_percent
                annotations_dict[i]['y_percent'] = a.y_percent
                annotations_dict[i]['z_percent'] = a.z_percent
                # annotations_dict[vol_id][i]['free_text'] = a.free_text
                annotations_dict[i]['volume_dimensions_xyz'] = a.dims

            # If no annotations available for the volume, do not save
            if not annotations_dict:
                continue
            out_file = os.path.join(out_dir, vol_id + '.json')

            try:
                with open(out_file, 'w') as fh:
                    fh.write(json.dumps(annotations_dict, sort_keys=True, indent = 4, separators = (',', ': ')))
            except (IOError, OSError):
                success = False
            else:
                saved_files.append(out_file)
        if not success:
            common.error_dialog(self, 'Error', 'The was an error writing the annotation files')
        else:
            msg = '\n'.join(saved_files)
            common.info_dialog(self, 'Success', 'Annotation files saved')

        self.annotation_recent_dir_signal.emit(out_dir)

    def activate_stage(self):
        """
        All radio buttons except e15.5 are incativated for now within QT designer
        Returns
        -------

        """
        # if self.ui.radioButtonE125.isChecked():
        #     # Set E145 terms as the default
        #     mp_terms = [x['mp_term'] for x in self.terms[Stage.e12_5]['mp'].values()]
        #     pato_terms = [x['pato_name'] for x in self.terms[Stage.e12_5]['pato'].values()]
        #     emap_terms = [x['emap_term'] for x in self.terms[Stage.e12_5]['emap'].values()]
        # elif self.ui.radioButtonE155.isChecked():
        #     # Set E145 terms as the default
        #     mp_terms = [x['mp_term'] for x in self.terms[Stage.e14_5]['mp'].values()]
        #     pato_terms = [x['pato_name'] for x in self.terms[Stage.e14_5]['pato'].values()]
        #     emap_terms = [x['emap_term'] for x in self.terms[Stage.e14_5]['emap'].values()]
        # elif self.ui.radioButtonE185.isChecked():
        #     # Set E145 terms as the default
        #     mp_terms = [x['mp_term'] for x in self.terms[Stage.e18_5]['mp'].values()]
        #     pato_terms = [x['pato_name'] for x in self.terms[Stage.e18_5]['pato'].values()]
        #     emap_terms = [x['emap_term'] for x in self.terms[Stage.e18_5]['emap'].values()]

        options = self.terms[Stage.e15_5]['option']
        emap_terms = [x['emap_term'] for x in self.terms[Stage.e15_5]['emap'].values()]


    def volume_changed(self, vol_id):
        self.controller.volume_changed(vol_id)
        self.update()

    def annotation_row_selected(self, cell):
        ann = self.controller.current_view.layers[Layer.vol1].vol.annotations[cell.row()]
        x = ann.x
        y = ann.y
        z = ann.z
        self.annotation_highlight_signal.emit(x, y, z, [0, 255, 0], self.annotation_radius)
        self.resize_table()

    def tab_changed(self, tab_indx):
        """
        When switching to annotation tab, make sure all views have same volume
        """
        vol = self.controller.current_view.layers[Layer.vol1].vol
        if not vol:
            return
        if tab_indx == 1:
            self.annotating = True
            for view in self.controller.views.values():
                view.layers[Layer.vol1].set_volume(vol.name)
            self.update()
        else:
            self.annotating = False

    def remove_annotation(self):
        indexes = self.ui.tableViewAvailableAnnotations.selectionModel().selectedRows()
        if len(indexes) > 0:
            selected_row = indexes[0].row()
            self.controller.current_view.layers[Layer.vol1].vol.annotations.remove(selected_row)
            self.annotations_table.layoutChanged.emit()

    def add_annotation(self):
        x = int(self.ui.labelXPos.text())
        y = int(self.ui.labelYPos.text())
        z = int(self.ui.labelZPos.text())

        if self.ui.radioButtonE145.isChecked():
            stage = Stage.e14_5
        elif self.ui.radioButtonE185.isChecked():
            stage = Stage.e18_5
        elif self.ui.radioButtonE125.isChecked():
            stage = Stage.e12_5
        elif self.ui.radioButtonE155.isChecked():
            stage = Stage.e15_5

        option = str(self.ui.comboBoxOptions.currentText())
        self.controller.current_view.layers[Layer.vol1].vol.annotations.add_emap_annotation(x, y, z, emap_term, option, stage)
        self.update()

    def mouse_pressed_annotate(self, view_index, x, y, orientation, vol_id):
        """
        Translate the view coordinates to volume coordinates
        :param own_index:
        :param x:
        :param y:
        :param orientation:
        :param vol_id:
        :return:
        """
        if self.annotating:
            vol = self.controller.current_view.layers[Layer.vol1].vol

            if orientation == Orientation.sagittal:
                z = copy.copy(y)
                y = copy.copy(x)
                x = view_index
            elif orientation == Orientation.axial:
                z = view_index
                x = x
                y = vol.dimension_length(Orientation.coronal) - y
            elif orientation == Orientation.coronal:
                z = copy.copy(y)
                y = view_index
                x = x

            # Populate the location boxes in the annotations manager
            self.ui.labelXPos.setText(str(x))
            self.ui.labelYPos.setText(str(y))
            self.ui.labelZPos.setText(str(z))
            self.annotation_highlight_signal.emit(int(x), int(y), int(z), [255, 0, 0], self.annotation_radius)

    def resize_table(self):
        self.ui.treeWidgetAvailableTerms.resizeColumnToContents(0)
        self.ui.treeWidgetAvailableTerms.resizeColumnToContents(1)

    def update(self):
        vol = self.controller.current_view.layers[Layer.vol1].vol
        if vol:
            self.annotations_table.set_data(vol.annotations)
            self.ui.comboBoxAnnotationsVolumes.clear()
            self.ui.comboBoxAnnotationsVolumes.addItems(self.controller.model.volume_id_list())
            self.ui.comboBoxAnnotationsVolumes.addItem("None")
            self.ui.comboBoxAnnotationsVolumes.setCurrentIndex(self.ui.comboBoxAnnotationsVolumes.findText(vol.name))
            self.annotations_table.layoutChanged.emit()
            self.resize_table()
