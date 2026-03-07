#%%
from time import sleep
from cyclopts import App
from protobase import flux
from axis import items, log, src
from IPython import embed
from rich import print

app = App()


def collect_reports(pkg: items.Package) -> tuple[log.Report, ...]:
    try:
        _ = pkg.entities_by_anchor
    except Exception as e:
        print(e)
    diagnostics = flux.collect_all(cls=log.Report)
    return tuple(diag for diag in diagnostics if isinstance(diag, log.Report))


@app.default
def main(
    package: str = "codebase/sandbox",
    repl: bool = False,
    watch: bool = False,
    tui: bool = False,
) -> None:
    """Axis package debug runner."""
    pkg = items.Package.from_path(package)

    if tui:
        from axis.tui.main import MainView
        return MainView(pkg).main()

    if repl:
        watcher = src.FSWatcher(pkg.dir)

        @watcher.on_change
        def collect_and_show_reports() -> None:
            sleep(0.5)
            for report in collect_reports(pkg):
                report.emit()

        watcher.start()
        try:
            embed()
        finally:
            watcher.stop()
        return

    if watch:
        watcher = src.FSWatcher(pkg.dir)

        @watcher.on_change
        def collect_and_show_reports() -> None:
            for report in collect_reports(pkg):
                report.emit()

        watcher.start()
        try:
            while True:
                sleep(0.5)
        except KeyboardInterrupt:
            watcher.stop()
        return

    for report in collect_reports(pkg):
        report.show()


if __name__ == "__main__":
    app()
