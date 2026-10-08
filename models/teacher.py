from pydantic import BaseModel


class TeacherCreate(BaseModel):
    name: str
    surname: str
    birthyear: int
    specialization: str
    email: str
    password: str       # plain password from the client; hashed before storage


class Teacher(BaseModel):
    ID: str
    name: str
    surname: str
    birthyear: int
    specialization: str
    email: str
    # hashed_password is intentionally never included here — never returned to clients