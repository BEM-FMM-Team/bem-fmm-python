from engines.lib import patch


def bem5_plot_surface(
    field_indexer,
    P,
    t,
    interface,
    plot_tissue=0,
    title="Plot",
    cmap_label="cmap_label",
    cmap="jet",
):
    plot_t_idx = interface[: len(t)] == plot_tissue  # WARN interface may not be right

    plot_t = t[plot_t_idx]
    plot_field = field_indexer(plot_t_idx)

    patch(
        vertices=P,
        faces=plot_t,
        cdata=plot_field,
        colormap=cmap,
        edge_color="black",
        title=title,
        cmap_label=cmap_label,
        axes={
            "c": "black",  # replaces set(gca,"Color","k")
            "xtitle": r"x",  # replaces xlabel("$x$")
            "ytitle": r"y",  # replaces ylabel("$y$")
            "ztitle": r"z",  # replaces zlabel("$z$")
        },
    ).show()
