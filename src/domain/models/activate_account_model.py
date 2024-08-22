from pydantic import BaseModel


class ActivateAccountModel(BaseModel):
    auth_id: int
    code: str
