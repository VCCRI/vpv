# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_save.ui'
#
# Created: Wed Oct  5 12:37:29 2016
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Save(object):
    def setupUi(self, Save):
        Save.setObjectName(_fromUtf8("Save"))
        Save.resize(854, 373)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Save.sizePolicy().hasHeightForWidth())
        Save.setSizePolicy(sizePolicy)
        Save.setMinimumSize(QtCore.QSize(500, 130))
        self.verticalLayout = QtGui.QVBoxLayout(Save)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.line_2 = QtGui.QFrame(Save)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.verticalLayout.addWidget(self.line_2)
        self.table = QtGui.QTableView(Save)
        self.table.setLineWidth(2)
        self.table.setMidLineWidth(1)
        self.table.setObjectName(_fromUtf8("table"))
        self.verticalLayout.addWidget(self.table)
        self.line = QtGui.QFrame(Save)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout.addWidget(self.line)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.pushButtonOK = QtGui.QPushButton(Save)
        self.pushButtonOK.setObjectName(_fromUtf8("pushButtonOK"))
        self.horizontalLayout_2.addWidget(self.pushButtonOK)
        self.pushButtonCancel = QtGui.QPushButton(Save)
        self.pushButtonCancel.setObjectName(_fromUtf8("pushButtonCancel"))
        self.horizontalLayout_2.addWidget(self.pushButtonCancel)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(Save)
        QtCore.QMetaObject.connectSlotsByName(Save)

    def retranslateUi(self, Save):
        Save.setWindowTitle(_translate("Save", "Dialog", None))
        self.pushButtonOK.setText(_translate("Save", "Save files", None))
        self.pushButtonCancel.setText(_translate("Save", "Cancel", None))

