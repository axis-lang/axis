# %%
from rich import print
from axis import sem, src, syn, val, expr, items


pkg = items.Package.from_path('codebase/std-core')

eval = val.Evaluator()

def print_eval(str: str):
    print(eval(syn.Expr.from_str(str)))

def print_syn(str: str):
    print(syn.Expr.from_str(str))


for item in pkg.all_items:
    if isinstance(item, items.Def):
        print(f"{item.expr=}")


#        print(f"  {item.expr=}")
# print(pkg.all_items)
# print(syn.Expr.from_str('Array[3,3] Natural'))

# a::[Shape]

# print_syn("if(a < b) {a} else {b}")
# print_eval("((a=1,2,3), b=(x=1, y=2))")
print_eval(
    """
    (
        (1,0,0),
        (0,1,0),
        (0,0,1)
    )
    """
)

# zip
# (..(a,b)): (..a, ..b) = ((1,2,3), (4,5,6))
# unzip
# ((..a: $a), (..b: $b)): (..(a: $a, b: $b)) = ((1,4), (2,5), (3,6))

# # with pkg as evaluator:
# #     # enter a repl
