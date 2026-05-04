from dataclasses import dataclass
from decimal import Decimal
from src.inventory.domain.entity import ItemEntity
from src.inventory.domain.ports import IItemRepository
from src.inventory.domain.unit import Unit
from src.shared.infrastructure.id_generator import IDGenerator


@dataclass
class CreateItemInput:
    name: str
    quantity: Decimal
    unit: str


class CreateItem:
    def __init__(self, repository: IItemRepository, id_generator: IDGenerator) -> None:
        self._repository = repository
        self._id_generator = id_generator

    async def execute(self, input: CreateItemInput) -> ItemEntity:
        unit = Unit.create(input.unit)  # validate unit before persisting
        item_id = self._id_generator.generate()
        item = ItemEntity(
            id=item_id,
            name=input.name.strip(),
            quantity=input.quantity,
            unit=unit,
        )
        return await self._repository.create(item)
