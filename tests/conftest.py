import os

import pytest

# every test solves from scratch instead of reading __compute_cache__
os.environ["BEMFMM_NO_CACHE"] = "1"
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# bemfmm.lib reads BEMFMM_NO_CACHE on import
from bemfmm.model import HeadModel, sphere_index


@pytest.fixture(scope="session")
def sphere():
    return HeadModel.load(sphere_index(), verbose=False)
