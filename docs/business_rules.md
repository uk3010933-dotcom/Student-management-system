# Business Rules

## Scope
This project models a primary-school student management system with Students, Classes, and Teachers.

## Entities
### Student
- A Student has: id, name, is_enrolled, class_id
- A Student belongs to exactly one Class.

### Class
- A Class has: id, name, grade, capacity, teacher_id
- A Class contains many Students.
- A Class is assigned to exactly one Teacher.

### Teacher
- A Teacher has: id, name, email
- A Teacher may be assigned to zero or many Classes.

## Rules & Constraints
1. Each Student must belong to exactly one Class. (Student.class_id is required)
2. Each Class must have exactly one Teacher. (Class.teacher_id is required)
3. A Teacher can be assigned to multiple Classes.
4. Class capacity must be a positive integer.
5. A Class cannot have more Students than its capacity. (enforced in API logic)
6. is_enrolled must always be True/False (never null).
7. Teacher email should be unique.

## Assumptions
- We only track a student's current class (no class-history yet).
- Each class represents a homeroom for a grade (e.g., "Year 3A"), not a subject.
- Students are primary school kids and do not enroll in multiple classes simultaneously.
