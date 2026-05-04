import pytest
from datetime import UTC, datetime
from decimal import Decimal
from src.inventory.domain.entity import ItemEntity
from src.inventory.domain.errors import InsufficientQuantityError
from src.inventory.domain.unit import Unit
from src.shared.domain.id import Id


def _make_item(quantity: str = "10.0000", unit: str = "kg") -> ItemEntity:
    now = datetime.now(UTC)
    return ItemEntity(
        id=Id.from_str("00000000-0000-0000-0000-000000000001"),
        name="Flour",
        quantity=Decimal(quantity),
        unit=Unit.create(unit),
        created_at=now,
        updated_at=now,
    )


class TestItemEntityQuantity:
    def test_add_positive_amount(self):
        item = _make_item("10.0000")
        updated = item.with_added_quantity(Decimal("5"))
        assert updated.quantity == Decimal("15")

    def test_add_preserves_other_fields(self):
        item = _make_item()
        updated = item.with_added_quantity(Decimal("1"))
        assert updated.id == item.id
        assert updated.name == item.name
        assert updated.unit == item.unit

    def test_add_zero_raises(self):
        with pytest.raises(ValueError, match="positive"):
            _make_item().with_added_quantity(Decimal("0"))

    def test_add_negative_raises(self):
        with pytest.raises(ValueError, match="positive"):
            _make_item().with_added_quantity(Decimal("-3"))

    def test_reduce_within_stock(self):
        item = _make_item("10.0000")
        updated = item.with_reduced_quantity(Decimal("4"))
        assert updated.quantity == Decimal("6")

    def test_reduce_exact_stock_to_zero(self):
        item = _make_item("10.0000")
        updated = item.with_reduced_quantity(Decimal("10"))
        assert updated.quantity == Decimal("0")

    def test_reduce_exceeds_stock_raises(self):
        item = _make_item("10.0000")
        with pytest.raises(InsufficientQuantityError):
            item.with_reduced_quantity(Decimal("11"))

    def test_reduce_zero_raises(self):
        with pytest.raises(ValueError, match="positive"):
            _make_item().with_reduced_quantity(Decimal("0"))

    def test_reduce_negative_raises(self):
        with pytest.raises(ValueError, match="positive"):
            _make_item().with_reduced_quantity(Decimal("-1"))

    def test_original_is_unchanged_after_add(self):
        item = _make_item("10.0000")
        item.with_added_quantity(Decimal("5"))
        assert item.quantity == Decimal("10.0000")

    def test_negative_initial_quantity_raises(self):
        now = datetime.now(UTC)
        with pytest.raises(ValueError, match="negative"):
            ItemEntity(
                id=Id.from_str("00000000-0000-0000-0000-000000000001"),
                name="X",
                quantity=Decimal("-1"),
                unit=Unit.create("kg"),
                created_at=now,
                updated_at=now,
            )
