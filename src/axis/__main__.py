# %%
from rich import print
from axis import sem, src, syn, val, expr, items


pkg = items.Package.from_path('codebase/std-core')

eval = val.Evaluator()


def print_eval(str: str):
    print(eval(syn.Expr.from_str(str)))

def print_syn(str: str):
    print(syn.Expr.from_str(str))


# print(pkg.all_items)
# print(syn.Expr.from_str('Array[3,3] Natural'))

# a::[Shape]

print_syn("T ..a")
# print_eval("((a=1,2,3), b=(x=1, y=2))")
# print_eval(
#     """
#     (
#         (1,0,0),
#         (0,1,0),
#         (0,0,1)
#     )
#     """
# )

# # with pkg as evaluator:
# #     # enter a repl
