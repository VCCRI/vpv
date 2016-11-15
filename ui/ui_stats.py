# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_stats.ui'
#
# Created: Wed Sep 24 20:50:52 2014
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

class Ui_Stats(object):
    def setupUi(self, Stats):
        Stats.setObjectName(_fromUtf8("Stats"))
        Stats.resize(493, 150)
        self.verticalLayout_3 = QtGui.QVBoxLayout(Stats)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(Stats)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(Stats)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)
        self.label_3 = QtGui.QLabel(Stats)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 0, 2, 1, 1)
        self.comboBoxBaseline = QtGui.QComboBox(Stats)
        self.comboBoxBaseline.setObjectName(_fromUtf8("comboBoxBaseline"))
        self.gridLayout.addWidget(self.comboBoxBaseline, 1, 0, 1, 1)
        self.comboBoxTestData = QtGui.QComboBox(Stats)
        self.comboBoxTestData.setObjectName(_fromUtf8("comboBoxTestData"))
        self.gridLayout.addWidget(self.comboBoxTestData, 1, 1, 1, 1)
        self.lineEditOutputName = QtGui.QLineEdit(Stats)
        self.lineEditOutputName.setObjectName(_fromUtf8("lineEditOutputName"))
        self.gridLayout.addWidget(self.lineEditOutputName, 1, 2, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_4 = QtGui.QLabel(Stats)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout.addWidget(self.label_4)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.comboBoxStats = QtGui.QComboBox(Stats)
        self.comboBoxStats.setObjectName(_fromUtf8("comboBoxStats"))
        self.horizontalLayout.addWidget(self.comboBoxStats)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButtonCancel = QtGui.QPushButton(Stats)
        self.pushButtonCancel.setObjectName(_fromUtf8("pushButtonCancel"))
        self.horizontalLayout.addWidget(self.pushButtonCancel)
        self.pushButtonGo = QtGui.QPushButton(Stats)
        self.pushButtonGo.setObjectName(_fromUtf8("pushButtonGo"))
        self.horizontalLayout.addWidget(self.pushButtonGo)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)

        self.retranslateUi(Stats)
        QtCore.QMetaObject.connectSlotsByName(Stats)

    def retranslateUi(self, Stats):
        Stats.setWindowTitle(_translate("Stats", "Dialog", None))
        self.label.setText(_translate("Stats", "Baseline", None))
        self.label_2.setText(_translate("Stats", "Test data", None))
        self.label_3.setText(_translate("Stats", "Output data name", None))
        self.label_4.setText(_translate("Stats", "Test", None))
        self.pushButtonCancel.setText(_translate("Stats", "Cancel", None))
        self.pushButtonGo.setText(_translate("Stats", "Go", None))

