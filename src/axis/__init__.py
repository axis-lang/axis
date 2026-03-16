from rich import pretty
from rich import traceback
pretty.install(
    crop=True,
    overflow="fold",
)
traceback.install()


import axis.src
import axis.syn
import axis.sem


