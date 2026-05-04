"""In-memory implementation of IMealRepository for unit tests."""
from src.meals.domain.entity import MealEntity
from src.meals.domain.ports import IMealRepository, ListMealsFilter


class InMemoryMealRepository(IMealRepository):
    def __init__(self) -> None:
        self._store: dict[str, MealEntity] = {}

    async def find_by_id(self, meal_id: str) -> MealEntity | None:
        return self._store.get(meal_id)

    async def list(
        self,
        filter: ListMealsFilter | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[MealEntity], int]:
        items = list(self._store.values())
        if filter is not None:
            if filter.category is not None:
                items = [m for m in items if m.category == filter.category]
            if filter.available is not None:
                items = [m for m in items if m.available == filter.available]
            if filter.search is not None:
                term = filter.search.lower()
                items = [m for m in items if term in m.name.lower()]
        total = len(items)
        start = (page - 1) * limit
        return items[start : start + limit], total

    async def create(self, entity: MealEntity) -> MealEntity:
        self._store[entity.id] = entity
        return entity

    async def update(self, entity: MealEntity) -> MealEntity:
        self._store[entity.id] = entity
        return entity

    async def delete(self, meal_id: str) -> None:
        self._store.pop(meal_id, None)
