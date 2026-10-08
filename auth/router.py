from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from neo4j import AsyncSession

from database import get_session
from auth.models import Token
from auth.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    # OAuth2PasswordRequestForm calls the field "username" — we treat it as email.
    # This shape (form-encoded, not JSON) is what lets Swagger's "Authorize"
    # button log in directly without any extra configuration.
    query = """
    MATCH (p:Person {email: $email})
    RETURN p.ID AS ID, p.email AS email, p.hashed_password AS hashed_password, labels(p) AS labels
    """
    result = await session.run(query, email=form_data.username)
    record = await result.single()

    if record is None or not verify_password(form_data.password, record["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    roles = [label for label in record["labels"] if label != "Person"]
    token = create_access_token(subject_id=record["ID"], email=record["email"], roles=roles)
    return Token(access_token=token)