from dataclasses import dataclass
from src.inventory.domain.errors import ItemNotFoundError
from src.inventory.domain.ports import IItemRepository


@dataclass
class DeleteItemInput:
    item_id: str


class DeleteItem:
    def __init__(self, repository: IItemRepository) -> None:
        self._repository = repository

    async def execute(self, input: DeleteItemInput) -> None:
        item = await self._repository.find_by_id(input.item_id)
        if item is None:
            raise ItemNotFoundError(input.item_id)
        await self._repository.delete(input.item_id)
