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

    print(t.shape)

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
