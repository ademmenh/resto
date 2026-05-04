from datetime import datetime
from decimal import Decimal
from src.inventory.domain.entity import ItemEntity
from src.shared.presentation.responses import CamelModel


class ItemRDTO(CamelModel):
    id: str
    name: str
    quantity: Decimal
    unit: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: ItemEntity) -> "ItemRDTO":
        return cls(
            id=entity.id.value,
            name=entity.name,
            quantity=entity.quantity,
            unit=entity.unit.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
