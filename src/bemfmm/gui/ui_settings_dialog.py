# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings_dialog.ui'
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
    QAbstractButton,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        if not SettingsDialog.objectName():
            SettingsDialog.setObjectName("SettingsDialog")
        SettingsDialog.resize(480, 380)
        self.dialogLayout = QVBoxLayout(SettingsDialog)
        self.dialogLayout.setObjectName("dialogLayout")
        self.appearanceGroup = QGroupBox(SettingsDialog)
        self.appearanceGroup.setObjectName("appearanceGroup")
        self.appearanceLayout = QFormLayout(self.appearanceGroup)
        self.appearanceLayout.setObjectName("appearanceLayout")
        self.themeLabel = QLabel(self.appearanceGroup)
        self.themeLabel.setObjectName("themeLabel")

        self.appearanceLayout.setWidget(
            0, QFormLayout.ItemRole.LabelRole, self.themeLabel
        )

        self.themeCombo = QComboBox(self.appearanceGroup)
        self.themeCombo.addItem("")
        self.themeCombo.addItem("")
        self.themeCombo.addItem("")
        self.themeCombo.setObjectName("themeCombo")

        self.appearanceLayout.setWidget(
            0, QFormLayout.ItemRole.FieldRole, self.themeCombo
        )

        self.dialogLayout.addWidget(self.appearanceGroup)

        self.modelGroup = QGroupBox(SettingsDialog)
        self.modelGroup.setObjectName("modelGroup")
        self.modelLayout = QFormLayout(self.modelGroup)
        self.modelLayout.setObjectName("modelLayout")
        self.skinLabel = QLabel(self.modelGroup)
        self.skinLabel.setObjectName("skinLabel")

        self.modelLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.skinLabel)

        self.skinEdit = QLineEdit(self.modelGroup)
        self.skinEdit.setObjectName("skinEdit")

        self.modelLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.skinEdit)

        self.startModeLabel = QLabel(self.modelGroup)
        self.startModeLabel.setObjectName("startModeLabel")

        self.modelLayout.setWidget(
            1, QFormLayout.ItemRole.LabelRole, self.startModeLabel
        )

        self.startModeCombo = QComboBox(self.modelGroup)
        self.startModeCombo.addItem("")
        self.startModeCombo.addItem("")
        self.startModeCombo.addItem("")
        self.startModeCombo.setObjectName("startModeCombo")

        self.modelLayout.setWidget(
            1, QFormLayout.ItemRole.FieldRole, self.startModeCombo
        )

        self.dialogLayout.addWidget(self.modelGroup)

        self.runsGroup = QGroupBox(SettingsDialog)
        self.runsGroup.setObjectName("runsGroup")
        self.runsLayout = QFormLayout(self.runsGroup)
        self.runsLayout.setObjectName("runsLayout")
        self.outputLabel = QLabel(self.runsGroup)
        self.outputLabel.setObjectName("outputLabel")

        self.runsLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.outputLabel)

        self.outputLayout = QHBoxLayout()
        self.outputLayout.setObjectName("outputLayout")
        self.outputEdit = QLineEdit(self.runsGroup)
        self.outputEdit.setObjectName("outputEdit")

        self.outputLayout.addWidget(self.outputEdit)

        self.browseButton = QPushButton(self.runsGroup)
        self.browseButton.setObjectName("browseButton")

        self.outputLayout.addWidget(self.browseButton)

        self.runsLayout.setLayout(0, QFormLayout.ItemRole.FieldRole, self.outputLayout)

        self.slicesCheck = QCheckBox(self.runsGroup)
        self.slicesCheck.setObjectName("slicesCheck")

        self.runsLayout.setWidget(
            1, QFormLayout.ItemRole.SpanningRole, self.slicesCheck
        )

        self.dialogLayout.addWidget(self.runsGroup)

        self.dialogSpacer = QSpacerItem(
            20, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.dialogLayout.addItem(self.dialogSpacer)

        self.buttonBox = QDialogButtonBox(SettingsDialog)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(
            QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.RestoreDefaults
        )

        self.dialogLayout.addWidget(self.buttonBox)

        self.retranslateUi(SettingsDialog)
        self.buttonBox.accepted.connect(SettingsDialog.accept)
        self.buttonBox.rejected.connect(SettingsDialog.reject)

        QMetaObject.connectSlotsByName(SettingsDialog)

    # setupUi

    def retranslateUi(self, SettingsDialog):
        SettingsDialog.setWindowTitle(
            QCoreApplication.translate("SettingsDialog", "Settings", None)
        )
        self.appearanceGroup.setTitle(
            QCoreApplication.translate("SettingsDialog", "Appearance", None)
        )
        self.themeLabel.setText(
            QCoreApplication.translate("SettingsDialog", "Theme", None)
        )
        self.themeCombo.setItemText(
            0, QCoreApplication.translate("SettingsDialog", "System", None)
        )
        self.themeCombo.setItemText(
            1, QCoreApplication.translate("SettingsDialog", "Light", None)
        )
        self.themeCombo.setItemText(
            2, QCoreApplication.translate("SettingsDialog", "Dark", None)
        )

        # if QT_CONFIG(tooltip)
        self.themeCombo.setToolTip(
            QCoreApplication.translate(
                "SettingsDialog",
                "System follows the light or dark setting of the operating system",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.modelGroup.setTitle(
            QCoreApplication.translate("SettingsDialog", "Model", None)
        )
        self.skinLabel.setText(
            QCoreApplication.translate("SettingsDialog", "Skin tissue", None)
        )
        # if QT_CONFIG(tooltip)
        self.skinEdit.setToolTip(
            QCoreApplication.translate(
                "SettingsDialog",
                "Name of the scalp surface in the tissue index. Coils and electrodes are placed on it unless another surface is picked",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.startModeLabel.setText(
            QCoreApplication.translate("SettingsDialog", "Start in", None)
        )
        self.startModeCombo.setItemText(
            0, QCoreApplication.translate("SettingsDialog", "Last used mode", None)
        )
        self.startModeCombo.setItemText(
            1, QCoreApplication.translate("SettingsDialog", "TMS", None)
        )
        self.startModeCombo.setItemText(
            2, QCoreApplication.translate("SettingsDialog", "tDCS", None)
        )

        self.runsGroup.setTitle(
            QCoreApplication.translate("SettingsDialog", "Runs", None)
        )
        self.outputLabel.setText(
            QCoreApplication.translate("SettingsDialog", "Output folder", None)
        )
        self.browseButton.setText(
            QCoreApplication.translate("SettingsDialog", "Browse...", None)
        )
        # if QT_CONFIG(tooltip)
        self.slicesCheck.setToolTip(
            QCoreApplication.translate(
                "SettingsDialog",
                "Adds a few seconds to a minute to each run, depending on the model",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.slicesCheck.setText(
            QCoreApplication.translate(
                "SettingsDialog", "Compute E-field slices after each run", None
            )
        )

    # retranslateUi
