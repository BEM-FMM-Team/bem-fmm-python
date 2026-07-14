from multiprocessing import Process


def plot_fields(
    P,
    plot_t,
    plot_t_idx,
    c,
    CoilP,
    Coilt,
    Ptot,
    En,
    Jn_in,
    obs_start,
    obs_end,
):
    ## 5. Plot Fields
    # Compute and plot the fields of interest on desired tissue.

    # fmt: off
    from ..constants import eps0
    plots = [
        ("Charge Solution on Surface: ",                "C/m²", eps0 * c[plot_t_idx]),
        ("Potential on Surface: ",                      "V",     Ptot[plot_t_idx]),
        ("Normal E-field (inner) on Surface: ",         "V/m",   En[plot_t_idx]),
        ("Normal Current Density (inner) on Surface: ", "A/m²", Jn_in[plot_t_idx]),
    ]
    # fmt: on
    from engines.plot import plot_coil_worker

    plots_p = [
        Process(
            target=plot_coil_worker,
            args=(
                P,
                plot_t,
                p,
                CoilP,
                Coilt,
                obs_start,
                obs_end,
            ),
        )
        for p in plots
    ]

    for p in plots_p:
        p.start()
