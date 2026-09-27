"""
Runs the reference cases through the library and reports timings, convergence
and the numbers that should not change between versions

    python scripts/benchmark.py                 sphere cases only
    python scripts/benchmark.py --head          adds the full head model
    python scripts/benchmark.py --save out.json keeps the numbers
    python scripts/benchmark.py --compare out.json

Set BEMFMM_NO_CACHE=1 to time the solver instead of the cache
"""

import json
from pathlib import Path
from time import perf_counter

import numpy as np
import typer

from bemfmm.coils import default_coil
from bemfmm.electrode import Electrode
from bemfmm.model import HeadModel, default_index, sphere_index
from bemfmm.solvers import tdcs, tms, uniform

SPHERE_ELECTRODES = [
    Electrode("E0", [0, 0, 0.042], 0.008, 1.0),
    Electrode("E1", [0, 0, -0.042], 0.008, -1.0),
    Electrode("E2", [0.042, 0, 0], 0.006, 0.5),
]


def summary(result, seconds):
    f = result.fields
    out = {
        "facets": int(result.t.shape[0]),
        "iterations": int(result.info["iterations"]),
        "relres": float(result.info["relres"]),
        "seconds": round(seconds, 1),
        "timings": {k: round(v, 2) for k, v in result.info["timings"].items()},
        "norm_c": float(np.linalg.norm(f["c"])),
        "max_Emag": float(np.max(f["Emag"])),
    }
    if "electrodes" in result.info and result.kind == "tdcs":
        out["currents_mA"] = [e["current"] * 1e3 for e in result.info["electrodes"]]
        out["power_W"] = result.info["power"]
    return out


def cases(head):
    sphere = HeadModel.load(sphere_index(), verbose=False)
    yield "sphere uniform", lambda: uniform.solve(sphere)
    yield "sphere tms", lambda: tms.solve(sphere, [default_coil()])
    yield "sphere tdcs", lambda: tdcs.solve(sphere, SPHERE_ELECTRODES)
    if head:
        model = HeadModel.load(default_index(), verbose=False)
        yield "head tms", lambda: tms.solve(model, [default_coil()])
        yield "head tdcs", lambda: tdcs.solve(model, tdcs.default_electrodes())


def main(
    head: bool = False,
    save: str = typer.Option(None, help="Write the numbers to this json"),
    compare: str = typer.Option(None, help="Compare with a json from --save"),
):
    reference = json.loads(Path(compare).read_text()) if compare else {}
    numbers = {}

    for name, run in cases(head):
        start = perf_counter()
        result = run()
        numbers[name] = summary(result, perf_counter() - start)

    print()
    print(f"{'case':<16}{'facets':>9}{'iters':>7}{'relres':>11}{'time [s]':>10}")
    for name, n in numbers.items():
        print(
            f"{name:<16}{n['facets']:>9,}{n['iterations']:>7}"
            f"{n['relres']:>11.2e}{n['seconds']:>10.1f}"
        )
        if "currents_mA" in n:
            currents = ", ".join(f"{c:.4f}" for c in n["currents_mA"])
            print(f"{'':<16}currents [mA]: {currents}")

    if reference:
        print()
        print("relative change against", compare)
        for name, n in numbers.items():
            if name not in reference:
                continue
            ref = reference[name]
            for key in ("norm_c", "max_Emag", "power_W"):
                if key in n and key in ref:
                    change = abs(n[key] - ref[key]) / abs(ref[key])
                    print(f"  {name:<16}{key:<10}{change:.2e}")

    if save:
        Path(save).write_text(json.dumps(numbers, indent=2))
        print(f"Saved {save}")


if __name__ == "__main__":
    typer.run(main)
