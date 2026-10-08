from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from auth.models import CurrentUser
from auth.security import decode_access_token

# tokenUrl just tells the OpenAPI docs where to get a token — doesn't affect verification
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    """Decodes the JWT and returns the identity it carries. Does NOT re-query the
    database — the token is the source of truth until it expires (stateless auth).
    If you change someone's roles, they'll need to log in again to get a fresh token."""
    try:
        payload = decode_access_token(token)
        return CurrentUser(
            ID=payload["sub"],
            email=payload.get("email", ""),
            roles=payload.get("roles", []),
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_role(*allowed_roles: str):
    """Usage: Depends(require_role("Teacher", "Admin"))
    Passes if the current user has ANY of the allowed roles (multi-label people
    like Student+Teacher will match on whichever role the route requires)."""

    def checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not set(current_user.roles) & set(allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires one of: {', '.join(allowed_roles)}",
            )
        return current_user

    return checker