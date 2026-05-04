from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from decimal import Decimal
from src.inventory.domain.unit import Unit
from src.shared.domain.id import Id


@dataclass(frozen=True)
class ItemEntity:
    id: Id
    name: str
    quantity: Decimal
    unit: Unit
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if self.quantity < Decimal("0"):
            raise ValueError("Item quantity cannot be negative")

    def with_added_quantity(self, amount: Decimal) -> ItemEntity:
        """Return a new entity with quantity increased by *amount*."""
        if amount <= Decimal("0"):
            raise ValueError("Amount to add must be positive")
        return replace(self, quantity=self.quantity + amount)

    def with_reduced_quantity(self, amount: Decimal) -> ItemEntity:
        """Return a new entity with quantity decreased by *amount*.

        Raises InsufficientQuantityError when the requested amount exceeds
        the current stock.
        """
        from src.inventory.domain.errors import InsufficientQuantityError

        if amount <= Decimal("0"):
            raise ValueError("Amount to reduce must be positive")
        if amount > self.quantity:
            raise InsufficientQuantityError(
                item_id=self.id.value,
                requested=amount,
                available=self.quantity,
            )
        return replace(self, quantity=self.quantity - amount)
