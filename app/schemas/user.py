from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator

from app.models.user import UserRole


# ---------------------------------------------------------------------------
# Pydantic schemas are your DTOs. The naming convention is:
#
#   UserCreate  → what the client sends when creating a user (request body)
#   UserUpdate  → what the client sends when updating (all fields optional)
#   UserRead    → what you send back to the client (response)
#
# IMPORTANT: These are completely separate from your SQLAlchemy model.
# The SQLAlchemy model is your DB concern.
# The Pydantic schema is your API contract concern.
#
# You never return a raw SQLAlchemy object to the client — you always
# convert it to a schema first. This way hashed_password never leaks.
#
# .NET equivalent:  your DTO / ViewModel / request model classes
# Java equivalent:  your @RequestBody / response DTO classes
# ---------------------------------------------------------------------------


class UserCreate(BaseModel):
    email: EmailStr           # Pydantic validates email format automatically
    username: str
    full_name: str
    password: str             # plain text in → hashed in the repository
    role: UserRole = UserRole.STAFF

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str) -> str:
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username must be alphanumeric (underscores and hyphens allowed)")
        return v.lower()

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserUpdate(BaseModel):
    """
    All fields are Optional — the client only sends what they want to change.
    This is for PATCH semantics (partial update), not PUT (full replace).
    """
    full_name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class UserRead(BaseModel):
    """
    This is what gets serialized and sent back to the client.
    Notice: no password field here at all — not even the hashed one.

    model_config from_attributes=True tells Pydantic it can read from
    SQLAlchemy ORM objects directly, not just plain dicts.
    In older Pydantic v1 this was called orm_mode = True.
    """
    id: int
    email: str
    username: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Auth schemas
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str