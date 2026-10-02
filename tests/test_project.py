import shutil

import pytest

from bemfmm.model import sphere_index
from bemfmm.project import PROJECT_FILE, Project, default_project


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
