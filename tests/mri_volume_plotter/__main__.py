"""
This wrapper script will load the head model,
build the coil geometry,
compute the impressed field due to current flowing through the coil,
and compute the charge solution.

In matlab, this takes about 2 minutes to run to completion.

DD, DT - 5/2026
SP 6/2026
"""

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.resolve().parent.resolve().parent.absolute()
sys.path.insert(0, str(root_dir))

test_dir = Path(__file__).resolve().parent.resolve().parent
coil_single_ring_dir = test_dir / "coil_single_ring"
sys.path.insert(0, str(coil_single_ring_dir))


ASSETS = (coil_single_ring_dir / "assets").resolve()

sys.path.insert(0, str(test_dir))


if __name__ == "__main__":
    # pyrefly: ignore [missing-import]
    import coil_single_ring

    (
        P,
        t,
        Center,
        Area,
        normals,
        c,
        interface,
        tissue_list,
        plot_t,
        plot_t_idx,
        CoilP,
        Coilt,
        Ptot,
        En,
        Jn_in,
        obs_start,
        obs_end,
        xyz,
    ) = coil_single_ring.main()

    from engines.plot import plot_slices

    plot_slices(
        P,
        t,
        Center,
        Area,
        normals,
        c,
        interface,
        tissue_list,
        xyz,
    )
