"""
### Wrapper Script
This wrapper script will load the head model,
build the coil geometry,
compute the impressed field due to current flowing through the coil,
and compute the charge solution.

In matlab, this takes about 2 minutes to run to completion.

DD, DT - 5/2026
"""

import numpy as np
import vedo
from load_model import load_model

# from setup_integrals import setup_integrals

eps0 = 8.85418782e-12
mu0 = 1.25663706e-06

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
        interface,
    ) = load_model()

    mesh = vedo.Mesh([P, t])
    mesh.show()

    # -- Neighbor integrals
    # setup_integrals()
    #
    # ## 2. Setup Coil
    # # -- Load coil geometry
    # coil_setup()
    # # -- Plot coil geometry on desired tissue
    # tissue_to_plot = "wm"
    # coil_plot()
    #
    # ## 3. Impressed Field
    # impressed_field()
    # ## 4. Charge Solution
    # charge_engine()
    ## 5. Plot Fields
    # Compute and plot the fields of interest on desired tissue.

    # tissue_to_plot = "wm"
    #
    # tissue_list = string(np.array([tissues.Tissue]))
    # plot_tissue = tissues(str(tissue_list) == str(tissue_to_plot)).ID
    # viewax = np.array([160, 20])
    # # -- Plot charge
    # bem05_plot_surface_c
    # # with coil
    # plot_coil
    # # -- Plot potential
    # bem05_plot_surface_P
    # # with coil
    # plot_coil
    # # -- Plot electric field
    # bem05_plot_surface_Enin
    # # with coil
    # plot_coil
    # # -- Plot current density
    # bem05_plot_surface_Jnin
    # # with coil
    # plot_coil
