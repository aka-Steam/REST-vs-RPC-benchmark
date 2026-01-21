from datetime import datetime

from pydantic import BaseModel, Field


class TermBase(BaseModel):
    keyword: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)


class TermCreate(TermBase):
    pass


class TermUpdate(BaseModel):
    keyword: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, min_length=1)


class TermOut(BaseModel):
    id: int
    keyword: str
    description: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


