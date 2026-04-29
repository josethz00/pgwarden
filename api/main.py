import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext

from app.auth.router import router as auth_router
from app.schemas.router import router as schema_router
from app.databases.router import router as database_router
from app.servers.router import router as server_router
from app.databases.sessions.router import router as sessions_router
from app.databases.locks.router import router as locks_router
from app.databases.configs.router import router as db_config_router
from app.servers.config.router import router as srv_config_router
from app.servers.metrics.router import router as srv_metrics_router
from app.schemas.exceptions import BaseAppException
from database.connection import DatabaseConnection
from database.models.base import User
from database.operations.base.user import UserRepository


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@asynccontextmanager
async def lifespan(app: FastAPI):

    if os.getenv("IS_TESTING") == "1":
        yield
        return

    email = os.getenv("PGWARDEN_EMAIL")
    password = os.getenv("PGWARDEN_PASSWORD")
    hashed_password = pwd_context.hash(password)

    try:
        async with DatabaseConnection() as conn:
            user_repo = UserRepository(conn)
            existing_user = await user_repo.find_by_email(email)
            if not existing_user:
                admin_user = User(
                    email=email,
                    password=hashed_password,
                    name="Admin",
                    is_admin=True,
                )
                await user_repo.insert(admin_user)
                print(f"Admin user {email} created successfully.")
    except Exception as e:
        print(f"Failed to initialize admin user: {e}")
        
    yield

tags_metadata = [
    {
        "name": "auth",
        "description": "Authentication and authorization endpoints. Handles login and JWT token refresh.",
    },
    {
        "name": "servers",
        "description": "Manage registered PostgreSQL servers. Connection credentials are encrypted and stored securely.",
    },
    {
        "name": "databases",
        "description": "Manage monitored databases linked to the registered servers.",
    },
    {
        "name": "schemas",
        "description": "Expose the currently collected schema metadata (tables, columns, indexes).",
    },
    {
        "name": "sessions",
        "description": "Real-time session monitoring via Server-Sent Events.",
    },
    {
        "name": "locks",
        "description": "Real-time lock monitoring via Server-Sent Events.",
    },
]

app = FastAPI(
    title="PGWarden API",
    description="""
    PGWarden API provides endpoints for managing monitored PostgreSQL servers and databases. 
    """,
    version="0.1.0",
    openapi_tags=tags_metadata,
    swagger_ui_parameters={
        "displayRequestDuration": True,
        "defaultModelsExpandDepth": -1,
    },
    lifespan=lifespan
)

@app.exception_handler(BaseAppException)
async def app_exception_handler(request: Request, exc: BaseAppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status_code": exc.status_code,
            "message": exc.message,
            "details": exc.details
        }
    )

app.include_router(auth_router, prefix="/v1")
app.include_router(schema_router, prefix="/v1")
app.include_router(database_router, prefix="/v1")
app.include_router(server_router, prefix="/v1")
app.include_router(sessions_router, prefix="/v1")
app.include_router(locks_router, prefix="/v1")
app.include_router(db_config_router, prefix="/v1")
app.include_router(srv_config_router, prefix="/v1")
app.include_router(srv_metrics_router, prefix="/v1")


# serve the SPA from the same origin as the api. /v1/* and /docs are
# already registered above and starlette matches in registration order, so
# the catch-all below only fires for paths that didn't match an api route.
# the directory is populated at image build time by the frontend-build stage
# in api/Dockerfile; if it's missing (e.g. running tests locally without a
# build) we just skip mounting and the api still works on its own.
_static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(_static_dir):
    _assets_dir = os.path.join(_static_dir, "assets")
    if os.path.isdir(_assets_dir):
        # vite emits hashed filenames into /assets/* so they can be cached
        # forever; we let starlette stream them directly.
        app.mount("/assets", StaticFiles(directory=_assets_dir), name="assets")

    _index_html = os.path.join(_static_dir, "index.html")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa(full_path: str):
        # serve a literal file under static/ if it exists (vite.svg, robots.txt,
        # favicon.ico, etc.) -- otherwise fall back to index.html so client-side
        # routes (tanstack-router) survive a hard refresh.
        if full_path:
            candidate = os.path.normpath(os.path.join(_static_dir, full_path))
            if candidate.startswith(_static_dir) and os.path.isfile(candidate):
                return FileResponse(candidate)
        return FileResponse(_index_html)

