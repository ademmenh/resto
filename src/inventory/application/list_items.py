from dataclasses import dataclass
from src.inventory.domain.entity import ItemEntity
from src.inventory.domain.ports import IItemRepository, ListItemsFilter
from src.inventory.domain.unit import UnitValue


@dataclass
class ListItemsInput:
    unit: UnitValue | None = None
    search: str | None = None
    page: int = 1
    limit: int = 20


class ListItems:
    def __init__(self, repository: IItemRepository) -> None:
        self._repository = repository

    async def execute(self, input: ListItemsInput) -> tuple[list[ItemEntity], int]:
        filter = (
            ListItemsFilter(unit=input.unit, search=input.search)
            if (input.unit or input.search)
            else None
        )
        return await self._repository.list(filter, page=input.page, limit=input.limit)
