from datetime import datetime
from decimal import Decimal
from src.meals.domain.entity import MealEntity
from src.shared.presentation.responses import CamelModel


class MealRDTO(CamelModel):
    id: str
    name: str
    description: str | None
    price: Decimal
    category: str
    available: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: MealEntity) -> "MealRDTO":
        return cls(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            price=entity.price,
            category=entity.category,
            available=entity.available,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
