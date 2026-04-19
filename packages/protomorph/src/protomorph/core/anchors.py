from __future__ import annotations

from .foundation import Anchor


any = Anchor("std.types.Any")
tuple = Anchor("std.types.Tuple")
index = Anchor("std.types.Index")
never = Anchor("std.types.Never")
integer = Anchor("std.types.Integer")
text = Anchor("std.types.Text")
decimal = Anchor("std.types.Decimal")
boolean = Anchor("std.types.Boolean")
empty = Anchor("std.types.Empty")
id = Anchor("std.types.Id")
anchor = Anchor("std.types.Anchor")

optional = Anchor("std.qualifiers.Optional")
#list = Anchor("std.qualifiers.List")
set = Anchor("std.qualifiers.Set")
map = Anchor("std.qualifiers.Map")
result = Anchor("std.qualifiers.Result")

type = Anchor("std.metas.Type")
specialization = Anchor("std.metas.Specialization")
qualification = Anchor("std.metas.Qualification")
union = Anchor("std.metas.Union")
uniform = Anchor("std.metas.Uniform")
varying = Anchor("std.metas.Varying")
indexed = Anchor("std.metas.Indexed")
shape = Anchor("std.metas.Shape")

conforms = Anchor("std.facts.Conforms")
