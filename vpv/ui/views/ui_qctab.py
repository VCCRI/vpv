# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_qctab.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_QC(object):
    def setupUi(self, QC):
        QC.setObjectName("QC")
        QC.resize(758, 848)
        self.verticalLayout = QtWidgets.QVBoxLayout(QC)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtWidgets.QLabel(QC)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.listWidgetQcSpecimens = QtWidgets.QListWidget(QC)
        self.listWidgetQcSpecimens.setObjectName("listWidgetQcSpecimens")
        self.verticalLayout.addWidget(self.listWidgetQcSpecimens)
        self.label = QtWidgets.QLabel(QC)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.listWidgetQcFlagged = QtWidgets.QListWidget(QC)
        self.listWidgetQcFlagged.setObjectName("listWidgetQcFlagged")
        self.verticalLayout.addWidget(self.listWidgetQcFlagged)
        self.label_3 = QtWidgets.QLabel(QC)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.listWidgetNotes = QtWidgets.QListWidget(QC)
        self.listWidgetNotes.setObjectName("listWidgetNotes")
        self.verticalLayout.addWidget(self.listWidgetNotes)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButtonOpenDir = QtWidgets.QPushButton(QC)
        self.pushButtonOpenDir.setObjectName("pushButtonOpenDir")
        self.horizontalLayout.addWidget(self.pushButtonOpenDir)
        self.pushButtonSaveQC = QtWidgets.QPushButton(QC)
        self.pushButtonSaveQC.setObjectName("pushButtonSaveQC")
        self.horizontalLayout.addWidget(self.pushButtonSaveQC)
        self.pushButtonLoadAtlasMetadata = QtWidgets.QPushButton(QC)
        self.pushButtonLoadAtlasMetadata.setObjectName("pushButtonLoadAtlasMetadata")
        self.horizontalLayout.addWidget(self.pushButtonLoadAtlasMetadata)
        self.pushButtonNextSpecimen = QtWidgets.QPushButton(QC)
        self.pushButtonNextSpecimen.setObjectName("pushButtonNextSpecimen")
        self.horizontalLayout.addWidget(self.pushButtonNextSpecimen)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(QC)
        QtCore.QMetaObject.connectSlotsByName(QC)

    def retranslateUi(self, QC):
        _translate = QtCore.QCoreApplication.translate
        QC.setWindowTitle(_translate("QC", "Form"))
        self.label_2.setText(_translate("QC", "Specimens"))
        self.label.setText(_translate("QC", "Qc flagged labels"))
        self.label_3.setText(_translate("QC", "Notes"))
        self.pushButtonOpenDir.setText(_translate("QC", "Open folder"))
        self.pushButtonSaveQC.setText(_translate("QC", "Save QC"))
        self.pushButtonLoadAtlasMetadata.setText(_translate("QC", "Load atlas metadata"))
        self.pushButtonNextSpecimen.setText(_translate("QC", "Next image"))
import resources_rc
