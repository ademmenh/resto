from dataclasses import dataclass
from src.meals.domain.errors import MealNotFoundError
from src.meals.domain.ports import IMealRepository


@dataclass
class DeleteMealInput:
    meal_id: str


class DeleteMeal:
    def __init__(self, meal_repository: IMealRepository) -> None:
        self._meal_repository = meal_repository

    async def execute(self, input: DeleteMealInput) -> None:
        meal = await self._meal_repository.find_by_id(input.meal_id)
        if meal is None:
            raise MealNotFoundError(input.meal_id)
        await self._meal_repository.delete(input.meal_id)
