import os
from dotenv import load_dotenv
from sqlmodel import Session,create_engine,SQLModel

load_dotenv()

Database_URL=os.getenv("DB_URL")

if not Database_URL:
    raise ValueError("Database url is not set")

engine=create_engine(
    Database_URL,
    echo=True,
    pool_pre_ping=True
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session