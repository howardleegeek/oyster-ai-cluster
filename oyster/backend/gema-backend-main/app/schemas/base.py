from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):
    def dict(self, exclude_none=True, **kwargs):
        return super().dict(exclude_none=exclude_none, **kwargs)

