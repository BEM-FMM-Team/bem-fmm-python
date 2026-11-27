"""
Runs the reference cases through the library and reports timings, convergence
and the numbers that should not change between versions

    python scripts/benchmark.py                 sphere cases only
    python scripts/benchmark.py --head          adds the full head model
    python scripts/benchmark.py --save out.json keeps the numbers
    python scripts/benchmark.py --compare out.json

Prints the machine it ran on first, and the peak memory of the run last.
Set BEMFMM_NO_CACHE=1 to time the solver instead of the cache
"""

import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from time import perf_counter

import numpy as np
import psutil
import typer

from bemfmm.coils import default_coil
from bemfmm.electrode import Electrode
from bemfmm.model import HeadModel, default_index, sphere_index
from bemfmm.results import git_commit
from bemfmm.solvers import tdcs, tms, uniform

SPHERE_ELECTRODES = [
    Electrode("E0", [0, 0, 0.042], 0.008, 1.0),
    Electrode("E1", [0, 0, -0.042], 0.008, -1.0),
    Electrode("E2", [0.042, 0, 0], 0.006, 0.5),
]


def cpu_name():
    if sys.platform == "linux":
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name"):
                return line.split(":", 1)[1].strip()
    if sys.platform == "darwin":
        cmd = ["sysctl", "-n", "machdep.cpu.brand_string"]
        return subprocess.check_output(cmd, text=True).strip()
    return platform.processor()


def machine():
    cores = f"{psutil.cpu_count(logical=False)} physical, {os.cpu_count()} logical"
    return {
        "CPU": cpu_name(),
        "Cores": cores,
        "RAM": f"{psutil.virtual_memory().total / 2**30:.1f} GiB",
        "OS": platform.platform(),
        "Python": platform.python_version(),
        "Commit": git_commit()[:10] or "not a git checkout",
        "OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS", "not set"),
        "Cache": "off" if os.environ.get("BEMFMM_NO_CACHE") else "on",
    }


def peak_ram():
    # highest memory use of this process so far, in bytes
    if sys.platform == "win32":
        return psutil.Process().memory_info().peak_wset
    import resource

    # ru_maxrss is in bytes on macos and in kilobytes on linux
    unit = 1 if sys.platform == "darwin" else 1024
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * unit


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

    info = machine()
    for key, value in info.items():
        print(f"{key + ':':<17}{value}")

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

    print()
    print("time per step [s]")
    for name, n in numbers.items():
        steps = ", ".join(f"{k} {v:.1f}" for k, v in n["timings"].items())
        print(f"  {name:<16}{steps}")

    info["Peak RAM"] = f"{peak_ram() / 2**30:.1f} GiB"
    print()
    print(f"{'Peak RAM:':<17}{info['Peak RAM']}")

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
        Path(save).write_text(json.dumps({"machine": info, **numbers}, indent=2))
        print(f"Saved {save}")


if __name__ == "__main__":
    typer.run(main)
