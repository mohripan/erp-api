from fastapi import APIRouter, status

from app.core.dependencies import UserServiceDep, CurrentUser, AdminUser
from app.schemas.user import UserCreate, UserUpdate, UserRead
from app.models.user import UserRole
from app.core.exceptions import ForbiddenException

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserRead])
def list_users(
    service: UserServiceDep,
    _admin: AdminUser,
    skip: int = 0,
    limit: int = 100,
):
    """List all users — Admin only."""
    return service.get_all(skip=skip, limit=limit)


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, service: UserServiceDep, _admin: AdminUser):
    """Create a new user — Admin only."""
    return service.create_user(payload)


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, service: UserServiceDep, current_user: CurrentUser):
    """
    Get a user by ID.
    Admins can fetch anyone.
    Regular users can only fetch their own profile.
    """
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise ForbiddenException("You can only view your own profile")
    return service.get_by_id_or_raise(user_id)


@router.patch("/{user_id}", response_model=UserRead)
def update_user(user_id: int, payload: UserUpdate, service: UserServiceDep, _admin: AdminUser):
    """Update user fields — Admin only."""
    return service.update_user(user_id, payload)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, service: UserServiceDep, _admin: AdminUser):
    """Delete a user — Admin only."""
    service.delete_user(user_id)