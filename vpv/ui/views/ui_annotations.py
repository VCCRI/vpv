# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_annotations.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Annotations(object):
    def setupUi(self, Annotations):
        Annotations.setObjectName("Annotations")
        Annotations.resize(599, 870)
        Annotations.setMinimumSize(QtCore.QSize(0, 40))
        self.verticalLayout_17 = QtWidgets.QVBoxLayout(Annotations)
        self.verticalLayout_17.setObjectName("verticalLayout_17")
        self.tabWidgetOptions = QtWidgets.QTabWidget(Annotations)
        self.tabWidgetOptions.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidgetOptions.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidgetOptions.setObjectName("tabWidgetOptions")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.layoutWidget = QtWidgets.QWidget(self.tab_3)
        self.layoutWidget.setGeometry(QtCore.QRect(0, 10, 581, 617))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.comboBoxAnnotationsVolumes = QtWidgets.QComboBox(self.layoutWidget)
        self.comboBoxAnnotationsVolumes.setObjectName("comboBoxAnnotationsVolumes")
        self.verticalLayout.addWidget(self.comboBoxAnnotationsVolumes)
        self.horizontalLayout_20 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_20.setObjectName("horizontalLayout_20")
        self.label_34 = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_34.sizePolicy().hasHeightForWidth())
        self.label_34.setSizePolicy(sizePolicy)
        self.label_34.setObjectName("label_34")
        self.horizontalLayout_20.addWidget(self.label_34)
        self.labelXPos = QtWidgets.QLabel(self.layoutWidget)
        self.labelXPos.setObjectName("labelXPos")
        self.horizontalLayout_20.addWidget(self.labelXPos)
        self.label_35 = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_35.sizePolicy().hasHeightForWidth())
        self.label_35.setSizePolicy(sizePolicy)
        self.label_35.setObjectName("label_35")
        self.horizontalLayout_20.addWidget(self.label_35)
        self.labelYPos = QtWidgets.QLabel(self.layoutWidget)
        self.labelYPos.setObjectName("labelYPos")
        self.horizontalLayout_20.addWidget(self.labelYPos)
        self.label_36 = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_36.sizePolicy().hasHeightForWidth())
        self.label_36.setSizePolicy(sizePolicy)
        self.label_36.setObjectName("label_36")
        self.horizontalLayout_20.addWidget(self.label_36)
        self.labelZPos = QtWidgets.QLabel(self.layoutWidget)
        self.labelZPos.setObjectName("labelZPos")
        self.horizontalLayout_20.addWidget(self.labelZPos)
        self.groupBoxAnnotationType = QtWidgets.QGroupBox(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBoxAnnotationType.sizePolicy().hasHeightForWidth())
        self.groupBoxAnnotationType.setSizePolicy(sizePolicy)
        self.groupBoxAnnotationType.setObjectName("groupBoxAnnotationType")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBoxAnnotationType)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.radioButtonE145 = QtWidgets.QRadioButton(self.groupBoxAnnotationType)
        self.radioButtonE145.setCheckable(False)
        self.radioButtonE145.setObjectName("radioButtonE145")
        self.horizontalLayout_2.addWidget(self.radioButtonE145)
        self.radioButtonE185 = QtWidgets.QRadioButton(self.groupBoxAnnotationType)
        self.radioButtonE185.setCheckable(False)
        self.radioButtonE185.setChecked(False)
        self.radioButtonE185.setObjectName("radioButtonE185")
        self.horizontalLayout_2.addWidget(self.radioButtonE185)
        self.radioButtonE125 = QtWidgets.QRadioButton(self.groupBoxAnnotationType)
        self.radioButtonE125.setCheckable(False)
        self.radioButtonE125.setObjectName("radioButtonE125")
        self.horizontalLayout_2.addWidget(self.radioButtonE125)
        self.radioButtonE155 = QtWidgets.QRadioButton(self.groupBoxAnnotationType)
        self.radioButtonE155.setChecked(True)
        self.radioButtonE155.setObjectName("radioButtonE155")
        self.horizontalLayout_2.addWidget(self.radioButtonE155)
        self.radioButtonE95 = QtWidgets.QRadioButton(self.groupBoxAnnotationType)
        self.radioButtonE95.setCheckable(False)
        self.radioButtonE95.setObjectName("radioButtonE95")
        self.horizontalLayout_2.addWidget(self.radioButtonE95)
        self.horizontalLayout_20.addWidget(self.groupBoxAnnotationType)
        self.verticalLayout.addLayout(self.horizontalLayout_20)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.verticalLayout.addLayout(self.gridLayout_2)
        self.line_3 = QtWidgets.QFrame(self.layoutWidget)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.verticalLayout.addWidget(self.line_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.line = QtWidgets.QFrame(self.layoutWidget)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout_4.addWidget(self.line)
        self.treeWidgetAvailableTerms = QtWidgets.QTreeWidget(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.treeWidgetAvailableTerms.sizePolicy().hasHeightForWidth())
        self.treeWidgetAvailableTerms.setSizePolicy(sizePolicy)
        self.treeWidgetAvailableTerms.setMinimumSize(QtCore.QSize(0, 300))
        self.treeWidgetAvailableTerms.setObjectName("treeWidgetAvailableTerms")
        self.treeWidgetAvailableTerms.headerItem().setText(0, "1")
        self.horizontalLayout_4.addWidget(self.treeWidgetAvailableTerms)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.textEditAnnotationInfo = QtWidgets.QTextEdit(self.layoutWidget)
        self.textEditAnnotationInfo.setMaximumSize(QtCore.QSize(16777215, 100))
        self.textEditAnnotationInfo.setObjectName("textEditAnnotationInfo")
        self.verticalLayout.addWidget(self.textEditAnnotationInfo)
        self.line_2 = QtWidgets.QFrame(self.layoutWidget)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout.addWidget(self.line_2)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_2 = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_6.addWidget(self.label_2)
        self.spinBoxAnnotationCircleSize = QtWidgets.QSpinBox(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinBoxAnnotationCircleSize.sizePolicy().hasHeightForWidth())
        self.spinBoxAnnotationCircleSize.setSizePolicy(sizePolicy)
        self.spinBoxAnnotationCircleSize.setProperty("value", 10)
        self.spinBoxAnnotationCircleSize.setObjectName("spinBoxAnnotationCircleSize")
        self.horizontalLayout_6.addWidget(self.spinBoxAnnotationCircleSize)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.pushButtonSaveAnnotations = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButtonSaveAnnotations.setObjectName("pushButtonSaveAnnotations")
        self.horizontalLayout_5.addWidget(self.pushButtonSaveAnnotations)
        self.pushButtonDiableRoi = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButtonDiableRoi.setObjectName("pushButtonDiableRoi")
        self.horizontalLayout_5.addWidget(self.pushButtonDiableRoi)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.verticalLayout_16 = QtWidgets.QVBoxLayout()
        self.verticalLayout_16.setObjectName("verticalLayout_16")
        self.verticalLayout.addLayout(self.verticalLayout_16)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/green_view.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabWidgetOptions.addTab(self.tab_3, icon, "")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.comboBox = QtWidgets.QComboBox(self.tab_4)
        self.comboBox.setGeometry(QtCore.QRect(50, 40, 86, 25))
        self.comboBox.setObjectName("comboBox")
        self.label_4 = QtWidgets.QLabel(self.tab_4)
        self.label_4.setGeometry(QtCore.QRect(150, 40, 67, 17))
        self.label_4.setObjectName("label_4")
        self.comboBox_2 = QtWidgets.QComboBox(self.tab_4)
        self.comboBox_2.setGeometry(QtCore.QRect(50, 80, 86, 25))
        self.comboBox_2.setObjectName("comboBox_2")
        self.label_5 = QtWidgets.QLabel(self.tab_4)
        self.label_5.setGeometry(QtCore.QRect(150, 80, 67, 17))
        self.label_5.setObjectName("label_5")
        self.widget = QtWidgets.QWidget(self.tab_4)
        self.widget.setGeometry(QtCore.QRect(31, 131, 280, 59))
        self.widget.setObjectName("widget")
        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.lineEditAnnotatorId = QtWidgets.QLineEdit(self.widget)
        self.lineEditAnnotatorId.setObjectName("lineEditAnnotatorId")
        self.gridLayout.addWidget(self.lineEditAnnotatorId, 0, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.widget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.widget)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 1, 1, 1)
        self.dateEdit = QtWidgets.QDateEdit(self.widget)
        self.dateEdit.setObjectName("dateEdit")
        self.gridLayout.addWidget(self.dateEdit, 1, 0, 1, 1)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/settings.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabWidgetOptions.addTab(self.tab_4, icon1, "")
        self.verticalLayout_17.addWidget(self.tabWidgetOptions)

        self.retranslateUi(Annotations)
        self.tabWidgetOptions.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(Annotations)

    def retranslateUi(self, Annotations):
        _translate = QtCore.QCoreApplication.translate
        Annotations.setWindowTitle(_translate("Annotations", "Form"))
        self.label_34.setText(_translate("Annotations", "X: "))
        self.labelXPos.setText(_translate("Annotations", "0"))
        self.label_35.setText(_translate("Annotations", "Y:"))
        self.labelYPos.setText(_translate("Annotations", "0"))
        self.label_36.setText(_translate("Annotations", "Z:"))
        self.labelZPos.setText(_translate("Annotations", "0"))
        self.groupBoxAnnotationType.setToolTip(_translate("Annotations", "Select embryo stage"))
        self.radioButtonE145.setText(_translate("Annotations", "E14.5"))
        self.radioButtonE185.setText(_translate("Annotations", "E18.5"))
        self.radioButtonE125.setText(_translate("Annotations", "E12.5"))
        self.radioButtonE155.setText(_translate("Annotations", "E15.5"))
        self.radioButtonE95.setText(_translate("Annotations", "E9.5"))
        self.label_2.setText(_translate("Annotations", "Circle radius"))
        self.spinBoxAnnotationCircleSize.setToolTip(_translate("Annotations", "radius of the marker"))
        self.pushButtonSaveAnnotations.setText(_translate("Annotations", "Save annotations"))
        self.pushButtonDiableRoi.setToolTip(_translate("Annotations", "Clear ROI coordinates"))
        self.pushButtonDiableRoi.setText(_translate("Annotations", "Reset roi"))
        self.label_4.setText(_translate("Annotations", "Centre"))
        self.label_5.setText(_translate("Annotations", "Stage"))
        self.label.setText(_translate("Annotations", "Annotator ID"))
        self.label_3.setText(_translate("Annotations", "Date of annotation"))

import resources_rc
