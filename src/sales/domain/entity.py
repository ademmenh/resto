from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import Literal

SaleStatus = Literal["pending", "completed", "cancelled"]


@dataclass(frozen=True)
class SaleEntity:
    id: str
    client_id: str
    meal_id: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    status: SaleStatus = "pending"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def is_pending(self) -> bool:
        return self.status == "pending"

    def belongs_to_client(self, client_id: str) -> bool:
        return self.client_id == client_id
