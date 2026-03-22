from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password

class UserRepository:
    """
    The repository's only job is to talk to the database.
    No business logic here — that belongs in the service layer.
    No HTTP concerns here either — that belongs in the route layer.

    This class only knows about:
      - The DB session
      - The User model
      - Basic CRUD operations

    .NET equivalent:  IUserRepository / UserRepository pattern
    Java equivalent:  Custom JpaRepository implementation
    """
    def __init__(self, db: Session):
        self.db = db
        
    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)
    
    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self.db.scalars(stmt).first()
    
    def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return self.db.scalars(stmt).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        stmt = select(User).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())
    
    def create(self, data: UserCreate) -> User:
        user = User(
            email=data.email,
            username=data.username,
            full_name=data.full_name,
            hashed_password=hash_password(data.password),
            role=data.role
        )
        self.db.add(user)
        self.db.commit()
        
        # refresh() reloads the object from the DB so we get the
        # server-generated fields: id, created_at, updated_at.
        # Without this, those fields would still be None in memory.
        self.db.refresh(user)
        return user
    
    def update(self, user: User, data: UserUpdate) -> User:
        # model_dump(exclude_unset=True) only returns fields the client
        # actually sent. This is what makes PATCH work correctly —
        # fields the client didn't mention are left untouched.
        #
        # Without exclude_unset=True, a PATCH with just {"full_name": "Bob"}
        # would also set role=None and is_active=None. Not what you want.
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()