"""
Writes the three layer (four shell) sphere used by `bemfmm sphere` as stl files
with a tissue index, so it loads like any other head model
"""

from pathlib import Path

import vedo

OUT = Path(__file__).resolve().parents[1] / "src/bemfmm/assets/sphere_3L"

# name: (radius [mm], condin [S/m], outside)
SHELLS = {
    "skin": (42, 0.465, "FreeSpace"),
    "bone": (36, 0.010, "skin"),
    "gm": (28, 0.275, "bone"),
    "wm": (25, 0.126, "gm"),
}

RES = 30


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Three layer sphere, radii 42, 36, 28 and 25 mm, all meshes in [mm]",
        "# Regenerate with scripts/make_sphere_model.py",
        "",
        "shells:",
    ]
    for name, (radius, cond, outside) in SHELLS.items():
        mesh = vedo.Sphere(r=1, res=RES)
        mesh.vertices = mesh.vertices * radius
        mesh.write(str(OUT / f"{name}.stl"), binary=True)
        lines.append(f'  {name:<4} : [{cond:.4f}, "{outside}", "{name}.stl"]')

    (OUT / "tissue_index.yaml").write_text("\n".join(lines) + "\n")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
