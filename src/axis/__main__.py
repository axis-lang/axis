# %%
from rich import print
from axis import syn, val, items


pkg = items.Package.from_path("codebase/sandbox")
db = pkg.database

eval = val.Evaluator()

def print_eval(str: str):
    print(eval(syn.Expr.from_str(str)))

def print_syn(str: str):
    print(syn.Expr.from_str(str))

print("database.entities", len(db.entities_by_shape))
print("database.namespaces", len(db.members_by_scope))
print("database.ref_shapes", tuple(ref.segments for ref in db.entities_by_shape))

def find_entity(*segments):
    return next(
        (
            entity
            for ref, entity in db.entities_by_shape.items()
            if ref.segments == tuple(segments)
        ),
        None,
    )

root_scope = next(
    (scope for scope in db.members_by_scope if scope.segments == ()),
    None,
)
if root_scope is not None:
    print("root.members", tuple(db.members_by_scope[root_scope].keys()))

sandbox_entity = find_entity("sandbox")
if sandbox_entity is not None:
    print("sandbox.members", tuple(sandbox_entity.members.keys()))
    print("sandbox.overloads", len(sandbox_entity.overload_buckets))
    print("sandbox.facts", len(sandbox_entity.facts))
    print("sandbox.constraints", len(sandbox_entity.constraints))

basic_entity = find_entity("sandbox", "basic")
if basic_entity is not None:
    print("sandbox.basic.members", tuple(basic_entity.members.keys()))
    print("sandbox.basic.overloads", len(basic_entity.overload_buckets))

demo_entity = find_entity("sandbox", "demo")
if demo_entity is not None:
    print("sandbox.demo.members", tuple(demo_entity.members.keys()))
    print("sandbox.demo.overloads", len(demo_entity.overload_buckets))

point_entity = find_entity("sandbox", "demo", "Point")
if point_entity is not None:
    print("sandbox.demo.Point.overloads", len(point_entity.overload_buckets))
    print("sandbox.demo.Point.returns", sum(len(b.returns) for b in point_entity.overload_buckets.values()))

add_entity = find_entity("sandbox", "demo", "Add")
if add_entity is not None:
    print("sandbox.demo.Add.overloads", len(add_entity.overload_buckets))
    print("sandbox.demo.Add.returns", sum(len(b.returns) for b in add_entity.overload_buckets.values()))

default_entity = find_entity("sandbox", "demo", "Default")
if default_entity is not None:
    print("sandbox.demo.Default.injectors", len(default_entity.overload_buckets))
    print("sandbox.demo.Default.constraints", len(default_entity.constraints))

id_entity = find_entity("sandbox", "demo", "Id")
if id_entity is not None:
    print("sandbox.demo.Id.overloads", len(id_entity.overload_buckets))
    print("sandbox.demo.Id.returns", sum(len(b.returns) for b in id_entity.overload_buckets.values()))

clamp_entity = find_entity("sandbox", "demo", "Clamp")
if clamp_entity is not None:
    print("sandbox.demo.Clamp.overloads", len(clamp_entity.overload_buckets))
    print("sandbox.demo.Clamp.returns", sum(len(b.returns) for b in clamp_entity.overload_buckets.values()))

origin_entity = find_entity("sandbox", "demo", "origin")
if origin_entity is not None:
    print("sandbox.demo.origin.facts", len(origin_entity.facts))
  
# print_eval(
#     """
#     (
#         (1,0,0),
#         (0,1,0),
#         (0,0,1),
#     )
#     """
# )

# zip
# (..(a,b)): (..a, ..b) = ((1,2,3), (4,5,6))
# unzip
# ((..a: $a), (..b: $b)): (..(a: $a, b: $b)) = ((1,4), (2,5), (3,6))

# # with pkg as evaluator:
# #     # enter a repl
