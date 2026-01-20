from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from app.database import create_db_and_tables, engine
from app.models import Student,Teachers, Classroom

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
    classroom = session.get(Classroom, student.classroom_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    current_students = session.exec(
        select(Student).where(Student.classroom_id == student.classroom_id)
    ).all()

    if len(current_students) >= classroom.capacity:
        raise HTTPException(status_code=400, detail="Classroom is full")

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

    classroom = session.get(Classroom, updated_student.classroom_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    if updated_student.classroom_id != student.classroom_id:
        current_students = session.exec(
            select(Student).where(Student.classroom_id == updated_student.classroom_id)
        ).all()

        if len(current_students) >= classroom.capacity:
            raise HTTPException(status_code=400, detail="Classroom is full")

    student.name = updated_student.name
    student.age = updated_student.age
    student.is_enrolled = updated_student.is_enrolled
    student.classroom_id = updated_student.classroom_id

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
    if teacher.email is not None:
        existing = session.exec(
            select(Teachers).where(Teachers.email == teacher.email)
        ).first()
        if existing:
            raise HTTPException(status_code=409, detail="Email already in use")

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
def update_teacher(teacher_id: int, updated_teacher: Teachers, session: Session = Depends(get_session)):
    teacher = session.get(Teachers, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    if updated_teacher.email is not None:
        existing = session.exec(
            select(Teachers).where(Teachers.email == updated_teacher.email)
        ).first()
        if existing and existing.id != teacher_id:
            raise HTTPException(status_code=409, detail="Email already in use")

    teacher.name = updated_teacher.name
    teacher.email = updated_teacher.email

    session.add(teacher)
    session.commit()
    session.refresh(teacher)
    return teacher


@app.get("/classrooms")
def get_classrooms(session: Session=Depends(get_session)):
    classrooms= session.exec(select(Classroom)).all()
    return classrooms

@app.get("/classrooms/{classroom_id}")
def get_classroom(classroom_id:int, session: Session=Depends(get_session)):
    classroom=session.get(Classroom, classroom_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    return classroom

@app.post("/classrooms")
def add_classroom(classroom: Classroom, session: Session = Depends(get_session)):
    teacher = session.get(Teachers, classroom.teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    if classroom.capacity <= 0:
        raise HTTPException(status_code=400, detail="Capacity must be a positive integer")

    session.add(classroom)
    session.commit()
    session.refresh(classroom)
    return classroom


@app.delete("/classrooms/{classroom_id}")
def delete_classroom(classroom_id: int, session: Session = Depends(get_session)):
    classroom = session.get(Classroom, classroom_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    session.delete(classroom)
    session.commit()
    return {"deleted": True, "classroom_id": classroom_id}

@app.put("/classrooms/{classroom_id}")
def update_classroom(classroom_id: int, updated_classroom: Classroom, session: Session = Depends(get_session)):
    classroom = session.get(Classroom, classroom_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    if updated_classroom.capacity <= 0:
        raise HTTPException(status_code=400, detail="Capacity must be a positive integer")

    if updated_classroom.teacher_id != classroom.teacher_id:
        teacher = session.get(Teachers, updated_classroom.teacher_id)
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")

    classroom.name = updated_classroom.name
    classroom.grade = updated_classroom.grade
    classroom.capacity = updated_classroom.capacity
    classroom.teacher_id = updated_classroom.teacher_id

    session.add(classroom)
    session.commit()
    session.refresh(classroom)
    return classroom

