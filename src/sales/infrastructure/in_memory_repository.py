"""In-memory implementation of ISaleRepository for unit tests."""
from src.sales.domain.entity import SaleEntity, SaleStatus
from src.sales.domain.ports import ISaleRepository, ListSalesFilter


class InMemorySaleRepository(ISaleRepository):
    def __init__(self) -> None:
        self._store: dict[str, SaleEntity] = {}

    async def find_by_id(self, sale_id: str) -> SaleEntity | None:
        return self._store.get(sale_id)

    async def list(
        self,
        filter: ListSalesFilter | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[SaleEntity], int]:
        items = list(self._store.values())
        if filter is not None:
            if filter.client_id is not None:
                items = [s for s in items if s.client_id == filter.client_id]
            if filter.status is not None:
                items = [s for s in items if s.status == filter.status]
        total = len(items)
        start = (page - 1) * limit
        return items[start : start + limit], total

    async def create(self, entity: SaleEntity) -> SaleEntity:
        self._store[entity.id] = entity
        return entity

    async def update_status(self, sale_id: str, status: SaleStatus) -> SaleEntity:
        from dataclasses import replace
        sale = self._store[sale_id]
        updated = replace(sale, status=status)
        self._store[sale_id] = updated
        return updated

    async def delete(self, sale_id: str) -> None:
        self._store.pop(sale_id, None)
