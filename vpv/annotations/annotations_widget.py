"""
A widget to display the manual annotations in the annotations tab of the data manager.
Works something like this:
- When a model.Volume is loaded the available terms from model.Volume.Annotations is loaded. When first run, these 
    should all be set to 'imageOnly'
- ...

"""
import os
from os.path import dirname, abspath, join, isdir
import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QTreeWidgetItem, QFileDialog, QComboBox, QCheckBox
from vpv.ui.views.ui_annotations import Ui_Annotations
from vpv.common import Layers, AnnotationOption, info_dialog, error_dialog, question_dialog
from vpv.annotations.annotations_model import centre_stage_options
from vpv.annotations import impc_xml
from functools import partial
import re


SCRIPT_DIR = dirname(abspath(__file__))

ROW_INDICES = {'term': 0,
               'name': 1,
               'option': 2,
               'done': 3}


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

        self.ui.spinBoxAnnotationCircleSize.setValue(self.appdata.annotation_circle_radius)
        self.ui.spinBoxAnnotationCircleSize.valueChanged.connect(self.annotation_radius_changed)

        self.annotating = False

        self.ui.treeWidgetAvailableTerms.itemClicked.connect(self.on_tree_clicked)

        self.ui.treeWidgetAvailableTerms.clear()

        self.reset_roi()

        self.set_current_date()

        if self.appdata.annotator_id:
            self.ui.lineEditAnnotatorId.setText(self.appdata.annotator_id)
        self.ui.lineEditAnnotatorId.textEdited.connect(self.annotator_id_changed)

        # Make the line edits non editable
        self.ui.lineEditStage.setReadOnly(True)
        self.ui.lineEditCentre.setReadOnly(True)
        self.first_run = True

    def d_pressed_slot(self):
        """
        Get the signal from the mainwindow when the d key is pressed. USe this signal to indicate if the currently
        active parameter should be marked as 'done'
        """
        if self.annotating:
            item = self.ui.treeWidgetAvailableTerms.currentItem()
            if item:
                checkbox = self.ui.treeWidgetAvailableTerms.itemWidget(item, 4)
                if checkbox:
                    # print(self.ui.treeWidgetAvailableTerms.child(i))
                    checkbox.toggle()

    def sroll_annotations(self, up: bool):
        current_row_idx = self.ui.treeWidgetAvailableTerms.currentIndex()
        if current_row_idx:
            cr = current_row_idx.row()
            new_row_idx = cr - 1 if up else cr + 1
        new_item = self.ui.treeWidgetAvailableTerms.itemFromIndex(new_row_idx)
        self.ui.treeWidgetAvailableTerms.setCurrentItem(new_item)

    def annotator_id_changed(self):
        id_ = str(self.ui.lineEditAnnotatorId.text())
        if not id_ or id_.isspace():
            return
        self.appdata.annotator_id = id_

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

        # Set the annotation info box
        self.ui.textEditAnnotationInfo.setText(info_str)
        if None in (ann.x, ann.y, ann.z):
            self.reset_roi()
            return
        self.annotation_highlight_signal.emit(ann.x, ann.y, ann.z, [0, 255, 0], self.appdata.annotation_circle_radius)

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
        if not vol or None in (vol.annotations.stage, vol.annotations.center):
            # info_dialog(self, 'Chose centre and stage', 'You must choose a centre and stage from the options tab')
            return

        self.ui.lineEditCentre.setText(vol.annotations.center)
        self.ui.lineEditStage.setText(vol.annotations.stage)

        def setup_option_box_signal(box_: QComboBox, child_: QTreeWidgetItem):
            """
            Connect the Qcombobox to a slot
            """
            box.activated.connect(partial(self.update_annotation, child_, box_))
            # Setup signal so when combobox is only opened, it sets the selection to that column
            box.highlighted.connect(partial(self.on_box_highlight, child))

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

        for i, ann in enumerate(sorted(vol.annotations, key=lambda an_: an_.order)):

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
            setup_option_box_signal(box, child)
            self.ui.treeWidgetAvailableTerms.setItemWidget(child, 2, box)

            done_checkbox = QtWidgets.QCheckBox()
            done_checkbox.setChecked(ann.looked_at)
            done_checkbox.stateChanged.connect(partial(self.parameter_done_signal, child, done_checkbox))
            self.ui.treeWidgetAvailableTerms.setItemWidget(child, 4, done_checkbox)

        # Set the roi coords to None
        self.roi_highlight_off_signal.emit()

    def on_box_highlight(self, child):
        if self.ui.treeWidgetAvailableTerms.currentItem() != child:
            self.reset_roi()
        self.ui.treeWidgetAvailableTerms.setCurrentItem(child)

    def annotation_radius_changed(self, radius: int):
        self.appdata.annotation_circle_radius = radius
        self.annotation_radius_signal.emit(radius)

    def save_annotations(self):

        date_of_annotation = self.ui.dateEdit.date().toString('yyyy-MM-dd')

        experimenter_id = self.ui.lineEditAnnotatorId.text()
        if experimenter_id.isspace() or not experimenter_id:
            error_dialog(self, 'Experimenter ID missing', "An annotator ID is required")
            return

        saved_file_paths = []

        for vol in self.controller.model.all_volumes():

            xml_exporter = impc_xml.ExportXML(date_of_annotation,
                                              experimenter_id,
                                              vol.annotations.metadata_parameter_file)

            ann = vol.annotations

            for i,  a in enumerate(ann.annotations):
                xml_exporter.add_parameter(a.term, a.selected_option)

                if all((a.x, a.y, a.z)):
                    xml_exporter.add_point(a.term, (a.x, a.y, a.z))

            xml_dir = vol.annotations.annotation_dir

            increment = get_increment(xml_dir)

            xml_file_name = "{}.{}.{}.experiment.impc.xml".format(vol.annotations.center,
                                                             date_of_annotation,
                                                             increment)
            xml_path = join(xml_dir, xml_file_name)

            try:
                xml_exporter.write(xml_path)
            except OSError as e:
                error_dialog(self, 'Save file failure', 'Annotation file not saved:{}'.format(e))
            else:
                saved_file_paths.append(xml_path)

        if saved_file_paths:
            sf_str = '\n'.join(saved_file_paths)
            info_dialog(self, 'Success', 'Annotation files saved:{}'.format(sf_str))

    def volume_changed(self, vol_id: str):
        stage = self.ui.lineEditStage.text()
        center = self.ui.lineEditCentre.text()

        self.controller.volume_changed(vol_id)
        vol = self.controller.current_annotation_volume()
        if vol:
            if (stage and not stage.isspace()) and (center and not center.isspace()):
                if (len(vol.annotations) == 0) or not all((vol.annotations.center, vol.annotations.stage)):
                    # Setting the stage and center will force the loading of default annotations
                    vol.annotations.center = center
                    vol.annotations.stage = stage
            # if not vol.annotations:
            #     vol.annotations._load_annotations()
        self.update()
        self.populate_available_terms()

    def parameter_done_signal(self, child: QTreeWidgetItem, check_box: QCheckBox):
        vol = self.controller.current_annotation_volume()
        if not vol:
            error_dialog(self, "Error", "No volume selected")
            return

        base_node = child
        term = base_node.text(1)
        ann = vol.annotations.get_by_term(term)
        ann.looked_at = bool(check_box.isChecked())

    def update_annotation(self, child: QTreeWidgetItem, cbox: QComboBox):
        """
        On getting a change signal from the parameter option combobox, set options on the volume.annotations object
        Also set the selected row to acrtive

        Parameters
        ----------
        child: is the node in the QTreeWidget that corresponds to our paramter option selection
        cbox: Qt combobox that was clicked
        row: The row of the qtreewidget where the combobox is

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

    def update(self):
        """
        Update the annotations comboboxes
        """
        vol = self.controller.current_view.layers[Layers.vol1].vol
        if vol:
            self.ui.comboBoxAnnotationsVolumes.clear()
            self.ui.comboBoxAnnotationsVolumes.addItems(self.controller.model.volume_id_list())
            self.ui.comboBoxAnnotationsVolumes.addItem("None")
            self.ui.comboBoxAnnotationsVolumes.setCurrentIndex(self.ui.comboBoxAnnotationsVolumes.findText(vol.name))


def get_increment(dir_):
    """
    Bedore saving xml annotation, look through the folder that we are saving to to see if there are already
    annoatations present. If there is, we presume it's from the same line, so we should increment the
    value

    Parameters
    ----------
    dir_: the directory to save the xml to

    Returns
    -------
    int: increment value

    """

    def inc_regegex(fname):
        res = re.search('(\d)+.experiment.impc.xml', fname)
        if res:
            try:
                int(res.group(1))
            except ValueError:
                print('Cannot get increment value from fname')
                return None
            else:
                return int(res.group(1))

    increments = []

    dir_ = abspath(dir_)

    dirs = os.listdir(join(dir_, '..'))
    for d in dirs:

        ann_folder = abspath(os.path.join(dir_, '..', d))

        if not os.path.isdir(ann_folder):
            continue

        files = os.listdir(ann_folder)

        for f in files:
            inc = inc_regegex(f)
            if ann_folder == dir_ and inc is not None:
                # If the current folder already contains an annotaiton file, just return it's present increment
                return inc
            if inc is not None:
                increments.append(inc)

    if len(increments) > 0:
        increments.sort(reverse=True)
        new_increment = increments[0] + 1
    else:
        new_increment = 0
    return new_increment


if __name__ == '__main__':
    inc = get_increment('/home/neil/Desktop/t/foriev/1261203_KO')
    print(inc)