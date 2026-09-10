# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tms.ui'
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
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class Ui_OptionsDialog(object):
    def setupUi(self, OptionsDialog):
        if not OptionsDialog.objectName():
            OptionsDialog.setObjectName("OptionsDialog")
        OptionsDialog.resize(650, 470)
        self.verticalLayout = QVBoxLayout(OptionsDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QLabel(OptionsDialog)
        self.label.setObjectName("label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tissueIndexPath = QLineEdit(OptionsDialog)
        self.tissueIndexPath.setObjectName("tissueIndexPath")

        self.horizontalLayout.addWidget(self.tissueIndexPath)

        self.browseTissueBtn = QPushButton(OptionsDialog)
        self.browseTissueBtn.setObjectName("browseTissueBtn")

        self.horizontalLayout.addWidget(self.browseTissueBtn)

        self.formLayout.setLayout(
            0, QFormLayout.ItemRole.FieldRole, self.horizontalLayout
        )

        self.label_2 = QLabel(OptionsDialog)
        self.label_2.setObjectName("label_2")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.numNeighbors = QSpinBox(OptionsDialog)
        self.numNeighbors.setObjectName("numNeighbors")
        self.numNeighbors.setMinimum(1)
        self.numNeighbors.setMaximum(10000)
        self.numNeighbors.setValue(4)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.numNeighbors)

        self.label_3 = QLabel(OptionsDialog)
        self.label_3.setObjectName("label_3")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.outputDirPath = QLineEdit(OptionsDialog)
        self.outputDirPath.setObjectName("outputDirPath")

        self.horizontalLayout_2.addWidget(self.outputDirPath)

        self.browseOutputBtn = QPushButton(OptionsDialog)
        self.browseOutputBtn.setObjectName("browseOutputBtn")

        self.horizontalLayout_2.addWidget(self.browseOutputBtn)

        self.formLayout.setLayout(
            2, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_2
        )

        self.label_4 = QLabel(OptionsDialog)
        self.label_4.setObjectName("label_4")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_4)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.radioNone = QRadioButton(OptionsDialog)
        self.radioNone.setObjectName("radioNone")
        self.radioNone.setChecked(True)

        self.horizontalLayout_3.addWidget(self.radioNone)

        self.radioMat = QRadioButton(OptionsDialog)
        self.radioMat.setObjectName("radioMat")

        self.horizontalLayout_3.addWidget(self.radioMat)

        self.radioCsv = QRadioButton(OptionsDialog)
        self.radioCsv.setObjectName("radioCsv")

        self.horizontalLayout_3.addWidget(self.radioCsv)

        self.radioNpz = QRadioButton(OptionsDialog)
        self.radioNpz.setObjectName("radioNpz")

        self.horizontalLayout_3.addWidget(self.radioNpz)

        self.radioPkl = QRadioButton(OptionsDialog)
        self.radioPkl.setObjectName("radioPkl")

        self.horizontalLayout_3.addWidget(self.radioPkl)

        self.formLayout.setLayout(
            3, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_3
        )

        self.labelIterations = QLabel(OptionsDialog)
        self.labelIterations.setObjectName("labelIterations")

        self.formLayout.setWidget(
            4, QFormLayout.ItemRole.LabelRole, self.labelIterations
        )

        self.iterations = QSpinBox(OptionsDialog)
        self.iterations.setObjectName("iterations")
        self.iterations.setMinimum(1)
        self.iterations.setMaximum(10000)
        self.iterations.setValue(20)

        self.formLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.iterations)

        self.labelRelres = QLabel(OptionsDialog)
        self.labelRelres.setObjectName("labelRelres")

        self.formLayout.setWidget(5, QFormLayout.ItemRole.LabelRole, self.labelRelres)

        self.relres = QDoubleSpinBox(OptionsDialog)
        self.relres.setObjectName("relres")
        self.relres.setDecimals(10)
        self.relres.setMinimum(0.000000000001000)
        self.relres.setMaximum(1.000000000000000)
        self.relres.setSingleStep(0.000010000000000)
        self.relres.setValue(0.000100000000000)

        self.formLayout.setWidget(5, QFormLayout.ItemRole.FieldRole, self.relres)

        self.labelWeight = QLabel(OptionsDialog)
        self.labelWeight.setObjectName("labelWeight")

        self.formLayout.setWidget(6, QFormLayout.ItemRole.LabelRole, self.labelWeight)

        self.weight = QDoubleSpinBox(OptionsDialog)
        self.weight.setObjectName("weight")
        self.weight.setDecimals(4)
        self.weight.setMinimum(0.000000000000000)
        self.weight.setMaximum(1.000000000000000)
        self.weight.setSingleStep(0.050000000000000)
        self.weight.setValue(0.500000000000000)

        self.formLayout.setWidget(6, QFormLayout.ItemRole.FieldRole, self.weight)

        self.labelSave = QLabel(OptionsDialog)
        self.labelSave.setObjectName("labelSave")

        self.formLayout.setWidget(7, QFormLayout.ItemRole.LabelRole, self.labelSave)

        self.saveLayout = QHBoxLayout()
        self.saveLayout.setObjectName("saveLayout")
        self.saveE = QCheckBox(OptionsDialog)
        self.saveE.setObjectName("saveE")
        self.saveE.setChecked(True)

        self.saveLayout.addWidget(self.saveE)

        self.saveC = QCheckBox(OptionsDialog)
        self.saveC.setObjectName("saveC")
        self.saveC.setChecked(True)

        self.saveLayout.addWidget(self.saveC)

        self.saveEn = QCheckBox(OptionsDialog)
        self.saveEn.setObjectName("saveEn")
        self.saveEn.setChecked(True)

        self.saveLayout.addWidget(self.saveEn)

        self.formLayout.setLayout(7, QFormLayout.ItemRole.FieldRole, self.saveLayout)

        self.verticalLayout.addLayout(self.formLayout)

        self.verticalSpacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.verticalLayout.addItem(self.verticalSpacer)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName("buttonLayout")
        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.buttonLayout.addItem(self.horizontalSpacer)

        self.okButton = QPushButton(OptionsDialog)
        self.okButton.setObjectName("okButton")

        self.buttonLayout.addWidget(self.okButton)

        self.cancelButton = QPushButton(OptionsDialog)
        self.cancelButton.setObjectName("cancelButton")

        self.buttonLayout.addWidget(self.cancelButton)

        self.verticalLayout.addLayout(self.buttonLayout)

        self.retranslateUi(OptionsDialog)
        self.okButton.clicked.connect(OptionsDialog.accept)
        self.cancelButton.clicked.connect(OptionsDialog.reject)

        QMetaObject.connectSlotsByName(OptionsDialog)

    # setupUi

    def retranslateUi(self, OptionsDialog):
        OptionsDialog.setWindowTitle(
            QCoreApplication.translate("OptionsDialog", "TMS Options", None)
        )
        self.label.setText(
            QCoreApplication.translate("OptionsDialog", "Tissue Index (YAML):", None)
        )
        self.browseTissueBtn.setText(
            QCoreApplication.translate("OptionsDialog", "Browse...", None)
        )
        self.label_2.setText(
            QCoreApplication.translate("OptionsDialog", "Number of Neighbors:", None)
        )
        self.label_3.setText(
            QCoreApplication.translate("OptionsDialog", "Output Directory:", None)
        )
        self.browseOutputBtn.setText(
            QCoreApplication.translate("OptionsDialog", "Browse...", None)
        )
        self.label_4.setText(
            QCoreApplication.translate("OptionsDialog", "Save Format:", None)
        )
        self.radioNone.setText(
            QCoreApplication.translate("OptionsDialog", "none", None)
        )
        self.radioMat.setText(QCoreApplication.translate("OptionsDialog", "mat", None))
        self.radioCsv.setText(QCoreApplication.translate("OptionsDialog", "csv", None))
        self.radioNpz.setText(QCoreApplication.translate("OptionsDialog", "npz", None))
        self.radioPkl.setText(QCoreApplication.translate("OptionsDialog", "pkl", None))
        self.labelIterations.setText(
            QCoreApplication.translate("OptionsDialog", "Iterations:", None)
        )
        self.labelRelres.setText(
            QCoreApplication.translate("OptionsDialog", "Relative Residual:", None)
        )
        self.labelWeight.setText(
            QCoreApplication.translate("OptionsDialog", "Weight:", None)
        )
        self.labelSave.setText(
            QCoreApplication.translate("OptionsDialog", "Save Components:", None)
        )
        self.saveE.setText(QCoreApplication.translate("OptionsDialog", "E", None))
        self.saveC.setText(QCoreApplication.translate("OptionsDialog", "c", None))
        self.saveEn.setText(QCoreApplication.translate("OptionsDialog", "En", None))
        self.okButton.setText(QCoreApplication.translate("OptionsDialog", "OK", None))
        self.cancelButton.setText(
            QCoreApplication.translate("OptionsDialog", "Cancel", None)
        )

    # retranslateUi
