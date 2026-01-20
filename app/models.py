from sqlmodel import SQLModel, Field
from typing import Optional
class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    age: int
    is_enrolled: bool = Field(nullable=False, default=True) 
    classroom_id: int= Field(foreign_key="classroom.id")

class Teachers(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: Optional[str] = None

class Classroom(SQLModel, table=True):
    id: Optional[int]=Field(default=None, primary_key=True)
    name: str
    grade: int
    teacher_id: int =Field(foreign_key="teachers.id")
    capacity: int