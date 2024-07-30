from typing import Optional

from pydantic import BaseModel, ConfigDict


class Ctx(BaseModel):

    model_config = ConfigDict(extra='forbid')

    ge: Optional[int] = None
    le: Optional[int] = None
    reason: Optional[str] = None
    error: Optional[dict] = {}


class Error(BaseModel):

    model_config = ConfigDict(extra='forbid')

    error: str


class ErrorParam(BaseModel):

    model_config = ConfigDict(extra='forbid')

    type: str
    loc: list[str]
    msg: str
    input: Optional[str | int | dict]
    ctx: Optional[Ctx] | Error = None


class ErrorParams(BaseModel):

    model_config = ConfigDict(extra='forbid')

    detail: list[ErrorParam] | str
