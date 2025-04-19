from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError
from typing import Optional, Annotated
from sqlmodel import Session, select

from .auth import Auth
from .models import FoodModel, UserModel
from .database import UserDB, get_session, FoodDB
from .responses import (
    MainResponse,
    FoodResponse,
    FoodResponses,
    UserResponse,
    UserResponses,
)
from .errors import (
    AlreadyExistsError,
    NotFoundError,
    ForbiddenError,
)

auth = Auth()
get_current_user = auth.get_current_user

SessionDep = Annotated[Session, Depends(get_session)]
CurrentUserDep = Annotated[UserDB, Depends(get_current_user)]


class Food:
    def __init__(self):
        self.router = APIRouter(prefix="/food")
        self._add_routes()

    def _add_routes(self):
        self.router.get("/get", response_model=FoodResponses)(self.get_foodlist)
        self.router.get("/get/{food_id}", response_model=FoodResponse)(self.get_food)
        self.router.post("/add", response_model=FoodResponse)(self.create_food)
        self.router.put("/update/{food_id}", response_model=FoodResponse)(
            self.update_food
        )
        self.router.delete("/delete/{food_id}", response_model=MainResponse)(
            self.delete_food
        )

    @staticmethod
    async def get_food(session: SessionDep, food_id: str) -> FoodResponse:
        food = session.get(FoodDB, food_id)
        if not food:
            raise NotFoundError(detail=f"No food item with {food_id} found")
        result = FoodModel.model_validate(
            food.dict()
        )  # Convert FoodDB instance to a dictionary
        return FoodResponse(result="ok", response="entity", data=result)

    @staticmethod
    async def get_foodlist(
        session: SessionDep,
        name: Optional[str] = None,
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
            FoodDB.name.ilike(f"%{name}%") if name else None,  # type: ignore
            FoodDB.calories >= min_calories if min_calories else None,
            FoodDB.calories <= max_calories if max_calories else None,
            FoodDB.protein >= min_protein if min_protein else None,
            FoodDB.protein <= max_protein if max_protein else None,
            FoodDB.total_carbohydrate >= min_carbohydrates
            if min_carbohydrates
            else None,
            FoodDB.total_carbohydrate <= max_carbohydrates
            if max_carbohydrates
            else None,
        ]
        query = query.where(*[f for f in filters if f]).offset(offset).limit(limit)
        results = session.exec(query).all()

        if not results:
            raise NotFoundError(detail="No food items match the criteria")
        data = [FoodModel.model_validate(f.dict()) for f in results]
        return FoodResponses(result="ok", response="list", data=data)

    @staticmethod
    async def create_food(food: FoodDB, session: SessionDep) -> FoodResponse:
        db_food = FoodDB(**food.model_dump(exclude_unset=True))
        if food.food_id:  # Use the provided UUID if it exists
            db_food.food_id = food.food_id
        try:
            session.add(db_food)
            session.commit()
            session.refresh(db_food)
        except IntegrityError:
            raise AlreadyExistsError(
                detail=f"Food with id {db_food.food_id} already exists"
            )
        return FoodResponse(
            result="ok",
            response="entity",
            data=FoodModel.model_validate(db_food.dict()),
        )

    @staticmethod
    async def update_food(
        food_id: str, food: FoodDB, session: SessionDep
    ) -> FoodResponse:
        existing = session.get(FoodDB, food_id)
        if not existing:
            raise NotFoundError(detail=f"Food with id {food_id} not found")
        for k, v in food.model_dump(exclude_unset=True).items():
            setattr(existing, k, v)
        session.commit()
        session.refresh(existing)
        return FoodResponse(
            result="ok",
            response="entity",
            data=FoodModel.model_validate(existing.dict()),  # Convert to dictionary
        )

    @staticmethod
    async def delete_food(
        food_id: str, session: SessionDep, current_user: CurrentUserDep
    ) -> MainResponse:
        if not current_user.is_admin:
            raise ForbiddenError(detail="Admin privileges needed to delete food.")
        db_food = session.get(FoodDB, food_id)
        if not db_food:
            raise NotFoundError(detail=f"Food with id {food_id} not found")
        session.delete(db_food)
        session.commit()
        return MainResponse(result="ok", data={"food_id": food_id})


class User:
    def __init__(self):
        self.router = APIRouter(prefix="/user")
        self._add_routes()

    def _add_routes(self):
        self.router.get("/get", response_model=UserResponses)(self.get_userlist)
        self.router.get("/get/{user_id}", response_model=UserResponse)(self.get_user)
        self.router.post("/add", response_model=UserResponse)(self.create_user)
        self.router.put("/update/{user_id}", response_model=UserResponse)(
            self.update_user
        )
        self.router.delete("/delete/{user_id}", response_model=MainResponse)(
            self.delete_user
        )

    @staticmethod
    async def get_user(session: SessionDep, user_id: str) -> UserResponse:
        user = session.get(UserDB, user_id)
        if not user:
            raise NotFoundError(detail="No users found")
        data = UserModel.model_validate(user).model_dump(
            exclude={"password", "is_admin"}
        )
        return UserResponse(result="ok", response="entity", data=data)

    @staticmethod
    async def get_userlist(
        session: SessionDep, limit: int = 5, offset: int = 0
    ) -> UserResponses:
        query = select(UserDB).offset(offset).limit(limit)
        results = session.exec(query).all()
        if not results:
            raise NotFoundError(detail="No users found")
        data = [
            UserModel.model_validate(u).model_dump(exclude={"password", "is_admin"})
            for u in results
        ]
        return UserResponses(result="ok", response="list", data=data)

    @staticmethod
    async def create_user(user: UserDB, session: SessionDep) -> UserResponse:
        user.password = UserDB.hash_password(user.password)
        db_user = UserDB(**user.model_dump(exclude_unset=True))
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return UserResponse(
            result="ok", response="entity", data=UserModel.model_validate(db_user)
        )

    @staticmethod
    async def update_user(
        user_id: str, user: UserDB, session: SessionDep
    ) -> UserResponse:
        db_user = session.get(UserDB, user_id)
        if not db_user:
            raise NotFoundError(detail=f"User with id {user_id} not found")
        if user.password:
            user.password = UserDB.hash_password(user.password)
        for k, v in user.model_dump(exclude_unset=True).items():
            setattr(db_user, k, v)
        session.commit()
        session.refresh(db_user)
        return UserResponse(
            result="ok", response="entity", data=UserModel.model_validate(db_user)
        )

    @staticmethod
    async def delete_user(
        user_id: str, session: SessionDep, current_user: CurrentUserDep
    ) -> MainResponse:
        if current_user.user_id != user_id and not current_user.is_admin:
            raise ForbiddenError(
                detail="Admin privileges needed to delete another user."
            )
        db_user = session.get(UserDB, user_id)
        if not db_user:
            raise NotFoundError(detail=f"User with id {user_id} not found")
        session.delete(db_user)
        session.commit()
        return MainResponse(result="ok", data={"user_id": user_id})
