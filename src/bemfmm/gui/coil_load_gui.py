from PySide6.QtWidgets import (QDialog, QDoubleSpinBox, QFormLayout,
                               QPushButton, QSpinBox)


def coil_load_gui(coil_type, window_cord=None):
    COIL_PARAMS = {
        "ring": {
            "radius": {"type": float, "default": 0.02},
            "diameter": {"type": float, "default": 0.002},
            "M": {"type": int, "default": 16},
            "flag": {"type": int, "default": 1},
            "sk": {"type": int, "default": 1},
        },
        "figure_eight": {
            "a0": {"type": float, "default": 0.01},
            "b0": {"type": float, "default": 0.001},
            "diameter": {"type": float, "default": 0.006},
            "M": {"type": int, "default": 16},
            "flag": {"type": int, "default": 2},
            "sk": {"type": int, "default": 1},
        },
        "figure_eightX": {
            "a0": {"type": float, "default": 0.01},
            "b0": {"type": float, "default": 0.001},
            "z_scale": {"type": float, "default": 0.004},
            "z_shift": {"type": float, "default": 6},
            "height": {"type": float, "default": 4e-3},
            "thickness": {"type": float, "default": 2.5e-3},
            "M": {"type": int, "default": 16},
            "flag": {"type": int, "default": 2},
            "sk": {"type": int, "default": 1},
        },
        "MagVenture_Cool_B35": {
            "turns": {"type": int, "default": 32},
            "a0": {"type": float, "default": 0.0115},
            "a": {"type": float, "default": 15.0e-3},
            "b": {"type": float, "default": 0.2e-3},
            "M": {"type": int, "default": 20},
            "flag": {"type": int, "default": 2},
            "sk": {"type": int, "default": 0},
        },
        "MagVenture_C_B60": {
            "a0": {"type": float, "default": 0.017},
            "b0": {"type": float, "default": 0.0006},
            "height": {"type": float, "default": 3.6e-3},
            "thickness": {"type": float, "default": 2.61e-3},
            "M": {"type": int, "default": 20},
            "flag": {"type": int, "default": 2},
            "sk": {"type": int, "default": 1},
        },
        "MagVenture_Cool40_Rat": {
            "a": {"type": float, "default": 3e-3},
            "b": {"type": float, "default": 0.5e-3},
            "M": {"type": int, "default": 20},
            "flag": {"type": int, "default": 2},
            "sk": {"type": int, "default": 1},
        },
        "MagVenture_D_B80": {
            "a0": {"type": float, "default": 0.024},
            "b0": {"type": float, "default": 0.00061},
            "a": {"type": float, "default": 6e-3},
            "b": {"type": float, "default": 2e-3},
            "M": {"type": int, "default": 20},
            "flag": {"type": int, "default": 2},
            "sk": {"type": int, "default": 1},
        },
        "MagVenture_MRiB91": {
            "height": {"type": float, "default": 3.5e-3},
            "thickness": {"type": float, "default": 2.2e-3},
            "M": {"type": int, "default": 32},
            "N": {"type": int, "default": 128},
            "flag": {"type": int, "default": 2},
            "sk": {"type": int, "default": 1},
        },
        "MagVenture_TMSMEG": {
            "a": {"type": float, "default": 0.0015},
            "M": {"type": int, "default": 16},
            "N": {"type": int, "default": 64},
            "flag": {"type": int, "default": 1},
            "sk": {"type": int, "default": 1},
        },
    }
    params = COIL_PARAMS[coil_type]
    entries = {}
    result = None
    dialog = QDialog()
    dialog.setWindowTitle(f"{coil_type} Parameters")
    if window_cord:
        dialog.move(window_cord[0], window_cord[1])
    layout = QFormLayout(dialog)

    def submit():
        nonlocal result
        result = {name: widget.value() for name, widget in entries.items()}
        dialog.accept()

    for name, info in params.items():
        default = info["default"]
        param_type = info["type"]
        if param_type is int:
            widget = QSpinBox()
            widget.setValue(default)
        else:
            widget = QDoubleSpinBox()
            widget.setDecimals(6)
            widget.setValue(default)
        entries[name] = widget
        layout.addRow(name, widget)
    ok_button = QPushButton("OK")
    ok_button.clicked.connect(submit)
    layout.addRow(ok_button)
    dialog.exec()
    return result
