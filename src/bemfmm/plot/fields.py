from multiprocessing import Process


def plot_fields(P, plot_t, plot_t_idx, coils, Emag):
    plots = [("E-field Magnitude on Surface: ", "V/m", Emag[plot_t_idx], "jet")]
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
