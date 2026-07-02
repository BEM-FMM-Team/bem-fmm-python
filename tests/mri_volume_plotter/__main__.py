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

from compute_efield_overlay import compute_efield_overlay_worker

ASSETS = (coil_single_ring_dir / "assets").resolve()

sys.path.insert(0, str(test_dir))
import coil_single_ring


def plot(
    P,
    t,
    Center,
    Area,
    normals,
    c,
    interface,
    tissue_list,
    single_p,
    plot_t,
    plot_t_idx,
    CoilP,
    Coilt,
    Ptot,
    En,
    Jn_in,
    resvec,
    obs_start,
    obs_end,
    xyz,
):
    unit_convert = 1e-3  # mm
    X = -37.4 * unit_convert
    Y = 20 * unit_convert
    Z = 20 * unit_convert

    X = xyz[0]
    Y = xyz[1]
    Z = xyz[2]

    compute_efield_overlay_worker(
        P, t, Center, Area, normals, c, "XY", Z, interface, tissue_list
    )
    compute_efield_overlay_worker(
        P, t, Center, Area, normals, c, "XZ", Y, interface, tissue_list
    )
    compute_efield_overlay_worker(
        P, t, Center, Area, normals, c, "YZ", X, interface, tissue_list
    )


if __name__ == "__main__":
    (
        P,
        t,
        Center,
        Area,
        normals,
        c,
        interface,
        tissue_list,
        single_p,
        plot_t,
        plot_t_idx,
        CoilP,
        Coilt,
        Ptot,
        En,
        Jn_in,
        resvec,
        obs_start,
        obs_end,
        xyz,
    ) = coil_single_ring.main()
    plot(
        P,
        t,
        Center,
        Area,
        normals,
        c,
        interface,
        tissue_list,
        single_p,
        plot_t,
        plot_t_idx,
        CoilP,
        Coilt,
        Ptot,
        En,
        Jn_in,
        resvec,
        obs_start,
        obs_end,
        xyz,
    )
