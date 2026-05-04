from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal


@dataclass(frozen=True)
class MealEntity:
    id: str
    name: str
    description: str | None
    price: Decimal
    category: str
    available: bool
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def is_available(self) -> bool:
        return self.available
