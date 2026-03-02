#%%
import argparse
from rich import print
from protobase import flux
from axis import src, syn, val, items
from IPython import embed

parser = argparse.ArgumentParser(description="Axis package debug runner")
parser.add_argument(
    "--package",
    #required=True,
    default="codebase/std.core",
    help="Path to the package root",
)
parser.add_argument(
    "--repl",
    action="store_true",
    help="Run the REPL",
)

# parser.add_argument(
#     "--watch",
#     action="store_true",
#     help="Watch the source directory for changes",
# )
# parser.add_argument(
#     "--tui",
#     action="store_true",
#     help="Run the Textual TUI (implies --watch)",
# )
args = parser.parse_args()

pkg = items.Package.from_path(args.package)

def collect_diagnostics() -> tuple[src.Diagnostic, ...]:
    try:
        _ = pkg.database
    except Exception:
        pass
    diagnostics = flux.collect_all(cls=src.Diagnostic)
    return tuple(diag for diag in diagnostics if isinstance(diag, src.Diagnostic))


pkg.database
for diag in collect_diagnostics():
    diag.emit()


if args.repl:
    embed()

"""
if args.tui:
    from axis.tui.main import MainView

    watch = src.FSWatcher(pkg.dir)
    app = MainView(collect_diagnostics=collect_diagnostics)

    @watch.on_change
    def collect_and_show_diagnostics() -> None:
        time.sleep(0.5)
        diagnostics = collect_diagnostics()
        app.call_from_thread(app.show_diagnostics, diagnostics)

    watch.start()
    try:
        app.run()
    finally:
        watch.stop()

elif args.watch:
    watch = src.FSWatcher(pkg.dir)

    @watch.on_change
    def collect_and_show_diagnostics() -> None:
        diagnostics = collect_diagnostics()
        for diag in diagnostics:
            diag.emit()

    watch.start()
    try:
        # starts a embedded repl here!!
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        watch.stop()
else:
    diagnostics = collect_diagnostics()
    for diag in diagnostics:
        diag.emit()
"""