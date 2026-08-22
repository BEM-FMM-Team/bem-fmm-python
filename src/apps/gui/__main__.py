import sys
from pathlib import Path
from typing import Optional

import typer
import yaml
from PySide6.QtWidgets import QApplication
from vedo import Mesh

from bemfmm.gui.gui_frontend_new import Frontend
from bemfmm.lib import get_asset_path

app = typer.Typer()


@app.command()
def main(tissue_index: Optional[str] = None):
    head_models = {}

    shells = [
        "bone",
        "cerebellum",
        "csf",
        "gm",
        "skin",
        "ventricles",
        "wm",
    ]

    if tissue_index:
        print("Using custom tissue_index")
        path = Path(tissue_index)
        if not path.is_file():
            raise ValueError(
                f"Invalid tissue index path is missing from {tissue_index}"
            )

        with open(tissue_index, "r") as f:
            d = f.read()
            data: dict[str, tuple[float, str]] = yaml.safe_load(d)

        shells = list(data.get("shells").keys())
        if not shells:
            raise ValueError(f"shells is missing from {tissue_index}")
    else:
        print("Using default tissue_index")
        tissue_index = get_asset_path(f"tissue_index.yaml")

    for name in shells:
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
