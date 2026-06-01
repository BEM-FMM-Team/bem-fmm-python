import multiprocessing
import os
import sys
from pathlib import Path

os.environ["MKL_NUM_THREADS"] = str(multiprocessing.cpu_count() - 1)
os.environ["OMP_NUM_THREADS"] = str(multiprocessing.cpu_count() - 1)

root_dir = Path(__file__).resolve().parent.resolve().parent.resolve().parent.absolute()
sys.path.insert(0, str(root_dir))

print(f"Setup environment {root_dir}")


"""
"Wrapper Script

Wrapper script for the multi-layer sphere model.

DD 5/2026
"""

from load_model import load_model
from setup_dipoles import setup_dipoles

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

    dipoles = setup_dipoles(
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
