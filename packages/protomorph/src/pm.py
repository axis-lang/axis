import sys
import protomorph
import protomorph.reasoning
import protomorph.reasoning.subst
import protomorph.reasoning.vars
import protomorph.reasoning.stratify
import protomorph.unification

# Register pm.* submodule aliases so that `from pm.reasoning import X`,
# `from pm.reasoning.subst import Y`, `from pm.unification import Z`, etc.
# all work transparently by delegating to the protomorph package.
_this = sys.modules[__name__]
sys.modules['pm.reasoning'] = protomorph.reasoning
sys.modules['pm.reasoning.subst'] = protomorph.reasoning.subst
sys.modules['pm.reasoning.vars'] = protomorph.reasoning.vars
sys.modules['pm.reasoning.stratify'] = protomorph.reasoning.stratify
sys.modules['pm.unification'] = protomorph.unification

_this.reasoning = protomorph.reasoning
_this.unification = protomorph.unification

from protomorph import *
from protomorph import _project_type, _bootstrap_defaults
