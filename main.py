"Main runner file"

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from server.database import create_db_and_tables

# from server.routes import Food
from server.router import Food, User
from server.auth import Auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(Food().router, prefix="/api", tags=["Food"])
app.include_router(User().router, prefix="/api", tags=["User"])
app.include_router(Auth().router, prefix="/api", tags=["Auth"])

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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    # Custom error response for validation errors
    return JSONResponse(
        status_code=400,
        content={"message": f"Custom validation error: {exc}"},
    )


@app.get("/api/ping", tags=["Status"])
@app.post("/api/ping", tags=["Status"])
def ping():
    return "pong"


if __name__ == "__main__":
    create_db_and_tables()
