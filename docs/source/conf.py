import tomllib
from pathlib import Path

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosummary",
    "sphinx_mdinclude",
]

html_theme = "alabaster"


ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = ROOT / "pyproject.toml"

data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))

project_data = data["project"]
project = project_data["name"]

authors = [a["name"] for a in project_data["authors"]]
author = authors[0]

version = project_data["version"]
release = version

copyright = ", ".join(authors)
