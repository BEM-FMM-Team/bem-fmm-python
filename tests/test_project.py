import shutil
import subprocess
import sys

import numpy as np
import pytest
import vedo

from bemfmm.cli import output_path
from bemfmm.model import read_index, sphere_index
from bemfmm.project import (
    PROJECT_FILE,
    Project,
    copy_project,
    default_project,
    makaroff_40_project,
    new_project,
    sphere_project,
)


def test_project(tmp_path):
    for path in sphere_index().parent.glob("*.stl"):
        shutil.copy(path, tmp_path)
    shutil.copy(sphere_index(), tmp_path)

    # a folder with a tissue index is a project before it has project.yaml
    implicit = Project.load(tmp_path / "gm.stl")
    assert (implicit.name, implicit.skin) == (tmp_path.name, "skin")
    assert not implicit.read_only and implicit.problems() == []

    Project(tmp_path, name="sphere", skin="bone").save()
    project = Project.load(tmp_path / PROJECT_FILE)
    assert (project.name, project.skin, project.root) == ("sphere", "bone", tmp_path)
    assert project.run_dir("tms", "20260930-120000").name == "tms-20260930-120000"

    project.skin = "scalp"
    assert project.problems() == ["The skin tissue scalp is not in tissue_index.yaml"]
    with pytest.raises(FileNotFoundError):
        Project.load(tmp_path / "missing")


def test_default_project():
    project = default_project()
    assert project.name == "Default head"
    assert not project.smooth_nonmanifold
    assert project.read_only and project.problems() == []


def test_makaroff_40_project_metadata():
    project = makaroff_40_project()
    shells = read_index(project.index_path)

    assert project.name == "Sim4Life 40-tissue head"
    assert project.flip_xy and project.deduplicate_interfaces
    assert project.smooth_nonmanifold
    assert project.skin == "Skin"
    assert project.read_only and project.problems() == []
    assert len(shells) == len(project.tissue_colors) == 40
    assert all(path.is_file() for _, _, path in shells.values())
    assert shells["Skin"][0] == pytest.approx(0.148297)
    assert project.tissue_colors["Air_internal"] == [0.0, 1.0, 0.0]


def test_new_project(tmp_path):
    # the sphere's surfaces under other names and out of order, one flipped
    sphere = sphere_index().parent
    names = {"wm": "white", "skin": "scalp", "gm": "cortex", "bone": "skull"}
    for tissue, name in names.items():
        mesh = vedo.Mesh(str(sphere / f"{tissue}.stl"))
        if tissue == "wm":
            mesh = vedo.Mesh([mesh.vertices, np.asarray(mesh.cells)[:, ::-1]])
        mesh.write(str(tmp_path / f"{name}.stl"))

    meshes = [tmp_path / f"{name}.stl" for name in names.values()]
    project, problems = new_project(tmp_path / "new", meshes, name="sphere")
    assert problems == ["The normals of white point inward"]
    assert (project.name, project.skin) == ("sphere", "scalp")
    shells = read_index(project.index_path)
    assert {t: (c, o) for t, (c, o, _) in shells.items()} == {
        "scalp": (0.465, "FreeSpace"),
        "skull": (0.01, "scalp"),
        "cortex": (0.275, "skull"),
        "white": (0.126, "cortex"),
    }
    assert all(path.parent == project.root for _, _, path in shells.values())
    with pytest.raises(FileExistsError):
        new_project(tmp_path / "new", meshes)


def test_copy_project(tmp_path):
    source = sphere_project()
    assert Project.for_index(source.index_path).name == "Three layer sphere"
    (tmp_path / "busy").mkdir()
    (tmp_path / "busy" / "file").touch()
    with pytest.raises(FileExistsError):
        copy_project(source, tmp_path / "busy")

    copy = copy_project(source, tmp_path / "copy")
    assert (copy.name, copy.read_only, copy.problems()) == (
        "Three layer sphere copy",
        False,
        [],
    )
    assert Project.for_index(copy.index_path).root == tmp_path / "copy"
    assert list(read_index(copy.index_path)) == list(read_index(source.index_path))

    copy.flip_xy = True
    copy.deduplicate_interfaces = True
    copy.tissue_colors = {"skin": [1.0, 1.0, 1.0]}
    copy.smooth_nonmanifold = True
    copy.save()
    copy2 = copy_project(copy, tmp_path / "copy-with-options")
    assert copy2.flip_xy and copy2.deduplicate_interfaces and copy2.smooth_nonmanifold
    assert copy2.tissue_colors == copy.tissue_colors


def test_gui_sets_up_opengl_before_vtk():
    # on Windows the software opengl32.dll has to be loaded before vtk, or vtk
    # keeps the system one. Checked in a fresh process, this one has vtk
    script = """
import sys
from bemfmm import softgl
from bemfmm.cli import app

def setup():
    print(any(name.startswith("vtkmodules") for name in sys.modules))
    raise SystemExit(0)

softgl.setup = setup
app(sys.argv[1:])
"""
    project = str(sphere_project().root)
    for args in (["gui"], ["gui", "--project", project]):
        out = subprocess.run(
            [sys.executable, "-c", script, *args], capture_output=True, text=True
        )
        assert out.stdout.strip() == "False", (args, out.stderr)


def test_output_path_gitignore(tmp_path):
    output_dir = output_path(tmp_path / "run")
    assert (output_dir / ".gitignore").read_text() == "*\n"
    # a .gitignore already there is kept
    (output_dir / ".gitignore").write_text("*.npz\n")
    output_path(output_dir)
    assert (output_dir / ".gitignore").read_text() == "*.npz\n"
