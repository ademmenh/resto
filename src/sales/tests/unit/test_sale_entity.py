from datetime import UTC, datetime
from decimal import Decimal
from src.sales.domain.entity import SaleEntity


def _make_sale(**kwargs) -> SaleEntity:
    defaults = dict(
        id="sale-1",
        client_id="client-1",
        meal_id="meal-1",
        quantity=2,
        unit_price=Decimal("10.00"),
        total_price=Decimal("20.00"),
        status="pending",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    return SaleEntity(**{**defaults, **kwargs})


def test_pending_sale_is_pending():
    assert _make_sale(status="pending").is_pending()


def test_completed_sale_is_not_pending():
    assert not _make_sale(status="completed").is_pending()


def test_belongs_to_correct_client():
    sale = _make_sale(client_id="abc")
    assert sale.belongs_to_client("abc")
    assert not sale.belongs_to_client("xyz")
