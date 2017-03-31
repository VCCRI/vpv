
import os
import copy
from PyQt4 import QtGui, QtCore
from ui.ui_annotations import Ui_Annotations
import json
import common
from common import Orientation, Stage, Layer, AnnotationOption
from lib.addict import Dict
from collections import defaultdict


OPTION_COLOR_MAP = {
    AnnotationOption.unobserved: (0, 255, 255, 100),
    AnnotationOption.image_only: (30, 30, 30, 100),
    AnnotationOption.normal: (0, 255, 0, 100),
    AnnotationOption.abnormal: (255, 0, 0, 100)}


# class VolumeAnnotationsTableModel(QtCore.QAbstractTableModel):
#     def __init__(self, parent=None):
#         super(VolumeAnnotationsTableModel, self).__init__(parent)
#         self.ann_data = None  # model.volume.VolumeAnnotations
#         self.header_data = ['x:y:z', 'EMAPA', 'option', 'stage']
#
#     def set_data(self, annotations_model):
#         self.ann_data = annotations_model
#
#     def rowCount(self, parent):
#         if self.ann_data:
#             return len(self.ann_data)
#         else:
#             return 0
#
#     def columnCount(self, parent):
#         if self.ann_data:
#             return self.ann_data.col_count
#         else:
#             return 0
#
#     def data(self, index, role):
#         if self.ann_data:
#             if not index.isValid():
#                 return None
#             elif role != QtCore.Qt.DisplayRole:
#                 return None
#             return self.ann_data[index.row()][index.column()]
#
#     def headerData(self, col, orientation, role):
#         if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
#             return self.header_data[col]
#         return None


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

        # Set E15_5 terms as the default
        self.ui.radioButtonE155.setChecked(True)

        # Something after here makes it crash
        self.ui.comboBoxAnnotationsVolumes.activated['QString'].connect(self.volume_changed)
        self.ui.pushButtonRemoveAnnotation.clicked.connect(self.remove_annotation)

        self.ui.pushButtonSaveAnnotations.clicked.connect(self.save_annotations)
        self.ui.spinBoxAnnotationCircleSize.valueChanged.connect(self.annotation_radius_changed)
        self.annotation_radius = 10
        self.annotating = False

        self.ui.treeWidgetAvailableTerms.itemClicked.connect(self.on_tree_clicked)
        # Make sure the tree is resized to fit contents
        self.ui.treeWidgetAvailableTerms.itemExpanded.connect(self.resize_table)
        self.ui.treeWidgetAvailableTerms.clear()

    def on_tree_clicked(self, item):
        """
        Get the annotation for that term and display it on the annotation info box
        Parameters
        ----------
        item: QTreeWidgetItem that has been clicked
        """
        term = item.text(1)
        vol = self.controller.current_annotation_volume()
        annotations = vol.annotations
        ann = annotations.get_by_term(term)
        if not ann:
            return
        info_str = "Annotation information\nterm: {}\noption: {}\nx:{}, y:{}, z:{}".format(
          ann.term, ann.option.value, ann.x, ann.y, ann.z
        )
        self.ui.textEditAnnotationInfo.setText(info_str)
        if None in (ann.x, ann.y, ann.z):
            return
        self.annotation_highlight_signal.emit(ann.x, ann.y, ann.z, [0, 255, 0], self.annotation_radius)

    def tab_is_active(self):

        vol = self.controller.current_annotation_volume()

        if not vol:
            return
        for view in self.controller.views.values():
            view.layers[Layer.vol1].set_volume(vol.name)
        self.populate_available_terms()
        self.update()

    def clear(self):
        self.ui.comboBoxAnnotationsVolumes.clear()

    def populate_available_terms(self):
        """
        Run this at start up
        Returns
        -------
        """
        self.ui.treeWidgetAvailableTerms.clear()

        def setup_signal(box_, child_):
            """
            Created this inner function otherwise the last cbox made was always giving the signal?
            """
            box.activated.connect(lambda: self.update_annotation(child_, box_))

        header = QtGui.QTreeWidgetItem(['category', 'term', 'option'])
        self.ui.treeWidgetAvailableTerms.setHeaderItem(header)
        ann_by_cat = defaultdict(list)  # sort the annotations into categories

        # Load the default 'unobserved' annotation for each term for the current volume
        vol = self.controller.current_annotation_volume()
        if not vol:
            return
        annotations = vol.annotations

        for ann in annotations:
            ann_by_cat[ann.category].append(ann)
        for category, annotations in ann_by_cat.items():
            parent = QtGui.QTreeWidgetItem(self.ui.treeWidgetAvailableTerms)
            parent.setText(0, category)
            parent.setFlags(parent.flags())
            for i, annotation in enumerate(annotations):
                child = QtGui.QTreeWidgetItem(parent)
                child.setText(1, annotation.term)
                option = annotation.option
                color = OPTION_COLOR_MAP[option]
                parent.addChild(child)
                box = QtGui.QComboBox()
                box.addItem(AnnotationOption.normal.value, AnnotationOption.normal)
                box.addItem(AnnotationOption.abnormal.value, AnnotationOption.abnormal)
                box.addItem(AnnotationOption.unobserved.value, AnnotationOption.unobserved)
                box.addItem(AnnotationOption.image_only.value, AnnotationOption.image_only)
                box.setCurrentIndex(box.findText(option.value))
                # Setup combobox selection signal
                setup_signal(box, child)
                self.ui.treeWidgetAvailableTerms.setItemWidget(child, 2, box)
                child.setBackgroundColor(1, QtGui.QColor(*color))  # Unpack the tuple of colors and opacity
        self.mark_complete_categories()

    def annotation_radius_changed(self, radius):
        self.annotation_radius = radius
        self.annotation_radius_signal.emit(radius)

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
                annotations_dict[i]['annotation_type'] = a.type
                annotations_dict[i]['emapa_term'] = a.term
                annotations_dict[i]['emapa_id'] = 'dummy id'
                annotations_dict[i]['option'] = a.option.value
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
        self.resize_table()

    def volume_changed(self, vol_id):
        self.controller.volume_changed(vol_id)
        self.update()
        self.populate_available_terms()

    def remove_annotation(self):
        return # currently not working
        indexes = self.ui.treeViewAvailableAnnotations.selectionModel().selectedRows()
        # if len(indexes) > 0:
        #     selected_row = indexes[0].row()
        #     self.controller.current_view.layers[Layer.vol1].vol.annotations.remove(selected_row)
        #     self.annotations_table.layoutChanged.emit()

    def update_annotation(self, child, cbox):
        """
        Returns
        -------

        """
        vol = self.controller.current_annotation_volume()
        if not vol:
            common.info_dialog(self, "Error", "No volume selected")
            return
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

        base_node = child
        term = base_node.text(1)
        if not term:
            common.info_dialog(self, "Error", "No term is selected!")
            return


        option = cbox.itemData(cbox.currentIndex(), QtCore.Qt.UserRole)

        color = OPTION_COLOR_MAP[option]
        base_node.setBackgroundColor(1, QtGui.QColor(*color))

        vol.annotations.add_emap_annotation(x, y, z, term, option, stage)
        self.mark_complete_categories()
        self.on_tree_clicked(base_node)

    def mark_complete_categories(self):
        """
        Check each category in the treewidget and if all items have been modified add a tick box to show it's been done
        """
        root = self.ui.treeWidgetAvailableTerms.invisibleRootItem()
        child_count = root.childCount()
        for i in range(child_count):
            cat = root.child(i)
            all_done = True
            for j in range(cat.childCount()):
                cbox = self.ui.treeWidgetAvailableTerms.itemWidget(cat.child(j), 2)
                option = cbox.currentText()
                if option == AnnotationOption.image_only.value:
                    all_done = False
                    break  # still some to be annotated
            if all_done:
                cat.setBackgroundColor(0, QtGui.QColor(0, 255, 0, 100))


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
            self.ui.comboBoxAnnotationsVolumes.clear()
            self.ui.comboBoxAnnotationsVolumes.addItems(self.controller.model.volume_id_list())
            self.ui.comboBoxAnnotationsVolumes.addItem("None")
            self.ui.comboBoxAnnotationsVolumes.setCurrentIndex(self.ui.comboBoxAnnotationsVolumes.findText(vol.name))
            self.resize_table()