import tomllib
from pathlib import Path

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

templates_path = ["_templates"]
exclude_patterns = []

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosummary",
    "sphinx_mdinclude",
]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]


ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = ROOT / "pyproject.toml"

data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))

project_data = data.get("project", {})
project = project_data.get("name", "bem-fmm-python")

authors = project_data.get("authors", [])
author = authors[0].get("name") if authors else "Unknown"

version = project_data.get("version", "0.0.0")
release = version

copyright = f"{release}"
