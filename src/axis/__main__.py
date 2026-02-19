# %%
from rich import print
from axis import syn, val, items


pkg = items.Package.from_path("codebase/std-core")
db = pkg.database

eval = val.Evaluator()

def print_eval(str: str):
    print(eval(syn.Expr.from_str(str)))

def print_syn(str: str):
    print(syn.Expr.from_str(str))

print("database.entities", len(db.entities_by_shape))
print("database.namespaces", len(db.members_by_scope))

std_entity = next(
    (entity for ref, entity in db.entities_by_shape.items() if ref.segments == ("std",)),
    None,
)
if std_entity is not None:
    print("std.members", tuple(std_entity.members.keys()))
  
print_eval(
    """
    (
        (1,0,0),
        (0,1,0),
        (0,0,1),
    )
    """
)

# zip
# (..(a,b)): (..a, ..b) = ((1,2,3), (4,5,6))
# unzip
# ((..a: $a), (..b: $b)): (..(a: $a, b: $b)) = ((1,4), (2,5), (3,6))

# # with pkg as evaluator:
# #     # enter a repl
