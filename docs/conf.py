from __future__ import annotations

import os
import sys

ROOT = os.path.abspath("..")
sys.path.insert(0, os.path.join(ROOT, "src"))

project = "Axis"
author = "jdluque"
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "myst_parser",
]

templates_path = []
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

language = "es"
source_suffix = {".md": "markdown"}
root_doc = "index"

html_theme = "pydata_sphinx_theme"
html_static_path = []

autodoc_typehints = "description"
