from contextlib import asynccontextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app import models  # noqa: F401
from app.core.config import settings
from app.db import SessionLocal
from app.routers import admin, auth, catalog, recipes, uploads, user
from app.seed import seed_defaults


settings.upload_path.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(_: FastAPI):
    backend_path = Path(__file__).resolve().parents[1]
    migration_config = Config(str(backend_path / "alembic.ini"))
    # Alembic resolves relative script_location values from the current
    # working directory. The API can be started from the repository root,
    # so make both the migration directory and app import path explicit.
    migration_config.set_main_option("script_location", str(backend_path / "migrations"))
    migration_config.set_main_option("prepend_sys_path", str(backend_path))
    migration_config.set_main_option("sqlalchemy.url", settings.database_url.replace("%", "%%"))
    command.upgrade(migration_config, "head")
    with SessionLocal() as db:
        seed_defaults(db)
    yield


app = FastAPI(
    title="Cooking Assistant API",
    version="0.1.0",
    description="家用做饭助手 API",
    lifespan=lifespan,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    session_cookie="cooking_session",
    same_site=settings.session_same_site,
    https_only=settings.session_https_only,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=settings.upload_path), name="uploads")

app.include_router(auth.router)
app.include_router(recipes.router)
app.include_router(admin.router)
app.include_router(uploads.router)
app.include_router(catalog.router)
app.include_router(user.router)


@app.get("/api/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Return a lightweight service health status."""

    return {"status": "ok", "service": "cooking-api"}


@app.get("/api", tags=["system"])
def api_info() -> dict[str, str]:
    return {
        "name": "Cooking Assistant API",
        "version": "0.1.0",
        "docs": "/docs",
    }
