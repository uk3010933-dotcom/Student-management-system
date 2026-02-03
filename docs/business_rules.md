# Business Rules

## Scope
This project models a primary-school student management system with role-based access control.  
The system manages Students, Classrooms, Teachers, and Users, and enforces permissions based on user roles.

---

## Entities

### Student
- A Student has: `id`, `name`, `age`, `is_enrolled`, `classroom_id`
- A Student belongs to **exactly one Classroom**.

### Classroom
- A Classroom has: `id`, `name`, `grade`, `capacity`, `teacher_id`
- A Classroom contains **many Students**.
- A Classroom is assigned to **exactly one Teacher**.

### Teacher
- A Teacher has: `id`, `name`, `email`, `user_id`
- A Teacher may be assigned to **zero or many Classrooms**.
- Each Teacher may be linked to **at most one User account**.

### User
- A User has: `id`, `email`, `hashed_password`, `is_admin`
- A User may be either an **Admin user** or a **Teacher user**.
- Teacher users are linked to Teacher records via `Teachers.user_id`.

---

## Core Data Rules & Constraints

1. Each Student must belong to exactly one Classroom. (`Student.classroom_id` is required)
2. Each Classroom must have exactly one Teacher. (`Classroom.teacher_id` is required)
3. A Teacher may be assigned to multiple Classrooms.
4. Classroom capacity must be a positive integer.
5. A Classroom cannot contain more Students than its capacity.
6. `is_enrolled` must always be either `true` or `false` (never null).
7. Teacher email addresses must be unique.

---

## Access Control Rules

### Admin Users
Admins have full access to the system and can:
- Create, view, update, and delete **Students**
- Create, view, update, and delete **Teachers**
- Create, view, update, and delete **Classrooms**
- Assign Teachers to Classrooms
- Assign Users to Teacher records

Admins are not restricted by classroom ownership.

---

### Teacher Users
Teacher users have restricted access and can only manage data related to the classrooms they teach.

Teacher users can:
- View **only the Classrooms** assigned to them
- View **only the Students** in their Classrooms
- Add Students **only to their own Classrooms**
- Update Students **only within their own Classrooms**
- Delete Students **only from their own Classrooms**
- Move a Student between Classrooms **only if they teach both Classrooms**

Teacher users **cannot**:
- Create or delete Classrooms
- Assign themselves to Classrooms
- View or modify Classrooms they do not teach
- View or modify Students belonging to other Teachers
- Create, update, or delete Teacher records

---

## Assumptions

- Each Student is enrolled in only one Classroom at a time (no class history tracking).
- Classrooms represent homerooms (e.g. "Year 3A"), not subject-specific classes.
- A Teacher may teach multiple Classrooms.
- A User can only be linked to one Teacher record.
- Access control is enforced at the API level and does not rely on frontend-only restrictions.

---

## Notes

- Ownership and permissions are enforced using authenticated Users and server-side role checks.
- All sensitive operations are validated on the backend to prevent unauthorized access.
