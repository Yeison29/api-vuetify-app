from fastapi import FastAPI
from src.infrastructure.contrrollers.routers import ApiRouter
from src.infrastructure.adapters.data_sources.db_config import create_tables, database, update_weeks_crops_periodicals
from fastapi.middleware.cors import CORSMiddleware

api_router = ApiRouter()


class App:
    def __init__(self):
        self.app = FastAPI()
        self.configure()
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["*"],
        )

    def configure(self):
        create_tables()
        update_weeks_crops_periodicals()
        self.app.include_router(api_router.router)

    @staticmethod
    async def startup():
        await database.connect()

    @staticmethod
    async def shutdown():
        await database.disconnect()


app = App()
