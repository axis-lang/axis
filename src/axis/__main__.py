# %%
from pathlib import Path
from time import sleep

from cyclopts import App
from axis import Codebase, Workspace, src
from IPython import embed
from rich import print

app = App()


@app.default
def main(
    package: str = "codebase/std-core",
    repl: bool = False,
    watch: bool = False,
    tui: bool = False,
) -> None:
    """Axis package debug runner."""
    package_path = Path(package).resolve()
    codebase = Codebase.from_path(package_path.parent)
    workspace = Workspace(codebase=codebase, roots=(package_path.name,))
    root_package = workspace.root_packages[0]

    if tui:
        raise RuntimeError("TUI is temporarily disabled during the workspace refactor")

    for report in workspace.all_reports:
        report.show()

    if repl or watch:
        watcher = src.FSWatcher(root_package.dir)

        @watcher.on_change
        def collect_and_show_reports() -> None:
            for report in workspace.all_reports:
                report.emit()

        watcher.start()

        try:
            if repl:
                with workspace:
                    embed()
            else:
                print(f"Watching {root_package.dir} for changes. Press Ctrl+C to stop.")
                while True:
                    sleep(1)
        finally:
            watcher.stop()
        return


if __name__ == "__main__":
    app()
