from dataclasses import dataclass, replace
from src.inventory.domain.entity import ItemEntity
from src.inventory.domain.errors import ItemNotFoundError
from src.inventory.domain.ports import IItemRepository
from src.inventory.domain.unit import Unit


@dataclass
class UpdateItemInput:
    item_id: str
    name: str | None = None
    unit: str | None = None


class UpdateItem:
    def __init__(self, repository: IItemRepository) -> None:
        self._repository = repository

    async def execute(self, input: UpdateItemInput) -> ItemEntity:
        item = await self._repository.find_by_id(input.item_id)
        if item is None:
            raise ItemNotFoundError(input.item_id)

        updates = {}
        if input.name is not None:
            updates["name"] = input.name.strip()
        if input.unit is not None:
            unit = Unit.create(input.unit)  # validate
            updates["unit"] = unit

        if updates:
            item = replace(item, **updates)

        return await self._repository.update(item)
