from fastapi import APIRouter, Depends
from neo4j import AsyncSession
import uuid

from database import get_session
from models import Student, StudentCreate
from auth.security import hash_password
from auth.dependencies import require_role

router = APIRouter(prefix="/students", tags=["students"])


@router.post("", response_model=Student)
async def create_student(student: StudentCreate, session: AsyncSession = Depends(get_session)):
    # MERGE on email (the identity key). If this email already belongs to a
    # Person (e.g. an existing Teacher), we just ADD the :Student label to that
    # same node instead of creating a duplicate person — this is what makes the
    # "student who is also a teacher" multi-label case work.
    query = """
    MERGE (p:Person {email: $email})
    ON CREATE SET p.ID = $ID, p.name = $name, p.surname = $surname,
                  p.birthyear = $birthyear, p.hashed_password = $hashed_password
    SET p:Student, p.semester = $semester
    RETURN p.ID AS ID, p.name AS name, p.surname AS surname,
           p.birthyear AS birthyear, p.semester AS semester, p.email AS email
    """
    new_id = str(uuid.uuid4())
    hashed = hash_password(student.password)
    params = student.model_dump(exclude={"password"})
    result = await session.run(query, ID=new_id, hashed_password=hashed, **params)
    record = await result.single()
    return Student(**record.data())


@router.get("", response_model=list[Student])
async def list_students(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_role("Student", "Teacher", "Admin")),
):
    query = """
    MATCH (s:Student)
    RETURN s.ID AS ID, s.name AS name, s.surname AS surname,
           s.birthyear AS birthyear, s.semester AS semester, s.email AS email
    """
    result = await session.run(query)
    records = await result.data()
    return [Student(**r) for r in records]