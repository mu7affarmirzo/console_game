from pydantic import BaseModel


class LoginForm(BaseModel):
    nickname: str


class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    nickname: str
    credits: int

