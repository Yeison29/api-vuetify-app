from pydantic import BaseModel
from typing import Optional


class AuthenticationModel(BaseModel):
    auth_password: str


class AuthenticationModelReceive(AuthenticationModel):
    auth_email_user: str
    auth_user_id: int


class AuthenticationModelIn(AuthenticationModelReceive):
    auth_disabled: bool
    code_valid: str


class AuthenticationModelOut(AuthenticationModelIn):
    id_auth: int


class AuthenticationModelOutToken(AuthenticationModelOut):
    name_user: str


class AuthenticationModelUpdate(AuthenticationModelIn):
    auth_email: Optional[str] = None
    auth_password: Optional[str] = None
    auth_disabled: Optional[bool] = None
    auth_user_id: int
