# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_dataviewer.ui'
#
# Created: Thu Oct  9 13:50:07 2014
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_DataViewer(object):
    def setupUi(self, DataViewer):
        DataViewer.setObjectName(_fromUtf8("DataViewer"))
        DataViewer.resize(430, 282)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.verticalLayout = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayoutInfo = QtGui.QGridLayout()
        self.gridLayoutInfo.setObjectName(_fromUtf8("gridLayoutInfo"))
        self.verticalLayout.addLayout(self.gridLayoutInfo)
        self.plotWidget = PlotWidget(self.dockWidgetContents)
        self.plotWidget.setObjectName(_fromUtf8("plotWidget"))
        self.verticalLayout.addWidget(self.plotWidget)
        DataViewer.setWidget(self.dockWidgetContents)

        self.retranslateUi(DataViewer)
        QtCore.QMetaObject.connectSlotsByName(DataViewer)

    def retranslateUi(self, DataViewer):
        DataViewer.setWindowTitle(QtGui.QApplication.translate("DataViewer", "DockWidget", None, QtGui.QApplication.UnicodeUTF8))

from pyqtgraph import PlotWidget
