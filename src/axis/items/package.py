from typing import Self

from axis import dom, src
from protobase import flux
from typing import cast

from axis.sem import Realm
from .item import Item
#from .index import GlobalIndex

class Package(Realm):
    dir: src.SourceDir

    @classmethod
    def from_path(cls, path: str | src.Path) -> Self:
        return cls(dir=src.SourceDir.from_path(path))

    @property
    def source_files(self) -> frozenset[src.SourceFile]:
        return frozenset(self.dir.glob("**/*.ax"))

    @flux.method
    def file_items(self, file: src.SourceFile) -> frozenset[Item]:
        from axis import items
        return frozenset(
            item for item in items.Unit.from_file(file, realm=self)
            if isinstance(item, Item)
        )

    @flux.property
    def items(self) -> frozenset[Item]:
        return frozenset(
            item
            for file in self.source_files
            for item in self.file_items(file)
        )

    @property
    def contexts(self):
        return tuple(self.items)


if __name__ == "__main__":

    def debug_package(path: str = "codebase/sandbox") -> None:
        from rich import print

        from axis import syn, val

        realm = Package.from_path(path)
        db = realm.database

        eval = val.Evaluator()

        def print_eval(value: str):
            print(eval(syn.Expr.from_str(value)))

        def print_syn(value: str):
            print(syn.Expr.from_str(value))

        print("database.entities", len(db.entities_by_ref))
        print("database.namespaces", len(db.members_by_scope))
        print("database.refs", tuple(dom.ref_segments(ref) for ref in db.entities_by_ref))

        def find_entity(*segments):
            return next(
                (
                    entity
                    for ref, entity in db.entities_by_ref.items()
                    if dom.ref_segments(ref) == tuple(segments)
                ),
                None,
            )

        sandbox_entity = find_entity("sandbox")
        if sandbox_entity is not None:
            print("sandbox.spec_buckets", len(sandbox_entity.spec_buckets))
            print("sandbox.overloads", len(sandbox_entity.overloads))

        basic_entity = find_entity("sandbox", "basic")
        if basic_entity is not None:
            print("sandbox.basic.spec_buckets", len(basic_entity.spec_buckets))
            print("sandbox.basic.overloads", len(basic_entity.overloads))

        demo_entity = find_entity("sandbox", "demo")
        if demo_entity is not None:
            print("sandbox.demo.spec_buckets", len(demo_entity.spec_buckets))
            print("sandbox.demo.overloads", len(demo_entity.overloads))

        print_eval(
            """
            (
                (1,0,0),
                (0,1,0),
                (0,0,1),
            )
            """
        )

    debug_package()

    # @property
    # def source_block_spec(self):
    #     from axis import items
    #     return items.Unit.build_outline_spec()

    # def unit_ast(self, path: src.Path):
    #     from axis import items

    #     file = src.File.from_path(self.dir.path / path)
    #     return self.source_block_spec.parse_outline(file)

    # def file_bindings(self, path: src.Path) -> frozenset[Binding]:
    #     from axis import items
    #     #return items.Unit.build_outline_spec()

    #     file = src.File.from_path(self.dir.path / path)
    #     ast_item = items.Unit.outline_spec.parse_outline(file)
    #     # ast_item = self.source_block_spec.parse_outline(file)
    #     return frozenset(Binding.generate_from(ast_item, pkg=self, parent=self.root_binding))

    # class RootBinding(Binding):
    #     @property
    #     def ref(self):
    #         return val.Ref.root

    # @cached_property
    # def root_binding(self):
    #     return self.RootBinding(
    #         pkg=self,
    #         parent=None,
    #         item=self, # XXX: self not subclass of Item
    #     )

    # @property
    # def global_index(self):
    #     all_bindings = set()

    #     for path in self.source_paths:
    #         all_bindings.update(self.file_bindings(path))

    #     return GlobalIndex.from_bindings(all_bindings)
