from sqlmodel import SQLModel, Field
from typing import Optional
class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    age: int
    is_enrolled: bool = Field(nullable=False, default=True) 

class Teachers(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: Optional[str] = None
