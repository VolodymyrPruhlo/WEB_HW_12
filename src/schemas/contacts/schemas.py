import pydantic
from datetime import datetime


class TestResponseSchema(pydantic.BaseModel):
    id: int
    name: str
    age: int
    email: str | None
    phone: str | None
    born_date: datetime | None

    class Config:
        orm_mode = True
        from_attributes = True


class TestRequestSchema(pydantic.BaseModel):
    name: str
    age: int
    email: str | None
    phone: str | None
    born_date: datetime | None

    class Config:
        orm_mode = True
        from_attributes = True
