# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'coil_params.ui'
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
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class Ui_CoilParamsDialog(object):
    def setupUi(self, CoilParamsDialog):
        if not CoilParamsDialog.objectName():
            CoilParamsDialog.setObjectName("CoilParamsDialog")
        CoilParamsDialog.resize(320, 300)
        self.dialogLayout = QVBoxLayout(CoilParamsDialog)
        self.dialogLayout.setObjectName("dialogLayout")
        self.description = QLabel(CoilParamsDialog)
        self.description.setObjectName("description")
        self.description.setWordWrap(True)

        self.dialogLayout.addWidget(self.description)

        self.form = QFormLayout()
        self.form.setObjectName("form")

        self.dialogLayout.addLayout(self.form)

        self.dialogSpacer = QSpacerItem(
            20, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.dialogLayout.addItem(self.dialogSpacer)

        self.buttonBox = QDialogButtonBox(CoilParamsDialog)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(
            QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.RestoreDefaults
        )

        self.dialogLayout.addWidget(self.buttonBox)

        self.retranslateUi(CoilParamsDialog)
        self.buttonBox.accepted.connect(CoilParamsDialog.accept)
        self.buttonBox.rejected.connect(CoilParamsDialog.reject)

        QMetaObject.connectSlotsByName(CoilParamsDialog)

    # setupUi

    def retranslateUi(self, CoilParamsDialog):
        CoilParamsDialog.setWindowTitle(
            QCoreApplication.translate("CoilParamsDialog", "Coil parameters", None)
        )
        self.description.setText(
            QCoreApplication.translate(
                "CoilParamsDialog", "Lengths are in meters", None
            )
        )

    # retranslateUi
