from dataclasses import dataclass
from src.sales.domain.entity import SaleEntity
from src.sales.domain.errors import SaleAccessDeniedError, SaleNotFoundError
from src.sales.domain.ports import ISaleRepository


@dataclass
class GetSaleInput:
    sale_id: str
    requester_id: str
    requester_role: str


class GetSale:
    def __init__(self, sale_repository: ISaleRepository) -> None:
        self._sale_repository = sale_repository

    async def execute(self, input: GetSaleInput) -> SaleEntity:
        sale = await self._sale_repository.find_by_id(input.sale_id)
        if sale is None:
            raise SaleNotFoundError(input.sale_id)

        is_privileged = input.requester_role in ("admin", "manager")
        if not is_privileged and not sale.belongs_to_client(input.requester_id):
            raise SaleAccessDeniedError()

        return sale
