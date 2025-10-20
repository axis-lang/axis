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
    print(item)
  
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
