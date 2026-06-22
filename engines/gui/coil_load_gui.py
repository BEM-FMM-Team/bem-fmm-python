import tkinter as tk
from tkinter import ttk


def coil_load_gui(coil_type):
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
    }
    params = COIL_PARAMS[coil_type]
    entries = {}
    row = 0
    editor = tk.Toplevel()
    editor.title("Ring Parameters")
    result = None

    def submit():
        nonlocal result

        result = {name: var.get() for name, var in entries.items()}
        editor.destroy()

    for name, info in params.items():

        ttk.Label(editor, text=name).grid(row=row, column=0, padx=5, pady=5)

        default = info["default"]
        param_type = info["type"]

        if param_type is int:
            var = tk.IntVar(value=default)
        else:
            var = tk.DoubleVar(value=default)

        ttk.Entry(editor, textvariable=var).grid(row=row, column=1, padx=5, pady=5)
        entries[name] = var
        row += 1
    ttk.Button(editor, text="OK", command=submit).grid(
        row=row, column=0, columnspan=2, pady=10
    )
    editor.grab_set()
    editor.wait_window()
    return result
