from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from src.inventory.domain.entity import ItemEntity
from src.inventory.domain.unit import UnitValue


@dataclass
class CreateItemRDTO:
    id: str
    name: str
    quantity: Decimal
    unit: str


@dataclass
class UpdateItemRDTO:
    name: str | None = None
    unit: str | None = None


@dataclass
class ListItemsFilter:
    unit: UnitValue | None = None
    search: str | None = None


class IItemRepository(ABC):
    @abstractmethod
    async def find_by_id(self, item_id: str) -> ItemEntity | None: ...

    @abstractmethod
    async def list(
        self,
        filter: ListItemsFilter | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[ItemEntity], int]: ...

    @abstractmethod
    async def create(self, entity: ItemEntity) -> ItemEntity: ...

    @abstractmethod
    async def update(self, entity: ItemEntity) -> ItemEntity: ...

    @abstractmethod
    async def update_quantity(self, item_id: str, new_quantity: Decimal) -> ItemEntity: ...

    @abstractmethod
    async def delete(self, item_id: str) -> None: ...
