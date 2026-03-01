from typing import Self

from axis import dom, src
from protobase import flux
from typing import cast

from axis.sem import Context, Realm
from .item import Item
#from .index import GlobalIndex

class Package(Realm):
    dir: src.Dir

    @classmethod
    def from_path(cls, path: str | src.Path) -> Self:
        return cls(dir=src.Dir.from_path(path))

    @property
    def source_paths(self) -> frozenset[src.Path]:  # path -> file
        return frozenset(self.dir.glob("**/*.ax"))

    @flux.method
    def file_items(self, path: src.Path) -> frozenset[Item]:
        from axis import items
        file = src.File.from_path(self.dir.path / path)
        return frozenset(items.Unit.from_file(file, realm=self))

    @flux.property
    def items(self) -> frozenset[Item]:
        return frozenset(
            item
            for path in self.source_paths
            for item in self.file_items(path)
        )

    @property
    def contexts(self):
        return self.items


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
            print("sandbox.members", tuple(sandbox_entity.members.keys()))
            print("sandbox.overloads", len(sandbox_entity.overload_buckets))
            print("sandbox.facts", len(sandbox_entity.facts))
            print("sandbox.constraints", len(sandbox_entity.constraints))

        basic_entity = find_entity("sandbox", "basic")
        if basic_entity is not None:
            print("sandbox.basic.members", tuple(basic_entity.members.keys()))
            print("sandbox.basic.overloads", len(basic_entity.overload_buckets))

        demo_entity = find_entity("sandbox", "demo")
        if demo_entity is not None:
            print("sandbox.demo.members", tuple(demo_entity.members.keys()))
            print("sandbox.demo.overloads", len(demo_entity.overload_buckets))

        point_entity = find_entity("sandbox", "demo", "Point")
        if point_entity is not None:
            print("sandbox.demo.Point.overloads", len(point_entity.overload_buckets))
            print(
                "sandbox.demo.Point.returns",
                sum(len(b.returns) for b in point_entity.overload_buckets.values()),
            )

        add_entity = find_entity("sandbox", "demo", "Add")
        if add_entity is not None:
            print("sandbox.demo.Add.overloads", len(add_entity.overload_buckets))
            print(
                "sandbox.demo.Add.returns",
                sum(len(b.returns) for b in add_entity.overload_buckets.values()),
            )

        default_entity = find_entity("sandbox", "demo", "Default")
        if default_entity is not None:
            print("sandbox.demo.Default.injectors", len(default_entity.overload_buckets))
            print("sandbox.demo.Default.constraints", len(default_entity.constraints))

        id_entity = find_entity("sandbox", "demo", "Id")
        if id_entity is not None:
            print("sandbox.demo.Id.overloads", len(id_entity.overload_buckets))
            print(
                "sandbox.demo.Id.returns",
                sum(len(b.returns) for b in id_entity.overload_buckets.values()),
            )

        clamp_entity = find_entity("sandbox", "demo", "Clamp")
        if clamp_entity is not None:
            print("sandbox.demo.Clamp.overloads", len(clamp_entity.overload_buckets))
            print(
                "sandbox.demo.Clamp.returns",
                sum(len(b.returns) for b in clamp_entity.overload_buckets.values()),
            )

        origin_entity = find_entity("sandbox", "demo", "origin")
        if origin_entity is not None:
            print("sandbox.demo.origin.facts", len(origin_entity.facts))

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
