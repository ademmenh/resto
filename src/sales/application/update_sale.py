from dataclasses import dataclass
from src.sales.domain.entity import SaleEntity, SaleStatus
from src.sales.domain.errors import SaleCannotBeCancelledError, SaleNotFoundError
from src.sales.domain.ports import ISaleRepository


@dataclass
class UpdateSaleInput:
    sale_id: str
    status: SaleStatus


class UpdateSale:
    def __init__(self, sale_repository: ISaleRepository) -> None:
        self._sale_repository = sale_repository

    async def execute(self, input: UpdateSaleInput) -> SaleEntity:
        sale = await self._sale_repository.find_by_id(input.sale_id)
        if sale is None:
            raise SaleNotFoundError(input.sale_id)

        if input.status == "cancelled" and not sale.is_pending():
            raise SaleCannotBeCancelledError()

        return await self._sale_repository.update_status(input.sale_id, input.status)
