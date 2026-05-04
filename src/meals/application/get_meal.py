from dataclasses import dataclass
from src.meals.domain.entity import MealEntity
from src.meals.domain.errors import MealNotFoundError
from src.meals.domain.ports import IMealRepository


@dataclass
class GetMealInput:
    meal_id: str


class GetMeal:
    def __init__(self, meal_repository: IMealRepository) -> None:
        self._meal_repository = meal_repository

    async def execute(self, input: GetMealInput) -> MealEntity:
        meal = await self._meal_repository.find_by_id(input.meal_id)
        if meal is None:
            raise MealNotFoundError(input.meal_id)
        return meal
