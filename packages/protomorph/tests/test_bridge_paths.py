from __future__ import annotations

import unittest
from typing import cast
from pathlib import Path
import sys

import protomorph as morph

sys.path.insert(0, str(Path(__file__).parent))

from support import UnsupportedQualifier


class BridgePathTests(unittest.TestCase):
    def test_context_manager_route_installs_and_restores_bridge_tokens(self):
        class Bridge(morph.SemanticBridgeBase):
            pass

        bridge = Bridge()
        before = morph.BRIDGE.get()
        with bridge:
            self.assertIs(morph.BRIDGE.get(), bridge)
            with bridge:
                self.assertIs(morph.BRIDGE.get(), bridge)
            self.assertIs(morph.BRIDGE.get(), bridge)
        self.assertIs(morph.BRIDGE.get(), before)

    def test_project_route_covers_struct_nominal_and_qualifier_paths(self):
        class Bridge(morph.SemanticBridgeBase):
            pass

        bridge = Bridge()
        inner = morph.StructType(meta_attrs=morph.Struct.new(name=morph.TEXT_TYPE))
        qualified = morph.nominal_qual("test.Future", underlying=inner)

        self.assertEqual(bridge.project(inner, "name"), morph.TEXT_TYPE)
        self.assertEqual(repr(morph.val(bridge.project(qualified, "name"))), "test.Future std.Text")

    def test_project_route_rejects_opaque_nominal_and_invalid_keys(self):
        class Bridge(morph.SemanticBridgeBase):
            pass

        bridge = Bridge()

        with self.assertRaises(KeyError):
            bridge.project(morph.nominal_type("test.Opaque"), "name")
        with self.assertRaises(TypeError):
            bridge.project(
                morph.StructType(meta_attrs=morph.Struct.new(name=morph.TEXT_TYPE)),
                cast(str | int, 1.5),
            )

    def test_lift_and_combine_routes_cover_default_exception_contracts(self):
        class Bridge(morph.SemanticBridgeBase):
            pass

        bridge = Bridge()
        lifted = bridge.lift(morph.nominal_qual("test.Future", underlying=morph.TEXT_TYPE), morph.INTEGER_TYPE)

        self.assertEqual(repr(morph.val(lifted)), "test.Future std.Integer")
        with self.assertRaises(NotImplementedError):
            bridge.combine(morph.INTEGER_TYPE, morph.INTEGER_TYPE, op="+")
        with self.assertRaises(NotImplementedError):
            bridge.lift(UnsupportedQualifier(underlying=morph.TEXT_TYPE), morph.INTEGER_TYPE)
