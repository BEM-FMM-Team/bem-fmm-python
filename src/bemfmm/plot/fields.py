from multiprocessing import Process


def plot_fields(
    P,
    plot_t,
    plot_t_idx,
    c,
    coils,
    Ptot,
    En,
    Emag,
    Jn_in,
):
    ## 5. Plot Fields
    # Compute and plot the fields of interest on desired tissue.

    # fmt: off
    from ..constants import eps0

    # plots = [
    #     ("Charge Solution on Surface: ",                "C/m²",  eps0 * c[plot_t_idx], "jet"),
    #     ("Secondary Potential on Surface: ",            "V",     Ptot[plot_t_idx], "jet"),
    #     ("Normal E-field (inner) on Surface: ",         "V/m",   En[plot_t_idx], "jet"),
    #     ("E-field Magnitude on Surface: ",              "V/m",   Emag[plot_t_idx], "jet"),
    #     ("Normal Current Density (inner) on Surface: ", "A/m²",  Jn_in[plot_t_idx], "jet"),
    # ]
    # For demo
    plots = [
        ("E-field Magnitude on Surface: ",              "V/m",   Emag[plot_t_idx], "jet")
    ]
    # fmt: on
    from bemfmm.plot import plot_coil_worker

    plots_p = [
        Process(
            target=plot_coil_worker,
            args=(
                P,
                plot_t,
                p,
                coils,
            ),
        )
        for p in plots
    ]

    for p in plots_p:
        p.start()
