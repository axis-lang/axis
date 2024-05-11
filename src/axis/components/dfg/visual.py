# %%
from typing import Callable
from graphviz import Digraph

from axis.components.dfg.model import Apply, Node, Trunk

from ..tuple import Tuple
from .evaluation import *
from .model import *

cluster_count = 0


class VisualizationContext(EvaluationContext[Node]):
    graph: Digraph

    def __enter__(self):
        global cluster_count
        super().__enter__()
        if self._parent_context is None:
            self.graph = Digraph()
            cluster_count = 0
        else:
            self.graph = Digraph(f"cluster_{cluster_count}")
            self.graph.attr(color="lightgrey", style="filled")
            cluster_count += 1

    def __exit__(self, exc_type, exc_value, traceback):
        if self._parent_context is None:
            self.graph.render("dfg", format="svg", cleanup=True, view=True)
        else:
            self._parent_context.graph.subgraph(self.graph)

        super().__exit__(exc_type, exc_value, traceback)

    def eval_leaf(self, leaf: Leaf):
        self.graph.attr(label=leaf.name)
        self.graph.node(leaf.ephimeral_id, label=leaf.name, shape="house")
        return super().eval_leaf(leaf)

    def eval_use(self, use: Use):
        # self.graph.node(
        #     use.ephimeral_id, label=f"U {use.entity}", shape="doubleoctagon"
        # )
        return super().eval_use(use)

    def eval_constant(self, constant: Constant):
        if isinstance(constant.value, Node):
            return constant.value

        self.graph.node(constant.ephimeral_id, label=f"{constant.value!r}", shape="box")
        return super().eval_constant(constant)

    def eval_composition(self, composition: Composition, inputs: Tuple[Node]):
        self.graph.node(composition.ephimeral_id, label="C", shape="invtriangle")

        for label, input in composition.inputs.items():
            self.graph.edge(
                input.ephimeral_id, composition.ephimeral_id, label=f"{label}"
            )
        return super().eval_composition(composition, inputs)

    def apply_builtin(self, apply: Apply, builtin: Callable, argument: Node):
        result = super().apply_builtin(apply, builtin, argument)
        self.graph.node(apply.ephimeral_id, label=builtin.__name__)
        self.graph.edge(apply.argument.ephimeral_id, apply.ephimeral_id, label="arg")
        return result

    def apply_trunk(self, apply: Apply, trunk: Trunk, argument: Node):
        result = super().apply_trunk(apply, trunk, argument)

        self.graph.node(apply.ephimeral_id, label=trunk.leaf.name)
        self.graph.edge(trunk.ephimeral_id, apply.ephimeral_id, label="ret")
        self.graph.edge(
            apply.argument.ephimeral_id, trunk.leaf.ephimeral_id, label="arg"
        )

        return result

    def eval_trunk(self, trunk: Trunk, result: Node):
        self.graph.node(trunk.ephimeral_id, label=trunk.leaf.name, shape="invhouse")
        self.graph.edge(trunk.result.ephimeral_id, trunk.ephimeral_id)
        return super().eval_trunk(trunk, result)
