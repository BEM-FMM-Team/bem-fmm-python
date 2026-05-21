#### Wrapper Script

# Wrapper script for the multi-layer sphere model.
#
# DD 5/2026
import numpy as np

from .load_model import load_model
from .setup_dipoles import setup_dipoles

eps0 = 8.85418782e-12
mu0 = 1.25663706e-06


if __name__ == "__main__":

    # -- Load model
    model = load_model()

    ## 2. Set up dipoles
    # Dipole positions are incorporated throught the primary field.
    plot_tissue = 1

    viewax = np.array([-120, 20])

    dipoles = setup_dipoles()
