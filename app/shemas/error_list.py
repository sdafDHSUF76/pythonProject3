from typing import Optional

from pydantic import BaseModel, Extra


class Ctx(BaseModel, extra=Extra.forbid):
    ge: Optional[int] = None
    le: Optional[int] = None
    reason: Optional[str] = None
    error: Optional[dict] = {}


class ErrorParam(BaseModel, extra=Extra.forbid):
    type: str
    loc: list[str]
    msg: str
    input: str | int
    ctx: Optional[Ctx] = None


class ErrorParams(BaseModel, extra=Extra.forbid):
    detail: list[ErrorParam]
