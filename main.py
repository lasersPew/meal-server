import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.openapi.utils import get_openapi
from server.database import create_db_and_tables
from alembic import command
from alembic.config import Config

# from server.routes import Food
from server.router import Food, User
from server.auth import Auth
from server.errors import NotFoundError, register_exceptions
from server.responses import APIResponse

MIGRATION_FLAG_FILE = "/tmp/migrations_applied.flag"  # Change path as needed


def run_migrations_once():
    """Run Alembic migrations only if they haven't been applied yet."""
    if not os.path.exists(MIGRATION_FLAG_FILE):
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        with open(MIGRATION_FLAG_FILE, "w") as f:
            f.write("Migrations applied")


@asynccontextmanager
async def lifespan(_: FastAPI):  # Replace 'app' with '_' to indicate it's unused
    create_db_and_tables()
    run_migrations_once()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(Food().router, prefix="/api", tags=["Food"])
app.include_router(User().router, prefix="/api", tags=["User"])
app.include_router(Auth().router, prefix="/api", tags=["Auth"])
register_exceptions(app)

security_scheme = {
    "type": "http",
    "scheme": "bearer",
    "bearerFormat": "JWT",
}


# Add the security scheme to the OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Plan-a-meal",
        version="1.0.0",
        description="""
Plan-a-meal is a meal planning application that allows users to create, manage, and share meal plans. The application provides a user-friendly interface for selecting recipes, generating shopping lists, and tracking nutritional information. Users can also customize their meal plans based on dietary preferences and restrictions.

This document describes API as it is right now, but it is not final. The API is still under development and may change in the future. 

Please refer to the documentation for the latest updates.

The API is designed to be RESTful and follows standard conventions for HTTP methods and status codes. Each endpoint is documented with its purpose, request parameters, and response formats.

The API supports authentication and authorization mechanisms to ensure secure access to user data.
                """,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {"BearerAuth": security_scheme}
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]  # Apply BearerAuth globally
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.api_route(
    "/api/ping", methods=["GET", "POST"], tags=["Status"], operation_id="ping_status"
)
def ping():
    return "pong"


@app.post("/api/migrate", tags=["Admin"], response_model=APIResponse)
async def run_migrations():
    """Run Alembic migrations."""
    try:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        return APIResponse(result="ok", message="Migrations applied successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    operation_id="catch_all_handler",
)
async def catch_all(request: Request):
    request_url = str(request.base_url).strip("/") + "/docs"
    raise NotFoundError(
        detail=f"Nope, this isn't the API you're looking for, maybe try checking the docs? at {request_url}",
    )


if __name__ == "__main__":
    create_db_and_tables()
    run_migrations_once()
