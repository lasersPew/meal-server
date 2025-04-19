from .models import UserModel, FoodModel
from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class MainResponse(BaseModel):
    result: str = "ok"
    data: Optional[dict]


class AuthResponse(BaseModel):
    result: str = "ok"
    data: Optional[str]


class ErrorResponse(BaseModel):
    result: str = "error"
    error: dict = {
        "status": int,
        "title": str,
        "detail": str,
        "context": Optional[str],
    }


class UserResponse(BaseModel):
    result: str = "ok"
    response: str = "entity"
    data: UserModel


class APIResponse(BaseModel):
    result: str = "ok"
    message: str


class FoodResponses(BaseModel):
    result: str = "ok"
    response: str = "list"
    data: List[FoodModel]


class FoodResponse(BaseModel):
    result: str = "ok"
    response: str = "entity"
    data: FoodModel


class UserResponses(BaseModel):
    result: str = "ok"
    response: str = "list"
    data: List[UserModel]

    model_config = ConfigDict(from_attributes=True)
