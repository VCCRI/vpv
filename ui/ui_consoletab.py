# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_consoletab.ui'
#
# Created: Sun Sep 25 11:57:58 2016
#      by: PyQt4 UI code generator 4.11.3
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

class Ui_console(object):
    def setupUi(self, console):
        console.setObjectName(_fromUtf8("console"))
        console.resize(761, 737)
        self.verticalLayout = QtGui.QVBoxLayout(console)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setObjectName(_fromUtf8("mainLayout"))
        self.verticalLayout.addLayout(self.mainLayout)

        self.retranslateUi(console)
        QtCore.QMetaObject.connectSlotsByName(console)

    def retranslateUi(self, console):
        console.setWindowTitle(_translate("console", "Form", None))

import resources_rc
