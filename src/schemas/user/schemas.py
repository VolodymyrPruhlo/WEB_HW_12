import pydantic

from datetime import datetime


class User(pydantic.BaseModel):
    username: str
    password: str


class UserDB(pydantic.BaseModel):
    id: int
    username: str
    hash_password: str
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class UserResponse(pydantic.BaseModel):
    user: UserDB
    detail: str = "User successfully created"


class TokenModel(pydantic.BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
