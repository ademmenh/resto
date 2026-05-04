from dataclasses import dataclass
from src.sales.domain.entity import SaleEntity, SaleStatus
from src.sales.domain.ports import ISaleRepository, ListSalesFilter


@dataclass
class ListSalesInput:
    requester_id: str
    requester_role: str
    status: SaleStatus | None = None
    page: int = 1
    limit: int = 20


class ListSales:
    def __init__(self, sale_repository: ISaleRepository) -> None:
        self._sale_repository = sale_repository

    async def execute(self, input: ListSalesInput) -> tuple[list[SaleEntity], int]:
        is_privileged = input.requester_role in ("admin", "manager")

        filter = ListSalesFilter(
            client_id=None if is_privileged else input.requester_id,
            status=input.status,
        )

        return await self._sale_repository.list(filter, page=input.page, limit=input.limit)
