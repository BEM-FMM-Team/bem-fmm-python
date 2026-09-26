# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
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
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMenuBar,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QSpacerItem,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1440, 900)
        self.actionNewSetup = QAction(MainWindow)
        self.actionNewSetup.setObjectName("actionNewSetup")
        self.actionOpenSetup = QAction(MainWindow)
        self.actionOpenSetup.setObjectName("actionOpenSetup")
        self.actionSaveSetup = QAction(MainWindow)
        self.actionSaveSetup.setObjectName("actionSaveSetup")
        self.actionSaveSetupAs = QAction(MainWindow)
        self.actionSaveSetupAs.setObjectName("actionSaveSetupAs")
        self.actionOpenIndex = QAction(MainWindow)
        self.actionOpenIndex.setObjectName("actionOpenIndex")
        self.actionSaveIndexAs = QAction(MainWindow)
        self.actionSaveIndexAs.setObjectName("actionSaveIndexAs")
        self.actionOpenResult = QAction(MainWindow)
        self.actionOpenResult.setObjectName("actionOpenResult")
        self.actionExportMatlab = QAction(MainWindow)
        self.actionExportMatlab.setObjectName("actionExportMatlab")
        self.actionQuit = QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")
        self.actionUndo = QAction(MainWindow)
        self.actionUndo.setObjectName("actionUndo")
        self.actionRedo = QAction(MainWindow)
        self.actionRedo.setObjectName("actionRedo")
        self.actionViewXY = QAction(MainWindow)
        self.actionViewXY.setObjectName("actionViewXY")
        self.actionViewXZ = QAction(MainWindow)
        self.actionViewXZ.setObjectName("actionViewXZ")
        self.actionViewYZ = QAction(MainWindow)
        self.actionViewYZ.setObjectName("actionViewYZ")
        self.actionResetView = QAction(MainWindow)
        self.actionResetView.setObjectName("actionResetView")
        self.actionRun = QAction(MainWindow)
        self.actionRun.setObjectName("actionRun")
        self.actionSphere = QAction(MainWindow)
        self.actionSphere.setObjectName("actionSphere")
        self.actionDipole = QAction(MainWindow)
        self.actionDipole.setObjectName("actionDipole")
        self.actionViewerHelp = QAction(MainWindow)
        self.actionViewerHelp.setObjectName("actionViewerHelp")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralLayout = QHBoxLayout(self.centralwidget)
        self.centralLayout.setObjectName("centralLayout")
        self.centralLayout.setContentsMargins(0, 0, 0, 0)
        self.splitter = QSplitter(self.centralwidget)
        self.splitter.setObjectName("splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.sideTabs = QTabWidget(self.splitter)
        self.sideTabs.setObjectName("sideTabs")
        self.sideTabs.setMinimumSize(QSize(400, 0))
        self.sideTabs.setMaximumSize(QSize(560, 16777215))
        self.sideTabs.setDocumentMode(True)
        self.modelTab = QWidget()
        self.modelTab.setObjectName("modelTab")
        self.modelLayout = QVBoxLayout(self.modelTab)
        self.modelLayout.setObjectName("modelLayout")
        self.indexGroup = QGroupBox(self.modelTab)
        self.indexGroup.setObjectName("indexGroup")
        self.indexLayout = QGridLayout(self.indexGroup)
        self.indexLayout.setObjectName("indexLayout")
        self.indexPath = QLineEdit(self.indexGroup)
        self.indexPath.setObjectName("indexPath")
        self.indexPath.setReadOnly(True)

        self.indexLayout.addWidget(self.indexPath, 0, 0, 1, 1)

        self.openIndexButton = QPushButton(self.indexGroup)
        self.openIndexButton.setObjectName("openIndexButton")

        self.indexLayout.addWidget(self.openIndexButton, 0, 1, 1, 1)

        self.modelSummary = QLabel(self.indexGroup)
        self.modelSummary.setObjectName("modelSummary")
        self.modelSummary.setWordWrap(True)

        self.indexLayout.addWidget(self.modelSummary, 1, 0, 1, 2)

        self.modelLayout.addWidget(self.indexGroup)

        self.tissueGroup = QGroupBox(self.modelTab)
        self.tissueGroup.setObjectName("tissueGroup")
        self.tissueLayout = QVBoxLayout(self.tissueGroup)
        self.tissueLayout.setObjectName("tissueLayout")
        self.tissueHint = QLabel(self.tissueGroup)
        self.tissueHint.setObjectName("tissueHint")
        self.tissueHint.setWordWrap(True)

        self.tissueLayout.addWidget(self.tissueHint)

        self.tissueTable = QTableWidget(self.tissueGroup)
        if self.tissueTable.columnCount() < 4:
            self.tissueTable.setColumnCount(4)
        __qtablewidgetitem = QTableWidgetItem()
        self.tissueTable.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tissueTable.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tissueTable.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tissueTable.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        self.tissueTable.setObjectName("tissueTable")
        self.tissueTable.setAlternatingRowColors(True)
        self.tissueTable.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.tissueTable.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.tissueTable.horizontalHeader().setStretchLastSection(True)
        self.tissueTable.verticalHeader().setVisible(False)

        self.tissueLayout.addWidget(self.tissueTable)

        self.tissueButtons = QHBoxLayout()
        self.tissueButtons.setObjectName("tissueButtons")
        self.addTissueButton = QPushButton(self.tissueGroup)
        self.addTissueButton.setObjectName("addTissueButton")

        self.tissueButtons.addWidget(self.addTissueButton)

        self.removeTissueButton = QPushButton(self.tissueGroup)
        self.removeTissueButton.setObjectName("removeTissueButton")

        self.tissueButtons.addWidget(self.removeTissueButton)

        self.tissueButtonSpacer = QSpacerItem(
            20, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.tissueButtons.addItem(self.tissueButtonSpacer)

        self.saveIndexButton = QPushButton(self.tissueGroup)
        self.saveIndexButton.setObjectName("saveIndexButton")

        self.tissueButtons.addWidget(self.saveIndexButton)

        self.applyIndexButton = QPushButton(self.tissueGroup)
        self.applyIndexButton.setObjectName("applyIndexButton")
        self.applyIndexButton.setEnabled(False)

        self.tissueButtons.addWidget(self.applyIndexButton)

        self.tissueLayout.addLayout(self.tissueButtons)

        self.modelLayout.addWidget(self.tissueGroup)

        self.displayGroup = QGroupBox(self.modelTab)
        self.displayGroup.setObjectName("displayGroup")
        self.displayGroupLayout = QVBoxLayout(self.displayGroup)
        self.displayGroupLayout.setObjectName("displayGroupLayout")
        self.displayScroll = QScrollArea(self.displayGroup)
        self.displayScroll.setObjectName("displayScroll")
        self.displayScroll.setFrameShape(QFrame.Shape.NoFrame)
        self.displayScroll.setWidgetResizable(True)
        self.displayContents = QWidget()
        self.displayContents.setObjectName("displayContents")
        self.displayLayout = QGridLayout(self.displayContents)
        self.displayLayout.setObjectName("displayLayout")
        self.displayScroll.setWidget(self.displayContents)

        self.displayGroupLayout.addWidget(self.displayScroll)

        self.modelLayout.addWidget(self.displayGroup)

        self.sideTabs.addTab(self.modelTab, "")
        self.stimulationTab = QWidget()
        self.stimulationTab.setObjectName("stimulationTab")
        self.stimulationLayout = QVBoxLayout(self.stimulationTab)
        self.stimulationLayout.setObjectName("stimulationLayout")
        self.modeGroup = QGroupBox(self.stimulationTab)
        self.modeGroup.setObjectName("modeGroup")
        self.modeLayout = QGridLayout(self.modeGroup)
        self.modeLayout.setObjectName("modeLayout")
        self.tmsRadio = QRadioButton(self.modeGroup)
        self.tmsRadio.setObjectName("tmsRadio")
        self.tmsRadio.setChecked(True)

        self.modeLayout.addWidget(self.tmsRadio, 0, 0, 1, 1)

        self.tdcsRadio = QRadioButton(self.modeGroup)
        self.tdcsRadio.setObjectName("tdcsRadio")

        self.modeLayout.addWidget(self.tdcsRadio, 0, 1, 1, 1)

        self.surfaceLabel = QLabel(self.modeGroup)
        self.surfaceLabel.setObjectName("surfaceLabel")

        self.modeLayout.addWidget(self.surfaceLabel, 1, 0, 1, 1)

        self.surfaceCombo = QComboBox(self.modeGroup)
        self.surfaceCombo.setObjectName("surfaceCombo")

        self.modeLayout.addWidget(self.surfaceCombo, 1, 1, 1, 1)

        self.stimulationLayout.addWidget(self.modeGroup)

        self.stimStack = QStackedWidget(self.stimulationTab)
        self.stimStack.setObjectName("stimStack")
        self.coilPage = QWidget()
        self.coilPage.setObjectName("coilPage")
        self.coilPageLayout = QVBoxLayout(self.coilPage)
        self.coilPageLayout.setObjectName("coilPageLayout")
        self.coilPageLayout.setContentsMargins(0, -1, 0, -1)
        self.addCoilLayout = QHBoxLayout()
        self.addCoilLayout.setObjectName("addCoilLayout")
        self.coilTypeCombo = QComboBox(self.coilPage)
        self.coilTypeCombo.setObjectName("coilTypeCombo")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.coilTypeCombo.sizePolicy().hasHeightForWidth()
        )
        self.coilTypeCombo.setSizePolicy(sizePolicy)

        self.addCoilLayout.addWidget(self.coilTypeCombo)

        self.addCoilButton = QPushButton(self.coilPage)
        self.addCoilButton.setObjectName("addCoilButton")

        self.addCoilLayout.addWidget(self.addCoilButton)

        self.coilPageLayout.addLayout(self.addCoilLayout)

        self.coilList = QListWidget(self.coilPage)
        self.coilList.setObjectName("coilList")
        self.coilList.setMaximumSize(QSize(16777215, 140))
        self.coilList.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.EditKeyPressed
        )

        self.coilPageLayout.addWidget(self.coilList)

        self.coilListButtons = QHBoxLayout()
        self.coilListButtons.setObjectName("coilListButtons")
        self.deleteCoilButton = QPushButton(self.coilPage)
        self.deleteCoilButton.setObjectName("deleteCoilButton")

        self.coilListButtons.addWidget(self.deleteCoilButton)

        self.coilListSpacer = QSpacerItem(
            20, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.coilListButtons.addItem(self.coilListSpacer)

        self.coilAlphaLabel = QLabel(self.coilPage)
        self.coilAlphaLabel.setObjectName("coilAlphaLabel")

        self.coilListButtons.addWidget(self.coilAlphaLabel)

        self.coilAlpha = QSlider(self.coilPage)
        self.coilAlpha.setObjectName("coilAlpha")
        self.coilAlpha.setMaximumSize(QSize(120, 16777215))
        self.coilAlpha.setMaximum(100)
        self.coilAlpha.setValue(100)
        self.coilAlpha.setOrientation(Qt.Orientation.Horizontal)

        self.coilListButtons.addWidget(self.coilAlpha)

        self.coilPageLayout.addLayout(self.coilListButtons)

        self.coilEditor = QGroupBox(self.coilPage)
        self.coilEditor.setObjectName("coilEditor")
        self.coilEditor.setEnabled(False)
        self.coilEditorLayout = QFormLayout(self.coilEditor)
        self.coilEditorLayout.setObjectName("coilEditorLayout")
        self.coilPositionLabel = QLabel(self.coilEditor)
        self.coilPositionLabel.setObjectName("coilPositionLabel")

        self.coilEditorLayout.setWidget(
            0, QFormLayout.ItemRole.LabelRole, self.coilPositionLabel
        )

        self.coilPositionLayout = QHBoxLayout()
        self.coilPositionLayout.setObjectName("coilPositionLayout")
        self.coilX = QDoubleSpinBox(self.coilEditor)
        self.coilX.setObjectName("coilX")

        self.coilPositionLayout.addWidget(self.coilX)

        self.coilY = QDoubleSpinBox(self.coilEditor)
        self.coilY.setObjectName("coilY")

        self.coilPositionLayout.addWidget(self.coilY)

        self.coilZ = QDoubleSpinBox(self.coilEditor)
        self.coilZ.setObjectName("coilZ")

        self.coilPositionLayout.addWidget(self.coilZ)

        self.coilEditorLayout.setLayout(
            0, QFormLayout.ItemRole.FieldRole, self.coilPositionLayout
        )

        self.coilRotationLabel = QLabel(self.coilEditor)
        self.coilRotationLabel.setObjectName("coilRotationLabel")

        self.coilEditorLayout.setWidget(
            1, QFormLayout.ItemRole.LabelRole, self.coilRotationLabel
        )

        self.coilRotationLayout = QHBoxLayout()
        self.coilRotationLayout.setObjectName("coilRotationLayout")
        self.coilRX = QDoubleSpinBox(self.coilEditor)
        self.coilRX.setObjectName("coilRX")

        self.coilRotationLayout.addWidget(self.coilRX)

        self.coilRY = QDoubleSpinBox(self.coilEditor)
        self.coilRY.setObjectName("coilRY")

        self.coilRotationLayout.addWidget(self.coilRY)

        self.coilRZ = QDoubleSpinBox(self.coilEditor)
        self.coilRZ.setObjectName("coilRZ")

        self.coilRotationLayout.addWidget(self.coilRZ)

        self.coilEditorLayout.setLayout(
            1, QFormLayout.ItemRole.FieldRole, self.coilRotationLayout
        )

        self.coilTwistLabel = QLabel(self.coilEditor)
        self.coilTwistLabel.setObjectName("coilTwistLabel")

        self.coilEditorLayout.setWidget(
            2, QFormLayout.ItemRole.LabelRole, self.coilTwistLabel
        )

        self.coilTwist = QDoubleSpinBox(self.coilEditor)
        self.coilTwist.setObjectName("coilTwist")

        self.coilEditorLayout.setWidget(
            2, QFormLayout.ItemRole.FieldRole, self.coilTwist
        )

        self.coilDistanceLabel = QLabel(self.coilEditor)
        self.coilDistanceLabel.setObjectName("coilDistanceLabel")

        self.coilEditorLayout.setWidget(
            3, QFormLayout.ItemRole.LabelRole, self.coilDistanceLabel
        )

        self.coilDistance = QDoubleSpinBox(self.coilEditor)
        self.coilDistance.setObjectName("coilDistance")

        self.coilEditorLayout.setWidget(
            3, QFormLayout.ItemRole.FieldRole, self.coilDistance
        )

        self.coilDIdtLabel = QLabel(self.coilEditor)
        self.coilDIdtLabel.setObjectName("coilDIdtLabel")

        self.coilEditorLayout.setWidget(
            4, QFormLayout.ItemRole.LabelRole, self.coilDIdtLabel
        )

        self.coilDIdt = QDoubleSpinBox(self.coilEditor)
        self.coilDIdt.setObjectName("coilDIdt")

        self.coilEditorLayout.setWidget(
            4, QFormLayout.ItemRole.FieldRole, self.coilDIdt
        )

        self.coilActionLayout = QHBoxLayout()
        self.coilActionLayout.setObjectName("coilActionLayout")
        self.autoOrientButton = QPushButton(self.coilEditor)
        self.autoOrientButton.setObjectName("autoOrientButton")

        self.coilActionLayout.addWidget(self.autoOrientButton)

        self.flipButton = QPushButton(self.coilEditor)
        self.flipButton.setObjectName("flipButton")

        self.coilActionLayout.addWidget(self.flipButton)

        self.moveCoilButton = QPushButton(self.coilEditor)
        self.moveCoilButton.setObjectName("moveCoilButton")
        self.moveCoilButton.setCheckable(True)

        self.coilActionLayout.addWidget(self.moveCoilButton)

        self.coilEditorLayout.setLayout(
            5, QFormLayout.ItemRole.SpanningRole, self.coilActionLayout
        )

        self.targetLabel = QLabel(self.coilEditor)
        self.targetLabel.setObjectName("targetLabel")

        self.coilEditorLayout.setWidget(
            6, QFormLayout.ItemRole.LabelRole, self.targetLabel
        )

        self.targetLayout = QHBoxLayout()
        self.targetLayout.setObjectName("targetLayout")
        self.targetCombo = QComboBox(self.coilEditor)
        self.targetCombo.setObjectName("targetCombo")
        sizePolicy.setHeightForWidth(self.targetCombo.sizePolicy().hasHeightForWidth())
        self.targetCombo.setSizePolicy(sizePolicy)

        self.targetLayout.addWidget(self.targetCombo)

        self.aimButton = QPushButton(self.coilEditor)
        self.aimButton.setObjectName("aimButton")
        self.aimButton.setCheckable(True)

        self.targetLayout.addWidget(self.aimButton)

        self.coilEditorLayout.setLayout(
            6, QFormLayout.ItemRole.FieldRole, self.targetLayout
        )

        self.coilPageLayout.addWidget(self.coilEditor)

        self.stimStack.addWidget(self.coilPage)
        self.electrodePage = QWidget()
        self.electrodePage.setObjectName("electrodePage")
        self.electrodePageLayout = QVBoxLayout(self.electrodePage)
        self.electrodePageLayout.setObjectName("electrodePageLayout")
        self.electrodePageLayout.setContentsMargins(0, -1, 0, -1)
        self.addElectrodeLayout = QHBoxLayout()
        self.addElectrodeLayout.setObjectName("addElectrodeLayout")
        self.electrodeHint = QLabel(self.electrodePage)
        self.electrodeHint.setObjectName("electrodeHint")

        self.addElectrodeLayout.addWidget(self.electrodeHint)

        self.addElectrodeSpacer = QSpacerItem(
            20, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.addElectrodeLayout.addItem(self.addElectrodeSpacer)

        self.addElectrodeButton = QPushButton(self.electrodePage)
        self.addElectrodeButton.setObjectName("addElectrodeButton")

        self.addElectrodeLayout.addWidget(self.addElectrodeButton)

        self.electrodePageLayout.addLayout(self.addElectrodeLayout)

        self.electrodeList = QListWidget(self.electrodePage)
        self.electrodeList.setObjectName("electrodeList")
        self.electrodeList.setMaximumSize(QSize(16777215, 140))
        self.electrodeList.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.EditKeyPressed
        )

        self.electrodePageLayout.addWidget(self.electrodeList)

        self.electrodeListButtons = QHBoxLayout()
        self.electrodeListButtons.setObjectName("electrodeListButtons")
        self.deleteElectrodeButton = QPushButton(self.electrodePage)
        self.deleteElectrodeButton.setObjectName("deleteElectrodeButton")

        self.electrodeListButtons.addWidget(self.deleteElectrodeButton)

        self.electrodeListSpacer = QSpacerItem(
            20, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.electrodeListButtons.addItem(self.electrodeListSpacer)

        self.electrodeAlphaLabel = QLabel(self.electrodePage)
        self.electrodeAlphaLabel.setObjectName("electrodeAlphaLabel")

        self.electrodeListButtons.addWidget(self.electrodeAlphaLabel)

        self.electrodeAlpha = QSlider(self.electrodePage)
        self.electrodeAlpha.setObjectName("electrodeAlpha")
        self.electrodeAlpha.setMaximumSize(QSize(120, 16777215))
        self.electrodeAlpha.setMaximum(100)
        self.electrodeAlpha.setValue(100)
        self.electrodeAlpha.setOrientation(Qt.Orientation.Horizontal)

        self.electrodeListButtons.addWidget(self.electrodeAlpha)

        self.electrodePageLayout.addLayout(self.electrodeListButtons)

        self.electrodeEditor = QGroupBox(self.electrodePage)
        self.electrodeEditor.setObjectName("electrodeEditor")
        self.electrodeEditor.setEnabled(False)
        self.electrodeEditorLayout = QFormLayout(self.electrodeEditor)
        self.electrodeEditorLayout.setObjectName("electrodeEditorLayout")
        self.electrodePositionLabel = QLabel(self.electrodeEditor)
        self.electrodePositionLabel.setObjectName("electrodePositionLabel")

        self.electrodeEditorLayout.setWidget(
            0, QFormLayout.ItemRole.LabelRole, self.electrodePositionLabel
        )

        self.electrodePositionLayout = QHBoxLayout()
        self.electrodePositionLayout.setObjectName("electrodePositionLayout")
        self.electrodeX = QDoubleSpinBox(self.electrodeEditor)
        self.electrodeX.setObjectName("electrodeX")

        self.electrodePositionLayout.addWidget(self.electrodeX)

        self.electrodeY = QDoubleSpinBox(self.electrodeEditor)
        self.electrodeY.setObjectName("electrodeY")

        self.electrodePositionLayout.addWidget(self.electrodeY)

        self.electrodeZ = QDoubleSpinBox(self.electrodeEditor)
        self.electrodeZ.setObjectName("electrodeZ")

        self.electrodePositionLayout.addWidget(self.electrodeZ)

        self.electrodeEditorLayout.setLayout(
            0, QFormLayout.ItemRole.FieldRole, self.electrodePositionLayout
        )

        self.electrodeRadiusLabel = QLabel(self.electrodeEditor)
        self.electrodeRadiusLabel.setObjectName("electrodeRadiusLabel")

        self.electrodeEditorLayout.setWidget(
            1, QFormLayout.ItemRole.LabelRole, self.electrodeRadiusLabel
        )

        self.electrodeRadius = QDoubleSpinBox(self.electrodeEditor)
        self.electrodeRadius.setObjectName("electrodeRadius")

        self.electrodeEditorLayout.setWidget(
            1, QFormLayout.ItemRole.FieldRole, self.electrodeRadius
        )

        self.electrodeVoltageLabel = QLabel(self.electrodeEditor)
        self.electrodeVoltageLabel.setObjectName("electrodeVoltageLabel")

        self.electrodeEditorLayout.setWidget(
            2, QFormLayout.ItemRole.LabelRole, self.electrodeVoltageLabel
        )

        self.electrodeVoltage = QDoubleSpinBox(self.electrodeEditor)
        self.electrodeVoltage.setObjectName("electrodeVoltage")

        self.electrodeEditorLayout.setWidget(
            2, QFormLayout.ItemRole.FieldRole, self.electrodeVoltage
        )

        self.electrodeActionLayout = QHBoxLayout()
        self.electrodeActionLayout.setObjectName("electrodeActionLayout")
        self.electrodeActionSpacer = QSpacerItem(
            20, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.electrodeActionLayout.addItem(self.electrodeActionSpacer)

        self.moveElectrodeButton = QPushButton(self.electrodeEditor)
        self.moveElectrodeButton.setObjectName("moveElectrodeButton")
        self.moveElectrodeButton.setCheckable(True)

        self.electrodeActionLayout.addWidget(self.moveElectrodeButton)

        self.electrodeEditorLayout.setLayout(
            3, QFormLayout.ItemRole.SpanningRole, self.electrodeActionLayout
        )

        self.electrodePageLayout.addWidget(self.electrodeEditor)

        self.stimStack.addWidget(self.electrodePage)

        self.stimulationLayout.addWidget(self.stimStack)

        self.planesGroup = QGroupBox(self.stimulationTab)
        self.planesGroup.setObjectName("planesGroup")
        self.planesLayout = QHBoxLayout(self.planesGroup)
        self.planesLayout.setObjectName("planesLayout")
        self.planeXLabel = QLabel(self.planesGroup)
        self.planeXLabel.setObjectName("planeXLabel")

        self.planesLayout.addWidget(self.planeXLabel)

        self.planeX = QDoubleSpinBox(self.planesGroup)
        self.planeX.setObjectName("planeX")

        self.planesLayout.addWidget(self.planeX)

        self.planeYLabel = QLabel(self.planesGroup)
        self.planeYLabel.setObjectName("planeYLabel")

        self.planesLayout.addWidget(self.planeYLabel)

        self.planeY = QDoubleSpinBox(self.planesGroup)
        self.planeY.setObjectName("planeY")

        self.planesLayout.addWidget(self.planeY)

        self.planeZLabel = QLabel(self.planesGroup)
        self.planeZLabel.setObjectName("planeZLabel")

        self.planesLayout.addWidget(self.planeZLabel)

        self.planeZ = QDoubleSpinBox(self.planesGroup)
        self.planeZ.setObjectName("planeZ")

        self.planesLayout.addWidget(self.planeZ)

        self.showPlanes = QCheckBox(self.planesGroup)
        self.showPlanes.setObjectName("showPlanes")

        self.planesLayout.addWidget(self.showPlanes)

        self.stimulationLayout.addWidget(self.planesGroup)

        self.stimulationSpacer = QSpacerItem(
            20, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.stimulationLayout.addItem(self.stimulationSpacer)

        self.sideTabs.addTab(self.stimulationTab, "")
        self.solveTab = QWidget()
        self.solveTab.setObjectName("solveTab")
        self.solveLayout = QVBoxLayout(self.solveTab)
        self.solveLayout.setObjectName("solveLayout")
        self.solveSummary = QLabel(self.solveTab)
        self.solveSummary.setObjectName("solveSummary")
        self.solveSummary.setWordWrap(True)

        self.solveLayout.addWidget(self.solveSummary)

        self.solverGroup = QGroupBox(self.solveTab)
        self.solverGroup.setObjectName("solverGroup")
        self.solverLayout = QFormLayout(self.solverGroup)
        self.solverLayout.setObjectName("solverLayout")
        self.numNeighborsLabel = QLabel(self.solverGroup)
        self.numNeighborsLabel.setObjectName("numNeighborsLabel")

        self.solverLayout.setWidget(
            0, QFormLayout.ItemRole.LabelRole, self.numNeighborsLabel
        )

        self.numNeighbors = QSpinBox(self.solverGroup)
        self.numNeighbors.setObjectName("numNeighbors")
        self.numNeighbors.setMinimum(1)
        self.numNeighbors.setMaximum(10000)
        self.numNeighbors.setValue(4)

        self.solverLayout.setWidget(
            0, QFormLayout.ItemRole.FieldRole, self.numNeighbors
        )

        self.numNeighborsPLabel = QLabel(self.solverGroup)
        self.numNeighborsPLabel.setObjectName("numNeighborsPLabel")

        self.solverLayout.setWidget(
            1, QFormLayout.ItemRole.LabelRole, self.numNeighborsPLabel
        )

        self.numNeighborsP = QSpinBox(self.solverGroup)
        self.numNeighborsP.setObjectName("numNeighborsP")
        self.numNeighborsP.setMinimum(1)
        self.numNeighborsP.setMaximum(10000)
        self.numNeighborsP.setValue(32)

        self.solverLayout.setWidget(
            1, QFormLayout.ItemRole.FieldRole, self.numNeighborsP
        )

        self.iterationsLabel = QLabel(self.solverGroup)
        self.iterationsLabel.setObjectName("iterationsLabel")

        self.solverLayout.setWidget(
            2, QFormLayout.ItemRole.LabelRole, self.iterationsLabel
        )

        self.iterations = QSpinBox(self.solverGroup)
        self.iterations.setObjectName("iterations")
        self.iterations.setMinimum(1)
        self.iterations.setMaximum(10000)
        self.iterations.setValue(20)

        self.solverLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.iterations)

        self.relresLabel = QLabel(self.solverGroup)
        self.relresLabel.setObjectName("relresLabel")

        self.solverLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.relresLabel)

        self.relres = QDoubleSpinBox(self.solverGroup)
        self.relres.setObjectName("relres")
        self.relres.setDecimals(10)
        self.relres.setMinimum(0.000000000001000)
        self.relres.setMaximum(1.000000000000000)
        self.relres.setSingleStep(0.000100000000000)
        self.relres.setValue(0.000100000000000)

        self.solverLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.relres)

        self.weightLabel = QLabel(self.solverGroup)
        self.weightLabel.setObjectName("weightLabel")

        self.solverLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.weightLabel)

        self.weight = QDoubleSpinBox(self.solverGroup)
        self.weight.setObjectName("weight")
        self.weight.setDecimals(4)
        self.weight.setMaximum(1.000000000000000)
        self.weight.setSingleStep(0.050000000000000)
        self.weight.setValue(0.500000000000000)

        self.solverLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.weight)

        self.solveLayout.addWidget(self.solverGroup)

        self.outputGroup = QGroupBox(self.solveTab)
        self.outputGroup.setObjectName("outputGroup")
        self.outputLayout = QFormLayout(self.outputGroup)
        self.outputLayout.setObjectName("outputLayout")
        self.outputDirLabel = QLabel(self.outputGroup)
        self.outputDirLabel.setObjectName("outputDirLabel")

        self.outputLayout.setWidget(
            0, QFormLayout.ItemRole.LabelRole, self.outputDirLabel
        )

        self.outputDirLayout = QHBoxLayout()
        self.outputDirLayout.setObjectName("outputDirLayout")
        self.outputDir = QLineEdit(self.outputGroup)
        self.outputDir.setObjectName("outputDir")

        self.outputDirLayout.addWidget(self.outputDir)

        self.browseOutputButton = QPushButton(self.outputGroup)
        self.browseOutputButton.setObjectName("browseOutputButton")

        self.outputDirLayout.addWidget(self.browseOutputButton)

        self.outputLayout.setLayout(
            0, QFormLayout.ItemRole.FieldRole, self.outputDirLayout
        )

        self.exportFormatLabel = QLabel(self.outputGroup)
        self.exportFormatLabel.setObjectName("exportFormatLabel")

        self.outputLayout.setWidget(
            1, QFormLayout.ItemRole.LabelRole, self.exportFormatLabel
        )

        self.exportFormat = QComboBox(self.outputGroup)
        self.exportFormat.addItem("")
        self.exportFormat.addItem("")
        self.exportFormat.addItem("")
        self.exportFormat.addItem("")
        self.exportFormat.addItem("")
        self.exportFormat.setObjectName("exportFormat")

        self.outputLayout.setWidget(
            1, QFormLayout.ItemRole.FieldRole, self.exportFormat
        )

        self.exportFieldsLabel = QLabel(self.outputGroup)
        self.exportFieldsLabel.setObjectName("exportFieldsLabel")

        self.outputLayout.setWidget(
            2, QFormLayout.ItemRole.LabelRole, self.exportFieldsLabel
        )

        self.exportFieldsLayout = QGridLayout()
        self.exportFieldsLayout.setObjectName("exportFieldsLayout")
        self.saveE = QCheckBox(self.outputGroup)
        self.saveE.setObjectName("saveE")
        self.saveE.setChecked(True)

        self.exportFieldsLayout.addWidget(self.saveE, 0, 0, 1, 1)

        self.saveEmag = QCheckBox(self.outputGroup)
        self.saveEmag.setObjectName("saveEmag")

        self.exportFieldsLayout.addWidget(self.saveEmag, 0, 1, 1, 1)

        self.saveEn = QCheckBox(self.outputGroup)
        self.saveEn.setObjectName("saveEn")
        self.saveEn.setChecked(True)

        self.exportFieldsLayout.addWidget(self.saveEn, 0, 2, 1, 1)

        self.saveC = QCheckBox(self.outputGroup)
        self.saveC.setObjectName("saveC")
        self.saveC.setChecked(True)

        self.exportFieldsLayout.addWidget(self.saveC, 1, 0, 1, 1)

        self.saveJn = QCheckBox(self.outputGroup)
        self.saveJn.setObjectName("saveJn")

        self.exportFieldsLayout.addWidget(self.saveJn, 1, 1, 1, 1)

        self.savePot = QCheckBox(self.outputGroup)
        self.savePot.setObjectName("savePot")

        self.exportFieldsLayout.addWidget(self.savePot, 1, 2, 1, 1)

        self.outputLayout.setLayout(
            2, QFormLayout.ItemRole.FieldRole, self.exportFieldsLayout
        )

        self.solveLayout.addWidget(self.outputGroup)

        self.runLayout = QHBoxLayout()
        self.runLayout.setObjectName("runLayout")
        self.runButton = QPushButton(self.solveTab)
        self.runButton.setObjectName("runButton")
        self.runButton.setMinimumSize(QSize(0, 34))

        self.runLayout.addWidget(self.runButton)

        self.cancelButton = QPushButton(self.solveTab)
        self.cancelButton.setObjectName("cancelButton")
        self.cancelButton.setEnabled(False)
        self.cancelButton.setMinimumSize(QSize(0, 34))

        self.runLayout.addWidget(self.cancelButton)

        self.solveLayout.addLayout(self.runLayout)

        self.stageLabel = QLabel(self.solveTab)
        self.stageLabel.setObjectName("stageLabel")

        self.solveLayout.addWidget(self.stageLabel)

        self.progressBar = QProgressBar(self.solveTab)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setValue(0)

        self.solveLayout.addWidget(self.progressBar)

        self.logView = QPlainTextEdit(self.solveTab)
        self.logView.setObjectName("logView")
        self.logView.setReadOnly(True)
        self.logView.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

        self.solveLayout.addWidget(self.logView)

        self.sideTabs.addTab(self.solveTab, "")
        self.resultsTab = QWidget()
        self.resultsTab.setObjectName("resultsTab")
        self.resultsLayout = QVBoxLayout(self.resultsTab)
        self.resultsLayout.setObjectName("resultsLayout")
        self.runGroup = QGroupBox(self.resultsTab)
        self.runGroup.setObjectName("runGroup")
        self.runInfoLayout = QFormLayout(self.runGroup)
        self.runInfoLayout.setObjectName("runInfoLayout")
        self.resultKindLabel = QLabel(self.runGroup)
        self.resultKindLabel.setObjectName("resultKindLabel")

        self.runInfoLayout.setWidget(
            0, QFormLayout.ItemRole.LabelRole, self.resultKindLabel
        )

        self.resultKind = QLabel(self.runGroup)
        self.resultKind.setObjectName("resultKind")

        self.runInfoLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.resultKind)

        self.resultCreatedLabel = QLabel(self.runGroup)
        self.resultCreatedLabel.setObjectName("resultCreatedLabel")

        self.runInfoLayout.setWidget(
            1, QFormLayout.ItemRole.LabelRole, self.resultCreatedLabel
        )

        self.resultCreated = QLabel(self.runGroup)
        self.resultCreated.setObjectName("resultCreated")

        self.runInfoLayout.setWidget(
            1, QFormLayout.ItemRole.FieldRole, self.resultCreated
        )

        self.resultConvergenceLabel = QLabel(self.runGroup)
        self.resultConvergenceLabel.setObjectName("resultConvergenceLabel")

        self.runInfoLayout.setWidget(
            2, QFormLayout.ItemRole.LabelRole, self.resultConvergenceLabel
        )

        self.resultConvergence = QLabel(self.runGroup)
        self.resultConvergence.setObjectName("resultConvergence")

        self.runInfoLayout.setWidget(
            2, QFormLayout.ItemRole.FieldRole, self.resultConvergence
        )

        self.resultFolderLabel = QLabel(self.runGroup)
        self.resultFolderLabel.setObjectName("resultFolderLabel")

        self.runInfoLayout.setWidget(
            3, QFormLayout.ItemRole.LabelRole, self.resultFolderLabel
        )

        self.resultFolder = QLabel(self.runGroup)
        self.resultFolder.setObjectName("resultFolder")
        self.resultFolder.setWordWrap(True)
        self.resultFolder.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        self.runInfoLayout.setWidget(
            3, QFormLayout.ItemRole.FieldRole, self.resultFolder
        )

        self.resultsLayout.addWidget(self.runGroup)

        self.showGroup = QGroupBox(self.resultsTab)
        self.showGroup.setObjectName("showGroup")
        self.showLayout = QFormLayout(self.showGroup)
        self.showLayout.setObjectName("showLayout")
        self.resultFieldLabel = QLabel(self.showGroup)
        self.resultFieldLabel.setObjectName("resultFieldLabel")

        self.showLayout.setWidget(
            0, QFormLayout.ItemRole.LabelRole, self.resultFieldLabel
        )

        self.resultField = QComboBox(self.showGroup)
        self.resultField.setObjectName("resultField")

        self.showLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.resultField)

        self.resultTissueLabel = QLabel(self.showGroup)
        self.resultTissueLabel.setObjectName("resultTissueLabel")

        self.showLayout.setWidget(
            1, QFormLayout.ItemRole.LabelRole, self.resultTissueLabel
        )

        self.resultTissue = QComboBox(self.showGroup)
        self.resultTissue.setObjectName("resultTissue")

        self.showLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.resultTissue)

        self.resultColormapLabel = QLabel(self.showGroup)
        self.resultColormapLabel.setObjectName("resultColormapLabel")

        self.showLayout.setWidget(
            2, QFormLayout.ItemRole.LabelRole, self.resultColormapLabel
        )

        self.resultColormap = QComboBox(self.showGroup)
        self.resultColormap.addItem("")
        self.resultColormap.addItem("")
        self.resultColormap.addItem("")
        self.resultColormap.addItem("")
        self.resultColormap.addItem("")
        self.resultColormap.setObjectName("resultColormap")

        self.showLayout.setWidget(
            2, QFormLayout.ItemRole.FieldRole, self.resultColormap
        )

        self.resultRangeLabel = QLabel(self.showGroup)
        self.resultRangeLabel.setObjectName("resultRangeLabel")

        self.showLayout.setWidget(
            3, QFormLayout.ItemRole.LabelRole, self.resultRangeLabel
        )

        self.resultRangeLayout = QHBoxLayout()
        self.resultRangeLayout.setObjectName("resultRangeLayout")
        self.autoRange = QCheckBox(self.showGroup)
        self.autoRange.setObjectName("autoRange")
        self.autoRange.setChecked(True)

        self.resultRangeLayout.addWidget(self.autoRange)

        self.rangeMin = QDoubleSpinBox(self.showGroup)
        self.rangeMin.setObjectName("rangeMin")
        self.rangeMin.setEnabled(False)

        self.resultRangeLayout.addWidget(self.rangeMin)

        self.rangeMax = QDoubleSpinBox(self.showGroup)
        self.rangeMax.setObjectName("rangeMax")
        self.rangeMax.setEnabled(False)

        self.resultRangeLayout.addWidget(self.rangeMax)

        self.showLayout.setLayout(
            3, QFormLayout.ItemRole.FieldRole, self.resultRangeLayout
        )

        self.resultStats = QLabel(self.showGroup)
        self.resultStats.setObjectName("resultStats")
        self.resultStats.setWordWrap(True)

        self.showLayout.setWidget(
            4, QFormLayout.ItemRole.SpanningRole, self.resultStats
        )

        self.showResultButton = QPushButton(self.showGroup)
        self.showResultButton.setObjectName("showResultButton")
        self.showResultButton.setEnabled(False)
        self.showResultButton.setCheckable(True)

        self.showLayout.setWidget(
            5, QFormLayout.ItemRole.SpanningRole, self.showResultButton
        )

        self.resultsLayout.addWidget(self.showGroup)

        self.electrodeResultGroup = QGroupBox(self.resultsTab)
        self.electrodeResultGroup.setObjectName("electrodeResultGroup")
        self.electrodeResultLayout = QVBoxLayout(self.electrodeResultGroup)
        self.electrodeResultLayout.setObjectName("electrodeResultLayout")
        self.electrodeTable = QTableWidget(self.electrodeResultGroup)
        if self.electrodeTable.columnCount() < 4:
            self.electrodeTable.setColumnCount(4)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.electrodeTable.setHorizontalHeaderItem(0, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.electrodeTable.setHorizontalHeaderItem(1, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.electrodeTable.setHorizontalHeaderItem(2, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.electrodeTable.setHorizontalHeaderItem(3, __qtablewidgetitem7)
        self.electrodeTable.setObjectName("electrodeTable")
        self.electrodeTable.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.electrodeTable.setAlternatingRowColors(True)
        self.electrodeTable.horizontalHeader().setStretchLastSection(True)
        self.electrodeTable.verticalHeader().setVisible(False)

        self.electrodeResultLayout.addWidget(self.electrodeTable)

        self.electrodeSummary = QLabel(self.electrodeResultGroup)
        self.electrodeSummary.setObjectName("electrodeSummary")

        self.electrodeResultLayout.addWidget(self.electrodeSummary)

        self.resultsLayout.addWidget(self.electrodeResultGroup)

        self.resultButtons = QHBoxLayout()
        self.resultButtons.setObjectName("resultButtons")
        self.convergenceButton = QPushButton(self.resultsTab)
        self.convergenceButton.setObjectName("convergenceButton")
        self.convergenceButton.setEnabled(False)

        self.resultButtons.addWidget(self.convergenceButton)

        self.plotWindowsButton = QPushButton(self.resultsTab)
        self.plotWindowsButton.setObjectName("plotWindowsButton")
        self.plotWindowsButton.setEnabled(False)

        self.resultButtons.addWidget(self.plotWindowsButton)

        self.openFolderButton = QPushButton(self.resultsTab)
        self.openFolderButton.setObjectName("openFolderButton")
        self.openFolderButton.setEnabled(False)

        self.resultButtons.addWidget(self.openFolderButton)

        self.resultsLayout.addLayout(self.resultButtons)

        self.resultsSpacer = QSpacerItem(
            20, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.resultsLayout.addItem(self.resultsSpacer)

        self.sideTabs.addTab(self.resultsTab, "")
        self.splitter.addWidget(self.sideTabs)
        self.viewPort = QWidget(self.splitter)
        self.viewPort.setObjectName("viewPort")
        sizePolicy1 = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.viewPort.sizePolicy().hasHeightForWidth())
        self.viewPort.setSizePolicy(sizePolicy1)
        self.splitter.addWidget(self.viewPort)

        self.centralLayout.addWidget(self.splitter)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuView = QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        self.menuRun = QMenu(self.menubar)
        self.menuRun.setObjectName("menuRun")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.mainToolBar = QToolBar(MainWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        self.mainToolBar.setMovable(False)
        self.mainToolBar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        MainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.mainToolBar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuRun.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionNewSetup)
        self.menuFile.addAction(self.actionOpenSetup)
        self.menuFile.addAction(self.actionSaveSetup)
        self.menuFile.addAction(self.actionSaveSetupAs)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionOpenIndex)
        self.menuFile.addAction(self.actionSaveIndexAs)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionOpenResult)
        self.menuFile.addAction(self.actionExportMatlab)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        self.menuEdit.addAction(self.actionUndo)
        self.menuEdit.addAction(self.actionRedo)
        self.menuView.addAction(self.actionViewXY)
        self.menuView.addAction(self.actionViewXZ)
        self.menuView.addAction(self.actionViewYZ)
        self.menuView.addAction(self.actionResetView)
        self.menuRun.addAction(self.actionRun)
        self.menuRun.addSeparator()
        self.menuRun.addAction(self.actionSphere)
        self.menuRun.addAction(self.actionDipole)
        self.menuHelp.addAction(self.actionViewerHelp)
        self.menuHelp.addAction(self.actionAbout)
        self.mainToolBar.addAction(self.actionOpenSetup)
        self.mainToolBar.addAction(self.actionSaveSetup)
        self.mainToolBar.addSeparator()
        self.mainToolBar.addAction(self.actionUndo)
        self.mainToolBar.addAction(self.actionRedo)
        self.mainToolBar.addSeparator()
        self.mainToolBar.addAction(self.actionViewXY)
        self.mainToolBar.addAction(self.actionViewXZ)
        self.mainToolBar.addAction(self.actionViewYZ)
        self.mainToolBar.addAction(self.actionResetView)
        self.mainToolBar.addSeparator()
        self.mainToolBar.addAction(self.actionRun)

        self.retranslateUi(MainWindow)

        self.sideTabs.setCurrentIndex(0)
        self.stimStack.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "BEM-FMM", None)
        )
        self.actionNewSetup.setText(
            QCoreApplication.translate("MainWindow", "&New setup", None)
        )
        # if QT_CONFIG(shortcut)
        self.actionNewSetup.setShortcut(
            QCoreApplication.translate("MainWindow", "Ctrl+N", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionOpenSetup.setText(
            QCoreApplication.translate("MainWindow", "&Open setup...", None)
        )
        # if QT_CONFIG(shortcut)
        self.actionOpenSetup.setShortcut(
            QCoreApplication.translate("MainWindow", "Ctrl+O", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionSaveSetup.setText(
            QCoreApplication.translate("MainWindow", "&Save setup", None)
        )
        # if QT_CONFIG(shortcut)
        self.actionSaveSetup.setShortcut(
            QCoreApplication.translate("MainWindow", "Ctrl+S", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionSaveSetupAs.setText(
            QCoreApplication.translate("MainWindow", "Save setup &as...", None)
        )
        # if QT_CONFIG(shortcut)
        self.actionSaveSetupAs.setShortcut(
            QCoreApplication.translate("MainWindow", "Ctrl+Shift+S", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionOpenIndex.setText(
            QCoreApplication.translate("MainWindow", "Open tissue &index...", None)
        )
        self.actionSaveIndexAs.setText(
            QCoreApplication.translate("MainWindow", "Save tissue index as...", None)
        )
        self.actionOpenResult.setText(
            QCoreApplication.translate("MainWindow", "Open &result...", None)
        )
        # if QT_CONFIG(shortcut)
        self.actionOpenResult.setShortcut(
            QCoreApplication.translate("MainWindow", "Ctrl+R", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionExportMatlab.setText(
            QCoreApplication.translate("MainWindow", "Export model to &MATLAB...", None)
        )
        self.actionQuit.setText(QCoreApplication.translate("MainWindow", "&Quit", None))
        # if QT_CONFIG(shortcut)
        self.actionQuit.setShortcut(
            QCoreApplication.translate("MainWindow", "Ctrl+Q", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionUndo.setText(QCoreApplication.translate("MainWindow", "&Undo", None))
        # if QT_CONFIG(shortcut)
        self.actionUndo.setShortcut(
            QCoreApplication.translate("MainWindow", "Ctrl+Z", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionRedo.setText(QCoreApplication.translate("MainWindow", "&Redo", None))
        # if QT_CONFIG(shortcut)
        self.actionRedo.setShortcut(
            QCoreApplication.translate("MainWindow", "Ctrl+Shift+Z", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionViewXY.setText(
            QCoreApplication.translate("MainWindow", "Top (XY)", None)
        )
        self.actionViewXY.setIconText(
            QCoreApplication.translate("MainWindow", "XY", None)
        )
        self.actionViewXZ.setText(
            QCoreApplication.translate("MainWindow", "Front (XZ)", None)
        )
        self.actionViewXZ.setIconText(
            QCoreApplication.translate("MainWindow", "XZ", None)
        )
        self.actionViewYZ.setText(
            QCoreApplication.translate("MainWindow", "Side (YZ)", None)
        )
        self.actionViewYZ.setIconText(
            QCoreApplication.translate("MainWindow", "YZ", None)
        )
        self.actionResetView.setText(
            QCoreApplication.translate("MainWindow", "Reset view", None)
        )
        self.actionResetView.setIconText(
            QCoreApplication.translate("MainWindow", "Reset", None)
        )
        self.actionRun.setText(
            QCoreApplication.translate("MainWindow", "Run &solver", None)
        )
        self.actionRun.setIconText(
            QCoreApplication.translate("MainWindow", "Run", None)
        )
        # if QT_CONFIG(shortcut)
        self.actionRun.setShortcut(QCoreApplication.translate("MainWindow", "F5", None))
        # endif // QT_CONFIG(shortcut)
        self.actionSphere.setText(
            QCoreApplication.translate(
                "MainWindow", "Sphere check (uniform field)", None
            )
        )
        self.actionDipole.setText(
            QCoreApplication.translate("MainWindow", "Dipole on skull", None)
        )
        self.actionViewerHelp.setText(
            QCoreApplication.translate("MainWindow", "3D view &keys", None)
        )
        self.actionAbout.setText(
            QCoreApplication.translate("MainWindow", "&About", None)
        )
        self.indexGroup.setTitle(
            QCoreApplication.translate("MainWindow", "Tissue index", None)
        )
        self.openIndexButton.setText(
            QCoreApplication.translate("MainWindow", "Open...", None)
        )
        self.modelSummary.setText(
            QCoreApplication.translate("MainWindow", "No model loaded", None)
        )
        self.tissueGroup.setTitle(
            QCoreApplication.translate("MainWindow", "Tissues", None)
        )
        self.tissueHint.setText(
            QCoreApplication.translate(
                "MainWindow",
                "Each tissue is a closed surface. Outside is the tissue just beyond that surface, FreeSpace for air.",
                None,
            )
        )
        ___qtablewidgetitem = self.tissueTable.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(
            QCoreApplication.translate("MainWindow", "Tissue", None)
        )
        ___qtablewidgetitem1 = self.tissueTable.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(
            QCoreApplication.translate("MainWindow", "S/m", None)
        )
        ___qtablewidgetitem2 = self.tissueTable.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(
            QCoreApplication.translate("MainWindow", "Outside", None)
        )
        ___qtablewidgetitem3 = self.tissueTable.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(
            QCoreApplication.translate("MainWindow", "Mesh file", None)
        )
        self.addTissueButton.setText(
            QCoreApplication.translate("MainWindow", "Add...", None)
        )
        self.removeTissueButton.setText(
            QCoreApplication.translate("MainWindow", "Remove", None)
        )
        self.saveIndexButton.setText(
            QCoreApplication.translate("MainWindow", "Save as...", None)
        )
        # if QT_CONFIG(tooltip)
        self.applyIndexButton.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Reload the model with the edited tissues", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.applyIndexButton.setText(
            QCoreApplication.translate("MainWindow", "Apply", None)
        )
        self.displayGroup.setTitle(
            QCoreApplication.translate("MainWindow", "Display", None)
        )
        self.sideTabs.setTabText(
            self.sideTabs.indexOf(self.modelTab),
            QCoreApplication.translate("MainWindow", "Model", None),
        )
        self.modeGroup.setTitle(QCoreApplication.translate("MainWindow", "Type", None))
        self.tmsRadio.setText(
            QCoreApplication.translate("MainWindow", "TMS coils", None)
        )
        self.tdcsRadio.setText(
            QCoreApplication.translate("MainWindow", "tDCS electrodes", None)
        )
        self.surfaceLabel.setText(
            QCoreApplication.translate("MainWindow", "Place on", None)
        )
        # if QT_CONFIG(tooltip)
        self.surfaceCombo.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Surface that coils and electrodes snap to and are dragged on",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.addCoilButton.setText(
            QCoreApplication.translate("MainWindow", "Add coil", None)
        )
        self.deleteCoilButton.setText(
            QCoreApplication.translate("MainWindow", "Delete", None)
        )
        self.coilAlphaLabel.setText(
            QCoreApplication.translate("MainWindow", "Opacity", None)
        )
        self.coilEditor.setTitle(
            QCoreApplication.translate("MainWindow", "Selected coil", None)
        )
        self.coilPositionLabel.setText(
            QCoreApplication.translate("MainWindow", "Position (mm)", None)
        )
        self.coilRotationLabel.setText(
            QCoreApplication.translate("MainWindow", "Rotation (deg)", None)
        )
        self.coilTwistLabel.setText(
            QCoreApplication.translate("MainWindow", "Twist (deg)", None)
        )
        # if QT_CONFIG(tooltip)
        self.coilTwist.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Rotation about the coil axis", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.coilDistanceLabel.setText(
            QCoreApplication.translate("MainWindow", "Distance (mm)", None)
        )
        # if QT_CONFIG(tooltip)
        self.coilDistance.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Distance from the bottom of the coil to the surface",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.coilDIdtLabel.setText(
            QCoreApplication.translate("MainWindow", "dI/dt (A/us)", None)
        )
        # if QT_CONFIG(tooltip)
        self.autoOrientButton.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Point the coil axis along the surface normal", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.autoOrientButton.setText(
            QCoreApplication.translate("MainWindow", "Auto orient", None)
        )
        self.flipButton.setText(QCoreApplication.translate("MainWindow", "Flip", None))
        # if QT_CONFIG(tooltip)
        self.moveCoilButton.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Click the coil in the 3D view, move it over the surface, click again to drop it",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.moveCoilButton.setText(
            QCoreApplication.translate("MainWindow", "Drag", None)
        )
        self.targetLabel.setText(
            QCoreApplication.translate("MainWindow", "Aim at", None)
        )
        # if QT_CONFIG(tooltip)
        self.targetCombo.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Tissue to pick the target point on", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(tooltip)
        self.aimButton.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Click a point on the target tissue, then press again to move the coil above it",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.aimButton.setText(
            QCoreApplication.translate("MainWindow", "Pick target", None)
        )
        self.electrodeHint.setText(
            QCoreApplication.translate(
                "MainWindow", "Electrodes are held at a fixed voltage", None
            )
        )
        self.addElectrodeButton.setText(
            QCoreApplication.translate("MainWindow", "Add electrode", None)
        )
        self.deleteElectrodeButton.setText(
            QCoreApplication.translate("MainWindow", "Delete", None)
        )
        self.electrodeAlphaLabel.setText(
            QCoreApplication.translate("MainWindow", "Opacity", None)
        )
        self.electrodeEditor.setTitle(
            QCoreApplication.translate("MainWindow", "Selected electrode", None)
        )
        self.electrodePositionLabel.setText(
            QCoreApplication.translate("MainWindow", "Position (mm)", None)
        )
        self.electrodeRadiusLabel.setText(
            QCoreApplication.translate("MainWindow", "Radius (mm)", None)
        )
        self.electrodeVoltageLabel.setText(
            QCoreApplication.translate("MainWindow", "Voltage (V)", None)
        )
        # if QT_CONFIG(tooltip)
        self.moveElectrodeButton.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Click the electrode in the 3D view, move it over the surface, click again to drop it",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.moveElectrodeButton.setText(
            QCoreApplication.translate("MainWindow", "Drag", None)
        )
        self.planesGroup.setTitle(
            QCoreApplication.translate("MainWindow", "Slice planes (mm)", None)
        )
        self.planeXLabel.setText(QCoreApplication.translate("MainWindow", "X", None))
        self.planeYLabel.setText(QCoreApplication.translate("MainWindow", "Y", None))
        self.planeZLabel.setText(QCoreApplication.translate("MainWindow", "Z", None))
        self.showPlanes.setText(QCoreApplication.translate("MainWindow", "Show", None))
        self.sideTabs.setTabText(
            self.sideTabs.indexOf(self.stimulationTab),
            QCoreApplication.translate("MainWindow", "Stimulation", None),
        )
        self.solveSummary.setText(
            QCoreApplication.translate("MainWindow", "Nothing to solve yet", None)
        )
        self.solverGroup.setTitle(
            QCoreApplication.translate("MainWindow", "Solver", None)
        )
        self.numNeighborsLabel.setText(
            QCoreApplication.translate("MainWindow", "Neighbor integrals", None)
        )
        # if QT_CONFIG(tooltip)
        self.numNeighbors.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Nearest facets integrated exactly for the E-field", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.numNeighborsPLabel.setText(
            QCoreApplication.translate("MainWindow", "Potential integrals", None)
        )
        # if QT_CONFIG(tooltip)
        self.numNeighborsP.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Nearest facets integrated exactly for the potential on electrodes",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.iterationsLabel.setText(
            QCoreApplication.translate("MainWindow", "Max iterations", None)
        )
        self.relresLabel.setText(
            QCoreApplication.translate("MainWindow", "Tolerance", None)
        )
        # if QT_CONFIG(tooltip)
        self.relres.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Stop when the relative residual is below this", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.weightLabel.setText(
            QCoreApplication.translate("MainWindow", "Conservation weight", None)
        )
        self.outputGroup.setTitle(
            QCoreApplication.translate("MainWindow", "Output", None)
        )
        self.outputDirLabel.setText(
            QCoreApplication.translate("MainWindow", "Folder", None)
        )
        self.browseOutputButton.setText(
            QCoreApplication.translate("MainWindow", "Browse...", None)
        )
        self.exportFormatLabel.setText(
            QCoreApplication.translate("MainWindow", "Also export", None)
        )
        self.exportFormat.setItemText(
            0, QCoreApplication.translate("MainWindow", "none", None)
        )
        self.exportFormat.setItemText(
            1, QCoreApplication.translate("MainWindow", "mat", None)
        )
        self.exportFormat.setItemText(
            2, QCoreApplication.translate("MainWindow", "npz", None)
        )
        self.exportFormat.setItemText(
            3, QCoreApplication.translate("MainWindow", "csv", None)
        )
        self.exportFormat.setItemText(
            4, QCoreApplication.translate("MainWindow", "pkl", None)
        )

        self.exportFieldsLabel.setText(
            QCoreApplication.translate("MainWindow", "Fields", None)
        )
        self.saveE.setText(QCoreApplication.translate("MainWindow", "E", None))
        self.saveEmag.setText(QCoreApplication.translate("MainWindow", "Emag", None))
        self.saveEn.setText(QCoreApplication.translate("MainWindow", "En", None))
        self.saveC.setText(QCoreApplication.translate("MainWindow", "c", None))
        self.saveJn.setText(QCoreApplication.translate("MainWindow", "Jn", None))
        self.savePot.setText(QCoreApplication.translate("MainWindow", "Pot", None))
        self.runButton.setText(QCoreApplication.translate("MainWindow", "Run", None))
        self.cancelButton.setText(
            QCoreApplication.translate("MainWindow", "Cancel", None)
        )
        self.stageLabel.setText(QCoreApplication.translate("MainWindow", "Idle", None))
        self.sideTabs.setTabText(
            self.sideTabs.indexOf(self.solveTab),
            QCoreApplication.translate("MainWindow", "Solve", None),
        )
        self.runGroup.setTitle(QCoreApplication.translate("MainWindow", "Run", None))
        self.resultKindLabel.setText(
            QCoreApplication.translate("MainWindow", "Type", None)
        )
        self.resultKind.setText(QCoreApplication.translate("MainWindow", "-", None))
        self.resultCreatedLabel.setText(
            QCoreApplication.translate("MainWindow", "Created", None)
        )
        self.resultCreated.setText(QCoreApplication.translate("MainWindow", "-", None))
        self.resultConvergenceLabel.setText(
            QCoreApplication.translate("MainWindow", "Convergence", None)
        )
        self.resultConvergence.setText(
            QCoreApplication.translate("MainWindow", "-", None)
        )
        self.resultFolderLabel.setText(
            QCoreApplication.translate("MainWindow", "Folder", None)
        )
        self.resultFolder.setText(QCoreApplication.translate("MainWindow", "-", None))
        self.showGroup.setTitle(QCoreApplication.translate("MainWindow", "Show", None))
        self.resultFieldLabel.setText(
            QCoreApplication.translate("MainWindow", "Field", None)
        )
        self.resultTissueLabel.setText(
            QCoreApplication.translate("MainWindow", "Tissue", None)
        )
        self.resultColormapLabel.setText(
            QCoreApplication.translate("MainWindow", "Colormap", None)
        )
        self.resultColormap.setItemText(
            0, QCoreApplication.translate("MainWindow", "jet", None)
        )
        self.resultColormap.setItemText(
            1, QCoreApplication.translate("MainWindow", "viridis", None)
        )
        self.resultColormap.setItemText(
            2, QCoreApplication.translate("MainWindow", "plasma", None)
        )
        self.resultColormap.setItemText(
            3, QCoreApplication.translate("MainWindow", "hot", None)
        )
        self.resultColormap.setItemText(
            4, QCoreApplication.translate("MainWindow", "RdBu_r", None)
        )

        self.resultRangeLabel.setText(
            QCoreApplication.translate("MainWindow", "Range", None)
        )
        self.autoRange.setText(QCoreApplication.translate("MainWindow", "Auto", None))
        self.resultStats.setText("")
        self.showResultButton.setText(
            QCoreApplication.translate("MainWindow", "Show in 3D view", None)
        )
        self.electrodeResultGroup.setTitle(
            QCoreApplication.translate("MainWindow", "Electrodes", None)
        )
        ___qtablewidgetitem4 = self.electrodeTable.horizontalHeaderItem(0)
        ___qtablewidgetitem4.setText(
            QCoreApplication.translate("MainWindow", "Electrode", None)
        )
        ___qtablewidgetitem5 = self.electrodeTable.horizontalHeaderItem(1)
        ___qtablewidgetitem5.setText(
            QCoreApplication.translate("MainWindow", "Set (V)", None)
        )
        ___qtablewidgetitem6 = self.electrodeTable.horizontalHeaderItem(2)
        ___qtablewidgetitem6.setText(
            QCoreApplication.translate("MainWindow", "Solved (V)", None)
        )
        ___qtablewidgetitem7 = self.electrodeTable.horizontalHeaderItem(3)
        ___qtablewidgetitem7.setText(
            QCoreApplication.translate("MainWindow", "Current (mA)", None)
        )
        self.electrodeSummary.setText("")
        self.convergenceButton.setText(
            QCoreApplication.translate("MainWindow", "Convergence", None)
        )
        # if QT_CONFIG(tooltip)
        self.plotWindowsButton.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Surface and slice plots in separate windows", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.plotWindowsButton.setText(
            QCoreApplication.translate("MainWindow", "Plot windows", None)
        )
        self.openFolderButton.setText(
            QCoreApplication.translate("MainWindow", "Open folder", None)
        )
        self.sideTabs.setTabText(
            self.sideTabs.indexOf(self.resultsTab),
            QCoreApplication.translate("MainWindow", "Results", None),
        )
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", "&File", None))
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", "&Edit", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", "&View", None))
        self.menuRun.setTitle(QCoreApplication.translate("MainWindow", "&Run", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", "&Help", None))
        self.mainToolBar.setWindowTitle(
            QCoreApplication.translate("MainWindow", "Main toolbar", None)
        )

    # retranslateUi
