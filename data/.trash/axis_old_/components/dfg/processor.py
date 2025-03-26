from typing import Iterator, Self

from .model import Apply, Composition, Constant, Leaf, Loop, Node, Switch, Trunk, Use


class Processor[T]:
    CONTINUE = object()

    def preprocess_node(self, node: Node) -> T:
        return self.CONTINUE

    def postprocess_node(self, node: Node, result: T):
        return result

    def process_leaf(self, leaf: Leaf) -> T:
        raise NotImplementedError(
            f"preprocess_leaf not implemented in {self.__class__}"
        )

    def process_use(self, use: Use) -> T:
        raise NotImplementedError(f"preprocess_use not implemented in {self.__class__}")

    def process_constant(self, constant: Constant) -> T:
        raise NotImplementedError(
            f"preprocess_constant not implemented in {self.__class__}"
        )

    def process_composition(self, composition: Composition) -> T:
        raise NotImplementedError(
            f"preprocess_composition not implemented in {self.__class__}"
        )

    def process_apply(self, apply: Apply) -> T:
        raise NotImplementedError(f"process_apply not implemented in {self.__class__}")

    def process_switch(self, switch: Switch) -> T:
        raise NotImplementedError(f"process_switch not implemented in {self.__class__}")

    def process_loop(self, loop: Loop) -> T:
        raise NotImplementedError(f"process_loop not implemented in {self.__class__}")

    def process_trunk(self, trunk: Trunk) -> T:
        raise NotImplementedError(f"process_trunk not implemented in {self.__class__}")

    def when_exception(self, node: Node, e: Exception):
        e.add_note(f"Error while processing {node}")
        raise e

    def __call__(self, node: Node):
        """
        Eval puede ser parametrizado via evaluation_context
        """
        preprocess_result = self.preprocess_node(node)

        if preprocess_result is not Processor.CONTINUE:  #
            return preprocess_result

        try:
            match node:
                case Leaf() as leaf:
                    result = self.process_leaf(leaf)
                case Use() as use:
                    result = self.process_use(use)
                case Constant() as constant:
                    result = self.process_constant(constant)
                case Composition() as composition:
                    result = self.process_composition(composition)
                case Apply() as apply:
                    result = self.process_apply(apply)
                case Switch() as switch:
                    result = self.process_switch(switch)
                case Loop() as loop:
                    result = self.process_loop(loop)
                case Trunk() as trunk:
                    result = self.process_trunk(trunk)
        except Exception as e:
            result = self.when_exception(node, e)

        return self.postprocess_node(node, result)


class BasicProcessor[T](Processor[T]):
    def __init__(self, parent: Self):
        super().__init__()
        self._parent = parent
        self._visited_nodes = {}

    def ancestors(self) -> Iterator[Self]:
        ctx = self
        yield ctx
        while ctx := ctx._parent:
            yield ctx

    def preprocess_node(self, node: Node) -> T:
        return self._visited_nodes.get(node, self.CONTINUE)

    def postprocess_node(self, node: Node, result: T):
        self._visited_nodes[node] = result
        return result

    def is_visited(self, node: Node):
        return node in self._visited_nodes
