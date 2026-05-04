from dataclasses import dataclass
from src.meals.domain.entity import MealEntity
from src.meals.domain.ports import IMealRepository, ListMealsFilter


@dataclass
class ListMealsInput:
    category: str | None = None
    available: bool | None = None
    search: str | None = None
    page: int = 1
    limit: int = 20


class ListMeals:
    def __init__(self, meal_repository: IMealRepository) -> None:
        self._meal_repository = meal_repository

    async def execute(self, input: ListMealsInput) -> tuple[list[MealEntity], int]:
        has_filter = (
            input.category is not None or input.available is not None or input.search is not None
        )
        filter = (
            ListMealsFilter(
                category=input.category,
                available=input.available,
                search=input.search,
            )
            if has_filter
            else None
        )
        return await self._meal_repository.list(filter, page=input.page, limit=input.limit)
