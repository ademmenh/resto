from dataclasses import dataclass
from src.inventory.domain.entity import ItemEntity
from src.inventory.domain.errors import ItemNotFoundError
from src.inventory.domain.ports import IItemRepository


@dataclass
class GetItemInput:
    item_id: str


class GetItem:
    def __init__(self, repository: IItemRepository) -> None:
        self._repository = repository

    async def execute(self, input: GetItemInput) -> ItemEntity:
        item = await self._repository.find_by_id(input.item_id)
        if item is None:
            raise ItemNotFoundError(input.item_id)
        return item
