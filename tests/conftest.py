import os

# every test solves from scratch instead of reading __compute_cache__
os.environ["BEMFMM_NO_CACHE"] = "1"
os.environ.setdefault("MPLBACKEND", "Agg")
