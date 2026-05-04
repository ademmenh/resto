from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from src.sales.domain.entity import SaleEntity, SaleStatus


@dataclass
class CreateSaleRDTO:
    id: str
    client_id: str
    meal_id: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal


@dataclass
class ListSalesFilter:
    client_id: str | None = None
    status: SaleStatus | None = None


class ISaleRepository(ABC):
    @abstractmethod
    async def find_by_id(self, sale_id: str) -> SaleEntity | None: ...

    @abstractmethod
    async def list(
        self,
        filter: ListSalesFilter | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[SaleEntity], int]: ...

    @abstractmethod
    async def create(self, entity: SaleEntity) -> SaleEntity: ...

    @abstractmethod
    async def update_status(self, sale_id: str, status: SaleStatus) -> SaleEntity: ...

    @abstractmethod
    async def delete(self, sale_id: str) -> None: ...
