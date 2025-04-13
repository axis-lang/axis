from pathlib import Path
from protobase import Object, cached_property
from axis.std import Id

class FileSystemLayer(Object, abstract=True):
    fs_path: Path
    fs_unit_glob: str = "**/*.ax"  # Annotated[]

    @property
    def fs_units(self):
        return {
            Id.from_fs_path(rel_path): path
            for path in self.fs_path.glob(self.fs_unit_glob)
            if (rel_path := path.relative_to(self.fs_path))
        }
    
    @cached_property
    def id(self):
        return Id(tuple(self.fs_path.name.split(".")[:-1]))
