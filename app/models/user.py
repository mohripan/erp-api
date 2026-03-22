import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base

class UserRole(str, enum.Enum):
    """
    Using str + enum means the value IS the string.
    So UserRole.ADMIN == "admin" is True.
    This plays nicely with Pydantic and JSON serialization automatically —
    no manual conversion needed.
    """
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"

class User(Base):
    """
    This is your Entity — the ORM model that maps to the 'users' table.

    We use the modern SQLAlchemy 2.0 style:
      Mapped[type] + mapped_column()

    You'll see older tutorials use Column() directly — avoid that style,
    it has no type hints and doesn't work well with modern tooling.

    .NET equivalent:  your [Table("users")] entity class in EF Core
    Java equivalent:  your @Entity @Table(name="users") class in JPA
    """
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.STAFF, nullable=False
    )
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # server_default means the DATABASE sets this value, not Python.
    # This is more reliable than setting it in application code —
    # the timestamp is always accurate regardless of app server timezone.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    
    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"