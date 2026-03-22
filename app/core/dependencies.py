from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.core.exceptions import ForbiddenException


# ---------------------------------------------------------------------------
# This is FastAPI's answer to .NET's IServiceCollection or Spring's IoC container.
#
# Instead of a DI container that wires everything at startup, FastAPI uses
# plain functions marked with Depends(). FastAPI calls them automatically
# and injects the results into your route handlers.
#
# The chain looks like this for a protected route:
#
#   HTTP Request
#       │
#       ▼
#   Route handler
#       │ needs CurrentUser
#       ▼
#   get_current_user(credentials, auth_service)
#       │ needs AuthService
#       ▼
#   get_auth_service(user_repo)
#       │ needs UserRepository
#       ▼
#   get_user_repository(db)
#       │ needs Session
#       ▼
#   get_db()  ← opens DB session, yields it, closes after request
#
# FastAPI resolves this entire chain automatically. You declare what you
# need, it figures out the order and wires it up.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Database session
# ---------------------------------------------------------------------------
def get_db():
    """
    'yield' makes this a context manager dependency.
    FastAPI guarantees the code after yield runs after the request completes,
    even if an exception was raised.

    This is equivalent to a using() block in C# or try-with-resources in Java.
    One session per request, closed when done — same as scoped DbContext in EF Core.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Repository & Service factories
# ---------------------------------------------------------------------------
def get_user_repository(db: Annotated[Session, Depends(get_db)]) -> UserRepository:
    return UserRepository(db)


def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)]
) -> UserService:
    return UserService(user_repo)


def get_auth_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)]
) -> AuthService:
    return AuthService(user_repo)


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

# Extracts the Bearer token from the Authorization header automatically.
# FastAPI returns 403 if the header is missing entirely.
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    """
    Add this as a dependency on any route that requires authentication.
    It validates the JWT and returns the User entity.
    """
    return auth_service.get_current_user_from_token(credentials.credentials)


# ---------------------------------------------------------------------------
# Authorization — role guards
# ---------------------------------------------------------------------------
def require_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.role != UserRole.ADMIN:
        raise ForbiddenException("Admin access required")
    return current_user


def require_manager_or_above(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    if current_user.role not in (UserRole.ADMIN, UserRole.MANAGER):
        raise ForbiddenException("Manager or Admin access required")
    return current_user


# ---------------------------------------------------------------------------
# Type aliases — this is purely a convenience to keep route signatures clean.
#
# Instead of writing this in every route:
#   user: User = Depends(get_current_user)
#
# You write:
#   user: CurrentUser
#
# Same thing, much cleaner.
# ---------------------------------------------------------------------------
DBSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_admin)]
ManagerUser = Annotated[User, Depends(require_manager_or_above)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]