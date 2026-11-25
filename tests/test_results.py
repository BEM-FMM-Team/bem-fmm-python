import numpy as np

from bemfmm.model import HeadModel
from bemfmm.results import Result


def test_shared_interface_is_available_from_both_tissues():
    result = Result(
        kind="tdcs",
        tissues=["inside", "outside"],
        P=np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]),
        t=np.array([[0, 1, 2]]),
        normals=np.array([[0.0, 0.0, 1.0]]),
        interface=np.array([[0, 1]]),
        fields={
            "c": np.array([2.0]),
            "Emag": np.array([3.0]),
            "En": np.array([4.0]),
            "Jn": np.array([5.0]),
            "Pot": np.array([6.0]),
        },
    )

    assert result.facets("inside").tolist() == [True]
    assert result.facets("outside").tolist() == [True]
    assert result.on("c", "inside").tolist() == [2.0]
    assert result.on("c", "outside").tolist() == [-2.0]
    assert result.on("En", "outside").tolist() == [-4.0]
    assert result.on("Jn", "outside").tolist() == [-5.0]
    assert result.on("Pot", "outside").tolist() == [6.0]
    assert result.on("Emag", "outside").tolist() == [3.0]
    assert result.triangles("outside").tolist() == [[0, 2, 1]]


def test_shared_model_surface_reverses_neighbor_orientation(tmp_path):
    model = HeadModel(
        index_path=tmp_path / "index.yaml",
        names=["inside", "outside"],
        files=[],
        condinner=[0.1, 0.2],
        condouter=[0.0, 0.0],
        outside=["FreeSpace", "FreeSpace"],
        P=np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]),
        t=np.array([[0, 1, 2]]),
        normals=np.array([[0.0, 0.0, 1.0]]),
        condin=np.array([0.1]),
        condout=np.array([0.2]),
        interface=np.array([[0, 1]]),
    )

    _, triangles = model.surface("outside")

    assert triangles.tolist() == [[0, 2, 1]]


