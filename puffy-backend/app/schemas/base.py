from pydantic import BaseModel as PydanticBaseModel
from typing import Any, Dict


class BaseModel(PydanticBaseModel):

    def dict(self, exclude_none=True, **kwargs):
        return super().dict(exclude_none=exclude_none, **kwargs)
    
    class Config:
        from_attributes = True
        use_enum_values = True
        orm_mode = True

