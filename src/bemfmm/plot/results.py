from multiprocessing import Process

import numpy as np
import vedo

from bemfmm.constants import eps0
from bemfmm.mesh import mesh_areas, mesh_tricenter
from bemfmm.results import Result

from .compute_efield_overlay import compute_efield_overlay
from .electrodes import plot_electrode_worker
from .fields import plot_fields
from .patch import plot_worker
from .residual import plot_residual
from .slice import SLICE_PLANES, plot_efield_slice


def tissue_or_last(result: Result, tissue):
    # models without the usual tissue names fall back to the innermost shell
    return tissue if tissue in result.tissues else result.tissues[-1]


def default_planes(result: Result, coils, tissue="wm"):
    # through the point where the first coil axis meets the tissue
    t = result.t[result.facets(tissue_or_last(result, tissue))]
    i = vedo.Mesh([result.P, t]).intersect_with_line(*coils[0].centerline)
    return i[0] if len(i) > 0 else [0.5, 0.5, 0.5]


def compute_slices(result: Result, xyz, th_tissue="gm", coils=(), progress=None):
    # Threshold to min and max of Emag on th_tissue
    th_tissue = tissue_or_last(result, th_tissue)
    Emag = result.fields["Emag"][result.facets(th_tissue)]
    center = mesh_tricenter(result.P, result.t)
    area = mesh_areas(result.P, result.t)

    slices = {}
    for i, (plane, val) in enumerate(zip(SLICE_PLANES, (xyz[2], xyz[1], xyz[0]))):
        if progress:
            progress("slices", i, len(SLICE_PLANES))
        slices[plane] = compute_efield_overlay(
            P=result.P,
            t=result.t,
            centers=center,
            area=area,
            normals=result.normals,
            c=result.fields["c"].reshape((-1, 1)),
            plane=plane,
            val=val,
            interface=result.interface,
            coils=list(coils),
            th1=np.nanmax(Emag),
            th2=np.nanmin(Emag),
        )
    if progress:
        progress("slices", len(SLICE_PLANES), len(SLICE_PLANES))
    return slices


def show_slices(result: Result, xyz, th_tissue, coils=(), slices=None):
    if slices is None:
        slices = compute_slices(result, xyz, th_tissue, coils)
    for data in slices.values():
        Process(target=plot_efield_slice, args=(data, result.tissues)).start()


def show_tms(
    result: Result,
    coils,
    planes=None,
    plot_tissue="wm",
    slice_tissue="gm",
    slices=None,
):
    plot_residual(result.resvec)

    plot_tissue = tissue_or_last(result, plot_tissue)
    plot_t_idx = result.facets(plot_tissue)
    plot_t = result.t[plot_t_idx]
    f = result.fields

    # move from m to mm for displaying
    plot_fields(
        result.P * 1e3,
        plot_t,
        plot_t_idx,
        f["c"].reshape((-1, 1)),
        [(coil.centerline * 1e3, coil.cad_P * 1e3, coil.t) for coil in coils],
        None,
        f["En"].reshape((-1, 1)),
        f["Emag"],
        f["Jn"].reshape((-1, 1)),
    )

    xyz = default_planes(result, coils, plot_tissue) if planes is None else planes
    show_slices(result, xyz, slice_tissue, coils, slices)


def show_tdcs(result: Result, planes, plot_tissue="gm", skin="skin", slices=None):
    plot_residual(result.resvec)

    f = result.fields
    P_mm = result.P * 1e3
    voltages = [e["voltage"] for e in result.info["electrodes"]]
    electrode_t = [result.t[result.electrodes == m + 1] for m in range(len(voltages))]

    plot_t_idx = result.facets(tissue_or_last(result, plot_tissue))
    skin_t_idx = result.facets(skin)

    # fmt: off
    Process(
        target=plot_electrode_worker,
        args=(
            P_mm,
            result.t[plot_t_idx],
            ("E-field Magnitude on Surface: ", "V/m", f["Emag"][plot_t_idx], "jet"),
            electrode_t,
            voltages,
        ),
    ).start()
    Process(
        target=plot_worker,
        args=(
            P_mm,
            result.t[skin_t_idx],
            ("Potential on Skin: ", "V", f["Pot"][skin_t_idx]),
        ),
    ).start()
    # fmt: on

    show_slices(result, planes, plot_tissue, slices=slices)


def show_uniform(result: Result, plot_tissue="gm"):
    plot_residual(result.resvec)

    plot_t_idx = result.facets(tissue_or_last(result, plot_tissue))
    plot_t = result.t[plot_t_idx]
    f = result.fields

    # fmt: off
    plots = [
        ("Charge Solution on Surface: ",                "C/m^2", eps0 * f["c"][plot_t_idx]),
        ("Potential on Surface: ",                      "V",     f["Pot"][plot_t_idx]),
        ("Normal E-field on Surface: ",                 "V/m",   f["En"][plot_t_idx]),
        ("Normal Current Density (inner) on Surface: ", "A/m^2", f["Jn"][plot_t_idx]),
    ]
    # fmt: on

    for p in plots:
        Process(target=plot_worker, args=(result.P, plot_t, p)).start()
