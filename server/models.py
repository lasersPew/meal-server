"""API Models"""

from typing import Union, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict


class UserModel(BaseModel):
    """User Model"""

    user_id: UUID = Field(default_factory=uuid4)
    username: str
    password: Optional[str] = None  # Make password optional
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_admin: bool = Field(default=False)

    # Pydantic configuration
    model_config = ConfigDict(from_attributes=True)

    def get_attribute(self, item):
        """Get attribute of the User object
        Args:
            item (str): Attribute name
        Returns:
            Union[str, None]: Attribute value or None
        """
        if not isinstance(item, str):
            raise TypeError("item must be a string")
        if not hasattr(self, item):
            raise AttributeError(f"{item} not found in User object")
        return getattr(self, item, None)

    def __str__(self):
        """String representation of the User object"""
        return f"User(username={self.username}, email={self.email}, is_admin={self.is_admin})"


class FoodQueryModel(BaseModel):
    """Food Query Model"""

    name: Optional[str]
    food_id: UUID = Field(default_factory=uuid4)
    min_calories: Optional[int]
    max_calories: Optional[int]
    min_protein: Optional[float]
    max_protein: Optional[float]
    min_carbohydrates: Optional[float]
    max_carbohydrates: Optional[float]


class UserQueryModel(BaseModel):
    """User Query Model"""

    user_id: UUID = Field(default_factory=uuid4)


class StatsDB(BaseModel):
    """Stats database model for managing statistics."""

    stats_id: UUID = Field(default_factory=uuid4)
    food_id: "FoodModel"
    date: str
    weight: float
    calories: float

    def __repr__(self):
        return f"<StatsDB(stats_id={self.stats_id}, date={self.date})>"


class FoodModel(BaseModel):
    """Food Item Model"""

    name: str
    food_id: UUID = Field(default_factory=uuid4)
    brand: Union[str, None]
    weight: Optional[float]

    # Nutritional facts
    calories: Optional[int]
    total_fat: Optional[float]
    saturated_fat: Optional[float]
    trans_fat: Optional[float]
    cholesterol: Optional[float]
    protein: Optional[float]
    dietary_fiber: Optional[float]
    total_carbohydrate: Optional[float]

    # Essential Minerals
    sodium: Optional[float]
    chloride: Optional[float]
    potassium: Optional[float]
    sugars: Optional[float]
    iron: Optional[float]
    zinc: Optional[float]
    selenium: Optional[float]
    calcium: Optional[float]
    iodine: Optional[float]
    magnesium: Optional[float]
    phosphorus: Optional[float]
    fluoride: Optional[float]

    # Essential Vitamins
    vitamin_a: Optional[float]
    vitamin_d: Optional[float]
    vitamin_e: Optional[float]
    vitamin_k: Optional[float]
    thiamin: Optional[float]
    riboflavin: Optional[float]
    niacin: Optional[float]
    vitamin_b1: Optional[float]
    vitamin_b6: Optional[float]
    vitamin_b12: Optional[float]
    folate: Optional[float]
    vitamin_c: Optional[float]

    def get_attribute(self, item):
        """Get attribute of the Food object
        Args:
            item (str): Attribute name
        Returns:
            Union[str, None]: Attribute value or None
        """
        if not isinstance(item, str):
            raise TypeError("item must be a string")
        if not hasattr(self, item):
            raise AttributeError(f"{item} not found in Food object")
        return getattr(self, item, None)

    def __str__(self):
        """String representation of the Food object"""
        return f"Food(name={self.name}, brand={self.brand}, weight={self.weight})"
