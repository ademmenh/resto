from datetime import datetime
from decimal import Decimal
from src.sales.domain.entity import SaleEntity
from src.shared.presentation.responses import CamelModel


class SaleRDTO(CamelModel):
    id: str
    client_id: str
    meal_id: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    status: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: SaleEntity) -> "SaleRDTO":
        return cls(
            id=entity.id,
            client_id=entity.client_id,
            meal_id=entity.meal_id,
            quantity=entity.quantity,
            unit_price=entity.unit_price,
            total_price=entity.total_price,
            status=entity.status,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
