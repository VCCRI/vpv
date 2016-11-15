# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_layer_widget.ui'
#
# Created: Wed Oct  1 13:14:25 2014
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Layer(object):
    def setupUi(self, Layer):
        Layer.setObjectName(_fromUtf8("Layer"))
        Layer.resize(1030, 51)
        self.horizontalLayout = QtGui.QHBoxLayout(Layer)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.comboBoxVol = QtGui.QComboBox(Layer)
        self.comboBoxVol.setObjectName(_fromUtf8("comboBoxVol"))
        self.gridLayout.addWidget(self.comboBoxVol, 0, 0, 1, 1)
        self.comboBoxLut = QtGui.QComboBox(Layer)
        self.comboBoxLut.setObjectName(_fromUtf8("comboBoxLut"))
        self.gridLayout.addWidget(self.comboBoxLut, 0, 1, 1, 1)
        self.horizontalLayout.addLayout(self.gridLayout)

        self.retranslateUi(Layer)
        QtCore.QMetaObject.connectSlotsByName(Layer)

    def retranslateUi(self, Layer):
        Layer.setWindowTitle(QtGui.QApplication.translate("Layer", "Form", None, QtGui.QApplication.UnicodeUTF8))

