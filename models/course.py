from pydantic import BaseModel


class CourseCreate(BaseModel):
    name: str
    semester: int


class Course(BaseModel):
    ID: str
    name: str
    semester: int