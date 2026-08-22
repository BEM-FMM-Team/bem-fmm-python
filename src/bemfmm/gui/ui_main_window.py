# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'gui.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDoubleSpinBox, QFrame,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QMainWindow,
    QMenu, QMenuBar, QPushButton, QScrollArea,
    QSizePolicy, QSlider, QSpacerItem, QStackedWidget,
    QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1012, 1052)
        self.actionLoad_Coil_Config = QAction(MainWindow)
        self.actionLoad_Coil_Config.setObjectName(u"actionLoad_Coil_Config")
        self.actionSave_Coil_Config = QAction(MainWindow)
        self.actionSave_Coil_Config.setObjectName(u"actionSave_Coil_Config")
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.action3D_viewer_Help = QAction(MainWindow)
        self.action3D_viewer_Help.setObjectName(u"action3D_viewer_Help")
        self.actionUndo = QAction(MainWindow)
        self.actionUndo.setObjectName(u"actionUndo")
        self.actionRedo = QAction(MainWindow)
        self.actionRedo.setObjectName(u"actionRedo")
        self.actionSphere_3L = QAction(MainWindow)
        self.actionSphere_3L.setObjectName(u"actionSphere_3L")
        self.actionPlot = QAction(MainWindow)
        self.actionPlot.setObjectName(u"actionPlot")
        self.actionDefault_TMS = QAction(MainWindow)
        self.actionDefault_TMS.setObjectName(u"actionDefault_TMS")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setEnabled(True)
        self.horizontalLayout_4 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.CameraXY = QPushButton(self.centralwidget)
        self.CameraXY.setObjectName(u"CameraXY")

        self.horizontalLayout_9.addWidget(self.CameraXY)

        self.CameraXZ = QPushButton(self.centralwidget)
        self.CameraXZ.setObjectName(u"CameraXZ")

        self.horizontalLayout_9.addWidget(self.CameraXZ)

        self.CameraYZ = QPushButton(self.centralwidget)
        self.CameraYZ.setObjectName(u"CameraYZ")

        self.horizontalLayout_9.addWidget(self.CameraYZ)


        self.verticalLayout_3.addLayout(self.horizontalLayout_9)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.PlanePlaceButton = QPushButton(self.centralwidget)
        self.PlanePlaceButton.setObjectName(u"PlanePlaceButton")

        self.gridLayout_2.addWidget(self.PlanePlaceButton, 1, 0, 1, 1)

        self.Load = QPushButton(self.centralwidget)
        self.Load.setObjectName(u"Load")

        self.gridLayout_2.addWidget(self.Load, 0, 1, 1, 1)

        self.Save = QPushButton(self.centralwidget)
        self.Save.setObjectName(u"Save")

        self.gridLayout_2.addWidget(self.Save, 0, 0, 1, 1)

        self.Run = QPushButton(self.centralwidget)
        self.Run.setObjectName(u"Run")

        self.gridLayout_2.addWidget(self.Run, 1, 1, 1, 1)

        self.Undo = QPushButton(self.centralwidget)
        self.Undo.setObjectName(u"Undo")

        self.gridLayout_2.addWidget(self.Undo, 2, 0, 1, 1)

        self.Redo = QPushButton(self.centralwidget)
        self.Redo.setObjectName(u"Redo")

        self.gridLayout_2.addWidget(self.Redo, 2, 1, 1, 1)


        self.verticalLayout_3.addLayout(self.gridLayout_2)

        self.loadTissueIndex = QPushButton(self.centralwidget)
        self.loadTissueIndex.setObjectName(u"loadTissueIndex")

        self.verticalLayout_3.addWidget(self.loadTissueIndex)

        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.MainGUI = QWidget()
        self.MainGUI.setObjectName(u"MainGUI")
        self.verticalLayout_4 = QVBoxLayout(self.MainGUI)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBox_3 = QGroupBox(self.MainGUI)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.verticalLayout_8 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.label_4 = QLabel(self.groupBox_3)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_12.addWidget(self.label_4)

        self.TypeDropdown = QComboBox(self.groupBox_3)
        self.TypeDropdown.setObjectName(u"TypeDropdown")

        self.horizontalLayout_12.addWidget(self.TypeDropdown)


        self.verticalLayout_8.addLayout(self.horizontalLayout_12)

        self.AddCoil = QPushButton(self.groupBox_3)
        self.AddCoil.setObjectName(u"AddCoil")

        self.verticalLayout_8.addWidget(self.AddCoil)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")

        self.verticalLayout_8.addLayout(self.horizontalLayout_5)


        self.verticalLayout_2.addWidget(self.groupBox_3)


        self.verticalLayout_4.addLayout(self.verticalLayout_2)

        self.groupBox_2 = QGroupBox(self.MainGUI)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_9 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.CoilList = QListWidget(self.groupBox_2)
        self.CoilList.setObjectName(u"CoilList")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.CoilList.sizePolicy().hasHeightForWidth())
        self.CoilList.setSizePolicy(sizePolicy)

        self.verticalLayout_7.addWidget(self.CoilList)


        self.verticalLayout_9.addLayout(self.verticalLayout_7)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_6 = QLabel(self.groupBox_2)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout_8.addWidget(self.label_6)

        self.CoilAlpha = QSlider(self.groupBox_2)
        self.CoilAlpha.setObjectName(u"CoilAlpha")
        self.CoilAlpha.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_8.addWidget(self.CoilAlpha)


        self.verticalLayout_9.addLayout(self.horizontalLayout_8)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.Edit = QPushButton(self.groupBox_2)
        self.Edit.setObjectName(u"Edit")

        self.gridLayout.addWidget(self.Edit, 0, 0, 1, 1)

        self.Delete = QPushButton(self.groupBox_2)
        self.Delete.setObjectName(u"Delete")

        self.gridLayout.addWidget(self.Delete, 0, 1, 1, 1)


        self.verticalLayout_9.addLayout(self.gridLayout)


        self.verticalLayout_4.addWidget(self.groupBox_2)

        self.groupBox = QGroupBox(self.MainGUI)
        self.groupBox.setObjectName(u"groupBox")
        self.horizontalLayout_7 = QHBoxLayout(self.groupBox)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.scrollArea = QScrollArea(self.groupBox)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 391, 124))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.horizontalLayout_7.addWidget(self.scrollArea)


        self.verticalLayout_4.addWidget(self.groupBox)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_2)

        self.stackedWidget.addWidget(self.MainGUI)
        self.EditGUI = QWidget()
        self.EditGUI.setObjectName(u"EditGUI")
        self.verticalLayout_11 = QVBoxLayout(self.EditGUI)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_2 = QLabel(self.EditGUI)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_6.addWidget(self.label_2)

        self.XSlider = QSlider(self.EditGUI)
        self.XSlider.setObjectName(u"XSlider")
        self.XSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_6.addWidget(self.XSlider)

        self.XEntry = QDoubleSpinBox(self.EditGUI)
        self.XEntry.setObjectName(u"XEntry")

        self.horizontalLayout_6.addWidget(self.XEntry)


        self.verticalLayout_5.addLayout(self.horizontalLayout_6)


        self.verticalLayout_11.addLayout(self.verticalLayout_5)

        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.label_10 = QLabel(self.EditGUI)
        self.label_10.setObjectName(u"label_10")

        self.horizontalLayout_14.addWidget(self.label_10)

        self.YSlider = QSlider(self.EditGUI)
        self.YSlider.setObjectName(u"YSlider")
        self.YSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_14.addWidget(self.YSlider)

        self.YEntry = QDoubleSpinBox(self.EditGUI)
        self.YEntry.setObjectName(u"YEntry")

        self.horizontalLayout_14.addWidget(self.YEntry)


        self.verticalLayout_11.addLayout(self.horizontalLayout_14)

        self.horizontalLayout_20 = QHBoxLayout()
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.label_16 = QLabel(self.EditGUI)
        self.label_16.setObjectName(u"label_16")

        self.horizontalLayout_20.addWidget(self.label_16)

        self.ZSlider = QSlider(self.EditGUI)
        self.ZSlider.setObjectName(u"ZSlider")
        self.ZSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_20.addWidget(self.ZSlider)

        self.ZEntry = QDoubleSpinBox(self.EditGUI)
        self.ZEntry.setObjectName(u"ZEntry")

        self.horizontalLayout_20.addWidget(self.ZEntry)


        self.verticalLayout_11.addLayout(self.horizontalLayout_20)

        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.label_11 = QLabel(self.EditGUI)
        self.label_11.setObjectName(u"label_11")

        self.horizontalLayout_15.addWidget(self.label_11)

        self.rXSlider = QSlider(self.EditGUI)
        self.rXSlider.setObjectName(u"rXSlider")
        self.rXSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_15.addWidget(self.rXSlider)

        self.rXEntry = QDoubleSpinBox(self.EditGUI)
        self.rXEntry.setObjectName(u"rXEntry")

        self.horizontalLayout_15.addWidget(self.rXEntry)


        self.verticalLayout_11.addLayout(self.horizontalLayout_15)

        self.horizontalLayout_16 = QHBoxLayout()
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.label_12 = QLabel(self.EditGUI)
        self.label_12.setObjectName(u"label_12")

        self.horizontalLayout_16.addWidget(self.label_12)

        self.rYSlider = QSlider(self.EditGUI)
        self.rYSlider.setObjectName(u"rYSlider")
        self.rYSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_16.addWidget(self.rYSlider)

        self.rYEntry = QDoubleSpinBox(self.EditGUI)
        self.rYEntry.setObjectName(u"rYEntry")

        self.horizontalLayout_16.addWidget(self.rYEntry)


        self.verticalLayout_11.addLayout(self.horizontalLayout_16)

        self.horizontalLayout_17 = QHBoxLayout()
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.label_13 = QLabel(self.EditGUI)
        self.label_13.setObjectName(u"label_13")

        self.horizontalLayout_17.addWidget(self.label_13)

        self.rZSlider = QSlider(self.EditGUI)
        self.rZSlider.setObjectName(u"rZSlider")
        self.rZSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_17.addWidget(self.rZSlider)

        self.rZEntry = QDoubleSpinBox(self.EditGUI)
        self.rZEntry.setObjectName(u"rZEntry")

        self.horizontalLayout_17.addWidget(self.rZEntry)


        self.verticalLayout_11.addLayout(self.horizontalLayout_17)

        self.horizontalLayout_19 = QHBoxLayout()
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.label_15 = QLabel(self.EditGUI)
        self.label_15.setObjectName(u"label_15")

        self.horizontalLayout_19.addWidget(self.label_15)

        self.TwistSlider = QSlider(self.EditGUI)
        self.TwistSlider.setObjectName(u"TwistSlider")
        self.TwistSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_19.addWidget(self.TwistSlider)

        self.TwistEntry = QDoubleSpinBox(self.EditGUI)
        self.TwistEntry.setObjectName(u"TwistEntry")

        self.horizontalLayout_19.addWidget(self.TwistEntry)


        self.verticalLayout_11.addLayout(self.horizontalLayout_19)

        self.horizontalLayout_18 = QHBoxLayout()
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.label_14 = QLabel(self.EditGUI)
        self.label_14.setObjectName(u"label_14")

        self.horizontalLayout_18.addWidget(self.label_14)

        self.dIdtEntry = QLineEdit(self.EditGUI)
        self.dIdtEntry.setObjectName(u"dIdtEntry")

        self.horizontalLayout_18.addWidget(self.dIdtEntry)


        self.verticalLayout_11.addLayout(self.horizontalLayout_18)

        self.AutoOrientButton = QPushButton(self.EditGUI)
        self.AutoOrientButton.setObjectName(u"AutoOrientButton")

        self.verticalLayout_11.addWidget(self.AutoOrientButton)

        self.FlipCoilButton = QPushButton(self.EditGUI)
        self.FlipCoilButton.setObjectName(u"FlipCoilButton")

        self.verticalLayout_11.addWidget(self.FlipCoilButton)

        self.WhiteMatterButton = QPushButton(self.EditGUI)
        self.WhiteMatterButton.setObjectName(u"WhiteMatterButton")

        self.verticalLayout_11.addWidget(self.WhiteMatterButton)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_3 = QLabel(self.EditGUI)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_2.addWidget(self.label_3)

        self.DistanceSlider = QSlider(self.EditGUI)
        self.DistanceSlider.setObjectName(u"DistanceSlider")
        self.DistanceSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_2.addWidget(self.DistanceSlider)

        self.DistanceEntry = QDoubleSpinBox(self.EditGUI)
        self.DistanceEntry.setObjectName(u"DistanceEntry")

        self.horizontalLayout_2.addWidget(self.DistanceEntry)


        self.verticalLayout_11.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.OKEdit = QPushButton(self.EditGUI)
        self.OKEdit.setObjectName(u"OKEdit")

        self.horizontalLayout.addWidget(self.OKEdit)

        self.CancelEdit = QPushButton(self.EditGUI)
        self.CancelEdit.setObjectName(u"CancelEdit")

        self.horizontalLayout.addWidget(self.CancelEdit)


        self.verticalLayout_11.addLayout(self.horizontalLayout)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_11.addItem(self.verticalSpacer_3)

        self.stackedWidget.addWidget(self.EditGUI)
        self.PlaneGUI = QWidget()
        self.PlaneGUI.setObjectName(u"PlaneGUI")
        self.verticalLayout_17 = QVBoxLayout(self.PlaneGUI)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.verticalLayout_16 = QVBoxLayout()
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.groupBox_4 = QGroupBox(self.PlaneGUI)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.verticalLayout_20 = QVBoxLayout(self.groupBox_4)
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.label_5 = QLabel(self.groupBox_4)
        self.label_5.setObjectName(u"label_5")

        self.verticalLayout_20.addWidget(self.label_5)

        self.verticalLayout_19 = QVBoxLayout()
        self.verticalLayout_19.setObjectName(u"verticalLayout_19")
        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.label_7 = QLabel(self.groupBox_4)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout_10.addWidget(self.label_7)

        self.XPlaneSlider = QSlider(self.groupBox_4)
        self.XPlaneSlider.setObjectName(u"XPlaneSlider")
        self.XPlaneSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_10.addWidget(self.XPlaneSlider)

        self.XPlaneSpin = QDoubleSpinBox(self.groupBox_4)
        self.XPlaneSpin.setObjectName(u"XPlaneSpin")

        self.horizontalLayout_10.addWidget(self.XPlaneSpin)


        self.verticalLayout_19.addLayout(self.horizontalLayout_10)


        self.verticalLayout_20.addLayout(self.verticalLayout_19)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.label_8 = QLabel(self.groupBox_4)
        self.label_8.setObjectName(u"label_8")

        self.horizontalLayout_11.addWidget(self.label_8)

        self.YPlaneSlider = QSlider(self.groupBox_4)
        self.YPlaneSlider.setObjectName(u"YPlaneSlider")
        self.YPlaneSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_11.addWidget(self.YPlaneSlider)

        self.YPlaneSpin = QDoubleSpinBox(self.groupBox_4)
        self.YPlaneSpin.setObjectName(u"YPlaneSpin")

        self.horizontalLayout_11.addWidget(self.YPlaneSpin)


        self.verticalLayout_20.addLayout(self.horizontalLayout_11)

        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.label_9 = QLabel(self.groupBox_4)
        self.label_9.setObjectName(u"label_9")

        self.horizontalLayout_13.addWidget(self.label_9)

        self.ZPlaneSlider = QSlider(self.groupBox_4)
        self.ZPlaneSlider.setObjectName(u"ZPlaneSlider")
        self.ZPlaneSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_13.addWidget(self.ZPlaneSlider)

        self.ZPlaneSpin = QDoubleSpinBox(self.groupBox_4)
        self.ZPlaneSpin.setObjectName(u"ZPlaneSpin")

        self.horizontalLayout_13.addWidget(self.ZPlaneSpin)


        self.verticalLayout_20.addLayout(self.horizontalLayout_13)


        self.verticalLayout_16.addWidget(self.groupBox_4)


        self.verticalLayout_17.addLayout(self.verticalLayout_16)

        self.horizontalLayout_21 = QHBoxLayout()
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.PlaneOK = QPushButton(self.PlaneGUI)
        self.PlaneOK.setObjectName(u"PlaneOK")

        self.horizontalLayout_21.addWidget(self.PlaneOK)


        self.verticalLayout_17.addLayout(self.horizontalLayout_21)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_17.addItem(self.verticalSpacer)

        self.stackedWidget.addWidget(self.PlaneGUI)

        self.verticalLayout_3.addWidget(self.stackedWidget)


        self.horizontalLayout_4.addLayout(self.verticalLayout_3)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.ViewPort = QFrame(self.centralwidget)
        self.ViewPort.setObjectName(u"ViewPort")
        self.ViewPort.setFrameShape(QFrame.Shape.StyledPanel)
        self.ViewPort.setFrameShadow(QFrame.Shadow.Raised)

        self.horizontalLayout_3.addWidget(self.ViewPort)


        self.horizontalLayout_4.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4.setStretch(1, 3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1012, 25))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        self.menuTests = QMenu(self.menubar)
        self.menuTests.setObjectName(u"menuTests")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuTests.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionLoad_Coil_Config)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave_Coil_Config)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuHelp.addAction(self.action3D_viewer_Help)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionAbout)
        self.menuTests.addAction(self.actionSphere_3L)
        self.menuTests.addAction(self.actionPlot)
        self.menuTests.addAction(self.actionDefault_TMS)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Coil Navigator", None))
        self.actionLoad_Coil_Config.setText(QCoreApplication.translate("MainWindow", u"Open Configuration", None))
        self.actionSave_Coil_Config.setText(QCoreApplication.translate("MainWindow", u"Save Configuration", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.action3D_viewer_Help.setText(QCoreApplication.translate("MainWindow", u"3D viewer Help", None))
        self.actionUndo.setText(QCoreApplication.translate("MainWindow", u"Undo", None))
        self.actionRedo.setText(QCoreApplication.translate("MainWindow", u"Redo", None))
        self.actionSphere_3L.setText(QCoreApplication.translate("MainWindow", u"Sphere 3L", None))
        self.actionPlot.setText(QCoreApplication.translate("MainWindow", u"Plot", None))
        self.actionDefault_TMS.setText(QCoreApplication.translate("MainWindow", u"Default TMS", None))
        self.CameraXY.setText(QCoreApplication.translate("MainWindow", u"XY", None))
        self.CameraXZ.setText(QCoreApplication.translate("MainWindow", u"XZ", None))
        self.CameraYZ.setText(QCoreApplication.translate("MainWindow", u"YZ", None))
        self.PlanePlaceButton.setText(QCoreApplication.translate("MainWindow", u"Slice Planes", None))
        self.Load.setText(QCoreApplication.translate("MainWindow", u"Load", None))
        self.Save.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.Run.setText(QCoreApplication.translate("MainWindow", u"Run TMS", None))
        self.Undo.setText(QCoreApplication.translate("MainWindow", u"Undo", None))
        self.Redo.setText(QCoreApplication.translate("MainWindow", u"Redo", None))
        self.loadTissueIndex.setText(QCoreApplication.translate("MainWindow", u"Load Custom Tissue Index", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"New Coil", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Type", None))
        self.AddCoil.setText(QCoreApplication.translate("MainWindow", u"Add Coil", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Edit Coils (double click to edit name)", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Coil Opacity", None))
        self.Edit.setText(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.Delete.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Head Model Opacity", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"X Position (mm)", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Y Position (mm)", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"Z Position (mm)", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"Rotation Around X (degrees)", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"Rotation Around Y (degrees)", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"Rotation Around Z (degrees)", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"Twist (degrees)", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"dIdt (A/?s)", None))
        self.AutoOrientButton.setText(QCoreApplication.translate("MainWindow", u"Auto Orient", None))
        self.FlipCoilButton.setText(QCoreApplication.translate("MainWindow", u"Flip Coil", None))
        self.WhiteMatterButton.setText(QCoreApplication.translate("MainWindow", u"Place With White Matter", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Skin Distance (mm)", None))
        self.OKEdit.setText(QCoreApplication.translate("MainWindow", u"OK", None))
        self.CancelEdit.setText(QCoreApplication.translate("MainWindow", u"Cancel", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("MainWindow", u"Move Slice Planes", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Places slice planes for imaging.", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"X Plane", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Y Plane", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Z Plane", None))
        self.PlaneOK.setText(QCoreApplication.translate("MainWindow", u"OK", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
        self.menuTests.setTitle(QCoreApplication.translate("MainWindow", u"Tests", None))
    # retranslateUi

