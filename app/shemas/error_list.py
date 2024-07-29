from typing import Optional

from pydantic import BaseModel, Extra, ConfigDict


class Ctx(BaseModel):

    model_config = ConfigDict(extra='forbid')

    ge: Optional[int] = None
    le: Optional[int] = None
    reason: Optional[str] = None
    error: Optional[dict] = {}


class ErrorParam(BaseModel):

    model_config = ConfigDict(extra='forbid')

    type: str
    loc: list[str]
    msg: str
    input: str | int
    ctx: Optional[Ctx] = None


class ErrorParams(BaseModel):

    model_config = ConfigDict(extra='forbid')

    detail: list[ErrorParam]
