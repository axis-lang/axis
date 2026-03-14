from __future__ import annotations

from collections.abc import Iterable

from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import RichLog, Static, TabbedContent, TabPane, Tree

from axis import items, log, src
from protobase import flux


class MainView(App[None]):
    CSS = """
    #left-view {
        width: 1fr;
    }

    #right-view {
        width: 1fr;
    }
    """

    def __init__(
        self,
        pkg: items.Package,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._pkg = pkg

        self._reports = pkg.all_reports

    def compose(self) -> ComposeResult:
        with Horizontal():
            with TabbedContent(id="left-view"):
                with TabPane("Entities"):
                    yield Tree("Entities", id="entities-tree")
            with TabbedContent(id="right-view"):
                with TabPane("Reports"):
                    yield RichLog(
                        id="reports-log",
                        highlight=False,
                        markup=False,
                        wrap=True,
                    )
                with TabPane("Details"):
                    yield Static("Select an entity to inspect", id="details-view")

    def on_mount(self) -> None:
        self.refresh_views()

    def main(self) -> None:
        watch = src.FSWatcher(self._pkg.dir)

        @watch.on_change
        def collect_and_show_reports() -> None:
            self._reports = self._pkg.all_reports
            self.call_from_thread(self.refresh_views)

        watch.start()
        try:
            self.run()
        finally:
            watch.stop()


    def refresh_views(self) -> None:
        self.refresh_tree()
        self.show_reports(self._reports)

    def refresh_tree(self) -> None:
        tree = self.query_one("#entities-tree", Tree)
        root = tree.root
        for child in list(root.children):
            child.remove()
        entities = self._pkg.entities_by_anchor
        for anchor in sorted(entities.keys(), key=lambda a: a.data):
            anchor_node = root.add(str(anchor), data=anchor)
            #anchor_node.add("Entity", data=("entity", anchor))
            anchor_node.add("Specs", data=("specs", anchor))
            anchor_node.add("Overloads", data=("overloads", anchor))
            anchor_node.add("Implementations", data=("impls", anchor))
        root.expand()

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        detail = self.query_one("#details-view", Static)
        payload = event.node.data
        if payload is None:
            detail.update("Select an entity to inspect")
            return
        match payload:
            case (kind, anchor):
                detail.update(f"{kind}: {anchor}")
            case anchor:
                detail.update(f"entity: {anchor}")

    def show_reports(self, reports: Iterable[object]) -> None:
        report_log = self.query_one("#reports-log", RichLog)
        report_log.clear()
        for report in reports:
            if not isinstance(report, log.Report):
                continue
            report_log.write(report)
            report_log.write("")
