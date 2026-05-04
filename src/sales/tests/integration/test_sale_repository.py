"""Integration tests for SaleRepository against the in-memory SQLite engine."""
import pytest
from decimal import Decimal
from datetime import datetime, UTC
from uuid import uuid4

from src.sales.domain.entity import SaleEntity
from src.sales.domain.ports import ListSalesFilter
from src.sales.infrastructure.repository import SaleRepository
from src.meals.infrastructure.repository import MealRepository
from src.users.infrastructure.repository import UserRepository
from src.shared.domain.id import Id
from src.shared.domain.email import Email
from src.users.domain.entity import UserEntity
from src.meals.domain.entity import MealEntity


async def _seed(engine) -> tuple[str, str]:
    """Seed a fresh user and meal for FK constraints. Returns (client_id, meal_id)."""
    u_repo = UserRepository(engine)
    m_repo = MealRepository(engine)
    now = datetime.now(UTC)
    client_id = str(uuid4())
    meal_id = str(uuid4())

    await u_repo.create(UserEntity(
        id=Id.from_str(client_id),
        name="SaleClient",
        email=Email.create(f"saleclient-{client_id[:8]}@e.com"),
        phone=None,
        password_hash="h",
        role="client",
        created_at=now,
        updated_at=now,
    ))
    await m_repo.create(MealEntity(
        id=meal_id,
        name=f"SaleMeal-{meal_id[:8]}",
        description=None,
        price=Decimal("10.00"),
        category="main",
        available=True,
        created_at=now,
        updated_at=now,
    ))
    return client_id, meal_id


def _sale(sale_id: str, client_id: str, meal_id: str) -> SaleEntity:
    now = datetime.now(UTC)
    return SaleEntity(
        id=sale_id,
        client_id=client_id,
        meal_id=meal_id,
        quantity=2,
        unit_price=Decimal("10.00"),
        total_price=Decimal("20.00"),
        status="pending",
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_sale_repo_create_and_find(engine):
    client_id, meal_id = await _seed(engine)
    repo = SaleRepository(engine)
    sale = await repo.create(_sale(str(uuid4()), client_id, meal_id))
    found = await repo.find_by_id(sale.id)
    assert found is not None
    assert found.status == "pending"


@pytest.mark.asyncio
async def test_sale_repo_find_returns_none_for_unknown(engine):
    repo = SaleRepository(engine)
    result = await repo.find_by_id("00000000-0000-0000-0000-000000000000")
    assert result is None


@pytest.mark.asyncio
async def test_sale_repo_list(engine):
    client_id, meal_id = await _seed(engine)
    repo = SaleRepository(engine)
    await repo.create(_sale(str(uuid4()), client_id, meal_id))
    await repo.create(_sale(str(uuid4()), client_id, meal_id))
    sales, total = await repo.list()
    assert total >= 2


@pytest.mark.asyncio
async def test_sale_repo_list_filter_by_client(engine):
    client_id, meal_id = await _seed(engine)
    repo = SaleRepository(engine)
    await repo.create(_sale(str(uuid4()), client_id, meal_id))
    sales, _ = await repo.list(ListSalesFilter(client_id=client_id))
    assert all(s.client_id == client_id for s in sales)


@pytest.mark.asyncio
async def test_sale_repo_list_filter_by_status(engine):
    client_id, meal_id = await _seed(engine)
    repo = SaleRepository(engine)
    sale = await repo.create(_sale(str(uuid4()), client_id, meal_id))
    await repo.update_status(sale.id, "completed")
    completed, _ = await repo.list(ListSalesFilter(status="completed"))
    assert any(s.status == "completed" for s in completed)


@pytest.mark.asyncio
async def test_sale_repo_update_status(engine):
    client_id, meal_id = await _seed(engine)
    repo = SaleRepository(engine)
    sale = await repo.create(_sale(str(uuid4()), client_id, meal_id))
    updated = await repo.update_status(sale.id, "completed")
    assert updated.status == "completed"


@pytest.mark.asyncio
async def test_sale_repo_delete(engine):
    client_id, meal_id = await _seed(engine)
    repo = SaleRepository(engine)
    sale = await repo.create(_sale(str(uuid4()), client_id, meal_id))
    await repo.delete(sale.id)
    assert await repo.find_by_id(sale.id) is None


@pytest.mark.asyncio
async def test_sale_repo_list_pagination(engine):
    client_id, meal_id = await _seed(engine)
    repo = SaleRepository(engine)
    for _ in range(5):
        await repo.create(_sale(str(uuid4()), client_id, meal_id))
    page1, total = await repo.list(page=1, limit=2)
    assert len(page1) <= 2
    assert total >= 5
