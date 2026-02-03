from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

from app.database import create_db_and_tables, engine
from app.models import Student, Teachers, Classroom

from app.auth import router as auth_router
from app.auth import get_current_user


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(auth_router)


def get_session():
    with Session(engine) as session:
        yield session


# ---------------- AUTH / ROLE DEPENDENCIES ----------------

def admin_required(current_user=Depends(get_current_user)):
    # strict: default False if missing
    is_admin = bool(getattr(current_user, "is_admin", False))
    if not is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


# ---------------- PAGES ----------------

@app.get("/")
def login_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/dashboard")
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


# ---------------- STARTUP ----------------

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# ---------------- HEALTH / ME ----------------

@app.get("/api/health")
def health():
    return {"message": "ok"}


@app.get("/api/me")
def me(current_user=Depends(get_current_user)):
    return {
        "message": "authenticated",
        "email": current_user.email,
        "is_admin": getattr(current_user, "is_admin", False),
    }


# ---------------- STUDENTS (ADMIN ONLY) ----------------

@app.get("/students")
def get_students(
    session: Session = Depends(get_session),
    _admin=Depends(admin_required),
):
    students = session.exec(select(Student)).all()
    return students


@app.post("/students")
def add_student(
    student: Student,
    session: Session = Depends(get_session),
    _admin=Depends(admin_required),
):
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
def delete_student(
    student_id: int,
    session: Session = Depends(get_session),
    _admin=Depends(admin_required),
):
    student = session.get(Student, student_id)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    session.delete(student)
    session.commit()

    return {"deleted": True, "student_id": student_id}


@app.put("/students/{student_id}")
def update_student(
    student_id: int,
    updated_student: Student,
    session: Session = Depends(get_session),
    _admin=Depends(admin_required),
):
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


# ---------------- TEACHERS (ADMIN ONLY) ----------------

@app.get("/teachers")
def get_teachers(
    session: Session = Depends(get_session),
    _admin=Depends(admin_required),
):
    teachers = session.exec(select(Teachers)).all()
    return teachers


@app.post("/teachers")
def add_teacher(
    teacher: Teachers,
    session: Session = Depends(get_session),
    _admin=Depends(admin_required),
):
    teacher.id = None

    if teacher.email is not None:
        existing = session.exec(
            select(Teachers).where(Teachers.email == teacher.email)
        ).first()
        if existing:
            raise HTTPException(status_code=409, detail="Email already in use")

    session.add(teacher)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Insert failed (duplicate id or email).")

    session.refresh(teacher)
    return teacher


@app.delete("/teachers/{teacher_id}")
def delete_teacher(
    teacher_id: int,
    session: Session = Depends(get_session),
    _admin=Depends(admin_required),
):
    teacher = session.get(Teachers, teacher_id)

    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    session.delete(teacher)
    session.commit()

    return {"deleted": True, "teacher_id": teacher_id}


@app.put("/teachers/{teacher_id}")
def update_teacher(
    teacher_id: int,
    updated_teacher: Teachers,
    session: Session = Depends(get_session),
    _admin=Depends(admin_required),
):
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


# ---------------- CLASSROOMS (ADMIN ONLY) ----------------

@app.get("/classrooms")
def get_classrooms(
    session: Session = Depends(get_session),
    _admin=Depends(admin_required),
):
    classrooms = session.exec(select(Classroom)).all()
    return classrooms


@app.get("/classrooms/{classroom_id}")
def get_classroom(
    classroom_id: int,
    session: Session = Depends(get_session),
    _admin=Depends(admin_required),
):
    classroom = session.get(Classroom, classroom_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    return classroom


@app.post("/classrooms")
def add_classroom(
    classroom: Classroom,
    session: Session = Depends(get_session),
    _admin=Depends(admin_required),
):
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
def delete_classroom(
    classroom_id: int,
    session: Session = Depends(get_session),
    _admin=Depends(admin_required),
):
    classroom = session.get(Classroom, classroom_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    session.delete(classroom)
    session.commit()
    return {"deleted": True, "classroom_id": classroom_id}


@app.put("/classrooms/{classroom_id}")
def update_classroom(
    classroom_id: int,
    updated_classroom: Classroom,
    session: Session = Depends(get_session),
    _admin=Depends(admin_required),
):
    classroom = session.get(Classroom, classroom_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    if updated_classroom.capacity <= 0:
        raise HTTPException(status_code=400, detail="Capacity must be a positive integer")

    current_students = session.exec(
        select(Student).where(Student.classroom_id == classroom_id)
    ).all()

    if updated_classroom.capacity < len(current_students):
        raise HTTPException(
            status_code=400,
            detail="Capacity cannot be less than current student count"
        )

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

def teacher_ctx(
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    # Admin can do everything
    if current_user.is_admin:
        return {"is_admin": True, "teacher": None}

    teacher = session.exec(
        select(Teachers).where(Teachers.user_id == current_user.id)
    ).first()

    if not teacher:
        raise HTTPException(status_code=403, detail="Not a teacher account")

    return {"is_admin": False, "teacher": teacher}

@app.get("/my/classrooms")
def my_classrooms(
    session: Session = Depends(get_session),
    ctx=Depends(teacher_ctx),
):
    if ctx["is_admin"]:
        raise HTTPException(status_code=400, detail="Admins use /classrooms")

    teacher = ctx["teacher"]
    return session.exec(
        select(Classroom).where(Classroom.teacher_id == teacher.id)
    ).all()

@app.get("/my/classrooms/{classroom_id}/students")
def my_students(
    classroom_id: int,
    session: Session = Depends(get_session),
    ctx=Depends(teacher_ctx),
):
    classroom = session.get(Classroom, classroom_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    if not ctx["is_admin"]:
        if classroom.teacher_id != ctx["teacher"].id:
            raise HTTPException(status_code=403, detail="Not your classroom")

    return session.exec(
        select(Student).where(Student.classroom_id == classroom_id)
    ).all()

@app.post("/my/students")
def teacher_add_student(
    student: Student,
    session: Session = Depends(get_session),
    ctx=Depends(teacher_ctx),
):
    if ctx["is_admin"]:
        raise HTTPException(status_code=400, detail="Admins use /students")

    classroom = session.get(Classroom, student.classroom_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    if classroom.teacher_id != ctx["teacher"].id:
        raise HTTPException(status_code=403, detail="Not your classroom")

    current = session.exec(
        select(Student).where(Student.classroom_id == classroom.id)
    ).all()

    if len(current) >= classroom.capacity:
        raise HTTPException(status_code=400, detail="Classroom is full")

    student.id = None
    session.add(student)
    session.commit()
    session.refresh(student)
    return student

@app.put("/my/students/{student_id}")
def teacher_update_student(
    student_id: int,
    updated: Student,
    session: Session = Depends(get_session),
    ctx=Depends(teacher_ctx),
):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    old_class = session.get(Classroom, student.classroom_id)
    new_class = session.get(Classroom, updated.classroom_id)

    if not new_class:
        raise HTTPException(status_code=404, detail="Classroom not found")

    if not ctx["is_admin"]:
        teacher_id = ctx["teacher"].id
        if old_class.teacher_id != teacher_id or new_class.teacher_id != teacher_id:
            raise HTTPException(status_code=403, detail="You must teach both classes")

    current = session.exec(
        select(Student).where(Student.classroom_id == new_class.id)
    ).all()

    if len(current) >= new_class.capacity:
        raise HTTPException(status_code=400, detail="Classroom is full")

    student.name = updated.name
    student.age = updated.age
    student.is_enrolled = updated.is_enrolled
    student.classroom_id = updated.classroom_id

    session.add(student)
    session.commit()
    session.refresh(student)
    return student

@app.delete("/my/students/{student_id}")
def teacher_delete_student(
    student_id: int,
    session: Session = Depends(get_session),
    ctx=Depends(teacher_ctx),
):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    classroom = session.get(Classroom, student.classroom_id)

    if not ctx["is_admin"]:
        if classroom.teacher_id != ctx["teacher"].id:
            raise HTTPException(status_code=403, detail="Not your student")

    session.delete(student)
    session.commit()
    return {"deleted": True}

