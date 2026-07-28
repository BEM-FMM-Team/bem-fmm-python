# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'gui1.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
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
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenuBar,
    QPushButton,
    QSizePolicy,
    QSlider,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(995, 1046)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setEnabled(True)
        self.horizontalLayout_4 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName("stackedWidget")
        self.MainGUI = QWidget()
        self.MainGUI.setObjectName("MainGUI")
        self.verticalLayout_4 = QVBoxLayout(self.MainGUI)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox_3 = QGroupBox(self.MainGUI)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_8 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.label_4 = QLabel(self.groupBox_3)
        self.label_4.setObjectName("label_4")

        self.horizontalLayout_12.addWidget(self.label_4)

        self.TypeDropdown = QComboBox(self.groupBox_3)
        self.TypeDropdown.setObjectName("TypeDropdown")

        self.horizontalLayout_12.addWidget(self.TypeDropdown)

        self.verticalLayout_8.addLayout(self.horizontalLayout_12)

        self.AddCoil = QPushButton(self.groupBox_3)
        self.AddCoil.setObjectName("AddCoil")

        self.verticalLayout_8.addWidget(self.AddCoil)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label = QLabel(self.groupBox_3)
        self.label.setObjectName("label")

        self.horizontalLayout_5.addWidget(self.label)

        self.CustomCoilEntry = QLineEdit(self.groupBox_3)
        self.CustomCoilEntry.setObjectName("CustomCoilEntry")

        self.horizontalLayout_5.addWidget(self.CustomCoilEntry)

        self.verticalLayout_8.addLayout(self.horizontalLayout_5)

        self.AddCustomCoil = QPushButton(self.groupBox_3)
        self.AddCustomCoil.setObjectName("AddCustomCoil")

        self.verticalLayout_8.addWidget(self.AddCustomCoil)

        self.verticalLayout_2.addWidget(self.groupBox_3)

        self.verticalLayout_4.addLayout(self.verticalLayout_2)

        self.groupBox_2 = QGroupBox(self.MainGUI)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_9 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.CoilList = QListWidget(self.groupBox_2)
        self.CoilList.setObjectName("CoilList")
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.CoilList.sizePolicy().hasHeightForWidth())
        self.CoilList.setSizePolicy(sizePolicy)

        self.verticalLayout_7.addWidget(self.CoilList)

        self.verticalLayout_9.addLayout(self.verticalLayout_7)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label_6 = QLabel(self.groupBox_2)
        self.label_6.setObjectName("label_6")

        self.horizontalLayout_8.addWidget(self.label_6)

        self.CoilAlpha = QSlider(self.groupBox_2)
        self.CoilAlpha.setObjectName("CoilAlpha")
        self.CoilAlpha.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_8.addWidget(self.CoilAlpha)

        self.verticalLayout_9.addLayout(self.horizontalLayout_8)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.Redo = QPushButton(self.groupBox_2)
        self.Redo.setObjectName("Redo")

        self.gridLayout.addWidget(self.Redo, 3, 1, 1, 1)

        self.Edit = QPushButton(self.groupBox_2)
        self.Edit.setObjectName("Edit")

        self.gridLayout.addWidget(self.Edit, 0, 0, 1, 1)

        self.Undo = QPushButton(self.groupBox_2)
        self.Undo.setObjectName("Undo")

        self.gridLayout.addWidget(self.Undo, 3, 0, 1, 1)

        self.Delete = QPushButton(self.groupBox_2)
        self.Delete.setObjectName("Delete")

        self.gridLayout.addWidget(self.Delete, 0, 1, 1, 1)

        self.Save = QPushButton(self.groupBox_2)
        self.Save.setObjectName("Save")

        self.gridLayout.addWidget(self.Save, 2, 0, 1, 1)

        self.Load = QPushButton(self.groupBox_2)
        self.Load.setObjectName("Load")

        self.gridLayout.addWidget(self.Load, 2, 1, 1, 1)

        self.Run = QPushButton(self.groupBox_2)
        self.Run.setObjectName("Run")

        self.gridLayout.addWidget(self.Run, 1, 1, 1, 1)

        self.PlanePlaceButton = QPushButton(self.groupBox_2)
        self.PlanePlaceButton.setObjectName("PlanePlaceButton")

        self.gridLayout.addWidget(self.PlanePlaceButton, 1, 0, 1, 1)

        self.verticalLayout_9.addLayout(self.gridLayout)

        self.verticalLayout_4.addWidget(self.groupBox_2)

        self.groupBox = QGroupBox(self.MainGUI)
        self.groupBox.setObjectName("groupBox")
        self.formLayout = QFormLayout(self.groupBox)
        self.formLayout.setObjectName("formLayout")
        self.bone = QCheckBox(self.groupBox)
        self.bone.setObjectName("bone")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.bone)

        self.csf = QCheckBox(self.groupBox)
        self.csf.setObjectName("csf")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.csf)

        self.csfAlpha = QSlider(self.groupBox)
        self.csfAlpha.setObjectName("csfAlpha")
        self.csfAlpha.setOrientation(Qt.Orientation.Horizontal)

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.csfAlpha)

        self.skin = QCheckBox(self.groupBox)
        self.skin.setObjectName("skin")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.skin)

        self.skinAlpha = QSlider(self.groupBox)
        self.skinAlpha.setObjectName("skinAlpha")
        self.skinAlpha.setOrientation(Qt.Orientation.Horizontal)

        self.formLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.skinAlpha)

        self.wm = QCheckBox(self.groupBox)
        self.wm.setObjectName("wm")

        self.formLayout.setWidget(5, QFormLayout.ItemRole.LabelRole, self.wm)

        self.wmAlpha = QSlider(self.groupBox)
        self.wmAlpha.setObjectName("wmAlpha")
        self.wmAlpha.setOrientation(Qt.Orientation.Horizontal)

        self.formLayout.setWidget(5, QFormLayout.ItemRole.FieldRole, self.wmAlpha)

        self.ventricles = QCheckBox(self.groupBox)
        self.ventricles.setObjectName("ventricles")

        self.formLayout.setWidget(6, QFormLayout.ItemRole.LabelRole, self.ventricles)

        self.ventriclesAlpha = QSlider(self.groupBox)
        self.ventriclesAlpha.setObjectName("ventriclesAlpha")
        self.ventriclesAlpha.setOrientation(Qt.Orientation.Horizontal)

        self.formLayout.setWidget(
            6, QFormLayout.ItemRole.FieldRole, self.ventriclesAlpha
        )

        self.gm = QCheckBox(self.groupBox)
        self.gm.setObjectName("gm")

        self.formLayout.setWidget(7, QFormLayout.ItemRole.LabelRole, self.gm)

        self.gmAlpha = QSlider(self.groupBox)
        self.gmAlpha.setObjectName("gmAlpha")
        self.gmAlpha.setOrientation(Qt.Orientation.Horizontal)

        self.formLayout.setWidget(7, QFormLayout.ItemRole.FieldRole, self.gmAlpha)

        self.cerebellum = QCheckBox(self.groupBox)
        self.cerebellum.setObjectName("cerebellum")

        self.formLayout.setWidget(8, QFormLayout.ItemRole.LabelRole, self.cerebellum)

        self.cerebellumAlpha = QSlider(self.groupBox)
        self.cerebellumAlpha.setObjectName("cerebellumAlpha")
        self.cerebellumAlpha.setOrientation(Qt.Orientation.Horizontal)

        self.formLayout.setWidget(
            8, QFormLayout.ItemRole.FieldRole, self.cerebellumAlpha
        )

        self.boneAlpha = QSlider(self.groupBox)
        self.boneAlpha.setObjectName("boneAlpha")
        self.boneAlpha.setOrientation(Qt.Orientation.Horizontal)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.boneAlpha)

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

        self.XSlider = QSlider(self.EditGUI)
        self.XSlider.setObjectName("XSlider")
        self.XSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_6.addWidget(self.XSlider)

        self.XEntry = QDoubleSpinBox(self.EditGUI)
        self.XEntry.setObjectName("XEntry")

        self.horizontalLayout_6.addWidget(self.XEntry)

        self.verticalLayout_5.addLayout(self.horizontalLayout_6)

        self.verticalLayout_11.addLayout(self.verticalLayout_5)

        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.label_10 = QLabel(self.EditGUI)
        self.label_10.setObjectName("label_10")

        self.horizontalLayout_14.addWidget(self.label_10)

        self.YSlider = QSlider(self.EditGUI)
        self.YSlider.setObjectName("YSlider")
        self.YSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_14.addWidget(self.YSlider)

        self.YEntry = QDoubleSpinBox(self.EditGUI)
        self.YEntry.setObjectName("YEntry")

        self.horizontalLayout_14.addWidget(self.YEntry)

        self.verticalLayout_11.addLayout(self.horizontalLayout_14)

        self.horizontalLayout_20 = QHBoxLayout()
        self.horizontalLayout_20.setObjectName("horizontalLayout_20")
        self.label_16 = QLabel(self.EditGUI)
        self.label_16.setObjectName("label_16")

        self.horizontalLayout_20.addWidget(self.label_16)

        self.ZSlider = QSlider(self.EditGUI)
        self.ZSlider.setObjectName("ZSlider")
        self.ZSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_20.addWidget(self.ZSlider)

        self.ZEntry = QDoubleSpinBox(self.EditGUI)
        self.ZEntry.setObjectName("ZEntry")

        self.horizontalLayout_20.addWidget(self.ZEntry)

        self.verticalLayout_11.addLayout(self.horizontalLayout_20)

        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.label_11 = QLabel(self.EditGUI)
        self.label_11.setObjectName("label_11")

        self.horizontalLayout_15.addWidget(self.label_11)

        self.rXSlider = QSlider(self.EditGUI)
        self.rXSlider.setObjectName("rXSlider")
        self.rXSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_15.addWidget(self.rXSlider)

        self.rXEntry = QDoubleSpinBox(self.EditGUI)
        self.rXEntry.setObjectName("rXEntry")

        self.horizontalLayout_15.addWidget(self.rXEntry)

        self.verticalLayout_11.addLayout(self.horizontalLayout_15)

        self.horizontalLayout_16 = QHBoxLayout()
        self.horizontalLayout_16.setObjectName("horizontalLayout_16")
        self.label_12 = QLabel(self.EditGUI)
        self.label_12.setObjectName("label_12")

        self.horizontalLayout_16.addWidget(self.label_12)

        self.rYSlider = QSlider(self.EditGUI)
        self.rYSlider.setObjectName("rYSlider")
        self.rYSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_16.addWidget(self.rYSlider)

        self.rYEntry = QDoubleSpinBox(self.EditGUI)
        self.rYEntry.setObjectName("rYEntry")

        self.horizontalLayout_16.addWidget(self.rYEntry)

        self.verticalLayout_11.addLayout(self.horizontalLayout_16)

        self.horizontalLayout_17 = QHBoxLayout()
        self.horizontalLayout_17.setObjectName("horizontalLayout_17")
        self.label_13 = QLabel(self.EditGUI)
        self.label_13.setObjectName("label_13")

        self.horizontalLayout_17.addWidget(self.label_13)

        self.rZSlider = QSlider(self.EditGUI)
        self.rZSlider.setObjectName("rZSlider")
        self.rZSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_17.addWidget(self.rZSlider)

        self.rZEntry = QDoubleSpinBox(self.EditGUI)
        self.rZEntry.setObjectName("rZEntry")

        self.horizontalLayout_17.addWidget(self.rZEntry)

        self.verticalLayout_11.addLayout(self.horizontalLayout_17)

        self.horizontalLayout_19 = QHBoxLayout()
        self.horizontalLayout_19.setObjectName("horizontalLayout_19")
        self.label_15 = QLabel(self.EditGUI)
        self.label_15.setObjectName("label_15")

        self.horizontalLayout_19.addWidget(self.label_15)

        self.TwistSlider = QSlider(self.EditGUI)
        self.TwistSlider.setObjectName("TwistSlider")
        self.TwistSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_19.addWidget(self.TwistSlider)

        self.TwistEntry = QDoubleSpinBox(self.EditGUI)
        self.TwistEntry.setObjectName("TwistEntry")

        self.horizontalLayout_19.addWidget(self.TwistEntry)

        self.verticalLayout_11.addLayout(self.horizontalLayout_19)

        self.horizontalLayout_18 = QHBoxLayout()
        self.horizontalLayout_18.setObjectName("horizontalLayout_18")
        self.label_14 = QLabel(self.EditGUI)
        self.label_14.setObjectName("label_14")

        self.horizontalLayout_18.addWidget(self.label_14)

        self.dIdtEntry = QLineEdit(self.EditGUI)
        self.dIdtEntry.setObjectName("dIdtEntry")

        self.horizontalLayout_18.addWidget(self.dIdtEntry)

        self.verticalLayout_11.addLayout(self.horizontalLayout_18)

        self.AutoOrientButton = QPushButton(self.EditGUI)
        self.AutoOrientButton.setObjectName("AutoOrientButton")

        self.verticalLayout_11.addWidget(self.AutoOrientButton)

        self.FlipCoilButton = QPushButton(self.EditGUI)
        self.FlipCoilButton.setObjectName("FlipCoilButton")

        self.verticalLayout_11.addWidget(self.FlipCoilButton)

        self.WhiteMatterButton = QPushButton(self.EditGUI)
        self.WhiteMatterButton.setObjectName("WhiteMatterButton")

        self.verticalLayout_11.addWidget(self.WhiteMatterButton)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_3 = QLabel(self.EditGUI)
        self.label_3.setObjectName("label_3")

        self.horizontalLayout_2.addWidget(self.label_3)

        self.DistanceSlider = QSlider(self.EditGUI)
        self.DistanceSlider.setObjectName("DistanceSlider")
        self.DistanceSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_2.addWidget(self.DistanceSlider)

        self.DistanceEntry = QDoubleSpinBox(self.EditGUI)
        self.DistanceEntry.setObjectName("DistanceEntry")

        self.horizontalLayout_2.addWidget(self.DistanceEntry)

        self.verticalLayout_11.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.OKEdit = QPushButton(self.EditGUI)
        self.OKEdit.setObjectName("OKEdit")

        self.horizontalLayout.addWidget(self.OKEdit)

        self.CancelEdit = QPushButton(self.EditGUI)
        self.CancelEdit.setObjectName("CancelEdit")

        self.horizontalLayout.addWidget(self.CancelEdit)

        self.verticalLayout_11.addLayout(self.horizontalLayout)

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

        self.stackedWidget.addWidget(self.PlaneGUI)

        self.verticalLayout_3.addWidget(self.stackedWidget)

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
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 995, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "Coil Navigator", None)
        )
        self.groupBox_3.setTitle(
            QCoreApplication.translate("MainWindow", "New Coils", None)
        )
        self.label_4.setText(QCoreApplication.translate("MainWindow", "Type", None))
        self.AddCoil.setText(QCoreApplication.translate("MainWindow", "Add Coil", None))
        self.label.setText(QCoreApplication.translate("MainWindow", "Custom", None))
        self.AddCustomCoil.setText(
            QCoreApplication.translate("MainWindow", "Add Custom Coil", None)
        )
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", "Edit", None))
        self.label_6.setText(
            QCoreApplication.translate("MainWindow", "Coil Opacity", None)
        )
        self.Redo.setText(QCoreApplication.translate("MainWindow", "Redo", None))
        self.Edit.setText(QCoreApplication.translate("MainWindow", "Edit", None))
        self.Undo.setText(QCoreApplication.translate("MainWindow", "Undo", None))
        self.Delete.setText(QCoreApplication.translate("MainWindow", "Delete", None))
        self.Save.setText(QCoreApplication.translate("MainWindow", "Save", None))
        self.Load.setText(QCoreApplication.translate("MainWindow", "Load", None))
        self.Run.setText(QCoreApplication.translate("MainWindow", "Run", None))
        self.PlanePlaceButton.setText(
            QCoreApplication.translate("MainWindow", "Slice Planes", None)
        )
        self.groupBox.setTitle(
            QCoreApplication.translate("MainWindow", "Head Model", None)
        )
        self.bone.setText(QCoreApplication.translate("MainWindow", "Bone", None))
        self.csf.setText(QCoreApplication.translate("MainWindow", "CSF", None))
        self.skin.setText(QCoreApplication.translate("MainWindow", "Skin", None))
        self.wm.setText(QCoreApplication.translate("MainWindow", "WM", None))
        self.ventricles.setText(
            QCoreApplication.translate("MainWindow", "Ventricles", None)
        )
        self.gm.setText(QCoreApplication.translate("MainWindow", "GM", None))
        self.cerebellum.setText(
            QCoreApplication.translate("MainWindow", "Cerebellum", None)
        )
        self.label_2.setText(
            QCoreApplication.translate("MainWindow", "X Position (mm)", None)
        )
        self.label_10.setText(
            QCoreApplication.translate("MainWindow", "Y Position (mm)", None)
        )
        self.label_16.setText(
            QCoreApplication.translate("MainWindow", "Z Position (mm)", None)
        )
        self.label_11.setText(
            QCoreApplication.translate(
                "MainWindow", "Rotation Around X (degrees)", None
            )
        )
        self.label_12.setText(
            QCoreApplication.translate(
                "MainWindow", "Rotation Around Y (degrees)", None
            )
        )
        self.label_13.setText(
            QCoreApplication.translate(
                "MainWindow", "Rotation Around Z (degrees)", None
            )
        )
        self.label_15.setText(
            QCoreApplication.translate("MainWindow", "Twist (degrees)", None)
        )
        self.label_14.setText(
            QCoreApplication.translate("MainWindow", "dIdt (A/\u03bcs)", None)
        )
        self.AutoOrientButton.setText(
            QCoreApplication.translate("MainWindow", "Auto Orient", None)
        )
        self.FlipCoilButton.setText(
            QCoreApplication.translate("MainWindow", "Flip Coil", None)
        )
        self.WhiteMatterButton.setText(
            QCoreApplication.translate("MainWindow", "Place With White Matter", None)
        )
        self.label_3.setText(
            QCoreApplication.translate("MainWindow", "Skin Distance (mm)", None)
        )
        self.OKEdit.setText(QCoreApplication.translate("MainWindow", "OK", None))
        self.CancelEdit.setText(
            QCoreApplication.translate("MainWindow", "Cancel", None)
        )
        self.groupBox_4.setTitle(
            QCoreApplication.translate("MainWindow", "GroupBox", None)
        )
        self.label_5.setText(
            QCoreApplication.translate(
                "MainWindow", "Places slice planes for imaging.", None
            )
        )
        self.label_7.setText(QCoreApplication.translate("MainWindow", "X Plane", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", "Y Plane", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", "Z Plane", None))
        self.PlaneOK.setText(QCoreApplication.translate("MainWindow", "OK", None))
        self.CameraXY.setText(QCoreApplication.translate("MainWindow", "XY", None))
        self.CameraXZ.setText(QCoreApplication.translate("MainWindow", "XZ", None))
        self.CameraYZ.setText(QCoreApplication.translate("MainWindow", "YZ", None))

    # retranslateUi
