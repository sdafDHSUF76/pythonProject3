from pydantic import BaseModel, ConfigDict, HttpUrl, field_validator


class Configs(BaseModel):
    model_config = ConfigDict(extra='forbid')

    base_url: HttpUrl

    @field_validator('base_url')
    @classmethod
    def convert_base_url_to_str(cls, v: HttpUrl) -> str:
        return str(v)
