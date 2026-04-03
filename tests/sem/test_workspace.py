from pathlib import Path
import unittest

from axis import Codebase, Workspace, items


CODEBASE_PATH = Path("codebase")


class WorkspaceSmokeTest(unittest.TestCase):
    def test_codebase_loads_std_core_package(self):
        codebase = Codebase.from_path(CODEBASE_PATH)

        package = codebase.package("std-core")

        self.assertIsInstance(package, items.Package)
        self.assertEqual(package.name, "std-core")

    def test_workspace_aggregates_root_package_contexts(self):
        codebase = Codebase.from_path(CODEBASE_PATH)
        workspace = Workspace(codebase=codebase, roots=("std-core",))

        self.assertEqual(tuple(pkg.name for pkg in workspace.root_packages), ("std-core",))
        self.assertTrue(workspace.all_contexts)
