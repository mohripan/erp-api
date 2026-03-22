from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings

# ---------------------------------------------------------------------------
# Engine — your connection pool.
# Equivalent to DbContext configuration in EF Core or DataSource in Spring.
#
# pool_pre_ping=True checks the connection is alive before using it.
# Important for long-running apps where DB connections can go stale.
#
# echo=True logs every SQL statement to the console — very useful while
# learning, you can see exactly what SQLAlchemy generates.
# ---------------------------------------------------------------------------
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG,
    )

# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------
# SessionLocal() creates a new DB session.
# Think of it like opening a DbContext in EF Core or an EntityManager in JPA.
# You open one per request, use it, then close it.
#
# autocommit=False → you control when to commit (explicit is better)
# autoflush=False  → SQLAlchemy won't auto-sync state to DB mid-session
# ---------------------------------------------------------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ---------------------------------------------------------------------------
# Base class for all ORM models
# ---------------------------------------------------------------------------
# Every model class you create will inherit from this Base.
# SQLAlchemy uses it to discover your table mappings.
# ---------------------------------------------------------------------------
class Base(DeclarativeBase):
    pass