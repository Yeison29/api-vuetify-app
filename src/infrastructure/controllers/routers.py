from fastapi import APIRouter
from typing import List
from src.infrastructure.controllers.api_rest import ApiRest
from src.domain.uses_cases.authentication_use_cases import TokenModel


class ApiRouter:

    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.post("/token", status_code=200, response_model=TokenModel, tags=['token'])(ApiRest.token)
