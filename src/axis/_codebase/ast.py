# %%

from axis.codebase.src import SourceLayer

from axis import syn, src
from axis import _std

from rich import print

class SyntacticLayer(SourceLayer, abstract=True):
    @property
    def unit_outline_spec(self):
        return _std.Unit.build_ouline_spec()

    def ast_of_unit(self, src_file: src.File) -> syn.Unit:
        return self.unit_outline_spec.parse_outline(src_file)
        #return outline.transform(syn.outline_transform_fn)
