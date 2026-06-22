"""
"Wrapper Script

Wrapper script for the multi-layer sphere model.

DD 5/2026
SP 6/2026
"""

import sys
from pathlib import Path

import numpy as np

root_dir = Path(__file__).resolve().parent.resolve().parent.resolve().parent.absolute()
sys.path.insert(0, str(root_dir))

print(f"Setup environment {root_dir}")

from load_model import load_model
from setup_dipoles import setup_dipoles

from engines.plot import patch

if __name__ == "__main__":
    # Load model
    (
        P,
        t,
        normals,
        Center,
        Area,
        contrast,
        condinner,
        condin,
        condouter,
        condout,
        tissuename,
    ) = load_model()

    ## 2. Set up dipoles
    # Dipole positions are incorporated throught the primary field.
    plot_tissue = 1

    Epri, Ppri = setup_dipoles(
        P,
        t,
        normals,
        Center,
        Area,
        contrast,
        condinner,
        condin,
        condouter,
        condout,
        tissuename,
    )

    ## Plot primary field
    Eprin = np.sum(Epri * normals, 1)

    plot_t_idx = np.ones(
        t.shape[0], dtype=bool
    )  # NOTE: for future reference this will be selecting a tissue
    plot_t = t[plot_t_idx]
    plot_field = Eprin[plot_t_idx]

    viewax = np.array([-120, 20])  # TODO embed

    _p = patch(
        vertices=P,
        faces=plot_t,
        cdata=plot_field,
        edge_color="none",
        title=rf"Primary Field Eⁱ on Surface: {tissuename[0]}",
        cmap_label="A/m²",
    )
    from engines.lib import io

    if io:
        _p.show()
