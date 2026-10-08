from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CurrentUser(BaseModel):
    ID: str
    email: str
    roles: list[str]   # e.g. ["Student"], ["Teacher"], or ["Student", "Teacher"]