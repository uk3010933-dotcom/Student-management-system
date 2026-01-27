# Student Management API

A backend API built with FastAPI and SQLite for managing students, teachers, classrooms, and authentication.  
The project focuses on clean API design, business rule enforcement, and testability.

---

## Tech Stack
- Python 3
- FastAPI
- SQLModel
- SQLite
- JWT Authentication
- Pytest
- Uvicorn

---

## Features
- User authentication using JWT (register, login, protected routes)
- Student CRUD operations
- Teacher CRUD operations
- Classroom CRUD operations
- One-to-many relationships:
  - Teacher → Classroom
  - Classroom → Student
- Business rule enforcement
- Separate test database with automated tests

---

## Business Rules
- A student must belong to exactly one classroom  
- A classroom can contain many students  
- A classroom has exactly one teacher  
- Classroom capacity cannot be exceeded  
- Classroom capacity cannot be lowered below current enrollment  
- Teachers must exist before classrooms can be created  
- Teacher emails must be unique  
- Authentication is required for protected endpoints  
- The first registered user is assigned admin privileges  

---

## Authentication Flow
- Users register with an email and password
- Passwords are hashed before being stored
- Login returns a JWT access token
- Protected endpoints require an `Authorization: Bearer <token>` header

---

## Project Structure
app/
├── auth.py        # Authentication routes and JWT logic
├── models.py      # SQLModel database models
├── database.py    # SQLite engine and session setup
├── security.py    # Password hashing and verification
├── main.py        # API entry point
tests/
├── test_engine.py
├── test_students.py
├── test_teachers.py
├── test_classrooms.py
## How to Run
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload

