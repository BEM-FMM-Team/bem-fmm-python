# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'project_dialog.ui'
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
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class Ui_ProjectDialog(object):
    def setupUi(self, ProjectDialog):
        if not ProjectDialog.objectName():
            ProjectDialog.setObjectName("ProjectDialog")
        ProjectDialog.resize(560, 380)
        self.dialogLayout = QVBoxLayout(ProjectDialog)
        self.dialogLayout.setObjectName("dialogLayout")
        self.description = QLabel(ProjectDialog)
        self.description.setObjectName("description")
        self.description.setWordWrap(True)

        self.dialogLayout.addWidget(self.description)

        self.projectList = QListWidget(ProjectDialog)
        self.projectList.setObjectName("projectList")

        self.dialogLayout.addWidget(self.projectList)

        self.projectButtons = QHBoxLayout()
        self.projectButtons.setObjectName("projectButtons")
        self.openFolderButton = QPushButton(ProjectDialog)
        self.openFolderButton.setObjectName("openFolderButton")

        self.projectButtons.addWidget(self.openFolderButton)

        self.newProjectButton = QPushButton(ProjectDialog)
        self.newProjectButton.setObjectName("newProjectButton")

        self.projectButtons.addWidget(self.newProjectButton)

        self.projectButtonSpacer = QSpacerItem(
            0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.projectButtons.addItem(self.projectButtonSpacer)

        self.askCheck = QCheckBox(ProjectDialog)
        self.askCheck.setObjectName("askCheck")
        self.askCheck.setChecked(True)

        self.projectButtons.addWidget(self.askCheck)

        self.dialogLayout.addLayout(self.projectButtons)

        self.buttonBox = QDialogButtonBox(ProjectDialog)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(
            QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Open
        )

        self.dialogLayout.addWidget(self.buttonBox)

        self.retranslateUi(ProjectDialog)
        self.buttonBox.accepted.connect(ProjectDialog.accept)
        self.buttonBox.rejected.connect(ProjectDialog.reject)

        QMetaObject.connectSlotsByName(ProjectDialog)

    # setupUi

    def retranslateUi(self, ProjectDialog):
        ProjectDialog.setWindowTitle(
            QCoreApplication.translate("ProjectDialog", "Open project", None)
        )
        self.description.setText(
            QCoreApplication.translate(
                "ProjectDialog",
                "A project is a folder with a head model, its setups and its runs. The bundled models are read only, copy one to work in it.",
                None,
            )
        )
        # if QT_CONFIG(tooltip)
        self.openFolderButton.setToolTip(
            QCoreApplication.translate(
                "ProjectDialog",
                "A folder with a project.yaml or a tissue_index.yaml",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.openFolderButton.setText(
            QCoreApplication.translate("ProjectDialog", "Open folder...", None)
        )
        # if QT_CONFIG(tooltip)
        self.newProjectButton.setToolTip(
            QCoreApplication.translate(
                "ProjectDialog",
                "A new project from closed surface meshes, nested by which contains which",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.newProjectButton.setText(
            QCoreApplication.translate("ProjectDialog", "New from surfaces...", None)
        )
        self.askCheck.setText(
            QCoreApplication.translate("ProjectDialog", "Ask at startup", None)
        )

    # retranslateUi
