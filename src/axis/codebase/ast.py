# %%

from axis.codebase.src import SourceLayer

from axis.dom import syn, src

from rich import print

class SyntacticLayer(SourceLayer, abstract=True):
    @property
    def outline_spec(self):
        return syn.OUTLINE_SPEC

    def ast_of_unit(self, src_file: src.File):

        outline = self.outline_spec.parse_tree(syn.Unit, src_file)

        return outline.transform(syn.outline_transform_fn)
