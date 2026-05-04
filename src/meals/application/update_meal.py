from dataclasses import dataclass, replace
from decimal import Decimal
from src.meals.domain.entity import MealEntity
from src.meals.domain.errors import MealNotFoundError
from src.meals.domain.ports import IMealRepository


@dataclass
class UpdateMealInput:
    meal_id: str
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None
    category: str | None = None
    available: bool | None = None


class UpdateMeal:
    def __init__(self, meal_repository: IMealRepository) -> None:
        self._meal_repository = meal_repository

    async def execute(self, input: UpdateMealInput) -> MealEntity:
        meal = await self._meal_repository.find_by_id(input.meal_id)
        if meal is None:
            raise MealNotFoundError(input.meal_id)

        updates = {}
        if input.name is not None:
            updates["name"] = input.name.strip()
        if input.description is not None:
            updates["description"] = input.description
        if input.price is not None:
            updates["price"] = input.price
        if input.category is not None:
            updates["category"] = input.category.strip()
        if input.available is not None:
            updates["available"] = input.available

        if updates:
            meal = replace(meal, **updates)

        return await self._meal_repository.update(meal)
