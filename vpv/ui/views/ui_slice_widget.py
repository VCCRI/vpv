# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_slice_widget.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SliceWidget(object):
    def setupUi(self, SliceWidget):
        SliceWidget.setObjectName("SliceWidget")
        SliceWidget.resize(554, 642)
        self.gridLayout = QtWidgets.QGridLayout(SliceWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.graphicsView = GraphicsLayoutWidget(SliceWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.graphicsView.sizePolicy().hasHeightForWidth())
        self.graphicsView.setSizePolicy(sizePolicy)
        self.graphicsView.setObjectName("graphicsView")
        self.verticalLayout.addWidget(self.graphicsView)
        self.controlsWidget = QtWidgets.QWidget(SliceWidget)
        self.controlsWidget.setMaximumSize(QtCore.QSize(16777215, 25))
        self.controlsWidget.setObjectName("controlsWidget")
        self.layout_index_slider = QtWidgets.QHBoxLayout(self.controlsWidget)
        self.layout_index_slider.setContentsMargins(20, 2, 15, 2)
        self.layout_index_slider.setObjectName("layout_index_slider")
        self.labelImageSeriesNumber = QtWidgets.QLabel(self.controlsWidget)
        self.labelImageSeriesNumber.setText("")
        self.labelImageSeriesNumber.setObjectName("labelImageSeriesNumber")
        self.layout_index_slider.addWidget(self.labelImageSeriesNumber)
        self.seriesSlider = QtWidgets.QSlider(self.controlsWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.seriesSlider.sizePolicy().hasHeightForWidth())
        self.seriesSlider.setSizePolicy(sizePolicy)
        self.seriesSlider.setMinimumSize(QtCore.QSize(200, 0))
        self.seriesSlider.setOrientation(QtCore.Qt.Horizontal)
        self.seriesSlider.setInvertedAppearance(False)
        self.seriesSlider.setInvertedControls(False)
        self.seriesSlider.setTickPosition(QtWidgets.QSlider.TicksAbove)
        self.seriesSlider.setTickInterval(1)
        self.seriesSlider.setObjectName("seriesSlider")
        self.layout_index_slider.addWidget(self.seriesSlider)
        self.labelSliceNumber = QtWidgets.QLabel(self.controlsWidget)
        self.labelSliceNumber.setText("")
        self.labelSliceNumber.setObjectName("labelSliceNumber")
        self.layout_index_slider.addWidget(self.labelSliceNumber)
        self.sliderSlice = QtWidgets.QSlider(self.controlsWidget)
        self.sliderSlice.setMaximumSize(QtCore.QSize(16777215, 10))
        self.sliderSlice.setOrientation(QtCore.Qt.Horizontal)
        self.sliderSlice.setTickInterval(0)
        self.sliderSlice.setObjectName("sliderSlice")
        self.layout_index_slider.addWidget(self.sliderSlice)
        self.pushButtonScrollLeft = QtWidgets.QPushButton(self.controlsWidget)
        self.pushButtonScrollLeft.setStyleSheet("border:none")
        self.pushButtonScrollLeft.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/scroll_arrow_left.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonScrollLeft.setIcon(icon)
        self.pushButtonScrollLeft.setIconSize(QtCore.QSize(15, 15))
        self.pushButtonScrollLeft.setObjectName("pushButtonScrollLeft")
        self.layout_index_slider.addWidget(self.pushButtonScrollLeft)
        self.pushButtonScrollRight = QtWidgets.QPushButton(self.controlsWidget)
        self.pushButtonScrollRight.setStyleSheet("border:none")
        self.pushButtonScrollRight.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/scroll_arrow_right.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon1.addPixmap(QtGui.QPixmap(":/icons/scroll_arrow_right_active.png"), QtGui.QIcon.Active, QtGui.QIcon.On)
        self.pushButtonScrollRight.setIcon(icon1)
        self.pushButtonScrollRight.setIconSize(QtCore.QSize(15, 15))
        self.pushButtonScrollRight.setObjectName("pushButtonScrollRight")
        self.layout_index_slider.addWidget(self.pushButtonScrollRight)
        self.pushButtonManageVolumes = QtWidgets.QPushButton(self.controlsWidget)
        self.pushButtonManageVolumes.setStyleSheet("border:none")
        self.pushButtonManageVolumes.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/settings.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonManageVolumes.setIcon(icon2)
        self.pushButtonManageVolumes.setIconSize(QtCore.QSize(15, 15))
        self.pushButtonManageVolumes.setFlat(False)
        self.pushButtonManageVolumes.setObjectName("pushButtonManageVolumes")
        self.layout_index_slider.addWidget(self.pushButtonManageVolumes)
        self.verticalLayout.addWidget(self.controlsWidget)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.retranslateUi(SliceWidget)
        QtCore.QMetaObject.connectSlotsByName(SliceWidget)

    def retranslateUi(self, SliceWidget):
        _translate = QtCore.QCoreApplication.translate
        SliceWidget.setWindowTitle(_translate("SliceWidget", "Form"))
        self.labelSliceNumber.setAccessibleName(_translate("SliceWidget", "sliceNumber"))
from pyqtgraph import GraphicsLayoutWidget
from . import resources_rc
