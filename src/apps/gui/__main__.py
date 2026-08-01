import sys

import typer
from PySide6.QtWidgets import QApplication
from vedo import Mesh

from bemfmm.gui.gui_frontend_new import Frontend
from bemfmm.lib import get_asset_path

app = typer.Typer()


@app.command()
def main():
    head_models = {}

    for name in [
        "bone",
        "cerebellum",
        "csf",
        "gm",
        "skin",
        "ventricles",
        "wm",
    ]:
        path = get_asset_path(f"{name}.stl")

        mesh = Mesh(str(path))
        mesh.vertices *= 1e-3

        head_models[name] = mesh

    qapp = QApplication(sys.argv)

    frontend = Frontend(
        head_models,
        [
            "ring",
            "figure_eight",
            "figure_eightX",
            "MagVenture_Cool_B35",
            # "MagVenture_C_B60",
            "MagVenture_Cool40_Rat",
            "MagVenture_D_B80",
            "MagVenture_MRiB91",
            "MagVenture_TMSMEG",
        ],
    )

    frontend.show()

    qapp.exec()


if __name__ == "__main__":
    app()
