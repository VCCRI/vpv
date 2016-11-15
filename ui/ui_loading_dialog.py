# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_loading_dialog.ui'
#
# Created: Fri Sep  2 14:43:40 2016
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

class Ui_Loading(object):
    def setupUi(self, Loading):
        Loading.setObjectName(_fromUtf8("Loading"))
        Loading.resize(501, 133)
        self.gridLayout = QtGui.QGridLayout(Loading)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.labelMessage1 = QtGui.QLabel(Loading)
        self.labelMessage1.setText(_fromUtf8(""))
        self.labelMessage1.setObjectName(_fromUtf8("labelMessage1"))
        self.gridLayout.addWidget(self.labelMessage1, 0, 0, 1, 1)
        self.labelMessage2 = QtGui.QLabel(Loading)
        self.labelMessage2.setText(_fromUtf8(""))
        self.labelMessage2.setObjectName(_fromUtf8("labelMessage2"))
        self.gridLayout.addWidget(self.labelMessage2, 1, 0, 1, 1)

        self.retranslateUi(Loading)
        QtCore.QMetaObject.connectSlotsByName(Loading)

    def retranslateUi(self, Loading):
        Loading.setWindowTitle(_translate("Loading", "Dialog", None))

