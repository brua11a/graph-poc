import uuid

from fastapi import APIRouter, Depends
from neo4j import AsyncSession

from database import get_session
from models import Course, CourseCreate
from auth.dependencies import require_role

router = APIRouter(prefix="/courses", tags=["courses"])


@router.post("", response_model=Course)
async def create_course(
    course: CourseCreate,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_role("Teacher", "Admin")),   # students CANNOT add courses
):
    query = """
    MERGE (c:Course {name: $name, semester: $semester})
    ON CREATE SET c.ID = $ID
    RETURN c.ID AS ID, c.name AS name, c.semester AS semester
    """
    new_id = str(uuid.uuid4())
    result = await session.run(query, ID=new_id, **course.model_dump())
    record = await result.single()
    return Course(**record.data())


@router.get("", response_model=list[Course])
async def list_courses(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_role("Student", "Teacher", "Admin")),
):
    query = "MATCH (c:Course) RETURN c.ID AS ID, c.name AS name, c.semester AS semester"
    result = await session.run(query)
    records = await result.data()
    return [Course(**r) for r in records]