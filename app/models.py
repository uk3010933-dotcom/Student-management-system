from sqlmodel import SQLModel, Field
from typing import Optional

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    is_admin: bool = Field(nullable=False, default=False)

class Teachers(SQLModel, table=True):
    __tablename__ = "teachers"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: Optional[str] = None
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", unique=True, index=True)

class Classroom(SQLModel, table=True):
    __tablename__ = "classrooms"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    grade: int
    teacher_id: int = Field(foreign_key="teachers.id")
    capacity: int

class Student(SQLModel, table=True):
    __tablename__ = "students"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    age: int
    is_enrolled: bool = Field(nullable=False, default=True)
    classroom_id: int = Field(foreign_key="classrooms.id")
