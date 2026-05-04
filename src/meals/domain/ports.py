from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from src.meals.domain.entity import MealEntity


@dataclass
class CreateMealRDTO:
    id: str
    name: str
    description: str | None
    price: Decimal
    category: str
    available: bool = True


@dataclass
class UpdateMealRDTO:
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None
    category: str | None = None
    available: bool | None = None


@dataclass
class ListMealsFilter:
    category: str | None = None
    available: bool | None = None
    search: str | None = None


class IMealRepository(ABC):
    @abstractmethod
    async def find_by_id(self, meal_id: str) -> MealEntity | None: ...

    @abstractmethod
    async def list(
        self,
        filter: ListMealsFilter | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[MealEntity], int]: ...

    @abstractmethod
    async def create(self, entity: MealEntity) -> MealEntity: ...

    @abstractmethod
    async def update(self, entity: MealEntity) -> MealEntity: ...

    @abstractmethod
    async def delete(self, meal_id: str) -> None: ...
