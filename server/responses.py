from .database import FoodDB, StatsDB, UserDB
from pydantic import BaseModel
from typing import List, Optional, Dict


# return {"result": "ok", "response": "entity", "data": db_food}
class BaseResponse(BaseModel):
    result: str


class AuthResponse(BaseResponse):
    result: str = "ok"
    access_token: str
    token_type: str = "bearer"


class ErrorResponse(BaseResponse):
    result: str = "error"
    error: dict = {
        "status": int,
        "title": str,
        "detail": str,
        "context": Optional[str],
    }


class UserResponse(BaseResponse):
    result: str = "ok"
    response: str = "entity"
    data: UserDB

    def to_dict(self):
        return {
            "result": self.result,
            "response": self.response,
            "data": self.data.model_dump(),
        }

    def to_json(self):
        return self.to_dict()


class FoodResponses(BaseResponse):
    response: str = "list"
    data: List[FoodDB]

    def to_dict(self):
        return {
            "result": self.result,
            "response": self.response,
            "data": [food.model_dump() for food in self.data],
        }

    def to_json(self):
        return self.to_dict()


class FoodResponse(BaseResponse):
    response: str = "entity"
    data: FoodDB

    def to_dict(self):
        return {
            "result": self.result,
            "response": self.response,
            "data": self.data.model_dump(),
        }

    def to_json(self):
        return self.to_dict()


class UserResponses(BaseResponse):
    response: str = "list"
    data: Dict[str, List]  # Expect a list of serialized dictionaries

    def to_dict(self):
        return {
            "result": self.result,
            "response": self.response,
            "data": self.data,
        }

    def to_json(self):
        return self.to_dict()


class StatsResponse(BaseResponse):
    response: str = "entity"
    data: StatsDB

    def to_dict(self):
        return {
            "result": self.result,
            "response": self.response,
            "data": self.data.model_dump(),
        }

    def to_json(self):
        return self.to_dict()
