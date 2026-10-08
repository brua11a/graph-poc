from fastapi import APIRouter, Depends
from neo4j import AsyncSession
import uuid

from database import get_session
from models import Teacher, TeacherCreate
from auth.security import hash_password
from auth.dependencies import require_role

router = APIRouter(prefix="/teachers", tags=["teachers"])


@router.post("", response_model=Teacher)
async def create_teacher(teacher: TeacherCreate, session: AsyncSession = Depends(get_session)):
    # Same Person-merge-by-email pattern as students — adds :Teacher label,
    # reusing the same node if this email already belongs to a Student.
    query = """
    MERGE (p:Person {email: $email})
    ON CREATE SET p.ID = $ID, p.name = $name, p.surname = $surname,
                  p.birthyear = $birthyear, p.hashed_password = $hashed_password
    SET p:Teacher, p.specialization = $specialization
    RETURN p.ID AS ID, p.name AS name, p.surname AS surname,
           p.birthyear AS birthyear, p.specialization AS specialization, p.email AS email
    """
    new_id = str(uuid.uuid4())
    hashed = hash_password(teacher.password)
    params = teacher.model_dump(exclude={"password"})
    result = await session.run(query, ID=new_id, hashed_password=hashed, **params)
    record = await result.single()
    return Teacher(**record.data())


@router.get("", response_model=list[Teacher])
async def list_teachers(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_role("Student", "Teacher", "Admin")),
):
    query = """
    MATCH (t:Teacher)
    RETURN t.ID AS ID, t.name AS name, t.surname AS surname,
           t.birthyear AS birthyear, t.specialization AS specialization, t.email AS email
    """
    result = await session.run(query)
    records = await result.data()
    return [Teacher(**r) for r in records]