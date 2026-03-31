"""MkDocs hooks: export marimo notebooks to HTML before build."""
from __future__ import annotations

import pathlib
import subprocess
import logging

log = logging.getLogger("mkdocs.hooks")


def on_pre_build(config) -> None:
    notebooks_dir = pathlib.Path(config["docs_dir"]) / "notebooks"
    for nb in sorted(notebooks_dir.glob("*.py")):
        output = nb.with_suffix(".html")
        log.info("Exporting marimo notebook: %s", nb.name)
        result = subprocess.run(
            ["marimo", "export", "html", str(nb), "-o", str(output)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            log.warning("marimo export failed for %s:\n%s", nb.name, result.stderr)
        else:
            log.info("  → %s", output.name)
