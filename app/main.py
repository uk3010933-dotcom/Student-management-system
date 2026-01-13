from fastapi import FastAPI
from app.database import create_db_and_tables
from app.models import Student

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/students")
def get_students():
    return []

@app.post("/students")
def add_student(student: Student):
    return student
