from dataclasses import dataclass
from decimal import Decimal
from src.meals.domain.entity import MealEntity
from src.meals.domain.ports import IMealRepository
from src.shared.infrastructure.id_generator import IDGenerator


@dataclass
class CreateMealInput:
    name: str
    description: str | None
    price: Decimal
    category: str
    available: bool = True


class CreateMeal:
    def __init__(
        self,
        meal_repository: IMealRepository,
        id_generator: IDGenerator,
    ) -> None:
        self._meal_repository = meal_repository
        self._id_generator = id_generator

    async def execute(self, input: CreateMealInput) -> MealEntity:
        meal_id = self._id_generator.generate()
        meal = MealEntity(
            id=meal_id.value,
            name=input.name.strip(),
            description=input.description,
            price=input.price,
            category=input.category.strip(),
            available=input.available,
        )
        return await self._meal_repository.create(meal)
