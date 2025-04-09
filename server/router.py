from fastapi import APIRouter, Depends
from uuid import UUID
from typing import Optional, Annotated
from sqlmodel import Session, select

from .database import UserDB, get_session, FoodDB  # SQLModel
from .responses import (
    BaseResponse,
    FoodResponse,
    FoodResponses,
    ErrorResponse,
    UserResponse,
    UserResponses,
)
from .errors import (
    NotFoundError,
    ValidationError,
    ForbiddenError,
)
from .auth import Auth  # Import Auth class

auth = Auth()  # Initialize Auth without session for dependency injection
get_current_user = auth.get_current_user  # Use the method as a dependency

SessionDep = Annotated[Session, Depends(get_session)]
CurrentUserDep = Annotated[UserDB, Depends(get_current_user)]


class Food:
    """Class for Food Routes"""

    def __init__(self):
        self.router = APIRouter(prefix="/food")
        self._add_routes()

    def _add_routes(self):
        self.router.get(
            "/get",
            response_model=FoodResponses,
            responses={
                200: {"model": FoodResponses},
                **{key: {"model": ErrorResponse} for key in [404, 422]},
            },
        )(self.get_food_data)

        self.router.post(
            "/add",
            response_model=FoodResponse,
            responses={
                200: {"model": FoodResponse},
                422: {"model": ErrorResponse},
            },
        )(self.create_food)

        self.router.delete(
            "/delete",
            response_model=BaseResponse,
            responses={
                200: {"model": FoodResponse},
                **{key: {"model": ErrorResponse} for key in [403, 404, 422]},
            },
        )(self.delete_food)

    async def get_food_data(
        self,
        session: SessionDep,
        name: Optional[str] = None,
        uuid: Optional[UUID] = None,
        min_calories: Optional[int] = None,
        max_calories: Optional[int] = None,
        min_protein: Optional[float] = None,
        max_protein: Optional[float] = None,
        min_carbohydrates: Optional[float] = None,
        max_carbohydrates: Optional[float] = None,
        limit: Optional[int] = 5,
        offset: Optional[int] = 0,
    ) -> FoodResponses:
        query = select(FoodDB)

        filters = [
            (FoodDB.uuid == uuid) if uuid else None,
            (FoodDB.name.ilike(f"%{name}%")) if name else None,
            (FoodDB.calories >= min_calories) if min_calories else None,
            (FoodDB.calories <= max_calories) if max_calories else None,
            (FoodDB.protein >= min_protein) if min_protein else None,
            (FoodDB.protein <= max_protein) if max_protein else None,
            (FoodDB.total_carbohydrate >= min_carbohydrates)
            if min_carbohydrates
            else None,
            (FoodDB.total_carbohydrate <= max_carbohydrates)
            if max_carbohydrates
            else None,
        ]
        filters = [filter for filter in filters if filter is not None]
        query = query.where(*filters)
        query = query.offset(offset).limit(limit)
        results = session.exec(query).all()

        if not results:
            raise NotFoundError(
                detail="No food items match the criteria",
                context={
                    key: value
                    for key, value in {
                        "name": name,
                        "uuid": uuid,
                        "min_calories": min_calories,
                        "max_calories": max_calories,
                        "min_protein": min_protein,
                        "max_protein": max_protein,
                        "min_carbohydrates": min_carbohydrates,
                        "max_carbohydrates": max_carbohydrates,
                    }.items()
                    if value is not None
                },
            )
        return FoodResponses(result="ok", response="entity", data=results)

    async def create_food(
        self,
        food: FoodDB,
        session: SessionDep,
    ) -> FoodResponse:
        if isinstance(food.uuid, str) and food.uuid:
            food.uuid = UUID(food.uuid)
        if food.uuid and not isinstance(food.uuid, UUID):
            raise ValidationError(detail="Invalid UUID format", context=None)
        db_food = FoodDB(**food.model_dump(exclude_unset=True))
        session.add(db_food)
        session.commit()
        session.refresh(db_food)
        return FoodResponse(result="ok", response="entity", data=db_food)

    async def delete_food(
        self,
        session: SessionDep,
        uuid: Optional[UUID],
        current_user: CurrentUserDep,  # Require authentication
    ) -> BaseResponse:
        if not current_user.is_admin:
            raise ForbiddenError(
                detail="Admin privileges needed to delete food.", context=None
            )
        if isinstance(uuid, str) and uuid:
            uuid = UUID(uuid)
        if uuid and not isinstance(uuid, UUID):
            raise ValidationError(detail="Invalid UUID format", context=None)
        db_food = session.get(FoodDB, uuid)
        if not db_food:
            raise NotFoundError(detail=f"Food with id {uuid} not found", context=None)
        session.delete(db_food)
        session.commit()
        return BaseResponse(result="ok")


class User:
    """Class for User Routes"""

    def __init__(self):
        self.router = APIRouter(prefix="/user")
        self._add_routes()

    def _add_routes(self):
        self.router.get(
            "/get/all",
            response_model=UserResponse,
            responses={
                200: {"model": UserResponse},
                **{key: {"model": ErrorResponse} for key in [403, 404, 422]},
            },
        )(self.get_all_users)

        self.router.get(
            "/get",
            response_model=UserResponse,
            responses={
                200: {"model": UserResponse},
                **{key: {"model": ErrorResponse} for key in [404, 422]},
            },
        )(self.get_user_data)

        self.router.post(
            "/add",
            response_model=UserResponse,
            responses={
                200: {"model": UserResponse},
                422: {"model": ErrorResponse},
            },
        )(self.create_user)

        self.router.delete(
            "/delete",
            response_model=UserResponse,
            responses={
                200: {"model": UserResponse},
                **{key: {"model": ErrorResponse} for key in [403, 404, 422]},
            },
        )(self.delete_user)

    async def get_all_users(
        self,
        session: SessionDep,
    ) -> UserResponses:
        query = session.exec(select(UserDB))
        results = query.all()

        if not results:
            raise NotFoundError(detail="No users found", context=None)
        # Explicitly serialize the UserDB objects into dictionaries
        return UserResponses(
            result="ok",
            response="list",
            data={"users": [user.model_dump() for user in results]},
        )

    async def get_user_data(
        self,
        session: SessionDep,
        uuid: UUID,
    ) -> UserResponse:
        if isinstance(uuid, str) and uuid:
            uuid = UUID(uuid)
        if uuid and not isinstance(uuid, UUID):
            raise ValidationError(detail="Invalid UUID format", context=None)
        user = session.get(UserDB, uuid)

        if not user:
            raise NotFoundError(detail=f"User with id {uuid} not found", context=None)
        # Serialize the UserDB object
        serialized_user = user.model_dump()
        return UserResponse(result="ok", response="entity", data=serialized_user)

    async def create_user(
        self,
        user: UserDB,
        session: SessionDep,
    ) -> UserResponse:
        if isinstance(user.uuid, str) and user.uuid:
            user.uuid = UUID(user.uuid)
        if user.uuid and not isinstance(user.uuid, UUID):
            raise ValidationError(detail="Invalid UUID format", context=None)
        user.password = UserDB.hash_password(user.password)
        db_user = UserDB(**user.model_dump(exclude_unset=True))
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return UserResponse(result="ok", response="entity", data=db_user)

    async def delete_user(
        self,
        session: SessionDep,
        uuid: UUID,
        current_user: CurrentUserDep,  # Require authentication
    ) -> BaseResponse:
        if isinstance(uuid, str) and uuid:
            uuid = UUID(uuid)
        if uuid and not isinstance(uuid, UUID):
            raise ValidationError(detail="Invalid UUID format", context=None)
        if current_user.uuid != uuid and not current_user.is_admin:
            raise ForbiddenError(
                detail="Admin privileges needed to delete another user.",
                context=None,
            )
        db_user = session.get(UserDB, uuid)
        if not db_user:
            raise NotFoundError(detail=f"User with id {uuid} not found", context=None)
        session.delete(db_user)
        session.commit()
        return BaseResponse(result="ok")
