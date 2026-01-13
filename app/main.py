from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from app.database import create_db_and_tables, engine
from app.models import Student

app = FastAPI()
def get_session():
    with Session(engine) as session:
        yield session

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/students")
def get_students(session: Session=Depends(get_session)):
    students=session.exec(select(Student)).all()
    return students

@app.post("/students")
def add_student(student: Student, session: Session = Depends(get_session)):
    session.add(student)
    session.commit()
    session.refresh(student)
    return student

@app.delete("/students/{student_id}")
def delete_student(student_id: int, session: Session = Depends(get_session)):
    student = session.get(Student, student_id)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    session.delete(student)
    session.commit()

    return {"deleted": True, "student_id": student_id}

@app.put("/students/{student_id}")
def update_student(student_id: int, updated_student: Student, session: Session = Depends(get_session)):
    student = session.get(Student, student_id)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student.name = updated_student.name
    student.age = updated_student.age

    session.add(student)
    session.commit()
    session.refresh(student)

    return student

