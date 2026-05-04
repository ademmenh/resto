from sqlalchemy import Row

from src.inventory.domain.entity import ItemEntity
from src.inventory.domain.unit import Unit
from src.shared.domain.id import Id


class ItemMapper:
    @staticmethod
    def to_domain(row: Row) -> ItemEntity:
        return ItemEntity(
            id=Id.from_str(row.id),
            name=row.name,
            quantity=row.quantity,
            unit=Unit.create(row.unit),
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    @staticmethod
    def to_values(entity: ItemEntity) -> dict:
        return {
            "id": entity.id.value,
            "name": entity.name,
            "quantity": entity.quantity,
            "unit": entity.unit.value,
        }
