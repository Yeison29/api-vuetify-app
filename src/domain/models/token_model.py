from pydantic import BaseModel


class TokenModel(BaseModel):
    access_token: str
    token_type: str
    name_user: str
    user_id: int
    email_user: str
