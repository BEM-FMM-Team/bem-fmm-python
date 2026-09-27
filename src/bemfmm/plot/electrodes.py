import vedo

from .patch import _PATCH_CONFIGS, patch


def plot_electrode_worker(P, plot_t, p, electrode_t, electrode_voltages):
    plt = patch(
        vertices=P,
        faces=plot_t,
        title=p[0],
        cmap_label=p[1],
        cdata=p[2],
        config=_PATCH_CONFIGS[p[3]],
    )

    for et, voltage in zip(electrode_t, electrode_voltages):
        color = "red" if voltage > 0 else "blue" if voltage < 0 else "grey"
        plt.add(vedo.Mesh([P, et]).color(color))

    plt.show()
