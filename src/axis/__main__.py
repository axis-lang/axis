# %%
from time import sleep
from cyclopts import App
from protobase import flux
from axis import items, log, src, expr, syn, sem
from IPython import embed
from rich import print
from protomorph import *

app = App()


@app.default
def main(
    package: str = "codebase/std-core",
    repl: bool = False,
    watch: bool = False,
    tui: bool = False,
) -> None:
    """Axis package debug runner."""
    pkg = items.Package.from_path(package)

    if tui:
        from axis.tui.main import MainView

        return MainView(pkg).main()

    for report in pkg.all_reports:
        report.show()

    if repl or watch:
        watcher = src.FSWatcher(pkg.dir)

        @watcher.on_change
        def collect_and_show_reports() -> None:
            for report in pkg.all_reports:
                report.emit()
            # print(f"Watching {pkg.dir} for changes. Press Ctrl+C to stop.")

        watcher.start()

        try:
            if repl:
                with pkg:
                    embed()
            else:
                print(f"Watching {pkg.dir} for changes. Press Ctrl+C to stop.")
                while True:
                    sleep(1)
        finally:
            watcher.stop()
        return


if __name__ == "__main__":
    app()
