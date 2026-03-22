from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.core.exceptions import NotFoundException, ConflictException

class UserService:
    """
    The service layer contains your business logic.
    It orchestrates repositories but doesn't touch HTTP or SQL directly.

    Rules:
      - Services know about repositories, not the other way around.
      - Services raise domain exceptions (NotFoundException, ConflictException).
      - Services do NOT know about HTTP request/response objects.
        This keeps the layer testable without spinning up a web server.

    .NET equivalent:  your Service / ApplicationService layer
    Java equivalent:  your @Service classes in Spring
    """
    
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        
    def get_by_id_or_raise(self, user_id: int) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(f"User with id {user_id} not found")
        return user
    
    def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        return self.user_repo.get_all(skip=skip, limit=limit)
    
    def create_user(self, data: UserCreate) -> User:
        # Business rules: email and username must be unique.
        # The repository doesn't enforce this — that's the service's job.
        if self.user_repo.get_by_email(data.email):
            raise ConflictException(f"Email '{data.email}' is already registered")
        if self.user_repo.get_by_username(data.username):
            raise ConflictException(f"Username '{data.username}' is already taken")
        return self.user_repo.create(data)
    
    def update_user(self, user_id: int, data: UserUpdate) -> User:
        user = self.get_by_id_or_raise(user_id)
        return self.user_repo.update(user, data)
    
    def delete_user(self, user_id: int) -> None:
        user = self.get_by_id_or_raise(user_id)
        self.user_repo.delete(user)