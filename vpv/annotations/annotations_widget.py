"""
A widget to display the manual annotations in the annotations tab of the data manager.
Works something like this:
- When a model.Volume is loaded the available terms from model.Volume.Annotations is loaded. When first run, these 
    should all be set to 'imageOnly'
- ...

"""
import os
from os.path import dirname, abspath, join
import datetime
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QWidget, QTreeWidgetItem, QFileDialog, QComboBox
from vpv.ui.views.ui_annotations import Ui_Annotations
import json
from vpv.common import Stage, Layers, AnnotationOption, info_dialog, error_dialog, question_dialog
from vpv.lib.addict import Dict
from vpv.annotations.annotations_model import centre_stage_options
from vpv.annotations import export_impc_xml


SCRIPT_DIR = dirname(abspath(__file__))
PROC_METADATA_PATH = join(SCRIPT_DIR, 'options', 'procedure_metadata.yaml')  # TODO: read this from the analysis zip. Just testing


OPTION_COLOR_MAP = {
    AnnotationOption.present: (0, 255, 0, 100),
    AnnotationOption.absent: (255, 0, 0, 200),
    AnnotationOption.abnormal: (255, 0, 0, 100),
    AnnotationOption.unobservable: (0, 255, 255, 100),
    AnnotationOption.ambiguous: (100, 100, 0, 100),
    AnnotationOption.image_only: (30, 30, 30, 100)
}


class AnnotationsWidget(QWidget):
    annotation_highlight_signal = QtCore.pyqtSignal(int, int, int, list, int)
    annotation_radius_signal = QtCore.pyqtSignal(int)
    annotation_recent_dir_signal = QtCore.pyqtSignal(str)
    roi_highlight_off_signal = QtCore.pyqtSignal()
    #reset_roi_signal = QtCore.pyqtSignal()  # Set the roi to None so can annotate without giving coords

    def __init__(self, controller, main_window):
        """
        Parameters
        ----------
        controller: vpv.Vpv
            The entry point of the app
        main_window: QtWidgets.QmainWindow
            The mainwindow. Used as a parent for other widgets
        """
        super(AnnotationsWidget, self).__init__(main_window)
        self.controller = controller

        self.ui = Ui_Annotations()

        self.ui.setupUi(self)

        self.appdata = self.controller.appdata

        # Set E15_5 terms as the default
        self.ui.radioButtonE155.setChecked(True)

        # The signal to change volumes from the combobox
        self.ui.comboBoxAnnotationsVolumes.activated['QString'].connect(self.volume_changed)

        # self.ui.pushButtonRemoveAnnotation.clicked.connect(self.remove_annotation)

        self.ui.pushButtonSaveAnnotations.clicked.connect(self.save_annotations)

        self.ui.pushButtonDiableRoi.clicked.connect(self.reset_roi)

        self.ui.spinBoxAnnotationCircleSize.valueChanged.connect(self.annotation_radius_changed)

        self.annotation_radius = 10

        self.annotating = False

        self.ui.treeWidgetAvailableTerms.itemClicked.connect(self.on_tree_clicked)

        # Make sure the tree is resized to fit contents
        self.ui.treeWidgetAvailableTerms.itemExpanded.connect(self.resize_table)

        self.ui.treeWidgetAvailableTerms.clear()

        self.reset_roi()

        self.set_current_date()

        self.ui.comboBoxCentre.activated['QString'].connect(self.ui.lineEditCentre.setText)
        self.ui.comboBoxStage.activated['QString'].connect(self.ui.lineEditStage.setText)
        self.ui.lineEditCentre.textChanged.connect(self.center_changed)
        self.ui.lineEditStage.textChanged.connect(self.stage_changed)

        self.ui.comboBoxCentre.addItems(centre_stage_options.all_centers())

    def center_changed(self, center):
        vol = self.controller.current_annotation_volume()
        if vol.annotations.center:
            a = question_dialog(self, 'Change centre?', 'Do you want to change center associated with this volume?\n'
                                'If you select YES, all annotaiton on this volume will be erased.')
            if a:
                vol.annotations.clear()

        vol.annotations.center = center
        self.populate_available_terms()
        self.ui.lineEditStage.clear()
        # Now we've changed center, we need to change the stage combobox. Set it to the first
        available_stages = centre_stage_options.all_stages(center)
        self.ui.comboBoxStage.addItems(available_stages)

    def stage_changed(self, stage):
        vol = self.controller.current_annotation_volume()
        if vol.annotations.stage:
            a = question_dialog(self, 'Change centre?', 'Do you want to change center associated with this volume?\n'
                                'If you select YES, all annotaiton on this volume will be erased.')
            if not a:
                return
        # If center and stage are now set, let's fill respective options
        vol.annotations.stage = stage
        self.populate_available_terms()

    def annotator_id_changed(self):
        id_ = str(self.ui.lineEditAnnotatorId.text())
        if not id_ or id_.isspace():
            return

    def set_current_date(self):
        d = datetime.datetime.now()

        self.ui.dateEdit.setDate(QtCore.QDate(d.year, d.month, d.day))

    def on_tree_clicked(self, item: QTreeWidgetItem):
        """
        Responds to clicks on the QtreeWidget containing the annoations

        Parameters
        ----------
        item: the item that has been clicked

        Notes
        -----
        - Gets the current volume
        - Retrieves the annotation information and fills the annotation info box at the bottom of the tab widget
        - Emits a signal with the corresponding coordinates so that the annotation marker can be set

        """
        term = item.text(1)
        vol = self.controller.current_annotation_volume()
        annotations = vol.annotations
        ann = annotations.get_by_term(term)
        if not ann:
            return
        info_str = "Annotation information\nterm: {}\noption: {}\nx:{}, y:{}, z:{}".format(
          ann.term, ann.selected_option, ann.x, ann.y, ann.z
        )
        self.ui.textEditAnnotationInfo.setText(info_str)
        if None in (ann.x, ann.y, ann.z):
            self.reset_roi()
            return
        self.annotation_highlight_signal.emit(ann.x, ann.y, ann.z, [0, 255, 0], self.annotation_radius)

    def activate_tab(self):  # Change function name

        vol = self.controller.current_annotation_volume()

        if not vol:
            return

        #  Ensure all the view ports contain the same image
        for view in self.controller.views.values():
            view.layers[Layers.vol1].set_volume(vol.name)

        self.populate_available_terms()
        self.update()

    def clear(self):
        self.ui.comboBoxAnnotationsVolumes.clear()

    def populate_available_terms(self):
        """
        Runs at start up and when volume is changed. Poulates the avaible annotation terms
        """

        self.ui.treeWidgetAvailableTerms.clear()

        vol = self.controller.current_annotation_volume()
        if not vol and None in (vol.annotations.stage, vol.annotations.center):
            # info_dialog(self, 'Chose centre and stage', 'You must choose a centre and stage from the options tab')
            return

        def setup_signal(box_: QComboBox, child_: QTreeWidgetItem):
            """
            Connect the Qcombobox
            """
            box.activated.connect(lambda: self.update_annotation(child_, box_))

        header = QTreeWidgetItem(['', 'term', 'name', 'option'])

        self.ui.treeWidgetAvailableTerms.setHeaderItem(header)
        # ann_by_cat = defaultdict(list)  # sort the annotations into categories

        parent = QTreeWidgetItem(self.ui.treeWidgetAvailableTerms)
        parent.setText(0, 'Parameters')
        parent.setFlags(parent.flags())

        for ann in vol.annotations:  # remember to make iteration occur in order in the ann model

            child = QTreeWidgetItem(parent)
            child.setText(1, ann.term)
            child.setText(2, ann.name)
            option = ann.selected_option
            # color = OPTION_COLOR_MAP[option]
            parent.addChild(child)

            # Set up the combobox and highlight the currently selected one
            box = QComboBox()
            for opt in ann.options:
                box.addItem(opt)

            box.setCurrentIndex(box.findText(option))
            # Setup combobox selection signal
            setup_signal(box, child)
            self.ui.treeWidgetAvailableTerms.setItemWidget(child, 3, box)
            # child.setBackground(1, QtGui.QBrush(QtGui.QColor(*color)))  # Unpack the tuple of colors and opacity

        # Set the roi coords to None
        self.roi_highlight_off_signal.emit()

    def annotation_radius_changed(self, radius: int):
        self.annotation_radius = radius
        self.annotation_radius_signal.emit(radius)

    def save_annotations(self):

        success = True
        saved_files = []

        date_of_annotation = self.ui.dateEdit.date()
        experimenter_id = self.ui.lineEditAnnotatorId.text()

        default_dir = self.appdata.get_last_dir_browsed()[0]
        if not os.path.isdir(default_dir):
            default_dir = os.path.expanduser("~")

        out_dir = str(QFileDialog.getExistingDirectory(
            self,
            'Select directory to save annotations',
            default_dir,
            QFileDialog.ShowDirsOnly))

        for vol in self.controller.model.all_volumes():

            xml_exporter = export_impc_xml.ExportXML(date_of_annotation, experimenter_id, PROC_METADATA_PATH)

            annotations_dict = Dict()
            ann = vol.annotations
            vol_id = vol.name
            space = vol.space
            for i,  a in enumerate(ann.annotations):
                annotations_dict[i]['annotation_type'] = a.type
                annotations_dict[i]['name'] = a.name
                annotations_dict[i]['impc_id'] = a.term
                annotations_dict[i]['selected_option'] = a.selected_option
                annotations_dict[i]['x'] = a.x
                annotations_dict[i]['y'] = a.y
                annotations_dict[i]['z'] = a.z
                annotations_dict[i]['x_percent'] = a.x_percent
                annotations_dict[i]['y_percent'] = a.y_percent
                annotations_dict[i]['z_percent'] = a.z_percent
                # annotations_dict[vol_id][i]['free_text'] = a.free_text
                annotations_dict[i]['volume_dimensions_xyz'] = a.dims
                annotations_dict[i]['space'] = space
                annotations_dict[i]['stage'] = a.stage

                xml_exporter.add_parameter(a.term, a.selected_option)

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

            xml_path = os.path.join(out_dir, vol_id + '.xml')
            xml_exporter.write(xml_path)

        if not success:
            error_dialog(self, 'Error', 'The was an error writing the annotation files')
        else:
            sf_str = '\n'.join(saved_files)
            info_dialog(self, 'Success', 'Annotation files saved:{}'.format(sf_str))

        self.annotation_recent_dir_signal.emit(out_dir)
        self.resize_table()

    def volume_changed(self, vol_id: str):
        self.controller.volume_changed(vol_id)
        self.update()
        self.populate_available_terms()

    def update_annotation(self, child: QTreeWidgetItem, cbox: QComboBox):
        """
        On getting a change signal from the parameter option combobox, set options on the volume.annotations object

        Parameters
        ----------
        child: is the node in the QTreeWidget that corresponds to our paramter option selection
        cbox: Qt combobox that was clicked

        """
        vol = self.controller.current_annotation_volume()
        if not vol:
            error_dialog(self, "Error", "No volume selected")
            return
        try:
            x = int(self.ui.labelXPos.text())
            y = int(self.ui.labelYPos.text())
            z = int(self.ui.labelZPos.text())
        except ValueError:
            x = y = z = None

        base_node = child
        term = base_node.text(1)

        option = cbox.currentText()

        # If we are updating the annotation to ImageOnly, we should wipe any coordinates that may have been added to
        # a previous annotation option.
        if option == 'imageOnly':
            x = y = z = None

        elif option in (centre_stage_options.opts['options_requiring_points']):
            if None in (x, y, z):
                info_dialog(self, 'Select a region!',
                                   "For option '{}' coordinates must be specified".format(option))
                # this will reset the option back to what it is on the volume.annotation object
                cbox.setCurrentIndex(cbox.findText(vol.annotations.get_by_term(term).selected_option))
                return

        if not term:
            error_dialog(self, "Error", "No term is selected!")
            return

        # color = OPTION_COLOR_MAP[option]
        # base_node.setBackground(1, QtGui.QBrush(QtGui.QColor(*color)))

        vol.annotations.update_annotation(term, x, y, z, option)
        self.on_tree_clicked(base_node)

    def reset_roi(self):
        self.ui.labelXPos.setText(None)
        self.ui.labelYPos.setText(None)
        self.ui.labelZPos.setText(None)
        self.roi_highlight_off_signal.emit()

    def set_annotation_position_label(self, x: int, y: int, z: int):
        """
        Set the coordnates in the annotations tab. This is before the annotation has been saved
        ----------
        view_index
        x
        y
        orientation
        vol_id

        Returns
        -------

        """
        if self.annotating:
            self.ui.labelXPos.setText(str(x))
            self.ui.labelYPos.setText(str(y))
            self.ui.labelZPos.setText(str(z))

    def resize_table(self):
        self.ui.treeWidgetAvailableTerms.resizeColumnToContents(0)
        self.ui.treeWidgetAvailableTerms.resizeColumnToContents(1)

    def update(self):

        vol = self.controller.current_view.layers[Layers.vol1].vol
        if vol:
            self.ui.comboBoxAnnotationsVolumes.clear()
            self.ui.comboBoxAnnotationsVolumes.addItems(self.controller.model.volume_id_list())
            self.ui.comboBoxAnnotationsVolumes.addItem("None")
            self.ui.comboBoxAnnotationsVolumes.setCurrentIndex(self.ui.comboBoxAnnotationsVolumes.findText(vol.name))
            self.resize_table()