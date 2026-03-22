"""
This file's only job is to import Base and ALL your models in one place.
Alembic reads this file when generating migrations — if a model isn't
imported here, Alembic won't know it exists and won't generate its table.

Think of it as registering your DbSet<T> in EF Core's DbContext,
except here it's done through imports rather than property declarations.
"""

from app.db.session import Base
from app.models.user import User