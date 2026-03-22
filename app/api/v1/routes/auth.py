from fastapi import APIRouter

from app.core.dependencies import AuthServiceDep, CurrentUser
from app.schemas.user import LoginRequest, TokenResponse, RefreshRequest, UserRead

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, auth_service: AuthServiceDep):
    return auth_service.login(email=payload.email, password=payload.password)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, auth_service: AuthServiceDep):
    return auth_service.refresh(payload.refresh_token)


@router.get("/me", response_model=UserRead)
def get_me(current_user: CurrentUser):
    """
    Returns the profile of the currently authenticated user.
    CurrentUser is our type alias — FastAPI resolves the entire
    DI chain automatically and injects the User entity here.
    """
    return current_user