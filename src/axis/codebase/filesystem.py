from pathlib import Path
from protobase import Object
from axis.std.core import Id

class FileSystemLayer(Object, abstract=True):
    fs_path: Path
    fs_glob: str = "**/*.ax"  # Annotated[]

    @property
    def fs_unit_paths(self):
        return {
            Id.from_path(rel_path): path
            for path in self.fs_path.glob(self.fs_glob)
            if (rel_path := path.relative_to(self.fs_path))
        }
