from sqlmodel import SQLModel, create_engine
from app.models import Student,Teachers,Classroom
from sqlmodel import Session
import os

TEST_DATABASE_URL = "sqlite:///./test.db"

test_engine = create_engine(TEST_DATABASE_URL)


def create_db_and_tables():
    SQLModel.metadata.create_all(test_engine)

def get_test_session():
    with Session(test_engine) as session:
        yield session
def reset_test_db():
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)