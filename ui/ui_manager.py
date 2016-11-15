# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_manager.ui'
#
# Created: Fri Sep 16 09:04:15 2016
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

class Ui_ManageViews(object):
    def setupUi(self, ManageViews):
        ManageViews.setObjectName(_fromUtf8("ManageViews"))
        ManageViews.resize(758, 834)
        ManageViews.setFeatures(QtGui.QDockWidget.AllDockWidgetFeatures)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.tabWidget = QtGui.QTabWidget(self.dockWidgetContents)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.verticalLayout_6.addWidget(self.tabWidget)
        ManageViews.setWidget(self.dockWidgetContents)

        self.retranslateUi(ManageViews)
        QtCore.QMetaObject.connectSlotsByName(ManageViews)

    def retranslateUi(self, ManageViews):
        ManageViews.setWindowTitle(_translate("ManageViews", "Data manager", None))

