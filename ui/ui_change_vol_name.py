# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_change_vol_name.ui'
#
# Created: Wed Aug 31 10:49:17 2016
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

class Ui_VolNameDialog(object):
    def setupUi(self, VolNameDialog):
        VolNameDialog.setObjectName(_fromUtf8("VolNameDialog"))
        VolNameDialog.resize(395, 94)
        self.gridLayout = QtGui.QGridLayout(VolNameDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lineEditVolName = QtGui.QLineEdit(VolNameDialog)
        self.lineEditVolName.setObjectName(_fromUtf8("lineEditVolName"))
        self.gridLayout.addWidget(self.lineEditVolName, 0, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.pushButtonOk = QtGui.QPushButton(VolNameDialog)
        self.pushButtonOk.setObjectName(_fromUtf8("pushButtonOk"))
        self.horizontalLayout.addWidget(self.pushButtonOk)
        self.pushButtonCancel = QtGui.QPushButton(VolNameDialog)
        self.pushButtonCancel.setObjectName(_fromUtf8("pushButtonCancel"))
        self.horizontalLayout.addWidget(self.pushButtonCancel)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.retranslateUi(VolNameDialog)
        QtCore.QMetaObject.connectSlotsByName(VolNameDialog)

    def retranslateUi(self, VolNameDialog):
        VolNameDialog.setWindowTitle(_translate("VolNameDialog", "Dialog", None))
        self.pushButtonOk.setText(_translate("VolNameDialog", "OK", None))
        self.pushButtonCancel.setText(_translate("VolNameDialog", "Cancel", None))

