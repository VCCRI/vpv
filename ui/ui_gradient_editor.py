# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_gradient_editor.ui'
#
# Created: Fri Dec 16 16:28:59 2016
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

class Ui_GradientEditor(object):
    def setupUi(self, GradientEditor):
        GradientEditor.setObjectName(_fromUtf8("GradientEditor"))
        GradientEditor.resize(674, 147)
        self.verticalLayout_2 = QtGui.QVBoxLayout(GradientEditor)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(GradientEditor)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(GradientEditor)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.horizontalLayoutMain = QtGui.QHBoxLayout()
        self.horizontalLayoutMain.setObjectName(_fromUtf8("horizontalLayoutMain"))
        self.pushButtonCancel = QtGui.QPushButton(GradientEditor)
        self.pushButtonCancel.setObjectName(_fromUtf8("pushButtonCancel"))
        self.horizontalLayoutMain.addWidget(self.pushButtonCancel)
        self.pushButtonOk = QtGui.QPushButton(GradientEditor)
        self.pushButtonOk.setObjectName(_fromUtf8("pushButtonOk"))
        self.horizontalLayoutMain.addWidget(self.pushButtonOk)
        self.verticalLayout_2.addLayout(self.horizontalLayoutMain)

        self.retranslateUi(GradientEditor)
        QtCore.QMetaObject.connectSlotsByName(GradientEditor)

    def retranslateUi(self, GradientEditor):
        GradientEditor.setWindowTitle(_translate("GradientEditor", "Dialog", None))
        self.label.setText(_translate("GradientEditor", "positve LUT", None))
        self.label_2.setText(_translate("GradientEditor", "negative LUT", None))
        self.pushButtonCancel.setText(_translate("GradientEditor", "Cancel", None))
        self.pushButtonOk.setText(_translate("GradientEditor", "OK", None))

