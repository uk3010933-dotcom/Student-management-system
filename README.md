# Student Management API
A backend API built with FastAPI and SQLite to manage student records.
Uses SQLModel for database modeling and provides a foundation for CRUD operations.
## Tech Stack
- Python 3
- FastAPI
- SQLModel
- SQLite
- Uvicorn
## Project Structure
- app/ — FastAPI application code
- models.py — database models
- database.py — SQLite engine and setup
- main.py — API entry point
## How to Run
```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
Visit http://127.0.0.1:8000/docs

## Current Features (12/01/2025)
- Student model defined using SQLModel
- SQLite database with auto table creation
- FastAPI server setup
- API documentation via Swagger UI
## Planned Features (12/01/2025)
- Full CRUD operations for students
- Additional models (teachers, classrooms)
- Basic frontend for interacting with the API

