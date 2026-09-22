# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'electrode_gui.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
    Qt,
)
from PySide6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QApplication,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMenuBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QSpacerItem,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)


class Ui_ElectrodeMainWindow(object):
    def setupUi(self, ElectrodeMainWindow):
        if not ElectrodeMainWindow.objectName():
            ElectrodeMainWindow.setObjectName("ElectrodeMainWindow")
        ElectrodeMainWindow.resize(1135, 909)
        self.actionLoad_Electrode_Config = QAction(ElectrodeMainWindow)
        self.actionLoad_Electrode_Config.setObjectName("actionLoad_Electrode_Config")
        self.actionSave_Electrode_Config = QAction(ElectrodeMainWindow)
        self.actionSave_Electrode_Config.setObjectName("actionSave_Electrode_Config")
        self.actionExit = QAction(ElectrodeMainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionAbout = QAction(ElectrodeMainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.action3D_viewer_Help = QAction(ElectrodeMainWindow)
        self.action3D_viewer_Help.setObjectName("action3D_viewer_Help")
        self.actionUndo = QAction(ElectrodeMainWindow)
        self.actionUndo.setObjectName("actionUndo")
        self.actionRedo = QAction(ElectrodeMainWindow)
        self.actionRedo.setObjectName("actionRedo")
        self.centralwidget = QWidget(ElectrodeMainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setEnabled(True)
        self.horizontalLayout_4 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.CameraXY = QPushButton(self.centralwidget)
        self.CameraXY.setObjectName("CameraXY")

        self.horizontalLayout_9.addWidget(self.CameraXY)

        self.CameraXZ = QPushButton(self.centralwidget)
        self.CameraXZ.setObjectName("CameraXZ")

        self.horizontalLayout_9.addWidget(self.CameraXZ)

        self.CameraYZ = QPushButton(self.centralwidget)
        self.CameraYZ.setObjectName("CameraYZ")

        self.horizontalLayout_9.addWidget(self.CameraYZ)

        self.verticalLayout_3.addLayout(self.horizontalLayout_9)

        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName("stackedWidget")
        self.MainGUI = QWidget()
        self.MainGUI.setObjectName("MainGUI")
        self.verticalLayout_4 = QVBoxLayout(self.MainGUI)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.loadTissueIndex = QPushButton(self.MainGUI)
        self.loadTissueIndex.setObjectName("loadTissueIndex")

        self.verticalLayout_4.addWidget(self.loadTissueIndex)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.PlanePlaceButton = QPushButton(self.MainGUI)
        self.PlanePlaceButton.setObjectName("PlanePlaceButton")

        self.gridLayout_2.addWidget(self.PlanePlaceButton, 2, 0, 1, 1)

        self.Save = QPushButton(self.MainGUI)
        self.Save.setObjectName("Save")

        self.gridLayout_2.addWidget(self.Save, 1, 0, 1, 1)

        self.Run = QPushButton(self.MainGUI)
        self.Run.setObjectName("Run")

        self.gridLayout_2.addWidget(self.Run, 2, 1, 1, 1)

        self.Load = QPushButton(self.MainGUI)
        self.Load.setObjectName("Load")

        self.gridLayout_2.addWidget(self.Load, 1, 1, 1, 1)

        self.Undo = QPushButton(self.MainGUI)
        self.Undo.setObjectName("Undo")

        self.gridLayout_2.addWidget(self.Undo, 3, 0, 1, 1)

        self.Redo = QPushButton(self.MainGUI)
        self.Redo.setObjectName("Redo")

        self.gridLayout_2.addWidget(self.Redo, 3, 1, 1, 1)

        self.verticalLayout_4.addLayout(self.gridLayout_2)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox_3 = QGroupBox(self.MainGUI)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_8 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.AddElectrode = QPushButton(self.groupBox_3)
        self.AddElectrode.setObjectName("AddElectrode")

        self.verticalLayout_8.addWidget(self.AddElectrode)

        self.verticalLayout_2.addWidget(self.groupBox_3)

        self.verticalLayout_4.addLayout(self.verticalLayout_2)

        self.groupBox_2 = QGroupBox(self.MainGUI)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_9 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.ElectrodeList = QListWidget(self.groupBox_2)
        self.ElectrodeList.setObjectName("ElectrodeList")
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.ElectrodeList.sizePolicy().hasHeightForWidth()
        )
        self.ElectrodeList.setSizePolicy(sizePolicy)

        self.verticalLayout_7.addWidget(self.ElectrodeList)

        self.verticalLayout_9.addLayout(self.verticalLayout_7)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label_6 = QLabel(self.groupBox_2)
        self.label_6.setObjectName("label_6")

        self.horizontalLayout_8.addWidget(self.label_6)

        self.ElectrodeAlpha = QSlider(self.groupBox_2)
        self.ElectrodeAlpha.setObjectName("ElectrodeAlpha")
        self.ElectrodeAlpha.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_8.addWidget(self.ElectrodeAlpha)

        self.verticalLayout_9.addLayout(self.horizontalLayout_8)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.Edit = QPushButton(self.groupBox_2)
        self.Edit.setObjectName("Edit")

        self.gridLayout.addWidget(self.Edit, 0, 0, 1, 1)

        self.Delete = QPushButton(self.groupBox_2)
        self.Delete.setObjectName("Delete")

        self.gridLayout.addWidget(self.Delete, 0, 1, 1, 1)

        self.verticalLayout_9.addLayout(self.gridLayout)

        self.verticalLayout_4.addWidget(self.groupBox_2)

        self.groupBox = QGroupBox(self.MainGUI)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_7 = QHBoxLayout(self.groupBox)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.scrollArea = QScrollArea(self.groupBox)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 391, 160))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.horizontalLayout_7.addWidget(self.scrollArea)

        self.verticalLayout_4.addWidget(self.groupBox)

        self.stackedWidget.addWidget(self.MainGUI)
        self.EditGUI = QWidget()
        self.EditGUI.setObjectName("EditGUI")
        self.verticalLayout_11 = QVBoxLayout(self.EditGUI)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_2 = QLabel(self.EditGUI)
        self.label_2.setObjectName("label_2")

        self.horizontalLayout_6.addWidget(self.label_2)

        self.RadiusSlider = QSlider(self.EditGUI)
        self.RadiusSlider.setObjectName("RadiusSlider")
        self.RadiusSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_6.addWidget(self.RadiusSlider)

        self.RadiusEntry = QDoubleSpinBox(self.EditGUI)
        self.RadiusEntry.setObjectName("RadiusEntry")

        self.horizontalLayout_6.addWidget(self.RadiusEntry)

        self.verticalLayout_5.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_18 = QHBoxLayout()
        self.horizontalLayout_18.setObjectName("horizontalLayout_18")
        self.label_14 = QLabel(self.EditGUI)
        self.label_14.setObjectName("label_14")

        self.horizontalLayout_18.addWidget(self.label_14)

        self.VoltageEntry = QLineEdit(self.EditGUI)
        self.VoltageEntry.setObjectName("VoltageEntry")

        self.horizontalLayout_18.addWidget(self.VoltageEntry)

        self.verticalLayout_5.addLayout(self.horizontalLayout_18)

        self.verticalLayout_11.addLayout(self.verticalLayout_5)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.OKEdit = QPushButton(self.EditGUI)
        self.OKEdit.setObjectName("OKEdit")

        self.horizontalLayout.addWidget(self.OKEdit)

        self.CancelEdit = QPushButton(self.EditGUI)
        self.CancelEdit.setObjectName("CancelEdit")

        self.horizontalLayout.addWidget(self.CancelEdit)

        self.verticalLayout_11.addLayout(self.horizontalLayout)

        self.verticalSpacer_3 = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.verticalLayout_11.addItem(self.verticalSpacer_3)

        self.stackedWidget.addWidget(self.EditGUI)
        self.PlaneGUI = QWidget()
        self.PlaneGUI.setObjectName("PlaneGUI")
        self.verticalLayout_17 = QVBoxLayout(self.PlaneGUI)
        self.verticalLayout_17.setObjectName("verticalLayout_17")
        self.verticalLayout_16 = QVBoxLayout()
        self.verticalLayout_16.setObjectName("verticalLayout_16")
        self.groupBox_4 = QGroupBox(self.PlaneGUI)
        self.groupBox_4.setObjectName("groupBox_4")
        self.verticalLayout_20 = QVBoxLayout(self.groupBox_4)
        self.verticalLayout_20.setObjectName("verticalLayout_20")
        self.label_5 = QLabel(self.groupBox_4)
        self.label_5.setObjectName("label_5")

        self.verticalLayout_20.addWidget(self.label_5)

        self.verticalLayout_19 = QVBoxLayout()
        self.verticalLayout_19.setObjectName("verticalLayout_19")
        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.label_7 = QLabel(self.groupBox_4)
        self.label_7.setObjectName("label_7")

        self.horizontalLayout_10.addWidget(self.label_7)

        self.XPlaneSlider = QSlider(self.groupBox_4)
        self.XPlaneSlider.setObjectName("XPlaneSlider")
        self.XPlaneSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_10.addWidget(self.XPlaneSlider)

        self.XPlaneSpin = QDoubleSpinBox(self.groupBox_4)
        self.XPlaneSpin.setObjectName("XPlaneSpin")

        self.horizontalLayout_10.addWidget(self.XPlaneSpin)

        self.verticalLayout_19.addLayout(self.horizontalLayout_10)

        self.verticalLayout_20.addLayout(self.verticalLayout_19)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.label_8 = QLabel(self.groupBox_4)
        self.label_8.setObjectName("label_8")

        self.horizontalLayout_11.addWidget(self.label_8)

        self.YPlaneSlider = QSlider(self.groupBox_4)
        self.YPlaneSlider.setObjectName("YPlaneSlider")
        self.YPlaneSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_11.addWidget(self.YPlaneSlider)

        self.YPlaneSpin = QDoubleSpinBox(self.groupBox_4)
        self.YPlaneSpin.setObjectName("YPlaneSpin")

        self.horizontalLayout_11.addWidget(self.YPlaneSpin)

        self.verticalLayout_20.addLayout(self.horizontalLayout_11)

        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.label_9 = QLabel(self.groupBox_4)
        self.label_9.setObjectName("label_9")

        self.horizontalLayout_13.addWidget(self.label_9)

        self.ZPlaneSlider = QSlider(self.groupBox_4)
        self.ZPlaneSlider.setObjectName("ZPlaneSlider")
        self.ZPlaneSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_13.addWidget(self.ZPlaneSlider)

        self.ZPlaneSpin = QDoubleSpinBox(self.groupBox_4)
        self.ZPlaneSpin.setObjectName("ZPlaneSpin")

        self.horizontalLayout_13.addWidget(self.ZPlaneSpin)

        self.verticalLayout_20.addLayout(self.horizontalLayout_13)

        self.verticalLayout_16.addWidget(self.groupBox_4)

        self.verticalLayout_17.addLayout(self.verticalLayout_16)

        self.horizontalLayout_21 = QHBoxLayout()
        self.horizontalLayout_21.setObjectName("horizontalLayout_21")
        self.PlaneOK = QPushButton(self.PlaneGUI)
        self.PlaneOK.setObjectName("PlaneOK")

        self.horizontalLayout_21.addWidget(self.PlaneOK)

        self.verticalLayout_17.addLayout(self.horizontalLayout_21)

        self.verticalSpacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.verticalLayout_17.addItem(self.verticalSpacer)

        self.stackedWidget.addWidget(self.PlaneGUI)

        self.verticalLayout_3.addWidget(self.stackedWidget)

        self.horizontalLayout_4.addLayout(self.verticalLayout_3)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.ViewPort = QFrame(self.centralwidget)
        self.ViewPort.setObjectName("ViewPort")
        self.ViewPort.setFrameShape(QFrame.Shape.StyledPanel)
        self.ViewPort.setFrameShadow(QFrame.Shadow.Raised)

        self.horizontalLayout_3.addWidget(self.ViewPort)

        self.horizontalLayout_4.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4.setStretch(1, 3)
        ElectrodeMainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(ElectrodeMainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 1135, 25))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        ElectrodeMainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(ElectrodeMainWindow)
        self.statusbar.setObjectName("statusbar")
        ElectrodeMainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionLoad_Electrode_Config)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave_Electrode_Config)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuHelp.addAction(self.action3D_viewer_Help)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionAbout)

        self.retranslateUi(ElectrodeMainWindow)

        self.stackedWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(ElectrodeMainWindow)

    # setupUi

    def retranslateUi(self, ElectrodeMainWindow):
        ElectrodeMainWindow.setWindowTitle(
            QCoreApplication.translate(
                "ElectrodeMainWindow", "Electrode Navigator", None
            )
        )
        self.actionLoad_Electrode_Config.setText(
            QCoreApplication.translate(
                "ElectrodeMainWindow", "Open Configuration", None
            )
        )
        self.actionSave_Electrode_Config.setText(
            QCoreApplication.translate(
                "ElectrodeMainWindow", "Save Configuration", None
            )
        )
        self.actionExit.setText(
            QCoreApplication.translate("ElectrodeMainWindow", "Exit", None)
        )
        self.actionAbout.setText(
            QCoreApplication.translate("ElectrodeMainWindow", "About", None)
        )
        self.action3D_viewer_Help.setText(
            QCoreApplication.translate("ElectrodeMainWindow", "3D viewer Help", None)
        )
        self.actionUndo.setText(
            QCoreApplication.translate("ElectrodeMainWindow", "Undo", None)
        )
        self.actionRedo.setText(
            QCoreApplication.translate("ElectrodeMainWindow", "Redo", None)
        )
        self.CameraXY.setText(
            QCoreApplication.translate("ElectrodeMainWindow", "XY", None)
        )
        self.CameraXZ.setText(
            QCoreApplication.translate("ElectrodeMainWindow", "XZ", None)
        )
        self.CameraYZ.setText(
            QCoreApplication.translate("ElectrodeMainWindow", "YZ", None)
        )
        self.loadTissueIndex.setText(
            QCoreApplication.translate(
                "ElectrodeMainWindow", "Load Custom Tissue Index", None
            )
        )
        self.PlanePlaceButton.setText(
            QCoreApplication.translate("ElectrodeMainWindow", "Slice Planes", None)
        )
        self.Save.setText(
            QCoreApplication.translate("ElectrodeMainWindow", "Save", None)
        )
        self.Run.setText(
            QCoreApplication.translate("ElectrodeMainWindow", "Run tDCS", None)
        )
        self.Load.setText(
            QCoreApplication.translate("ElectrodeMainWindow", "Load", None)
        )
        self.Undo.setText(
            QCoreApplication.translate("ElectrodeMainWindow", "Undo", None)
        )
        self.Redo.setText(
            QCoreApplication.translate("ElectrodeMainWindow", "Redo", None)
        )
        self.groupBox_3.setTitle(
            QCoreApplication.translate("ElectrodeMainWindow", "New Electrode", None)
        )
        self.AddElectrode.setText(
            QCoreApplication.translate("ElectrodeMainWindow", "Add Electrode", None)
        )
        self.groupBox_2.setTitle(
            QCoreApplication.translate(
                "ElectrodeMainWindow",
                "Edit Electrodes (double click to edit name)",
                None,
            )
        )
        self.label_6.setText(
            QCoreApplication.translate("ElectrodeMainWindow", "Electrode Opacity", None)
        )
        self.Edit.setText(
            QCoreApplication.translate("ElectrodeMainWindow", "Edit", None)
        )
        self.Delete.setText(
            QCoreApplication.translate("ElectrodeMainWindow", "Delete", None)
        )
        self.groupBox.setTitle(
            QCoreApplication.translate(
                "ElectrodeMainWindow", "Head Model Opacity", None
            )
        )
        self.label_2.setText(
            QCoreApplication.translate("ElectrodeMainWindow", "Radius (mm)", None)
        )
        self.label_14.setText(
            QCoreApplication.translate("ElectrodeMainWindow", "Voltage (V)", None)
        )
        self.OKEdit.setText(
            QCoreApplication.translate("ElectrodeMainWindow", "OK", None)
        )
        self.CancelEdit.setText(
            QCoreApplication.translate("ElectrodeMainWindow", "Cancel", None)
        )
        self.groupBox_4.setTitle(
            QCoreApplication.translate("ElectrodeMainWindow", "Move Slice Planes", None)
        )
        self.label_5.setText(
            QCoreApplication.translate(
                "ElectrodeMainWindow", "Places slice planes for imaging.", None
            )
        )
        self.label_7.setText(
            QCoreApplication.translate("ElectrodeMainWindow", "X Plane", None)
        )
        self.label_8.setText(
            QCoreApplication.translate("ElectrodeMainWindow", "Y Plane", None)
        )
        self.label_9.setText(
            QCoreApplication.translate("ElectrodeMainWindow", "Z Plane", None)
        )
        self.PlaneOK.setText(
            QCoreApplication.translate("ElectrodeMainWindow", "OK", None)
        )
        self.menuFile.setTitle(
            QCoreApplication.translate("ElectrodeMainWindow", "File", None)
        )
        self.menuHelp.setTitle(
            QCoreApplication.translate("ElectrodeMainWindow", "Help", None)
        )

    # retranslateUi
