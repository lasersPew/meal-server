"""Does things on database"""

import os
from passlib.context import CryptContext
from uuid import uuid4
from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine
from dotenv import load_dotenv

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
# Password hashing context (argon2id by default)
load_dotenv()
# load environment variables from .env file

# create SQLAlchemy compatible engine
engine = create_engine(
    os.environ.get("DATABASE_URL", "sqlite:///database.db"),
    connect_args={"check_same_thread": False},
)


def create_db_and_tables():
    """Create Database Tables(done when starting the app.)"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get a session for the database"""
    with Session(engine) as session:
        yield session


class UserDB(SQLModel, table=True):
    """User database model for managing user data."""

    __tablename__: str = os.environ.get("USER_TABLE_NAME", "testuser")  # type: ignore

    user_id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    username: str = Field(nullable=False, unique=True)
    password: str = Field(nullable=False)
    email: str = Field(nullable=False, unique=True)
    first_name: Optional[str] = Field(nullable=True)
    last_name: Optional[str] = Field(nullable=True)
    is_admin: bool = Field(default=False, nullable=False)

    def __repr__(self) -> str:
        return f"UserDB(uuid={self.user_id}, username={self.username}, email={self.email}, is_admin={self.is_admin})"

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash the password using Argon2id"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(stored_password: str, password: str) -> bool:
        """Verify the provided password against the stored hashed password"""
        return pwd_context.verify(password, stored_password)

    def set_password(self, password: str):
        """Hash and set the user's password"""
        self.password = self.hash_password(password)

    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash"""
        return self.verify_password(self.password, password)


# class StatsDB(SQLModel, table=True):
#     """Stats database model for managing statistics."""

#     __tablename__: str = os.environ.get("STATS_TABLE_NAME", "teststats")  # type: ignore

#     stats_id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
#     food_id: str = Field(foreign_key="testfood.food_id", unique=True)
#     food: "FoodDB" = Relationship("FoodModel", backref="stats", foreign_keys=[food_id])

#     hits: int = Field(default=0)

#     def __repr__(self):
#         return f"<StatsDB(stats_id={self.stats_id}, hits={self.hits})>"


class FoodDB(SQLModel, table=True):
    """Food database model for managing food data."""

    __tablename__: str = os.environ.get("FOOD_TABLE_NAME", "testfood")  # type: ignore

    food_id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    # stats_id: Optional[str] = Field(unique=True, foreign_key="teststats.stats_id")
    # stats: Optional[StatsDB] = Relationship(back_populates="food")

    name: str = Field(nullable=False)
    brand: str = Field(nullable=True)
    weight: float = Field(nullable=True)

    calories: float = Field(nullable=True)
    total_fat: float = Field(nullable=True)
    saturated_fat: float = Field(nullable=True)
    trans_fat: float = Field(nullable=True)
    cholesterol: float = Field(nullable=True)
    protein: float = Field(nullable=True)
    dietary_fiber: float = Field(nullable=True)
    total_carbohydrate: float = Field(nullable=True)

    sodium: float = Field(nullable=True)
    chloride: float = Field(nullable=True)
    potassium: float = Field(nullable=True)
    sugars: float = Field(nullable=True)
    iron: float = Field(nullable=True)
    zinc: float = Field(nullable=True)
    selenium: float = Field(nullable=True)
    calcium: float = Field(nullable=True)
    iodine: float = Field(nullable=True)
    magnesium: float = Field(nullable=True)
    phosphorus: float = Field(nullable=True)
    fluoride: float = Field(nullable=True)

    vitamin_a: float = Field(nullable=True)
    vitamin_d: float = Field(nullable=True)
    vitamin_e: float = Field(nullable=True)
    vitamin_k: float = Field(nullable=True)
    thiamin: float = Field(nullable=True)
    riboflavin: float = Field(nullable=True)
    niacin: float = Field(nullable=True)
    vitamin_b1: float = Field(nullable=True)
    vitamin_b6: float = Field(nullable=True)
    vitamin_b12: float = Field(nullable=True)
    folate: float = Field(nullable=True)
    vitamin_c: float = Field(nullable=True)

    def __repr__(self):
        return f"<FoodDB(name={self.name}, uuid={self.food_id})>"

    # def increment_hits(self):
    #     if self.stats:
    #         self.stats.hits += 1
