from sqlmodel import SQLModel, create_engine
from app.models import Student

DATABASE_URL = "sqlite:///students.db"

engine = create_engine(DATABASE_URL)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
