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
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QWidget, QTreeWidgetItem, QFileDialog, QComboBox
from vpv.ui.views.ui_annotations import Ui_Annotations
from vpv.common import Layers, AnnotationOption, info_dialog, error_dialog, question_dialog
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

        if self.appdata.annotator_id:
            self.ui.lineEditAnnotatorId.setText(self.appdata.annotator_id)
        self.ui.lineEditAnnotatorId.textEdited.connect(self.annotator_id_changed)

        self.ui.comboBoxCentre.activated['QString'].connect(self.center_changed)
        self.ui.comboBoxStage.activated['QString'].connect(self.stage_changed)

        # Make the line edits non editable
        self.ui.lineEditStage.setReadOnly(True)
        self.ui.lineEditCentre.setReadOnly(True)

        self.ui.comboBoxCentre.addItems(centre_stage_options.all_centers())
        if self.appdata.annotation_centre:
            self.ui.comboBoxCentre.setCurrentText(self.appdata.annotation_centre)

        if self.appdata.annotation_stage:
            self.ui.comboStage.setCurrentText(self.appdata.annotation_stage)

    def annotator_id_changed(self):
        id_ = str(self.ui.lineEditAnnotatorId.text())
        if not id_ or id_.isspace():
            return
        self.appdata.annotator_id = id_

    def center_changed(self, center):
        vol = self.controller.current_annotation_volume()
        self.ui.lineEditCentre.setText(center)
        # Set the availabe stages for this centre
        available_stages = centre_stage_options.all_stages(center)
        self.ui.comboBoxStage.clear()
        self.ui.comboBoxStage.addItems(available_stages)

        if vol:
            if vol.annotations.center:
                a = question_dialog(self, 'Change centre?', 'Do you want to change center associated with this volume?\n'
                                    'If you select YES, all annotaiton on this volume will be erased.')
                if a:
                    vol.annotations.clear()
                else:
                    return

            vol.annotations.center = center
            self.populate_available_terms()
            self.ui.lineEditStage.clear()
            self.appdata.annotation_centre = center

    def stage_changed(self, stage):
        self.ui.lineEditStage.setText(stage)
        vol = self.controller.current_annotation_volume()

        if vol:
            if vol.annotations.stage:
                a = question_dialog(self, 'stage?', 'Do you want to change stage associated with this volume?\n'
                                    'If you select YES, all annotaiton on this volume will be erased.')
                if a:
                    vol.annotations.clear()
                else:
                    return

            # If center and stage are now set, let's fill respective options
            vol.annotations.stage = stage
            self.populate_available_terms()

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

        header_labels = QTreeWidgetItem(['', 'term', 'name', 'option', 'done?'])

        self.ui.treeWidgetAvailableTerms.setHeaderItem(header_labels)

        parent = QTreeWidgetItem(self.ui.treeWidgetAvailableTerms)
        parent.setText(0, '')
        parent.setFlags(parent.flags())
        parent.setExpanded(True)

        header = self.ui.treeWidgetAvailableTerms.header()

        # Set root column to invisible
        self.ui.treeWidgetAvailableTerms.setColumnWidth(0, 0)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)

        for ann in sorted(vol.annotations, key=lambda an_: an_.order):

            child = QTreeWidgetItem(parent)
            child.setText(1, ann.term)
            child.setText(3, ann.name)
            option = ann.selected_option
            # color = OPTION_COLOR_MAP[option]
            parent.addChild(child)

            # Set up the combobox and highlight the currently selected one
            box = QComboBox()
            box.setSizeAdjustPolicy(QComboBox.AdjustToContents)
            for opt in ann.options:
                box.addItem(opt)

            box.setCurrentIndex(box.findText(option))
            # Setup combobox selection signal
            setup_signal(box, child)
            self.ui.treeWidgetAvailableTerms.setItemWidget(child, 2, box)
            self.ui.treeWidgetAvailableTerms.setItemWidget(child, 4, QtWidgets.QCheckBox())
            # child.setBackground(1, QtGui.QBrush(QtGui.QColor(*color)))  # Unpack the tuple of colors and opacity

        # Set the roi coords to None
        self.roi_highlight_off_signal.emit()

    def annotation_radius_changed(self, radius: int):
        self.annotation_radius = radius
        self.annotation_radius_signal.emit(radius)

    def save_annotations(self):

        date_of_annotation = self.ui.dateEdit.date()

        experimenter_id = self.ui.lineEditAnnotatorId.text()
        if experimenter_id.isspace() or not experimenter_id:
            error_dialog(self, 'Experimenter ID missing', "An annotator ID is required")
            return

        default_dir = self.appdata.get_last_dir_browsed()[0]
        if not os.path.isdir(default_dir):
            default_dir = os.path.expanduser("~")

        out_dir = str(QFileDialog.getExistingDirectory(
            self,
            'Select directory to save annotations',
            default_dir,
            QFileDialog.ShowDirsOnly))

        saved_file_paths = []

        for vol in self.controller.model.all_volumes():

            xml_exporter = export_impc_xml.ExportXML(date_of_annotation, experimenter_id, PROC_METADATA_PATH)

            ann = vol.annotations
            vol_id = vol.name

            for i,  a in enumerate(ann.annotations):
                xml_exporter.add_parameter(a.term, a.selected_option)

                if all((a.x, a.y, a.z)):
                    xml_exporter.add_point(a.term, (a.x, a.y, a.z))

            xml_path = os.path.join(out_dir, vol_id + '.xml')

            try:
                xml_exporter.write(xml_path)
            except OSError as e:
                error_dialog(self, 'Save file failure', 'Annotation file not saved:{}'.format(sf_str))
            else:
                saved_file_paths.append(xml_path)

            sf_str = '\n'.join(saved_file_paths)
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