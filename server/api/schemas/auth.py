from pydantic import BaseModel


class LoginSchema(BaseModel):
    nickname: str

