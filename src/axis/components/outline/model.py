from typing import Optional
from protobase import Object, traits

class Rule(Object, traits.Basic):
    name: str
    file_extension: Optional[str]
    keyword: Optional[str]
    