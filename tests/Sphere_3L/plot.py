from engines.lib import patch


def bem5_plot_surface(
    fn,
    c,
    P,
    t,
    normals,
    interface,
    tissuename,
    plot_tissue=0,
    cmap="jet",
    title="Plot",
    cmap_label="cmap_title",
):
    plot_t_idx = interface[: len(t)] == plot_tissue  # WARN interface may not be right
    plot_t = t[plot_t_idx]
    plot_field = fn(plot_t_idx)

    patch(
        vertices=P,
        faces=plot_t,
        colors=plot_field,  # replaces p.FaceVertexCData = plot_field
        cmap="jet",  # replaces colormap("jet")
        edge_color="red",  # replaces: p.EdgeColor = "none"
        title=rf"Primary Field E^i on Surface: {tissuename}",
        colorbar_label="fn",
        axes={
            "c": "black",  # replaces set(gca,"Color","k")
            "xtitle": r"x",  # replaces xlabel("$x$")
            "ytitle": r"y",  # replaces ylabel("$y$")
            "ztitle": r"z",  # replaces zlabel("$z$")
        },
    ).show()
