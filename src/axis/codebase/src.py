from pathlib import Path
from protobase import Object, cached_property
from axis.dom import Id, ref, src

class SourceLayer(Object, abstract=True):
    src_path: Path
    src_glob: str = "**/*.ax"  # Annotated[]

    @property
    def src_abs_path(self) -> Path:
        return self.src_path.resolve()

    @property
    def src_files(self):
        return tuple(src.File(path) for path in self.src_abs_path.glob(self.src_glob))

