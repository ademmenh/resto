"""In-memory implementation of IItemRepository for unit tests."""
from decimal import Decimal
from dataclasses import replace

from src.inventory.domain.entity import ItemEntity
from src.inventory.domain.ports import IItemRepository, ListItemsFilter


class InMemoryItemRepository(IItemRepository):
    def __init__(self) -> None:
        self._store: dict[str, ItemEntity] = {}

    async def find_by_id(self, item_id: str) -> ItemEntity | None:
        return self._store.get(item_id)

    async def list(
        self,
        filter: ListItemsFilter | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[ItemEntity], int]:
        items = list(self._store.values())
        if filter is not None:
            if filter.unit is not None:
                items = [i for i in items if i.unit.value == filter.unit]
            if filter.search is not None:
                term = filter.search.lower()
                items = [i for i in items if term in i.name.lower()]
        total = len(items)
        start = (page - 1) * limit
        return items[start : start + limit], total

    async def create(self, entity: ItemEntity) -> ItemEntity:
        self._store[entity.id.value] = entity
        return entity

    async def update(self, entity: ItemEntity) -> ItemEntity:
        self._store[entity.id.value] = entity
        return entity

    async def update_quantity(self, item_id: str, new_quantity: Decimal) -> ItemEntity:
        item = self._store[item_id]
        updated = replace(item, quantity=new_quantity)
        self._store[item_id] = updated
        return updated

    async def delete(self, item_id: str) -> None:
        self._store.pop(item_id, None)
