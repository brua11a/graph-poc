from fastapi import APIRouter, Depends, HTTPException
from neo4j import AsyncSession

from database import get_session
from models import Student, Teacher
from auth.dependencies import require_role, CurrentUser

router = APIRouter(tags=["relationships"])


@router.post("/students/{student_id}/attends/{course_id}")
async def student_attends_course(
    student_id: str,
    course_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(require_role("Student")),
):
    # Object-level check: a student may only enroll THEMSELVES, never another student.
    # Role check alone isn't enough here — without this, any student could enroll
    # someone else just by changing the URL.
    if current_user.ID != student_id:
        raise HTTPException(status_code=403, detail="You can only enroll yourself")

    query = """
    MATCH (s:Student {ID: $student_id}), (c:Course {ID: $course_id})
    MERGE (s)-[:ATTENDS]->(c)
    RETURN s.ID AS student_id, c.ID AS course_id
    """
    result = await session.run(query, student_id=student_id, course_id=course_id)
    record = await result.single()
    if record is None:
        raise HTTPException(status_code=404, detail="Student or Course not found")
    return {"status": "linked", "student_id": student_id, "course_id": course_id}


@router.post("/teachers/{teacher_id}/teaches/{course_id}")
async def teacher_teaches_course(
    teacher_id: str,
    course_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(require_role("Teacher", "Admin")),
):
    # Teachers may only assign themselves; Admins may assign anyone.
    if "Admin" not in current_user.roles and current_user.ID != teacher_id:
        raise HTTPException(status_code=403, detail="You can only assign yourself to a course")

    query = """
    MATCH (t:Teacher {ID: $teacher_id}), (c:Course {ID: $course_id})
    MERGE (t)-[:TEACHES]->(c)
    RETURN t.ID AS teacher_id, c.ID AS course_id
    """
    result = await session.run(query, teacher_id=teacher_id, course_id=course_id)
    record = await result.single()
    if record is None:
        raise HTTPException(status_code=404, detail="Teacher or Course not found")
    return {"status": "linked", "teacher_id": teacher_id, "course_id": course_id}


@router.get("/courses/{course_id}/students", response_model=list[Student])
async def get_course_students(
    course_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(require_role("Student", "Teacher", "Admin")),
):
    query = """
    MATCH (s:Student)-[:ATTENDS]->(c:Course {ID: $course_id})
    RETURN s.ID AS ID, s.name AS name, s.surname AS surname,
           s.birthyear AS birthyear, s.semester AS semester, s.email AS email
    """
    result = await session.run(query, course_id=course_id)
    records = await result.data()
    return [Student(**r) for r in records]


@router.get("/courses/{course_id}/teachers", response_model=list[Teacher])
async def get_course_teachers(
    course_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(require_role("Student", "Teacher", "Admin")),
):
    query = """
    MATCH (t:Teacher)-[:TEACHES]->(c:Course {ID: $course_id})
    RETURN t.ID AS ID, t.name AS name, t.surname AS surname,
           t.birthyear AS birthyear, t.specialization AS specialization, t.email AS email
    """
    result = await session.run(query, course_id=course_id)
    records = await result.data()
    return [Teacher(**r) for r in records]