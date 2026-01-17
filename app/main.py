from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from app.database import create_db_and_tables, engine
from app.models import Student,Teachers

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
@app.get("/teachers")
def get_teachers(session: Session = Depends(get_session)):
    teachers = session.exec(select(Teachers)).all()
    return teachers

@app.post("/teachers")
def add_teacher(teacher: Teachers, session: Session = Depends(get_session)):
    teacher.id = None
    session.add(teacher)
    session.commit()
    session.refresh(teacher)
    return teacher

@app.delete("/teachers/{teacher_id}")
def delete_teacher(teacher_id: int, session: Session = Depends(get_session)):
    teacher = session.get(Teachers, teacher_id)

    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    session.delete(teacher)
    session.commit()

    return {"deleted": True, "teacher_id": teacher_id}

@app.put("/teachers/{teacher_id}")
def update_teacher(teacher_id: int,updated_teacher: Teachers, session: Session=Depends(get_session)):
    teacher= session.get(Teacher, teacher_id)
    
    if not teacher:
        raise HTTPException(status_code=404,detail="Teacher not found")
    teacher.name= updated_teacher.name
    teacher.email = updated_teacher.email
    
    session.add(teacher)
    session.commit()
    session.refresh(teacher)

    return teacher