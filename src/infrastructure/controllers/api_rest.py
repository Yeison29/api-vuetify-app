from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from src.domain.uses_cases.user_use_cases import AuthenticationModel, AuthenticationUseCase

oauth2_scheme = OAuth2PasswordBearer("/token")


class ApiRest:

    @staticmethod
    async def token(form_data: OAuth2PasswordRequestForm = Depends()):
        response = await AuthenticationUseCase.authenticate_user(form_data.password, form_data.username)
        return response
