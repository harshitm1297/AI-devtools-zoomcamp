from typing import Annotated

from fastapi import Header, HTTPException, status

from .schemas import Member


DEMO_TOKEN = "demo-token"
DEMO_MANAGER = Member(
    id="user-1",
    name="Maya Chen",
    initials="MC",
    role="Project manager",
)


def require_user(
    authorization: Annotated[str | None, Header()] = None,
) -> Member:
    if authorization != f"Bearer {DEMO_TOKEN}":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid bearer token is required.",
        )
    return DEMO_MANAGER
