from pydantic import BaseModel


class StudentCreate(BaseModel):
    name: str
    surname: str
    birthyear: int
    semester: int
    email: str
    password: str       # plain password from the client; hashed before storage


class Student(BaseModel):
    ID: str
    name: str
    surname: str
    birthyear: int
    semester: int
    email: str
    # hashed_password is intentionally never included here — never returned to clients