from typing import Self
from protobase import Record, cached_property

from axis import src, syn, val
from .index import GlobalIndex
from .binding import Binding

class Package(Record, frozen=True):
    dir: src.Dir

    """
      el src spec de un package (dir) son los globs y archivos relativos y su parser 
      {
        '**/*.ax': Unit,
        'README.md': markdown, # indice documental del package
        'package.toml'
      }

    """

    @classmethod
    def from_path(cls, path: str | src.Path) -> Self:
        return cls(dir=src.Dir.from_path(path))

    @property
    def source_paths(self):  # path -> file
        return self.dir.glob("**/*.ax")

    @property
    def source_block_spec(self):
        from axis import items
        return items.Unit.build_outline_spec()

    # def unit_ast(self, path: src.Path):
    #     from axis import items

    #     file = src.File.from_path(self.dir.path / path)
    #     return self.source_block_spec.parse_outline(file)

    def file_bindings(self, path: src.Path) -> frozenset[Binding]:
        file = src.File.from_path(self.dir.path / path)
        ast_item = self.source_block_spec.parse_outline(file)
        return frozenset(Binding.generate_from(ast_item, pkg=self, parent=self.root_binding))

    class RootBinding(Binding):
        @property
        def ref(self):
            return val.Ref.root

    @cached_property
    def root_binding(self):
        return self.RootBinding(
            pkg=self,
            parent=None,
            item=self, # XXX: self not subclass of Item
        )

    @property
    def global_index(self):
        all_bindings = set()

        for path in self.source_paths:
            all_bindings.update(self.file_bindings(path))

        return GlobalIndex.from_bindings(all_bindings)
