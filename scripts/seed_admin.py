"""
Creates the first admin user so you can log in and test the API.
Run with:  python -m scripts.seed_admin
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.models.user import UserRole


def seed():
    db = SessionLocal()
    try:
        repo = UserRepository(db)

        if repo.get_by_email("admin@erp-system.com"):
            print("⚠️  Admin user already exists, skipping.")
            return

        admin = repo.create(
            UserCreate(
                email="admin@erp-system.com",
                username="admin",
                full_name="System Administrator",
                password="Admin1234!",
                role=UserRole.ADMIN,
            )
        )
        print(f"✅ Admin created — email: {admin.email} | id: {admin.id}")
        print("   Password: Admin1234!")
    finally:
        db.close()


if __name__ == "__main__":
    seed()