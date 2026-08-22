# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tms.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QFormLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QRadioButton,
    QSizePolicy, QSpacerItem, QSpinBox, QVBoxLayout,
    QWidget)

class Ui_OptionsDialog(object):
    def setupUi(self, OptionsDialog):
        if not OptionsDialog.objectName():
            OptionsDialog.setObjectName(u"OptionsDialog")
        OptionsDialog.resize(498, 196)
        self.verticalLayout = QVBoxLayout(OptionsDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(OptionsDialog)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.tissueIndexPath = QLineEdit(OptionsDialog)
        self.tissueIndexPath.setObjectName(u"tissueIndexPath")

        self.horizontalLayout.addWidget(self.tissueIndexPath)

        self.browseTissueBtn = QPushButton(OptionsDialog)
        self.browseTissueBtn.setObjectName(u"browseTissueBtn")

        self.horizontalLayout.addWidget(self.browseTissueBtn)


        self.formLayout.setLayout(0, QFormLayout.ItemRole.FieldRole, self.horizontalLayout)

        self.label_2 = QLabel(OptionsDialog)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.numNeighbors = QSpinBox(OptionsDialog)
        self.numNeighbors.setObjectName(u"numNeighbors")
        self.numNeighbors.setMinimum(1)
        self.numNeighbors.setMaximum(10000)
        self.numNeighbors.setValue(4)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.numNeighbors)

        self.label_3 = QLabel(OptionsDialog)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.outputDirPath = QLineEdit(OptionsDialog)
        self.outputDirPath.setObjectName(u"outputDirPath")

        self.horizontalLayout_2.addWidget(self.outputDirPath)

        self.browseOutputBtn = QPushButton(OptionsDialog)
        self.browseOutputBtn.setObjectName(u"browseOutputBtn")

        self.horizontalLayout_2.addWidget(self.browseOutputBtn)


        self.formLayout.setLayout(2, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_2)

        self.label_4 = QLabel(OptionsDialog)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_4)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.radioNone = QRadioButton(OptionsDialog)
        self.radioNone.setObjectName(u"radioNone")
        self.radioNone.setChecked(True)

        self.horizontalLayout_3.addWidget(self.radioNone)

        self.radioMat = QRadioButton(OptionsDialog)
        self.radioMat.setObjectName(u"radioMat")

        self.horizontalLayout_3.addWidget(self.radioMat)

        self.radioCsv = QRadioButton(OptionsDialog)
        self.radioCsv.setObjectName(u"radioCsv")

        self.horizontalLayout_3.addWidget(self.radioCsv)

        self.radioNpz = QRadioButton(OptionsDialog)
        self.radioNpz.setObjectName(u"radioNpz")

        self.horizontalLayout_3.addWidget(self.radioNpz)

        self.radioPkl = QRadioButton(OptionsDialog)
        self.radioPkl.setObjectName(u"radioPkl")

        self.horizontalLayout_3.addWidget(self.radioPkl)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)


        self.formLayout.setLayout(3, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_3)


        self.verticalLayout.addLayout(self.formLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_2)

        self.okButton = QPushButton(OptionsDialog)
        self.okButton.setObjectName(u"okButton")

        self.horizontalLayout_4.addWidget(self.okButton)

        self.cancelButton = QPushButton(OptionsDialog)
        self.cancelButton.setObjectName(u"cancelButton")

        self.horizontalLayout_4.addWidget(self.cancelButton)


        self.verticalLayout.addLayout(self.horizontalLayout_4)


        self.retranslateUi(OptionsDialog)
        self.okButton.clicked.connect(OptionsDialog.accept)
        self.cancelButton.clicked.connect(OptionsDialog.reject)

        QMetaObject.connectSlotsByName(OptionsDialog)
    # setupUi

    def retranslateUi(self, OptionsDialog):
        OptionsDialog.setWindowTitle(QCoreApplication.translate("OptionsDialog", u"TMS Options", None))
        self.label.setText(QCoreApplication.translate("OptionsDialog", u"Tissue Index (YAML):", None))
        self.browseTissueBtn.setText(QCoreApplication.translate("OptionsDialog", u"Browse...", None))
        self.label_2.setText(QCoreApplication.translate("OptionsDialog", u"Number of Neighbors:", None))
        self.label_3.setText(QCoreApplication.translate("OptionsDialog", u"Output Directory:", None))
        self.browseOutputBtn.setText(QCoreApplication.translate("OptionsDialog", u"Browse...", None))
        self.label_4.setText(QCoreApplication.translate("OptionsDialog", u"Save Format:", None))
        self.radioNone.setText(QCoreApplication.translate("OptionsDialog", u"none", None))
        self.radioMat.setText(QCoreApplication.translate("OptionsDialog", u"mat", None))
        self.radioCsv.setText(QCoreApplication.translate("OptionsDialog", u"csv", None))
        self.radioNpz.setText(QCoreApplication.translate("OptionsDialog", u"npz", None))
        self.radioPkl.setText(QCoreApplication.translate("OptionsDialog", u"pkl", None))
        self.okButton.setText(QCoreApplication.translate("OptionsDialog", u"OK", None))
        self.cancelButton.setText(QCoreApplication.translate("OptionsDialog", u"Cancel", None))
    # retranslateUi

