from pydantic import BaseModel

from .guide import Guide


class IgList(BaseModel):
    guides: list[Guide] = []
