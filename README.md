# Student Management API

A backend API built with FastAPI and SQLite for managing students, teachers, classrooms, and users, with **role-based access control**.

The project focuses on clean API design, strict business rule enforcement, and testability, and models a realistic primary-school management system.

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
- Role-based access control (Admin vs Teacher)
- Student CRUD operations with ownership enforcement
- Teacher CRUD operations (admin-only)
- Classroom CRUD operations (admin-only)
- Teacher-scoped student management
- One-to-many relationships:
  - Teacher → Classrooms
  - Classroom → Students
- Business rule enforcement at the API level
- Separate test database with automated tests

---

## Roles & Permissions

### Admin Users
Admins have full system access and can:
- Create, view, update, and delete Students
- Create, view, update, and delete Teachers
- Create, view, update, and delete Classrooms
- Assign Teachers to Classrooms
- Link Users to Teacher records

Admins are not restricted by classroom ownership.

---

### Teacher Users
Teacher users have restricted access based on ownership.

Teachers can:
- View **only the Classrooms they teach**
- View **only the Students in their Classrooms**
- Add Students **to their own Classrooms**
- Update Students **in their own Classrooms**
- Delete Students **from their own Classrooms**
- Move a Student between Classrooms **only if they teach both Classrooms**

Teachers cannot:
- Create or delete Classrooms
- Assign themselves to Classrooms
- View or modify other Teachers
- Access Students or Classrooms they do not teach

---

## Business Rules
- A Student must belong to exactly one Classroom  
- A Classroom can contain many Students  
- A Classroom has exactly one Teacher  
- A Teacher may teach multiple Classrooms  
- Classroom capacity must be a positive integer  
- Classroom capacity cannot be exceeded  
- Classroom capacity cannot be lowered below current enrollment  
- Teachers must exist before Classrooms can be created  
- Teacher email addresses must be unique  
- Each Teacher may be linked to at most one User account  
- Authentication is required for all protected endpoints  
- Authorization is enforced at the API level (not frontend-only)  

---

## Authentication Flow
- Users register with an email and password
- Passwords are hashed before being stored
- Login returns a JWT access token
- Protected endpoints require an  
  `Authorization: Bearer <token>` header
- User role (`is_admin`) determines access level

---

## Project Structure
app/
├── auth.py # Authentication routes and JWT logic
├── models.py # SQLModel database models
├── database.py # SQLite engine and session setup
├── security.py # Password hashing and verification
├── main.py # API entry point
tests/
├── test_engine.py
├── test_students.py
├── test_teachers.py
├── test_classrooms.py

## How to Run
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload