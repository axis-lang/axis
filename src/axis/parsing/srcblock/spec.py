# %%

from pathlib import Path
from re import compile, Pattern, escape
from typing import Optional
from protobase import Object, Record
from zmq import Enum


ITEM_RE = compile(r"^(\w+)$")
REL_RE = compile(r"^(\w+)\s*([|>])\s*(\w+)$")


class Identation(str, Enum):
    SAME = "|"
    NEST = ">"

    @property
    def re(self) -> str:
        return _IDENT_RE[self]


_IDENT_RE = {
    Identation.SAME: "",
    Identation.NEST: "(?:[ \t]+)",
}

_KEYWORK_SEP = " :\t"


class Item(Record):
    keyword: str
    keyword_separators: str


class Rel(Record):
    identation: Identation


class Spec(Object):

    class Rule(Record, frozen=True):
        item_id: str
        child_items: tuple[str]
        child_pattern: Pattern

        def match_line(self, line: str, pos: int=0) -> Optional[str]:
            if len(self.child_items) == 0:
                return None
            if m := self.child_pattern.match(line, pos):
                return self.child_items[m.lastindex - 1]
            return None

    ruleset: dict[str, Rule]

    @classmethod
    def from_yaml(cls, entry: Path):
        from yaml import safe_load

        with entry.open() as f:
            entries = safe_load(f)

        items: dict[str, Item] = {}
        rels: dict[str, dict[str, Rel]] = {}

        for entry, content in entries.items():
            if content is None:
                content = {}

            if match := ITEM_RE.match(entry):
                items[match.group(1)] = Item(
                    keyword=content.get("keyword", match.group(1)),
                    keyword_separators=content.get("keyword_separator", _KEYWORK_SEP),
                )

            elif match := REL_RE.match(entry):
                rels.setdefault(match.group(1), {})[match.group(3)] = Rel(
                    identation=Identation(match.group(2))
                )

            else:
                raise ValueError(f"Invalid srcblock.Spec entry: {entry}")

        return cls(make_ruleset(items, rels))


def make_ruleset(
    items: dict[str, Item],
    rels: dict[str, dict[str, Rel]],
) -> dict[str, Spec.Rule]:

    ruleset: dict[str, Spec.Rule] = {}

    for item_id, item in items.items():

        child_items = []
        child_patterns = []

        for rel_id, rel in rels.get(item_id, {}).items():
            rel_item = items.get(rel_id)
            child_items.append(rel_id)
            # kw_sep = rel_item.get("kw_separator", _KEYWORK_SEP)
            child_patterns.append(
                f"("
                f"{rel.identation.re}"
                f"{escape(rel_item.keyword)}"
                f"(?:[{escape(rel_item.keyword_separators)}])"
                f")"
            )

        ruleset[item_id] = Spec.Rule(
            item_id=item_id,
            child_items=tuple(child_items),
            # child_pattern=compile("^" + "|".join(child_patterns) + "$"),
            child_pattern=compile("^" + "|".join(child_patterns)),
        )

    return ruleset


