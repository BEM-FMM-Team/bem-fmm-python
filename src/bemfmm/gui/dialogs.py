from PySide6.QtWidgets import QDialog, QDialogButtonBox, QDoubleSpinBox, QSpinBox

from bemfmm.coils import COIL_PARAMS

from .ui_coil_params import Ui_CoilParamsDialog


class CoilParamsDialog(QDialog):
    """
    Generator parameters for a new coil, one row per parameter
    """

    def __init__(self, coil_type, parent=None):
        super().__init__(parent)
        self.ui = Ui_CoilParamsDialog()
        self.ui.setupUi(self)
        self.setWindowTitle(f"{coil_type} parameters")

        self.params = COIL_PARAMS[coil_type]
        self.entries = {}
        for name, info in self.params.items():
            if info["type"] is int:
                widget = QSpinBox()
                widget.setRange(0, 100000)
            else:
                widget = QDoubleSpinBox()
                widget.setDecimals(6)
                widget.setRange(-1000.0, 1000.0)
                widget.setSingleStep(0.0005)
            self.entries[name] = widget
            self.ui.form.addRow(name, widget)

        self.restore_defaults()
        self.ui.buttonBox.button(
            QDialogButtonBox.StandardButton.RestoreDefaults
        ).clicked.connect(self.restore_defaults)

    def restore_defaults(self):
        for name, widget in self.entries.items():
            widget.setValue(self.params[name]["default"])

    def values(self):
        return {name: widget.value() for name, widget in self.entries.items()}
