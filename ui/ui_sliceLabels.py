# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_sliceLabels.ui'
#
# Created: Sat Jan 16 10:54:50 2016
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

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(526, 81)
        self.verticalLayout = QtGui.QVBoxLayout(Form)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.labelVolume = QtGui.QLabel(Form)
        self.labelVolume.setObjectName(_fromUtf8("labelVolume"))
        self.verticalLayout.addWidget(self.labelVolume)
        self.labelData = QtGui.QLabel(Form)
        self.labelData.setObjectName(_fromUtf8("labelData"))
        self.verticalLayout.addWidget(self.labelData)
        self.labelVectors = QtGui.QLabel(Form)
        self.labelVectors.setObjectName(_fromUtf8("labelVectors"))
        self.verticalLayout.addWidget(self.labelVectors)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.labelVolume.setText(_translate("Form", "TextLabel", None))
        self.labelData.setText(_translate("Form", "TextLabel", None))
        self.labelVectors.setText(_translate("Form", "TextLabel", None))

