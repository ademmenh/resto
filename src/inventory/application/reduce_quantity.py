from dataclasses import dataclass
from decimal import Decimal
from src.inventory.domain.entity import ItemEntity
from src.inventory.domain.errors import ItemNotFoundError
from src.inventory.domain.ports import IItemRepository


@dataclass
class ReduceQuantityInput:
    item_id: str
    amount: Decimal


class ReduceQuantity:
    def __init__(self, repository: IItemRepository) -> None:
        self._repository = repository

    async def execute(self, input: ReduceQuantityInput) -> ItemEntity:
        item = await self._repository.find_by_id(input.item_id)
        if item is None:
            raise ItemNotFoundError(input.item_id)

        # domain entity enforces the "no negative stock" rule
        updated = item.with_reduced_quantity(input.amount)
        return await self._repository.update_quantity(input.item_id, updated.quantity)
