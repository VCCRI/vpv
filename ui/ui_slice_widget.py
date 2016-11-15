# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_slice_widget.ui'
#
# Created: Wed Sep  7 09:44:11 2016
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

class Ui_SliceWidget(object):
    def setupUi(self, SliceWidget):
        SliceWidget.setObjectName(_fromUtf8("SliceWidget"))
        SliceWidget.resize(554, 642)
        self.gridLayout = QtGui.QGridLayout(SliceWidget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.graphicsView = GraphicsLayoutWidget(SliceWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.graphicsView.sizePolicy().hasHeightForWidth())
        self.graphicsView.setSizePolicy(sizePolicy)
        self.graphicsView.setObjectName(_fromUtf8("graphicsView"))
        self.verticalLayout.addWidget(self.graphicsView)
        self.controlsWidget = QtGui.QWidget(SliceWidget)
        self.controlsWidget.setMaximumSize(QtCore.QSize(16777215, 25))
        self.controlsWidget.setObjectName(_fromUtf8("controlsWidget"))
        self.layout_index_slider = QtGui.QHBoxLayout(self.controlsWidget)
        self.layout_index_slider.setContentsMargins(20, 2, 15, 2)
        self.layout_index_slider.setObjectName(_fromUtf8("layout_index_slider"))
        self.labelImageSeriesNumber = QtGui.QLabel(self.controlsWidget)
        self.labelImageSeriesNumber.setText(_fromUtf8(""))
        self.labelImageSeriesNumber.setObjectName(_fromUtf8("labelImageSeriesNumber"))
        self.layout_index_slider.addWidget(self.labelImageSeriesNumber)
        self.seriesSlider = QtGui.QSlider(self.controlsWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.seriesSlider.sizePolicy().hasHeightForWidth())
        self.seriesSlider.setSizePolicy(sizePolicy)
        self.seriesSlider.setMinimumSize(QtCore.QSize(200, 0))
        self.seriesSlider.setOrientation(QtCore.Qt.Horizontal)
        self.seriesSlider.setInvertedAppearance(False)
        self.seriesSlider.setInvertedControls(False)
        self.seriesSlider.setTickPosition(QtGui.QSlider.TicksAbove)
        self.seriesSlider.setTickInterval(1)
        self.seriesSlider.setObjectName(_fromUtf8("seriesSlider"))
        self.layout_index_slider.addWidget(self.seriesSlider)
        self.labelSliceNumber = QtGui.QLabel(self.controlsWidget)
        self.labelSliceNumber.setText(_fromUtf8(""))
        self.labelSliceNumber.setObjectName(_fromUtf8("labelSliceNumber"))
        self.layout_index_slider.addWidget(self.labelSliceNumber)
        self.sliderSlice = QtGui.QSlider(self.controlsWidget)
        self.sliderSlice.setMaximumSize(QtCore.QSize(16777215, 10))
        self.sliderSlice.setOrientation(QtCore.Qt.Horizontal)
        self.sliderSlice.setTickInterval(0)
        self.sliderSlice.setObjectName(_fromUtf8("sliderSlice"))
        self.layout_index_slider.addWidget(self.sliderSlice)
        self.pushButtonScrollLeft = QtGui.QPushButton(self.controlsWidget)
        self.pushButtonScrollLeft.setStyleSheet(_fromUtf8("border:none"))
        self.pushButtonScrollLeft.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/scroll_arrow_left.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonScrollLeft.setIcon(icon)
        self.pushButtonScrollLeft.setIconSize(QtCore.QSize(15, 15))
        self.pushButtonScrollLeft.setObjectName(_fromUtf8("pushButtonScrollLeft"))
        self.layout_index_slider.addWidget(self.pushButtonScrollLeft)
        self.pushButtonScrollRight = QtGui.QPushButton(self.controlsWidget)
        self.pushButtonScrollRight.setStyleSheet(_fromUtf8("border:none"))
        self.pushButtonScrollRight.setText(_fromUtf8(""))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/scroll_arrow_right.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/scroll_arrow_right_active.png")), QtGui.QIcon.Active, QtGui.QIcon.On)
        self.pushButtonScrollRight.setIcon(icon1)
        self.pushButtonScrollRight.setIconSize(QtCore.QSize(15, 15))
        self.pushButtonScrollRight.setObjectName(_fromUtf8("pushButtonScrollRight"))
        self.layout_index_slider.addWidget(self.pushButtonScrollRight)
        self.pushButtonManageVolumes = QtGui.QPushButton(self.controlsWidget)
        self.pushButtonManageVolumes.setStyleSheet(_fromUtf8("border:none"))
        self.pushButtonManageVolumes.setText(_fromUtf8(""))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/settings.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonManageVolumes.setIcon(icon2)
        self.pushButtonManageVolumes.setIconSize(QtCore.QSize(15, 15))
        self.pushButtonManageVolumes.setFlat(False)
        self.pushButtonManageVolumes.setObjectName(_fromUtf8("pushButtonManageVolumes"))
        self.layout_index_slider.addWidget(self.pushButtonManageVolumes)
        self.verticalLayout.addWidget(self.controlsWidget)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.retranslateUi(SliceWidget)
        QtCore.QMetaObject.connectSlotsByName(SliceWidget)

    def retranslateUi(self, SliceWidget):
        SliceWidget.setWindowTitle(_translate("SliceWidget", "Form", None))
        self.labelSliceNumber.setAccessibleName(_translate("SliceWidget", "sliceNumber", None))

from pyqtgraph import GraphicsLayoutWidget
import resources_rc
