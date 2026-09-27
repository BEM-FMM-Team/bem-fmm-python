# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'export_dialog.ui'
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
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class Ui_ExportDialog(object):
    def setupUi(self, ExportDialog):
        if not ExportDialog.objectName():
            ExportDialog.setObjectName("ExportDialog")
        ExportDialog.resize(460, 420)
        self.dialogLayout = QVBoxLayout(ExportDialog)
        self.dialogLayout.setObjectName("dialogLayout")
        self.description = QLabel(ExportDialog)
        self.description.setObjectName("description")
        self.description.setWordWrap(True)

        self.dialogLayout.addWidget(self.description)

        self.form = QFormLayout()
        self.form.setObjectName("form")
        self.fieldsLabel = QLabel(ExportDialog)
        self.fieldsLabel.setObjectName("fieldsLabel")

        self.form.setWidget(0, QFormLayout.ItemRole.LabelRole, self.fieldsLabel)

        self.fieldList = QListWidget(ExportDialog)
        self.fieldList.setObjectName("fieldList")
        self.fieldList.setMaximumSize(QSize(16777215, 150))

        self.form.setWidget(0, QFormLayout.ItemRole.FieldRole, self.fieldList)

        self.tissueLabel = QLabel(ExportDialog)
        self.tissueLabel.setObjectName("tissueLabel")

        self.form.setWidget(1, QFormLayout.ItemRole.LabelRole, self.tissueLabel)

        self.tissueCombo = QComboBox(ExportDialog)
        self.tissueCombo.setObjectName("tissueCombo")

        self.form.setWidget(1, QFormLayout.ItemRole.FieldRole, self.tissueCombo)

        self.formatLabel = QLabel(ExportDialog)
        self.formatLabel.setObjectName("formatLabel")

        self.form.setWidget(2, QFormLayout.ItemRole.LabelRole, self.formatLabel)

        self.formatCombo = QComboBox(ExportDialog)
        self.formatCombo.addItem("")
        self.formatCombo.addItem("")
        self.formatCombo.addItem("")
        self.formatCombo.setObjectName("formatCombo")

        self.form.setWidget(2, QFormLayout.ItemRole.FieldRole, self.formatCombo)

        self.folderLabel = QLabel(ExportDialog)
        self.folderLabel.setObjectName("folderLabel")

        self.form.setWidget(3, QFormLayout.ItemRole.LabelRole, self.folderLabel)

        self.folderLayout = QHBoxLayout()
        self.folderLayout.setObjectName("folderLayout")
        self.folderEdit = QLineEdit(ExportDialog)
        self.folderEdit.setObjectName("folderEdit")

        self.folderLayout.addWidget(self.folderEdit)

        self.browseButton = QPushButton(ExportDialog)
        self.browseButton.setObjectName("browseButton")

        self.folderLayout.addWidget(self.browseButton)

        self.form.setLayout(3, QFormLayout.ItemRole.FieldRole, self.folderLayout)

        self.meshCheck = QCheckBox(ExportDialog)
        self.meshCheck.setObjectName("meshCheck")

        self.form.setWidget(4, QFormLayout.ItemRole.FieldRole, self.meshCheck)

        self.dialogLayout.addLayout(self.form)

        self.dialogSpacer = QSpacerItem(
            20, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.dialogLayout.addItem(self.dialogSpacer)

        self.buttonBox = QDialogButtonBox(ExportDialog)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok
        )

        self.dialogLayout.addWidget(self.buttonBox)

        self.retranslateUi(ExportDialog)
        self.buttonBox.accepted.connect(ExportDialog.accept)
        self.buttonBox.rejected.connect(ExportDialog.reject)

        QMetaObject.connectSlotsByName(ExportDialog)

    # setupUi

    def retranslateUi(self, ExportDialog):
        ExportDialog.setWindowTitle(
            QCoreApplication.translate("ExportDialog", "Export fields", None)
        )
        self.description.setText(
            QCoreApplication.translate(
                "ExportDialog",
                "One file per field with a value per facet. Vector fields have three columns",
                None,
            )
        )
        self.fieldsLabel.setText(
            QCoreApplication.translate("ExportDialog", "Fields", None)
        )
        self.tissueLabel.setText(
            QCoreApplication.translate("ExportDialog", "Facets", None)
        )
        self.formatLabel.setText(
            QCoreApplication.translate("ExportDialog", "Format", None)
        )
        self.formatCombo.setItemText(
            0, QCoreApplication.translate("ExportDialog", "mat", None)
        )
        self.formatCombo.setItemText(
            1, QCoreApplication.translate("ExportDialog", "npz", None)
        )
        self.formatCombo.setItemText(
            2, QCoreApplication.translate("ExportDialog", "csv", None)
        )

        self.folderLabel.setText(
            QCoreApplication.translate("ExportDialog", "Folder", None)
        )
        self.browseButton.setText(
            QCoreApplication.translate("ExportDialog", "Browse...", None)
        )
        # if QT_CONFIG(tooltip)
        self.meshCheck.setToolTip(
            QCoreApplication.translate(
                "ExportDialog",
                "Vertices P in meters and facets t, numbered from 1 in .mat files and from 0 otherwise",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.meshCheck.setText(
            QCoreApplication.translate(
                "ExportDialog", "Include the mesh (P and t)", None
            )
        )

    # retranslateUi
