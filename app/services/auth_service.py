from jose import JWTError

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.exceptions import UnauthorizedException
from app.schemas.user import TokenResponse


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def login(self, email: str, password: str) -> TokenResponse:
        user = self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")
        if not user.is_active:
            raise UnauthorizedException("Account is disabled")
        return TokenResponse(
            access_token=create_access_token(subject=user.id),
            refresh_token=create_refresh_token(subject=user.id),
        )

    def refresh(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise UnauthorizedException("Invalid token type")
            user_id: int = int(payload["sub"])
        except (JWTError, KeyError, ValueError):
            raise UnauthorizedException("Invalid or expired refresh token")
        user = self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")
        return TokenResponse(
            access_token=create_access_token(subject=user.id),
            refresh_token=create_refresh_token(subject=user.id),
        )

    def get_current_user_from_token(self, token: str) -> User:
        try:
            payload = decode_token(token)
            if payload.get("type") != "access":
                raise UnauthorizedException("Invalid token type")
            user_id: int = int(payload["sub"])
        except (JWTError, KeyError, ValueError):
            raise UnauthorizedException()
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UnauthorizedException("User not found")
        if not user.is_active:
            raise UnauthorizedException("Account is disabled")
        return user