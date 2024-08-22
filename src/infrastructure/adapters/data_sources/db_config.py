from sqlalchemy import create_engine
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
import os
import pytz

time_zone = pytz.timezone('America/Bogota')

load_dotenv()

host = os.getenv('HOST_NAME')
port = os.getenv('PORT')
database = os.getenv('DB_NAME')
user = os.getenv('USER_NAME')
schema = os.getenv("SCHEMA", 'public')
password = os.getenv('PASSWORD')
secret_key = os.getenv('SECRET_KEY')
algorithm = os.getenv('ALGORITHM')

DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}/{database}"

engine = create_engine(DATABASE_URL)


def create_tables():
    agro_web_entity.Base.metadata.create_all(engine)


Session = sessionmaker(bind=engine)
session = Session()
