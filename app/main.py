from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import router as v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Code before yield runs at STARTUP.
    Code after yield runs at SHUTDOWN.

    .NET equivalent:  IHostedService or WebApplication.Lifetime events
    Java equivalent:  @PostConstruct / ApplicationListener<ContextRefreshedEvent>
    """
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} starting up...")
    yield
    print("👋 Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    # Swagger UI only available in debug mode
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
# All routes are now under /api/v1/...
# e.g. /api/v1/auth/login, /api/v1/users/
app.include_router(v1_router, prefix="/api")


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}