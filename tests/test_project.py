import shutil

import numpy as np
import pytest
import vedo

from bemfmm.model import read_index, sphere_index
from bemfmm.project import (
    PROJECT_FILE,
    Project,
    copy_project,
    default_project,
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
    assert project.read_only and project.problems() == []


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
