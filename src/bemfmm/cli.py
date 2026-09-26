import os
import sys
from pathlib import Path
from time import perf_counter
from typing import Literal, Optional

import typer

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    help="Charge based BEM-FMM for TMS and tDCS",
)

SaveFormat = Literal["none", "csv", "mat", "npz", "pkl"]


def resolve_index(tissue_index, scene):
    from bemfmm.model import default_index

    if tissue_index:
        return Path(tissue_index)
    if scene is not None and scene.tissue_index:
        return Path(scene.tissue_index)
    return default_index()


def output_path(output_dir):
    if output_dir is None:
        output_dir = Path(os.getcwd()) / "__output__"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    f = open(output_dir / ".gitignore", "w")
    f.close()
    return output_dir


def progress_printer(enabled):
    # machine readable progress for the gui, one line per update
    if not enabled:
        return None

    def progress(stage, done, total):
        print(f"@progress {stage} {done} {total}", flush=True)

    return progress


def save_fields(result, output_dir, save_format, save):
    if save_format == "none":
        return
    names = []
    for name in save:
        if name not in result.fields:
            print(f"{name} is not a field of this result, skipping")
            continue
        names.append(name)
    # per facet values are written as columns, like the matlab code
    for name, path in zip(names, result.export(output_dir, names, save_format)):
        print(f"Saved {name} to {path}")


def write_slices(result, output_dir, planes, coils=(), progress=None):
    from bemfmm.plot.results import compute_slices, default_planes
    from bemfmm.plot.slice import save_slices

    if planes is None:
        planes = default_planes(result, coils) if coils else (0.0, 0.0, 0.0)
    start = perf_counter()
    slices = compute_slices(result, planes, "gm", coils, progress)
    path = save_slices(
        output_dir / "slices.npz",
        slices,
        planes,
        result.tissues,
        result.info.get("created", ""),
    )
    print(f"Saved slices to {path} in {perf_counter() - start:.1f}s")
    return slices


def saved_slices(directory, result):
    # slices.npz from `bemfmm slices` or --slices, if it belongs to this result
    from bemfmm.plot.slice import load_slices

    path = Path(directory) / "slices.npz"
    if not path.is_file():
        return None
    data = load_slices(path)
    if data["created"] != result.info.get("created", ""):
        return None
    return data


def wait_for_windows(plot):
    # the plot windows are child processes, keep the terminal open until they close
    if plot:
        print("Close all plot windows to exit")


@app.command()
def gui(
    tissue_index: Optional[str] = typer.Option(None, help="Tissue index to open"),
    setup: Optional[str] = typer.Option(None, help="Setup (.json) to open"),
    no_3d: bool = typer.Option(
        False, "--no-3d", help="Run without the 3D view, for remote desktops"
    ),
):
    """Open the graphical interface."""
    from bemfmm.gui.app import run

    sys.exit(run(tissue_index, setup, no_3d))


@app.command()
def tms(
    setup: Optional[str] = typer.Option(None, help="Setup (.json) with coils"),
    tissue_index: Optional[str] = None,
    num_neighbors: int = 4,
    iter: int = 20,  # for best results, set to 50
    relres: float = 1e-4,  # for best results, set to 1e-6
    weight: float = 0.5,
    output_dir: Optional[str] = None,
    save_format: SaveFormat = "none",
    save: list[str] = typer.Option(["E", "c", "En"], "--save", "-s"),
    plot_tissue: str = "wm",
    slices: bool = typer.Option(False, help="Also save E-field slices"),
    plot: bool = True,
    progress: bool = typer.Option(False, hidden=True),
):
    """Solve TMS for the coils in a setup, or the default coil."""
    from bemfmm.coils import default_coil
    from bemfmm.model import HeadModel
    from bemfmm.plot.results import show_tms
    from bemfmm.scene import Scene
    from bemfmm.solvers.tms import TMSOptions, solve

    scene = Scene.load(setup) if setup else None
    model = HeadModel.load(resolve_index(tissue_index, scene))

    if scene is None:
        coils, planes = [default_coil()], None
        print("Using Default coil")
    else:
        coils, planes = scene.coils, scene.planes
        print(f"Using coils from {setup}")

    start = perf_counter()
    result = solve(
        model,
        coils,
        TMSOptions(num_neighbors, iter, relres, weight),
        progress_printer(progress),
    )
    print(f"Solved in {perf_counter() - start:.1f}s")

    output_dir = output_path(output_dir)
    print(f"Saved result to {result.save(output_dir)}")
    save_fields(result, output_dir, save_format, save)
    slice_data = None
    if slices:
        slice_data = write_slices(
            result, output_dir, planes, coils, progress_printer(progress)
        )

    if plot:
        show_tms(result, coils, planes, plot_tissue, slices=slice_data)
    wait_for_windows(plot)


@app.command()
def tdcs(
    setup: Optional[str] = typer.Option(None, help="Setup (.json) with electrodes"),
    tissue_index: Optional[str] = None,
    skin: Optional[str] = typer.Option(
        None, help="Tissue the electrodes sit on, from the setup or skin"
    ),
    num_neighbors: int = 4,
    num_neighbors_p: int = 32,
    iter: int = 50,
    relres: float = 1e-6,
    weight: float = 0.5,
    output_dir: Optional[str] = None,
    save_format: SaveFormat = "none",
    save: list[str] = typer.Option(["E", "c", "En"], "--save", "-s"),
    plot_tissue: str = "gm",
    slices: bool = typer.Option(False, help="Also save E-field slices"),
    plot: bool = True,
    progress: bool = typer.Option(False, hidden=True),
):
    """Solve tDCS for the electrodes in a setup, or the default montage."""
    from bemfmm.model import HeadModel
    from bemfmm.plot.results import show_tdcs
    from bemfmm.scene import Scene
    from bemfmm.solvers.tdcs import TDCSOptions, default_electrodes, solve

    scene = Scene.load(setup) if setup else None
    model = HeadModel.load(resolve_index(tissue_index, scene))

    if scene is None:
        electrodes, planes = default_electrodes(), (0.0, 0.0, 0.0)
        print("Using Default electrodes")
    else:
        electrodes, planes = scene.electrodes, scene.planes
        print(f"Using electrodes from {setup}")
    skin = skin or (scene.skin if scene else "") or "skin"

    start = perf_counter()
    result = solve(
        model,
        electrodes,
        TDCSOptions(num_neighbors, num_neighbors_p, iter, relres, weight, skin),
        progress_printer(progress),
    )
    print(f"Solved in {perf_counter() - start:.1f}s")

    info = result.info
    print("\nElectrode      Set [V]   Solved [V]   Current [mA]")
    for e in info["electrodes"]:
        print(
            f"{e['name']:<12} {e['voltage']:>9.4f} {e['solved_voltage']:>12.4f} {e['current'] * 1e3:>14.4f}"
        )
    print(
        f"""Total current (should be ~0): {info['total_current'] * 1e3:.4e} mA
Power loss: {info['power']:.4e} W"""
    )

    output_dir = output_path(output_dir)
    print(f"Saved result to {result.save(output_dir)}")
    save_fields(result, output_dir, save_format, save)
    slice_data = None
    if slices:
        slice_data = write_slices(
            result, output_dir, planes, progress=progress_printer(progress)
        )

    if plot:
        show_tdcs(result, planes, plot_tissue, skin, slice_data)
    wait_for_windows(plot)


@app.command()
def sphere(
    num_neighbors: int = typer.Option(0, help="0 skips the neighbor integrals"),
    output_dir: Optional[str] = None,
    plot: bool = True,
    progress: bool = typer.Option(False, hidden=True),
):
    """Three layer sphere in a uniform field, a check of the charge engine."""
    from bemfmm.model import HeadModel, sphere_index
    from bemfmm.plot.results import show_uniform
    from bemfmm.solvers.uniform import UniformOptions, solve

    model = HeadModel.load(sphere_index())
    result = solve(
        model, UniformOptions(num_neighbors=num_neighbors), progress_printer(progress)
    )

    output_dir = output_path(output_dir)
    print(f"Saved result to {result.save(output_dir)}")

    if plot:
        show_uniform(result)
    wait_for_windows(plot)


@app.command()
def show(
    result: str = typer.Argument(..., help="Result folder or its result.json"),
    plot_tissue: Optional[str] = None,
):
    """Open the plot windows for a saved result."""
    from bemfmm.coils import Coil
    from bemfmm.plot.results import show_tdcs, show_tms, show_uniform
    from bemfmm.results import Result
    from bemfmm.scene import Scene

    path = Path(result)
    directory = path if path.is_dir() else path.parent
    res = Result.load(directory)

    setup = directory / "setup.json"
    planes = Scene.load(setup).planes if setup.is_file() else None
    saved = saved_slices(directory, res)
    slices = None
    if saved is not None:
        slices, planes = saved["slices"], saved["planes"]

    if res.kind == "tms":
        coils = [Coil.from_dict(d) for d in res.info["coils"]]
        show_tms(res, coils, planes, plot_tissue or "wm", slices=slices)
    elif res.kind == "tdcs":
        skin = res.info["options"]["skin"]
        planes = planes or (0.0, 0.0, 0.0)
        show_tdcs(res, planes, plot_tissue or "gm", skin, slices)
    else:
        show_uniform(res, plot_tissue or "gm")
    wait_for_windows(True)


@app.command("slices")
def slices_command(
    result: str = typer.Argument(..., help="Result folder or its result.json"),
    planes: Optional[tuple[float, float, float]] = typer.Option(
        None, help="x y z of the slice planes in mm, from the setup by default"
    ),
    progress: bool = typer.Option(False, hidden=True),
):
    """Compute E-field slices for a saved result, saved next to it."""
    from bemfmm.coils import Coil
    from bemfmm.results import Result
    from bemfmm.scene import Scene

    path = Path(result)
    directory = path if path.is_dir() else path.parent
    res = Result.load(directory)
    coils = [Coil.from_dict(d) for d in res.info.get("coils", [])]

    if planes:
        planes = tuple(p * 1e-3 for p in planes)
    elif (directory / "setup.json").is_file():
        planes = Scene.load(directory / "setup.json").planes
    else:
        planes = None
    write_slices(res, directory, planes, coils, progress_printer(progress))


@app.command()
def dipole():
    """Primary field of a current dipole on a skull surface."""
    from bemfmm.examples.dipole import run

    run()


@app.command("export-matlab")
def export_matlab(
    tissue_index: Optional[str] = None,
    out: str = typer.Option("CombinedMesh.mat", help="Output .mat file"),
):
    """Write a tissue index as CombinedMesh.mat for the matlab scripts."""
    from bemfmm.export import export_matlab as export
    from bemfmm.model import HeadModel

    model = HeadModel.load(resolve_index(tissue_index, None))
    export(model, out)
    print(f"Saved {out}")


if __name__ == "__main__":
    app()
