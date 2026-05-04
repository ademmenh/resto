"""Unit tests for the sales use cases (using in-memory repos)."""
import pytest
from decimal import Decimal
from datetime import datetime, UTC

from src.meals.domain.entity import MealEntity
from src.meals.infrastructure.in_memory_repository import InMemoryMealRepository
from src.sales.application.create_sale import CreateSale, CreateSaleInput
from src.sales.application.get_sale import GetSale, GetSaleInput
from src.sales.application.list_sales import ListSales, ListSalesInput
from src.sales.application.update_sale import UpdateSale, UpdateSaleInput
from src.sales.domain.errors import SaleAccessDeniedError, SaleCannotBeCancelledError, SaleNotFoundError
from src.sales.infrastructure.in_memory_repository import InMemorySaleRepository
from src.shared.infrastructure.id_generator import IDGenerator
from src.users.domain.entity import UserEntity
from src.users.infrastructure.in_memory_repository import InMemoryUserRepository
from src.shared.domain.id import Id
from src.shared.domain.email import Email


CLIENT_ID = "00000000-0000-0000-0000-aaaaaaaaaaaa"
MEAL_ID = "00000000-0000-0000-0000-bbbbbbbbbbbb"
ADMIN_ID = "00000000-0000-0000-0000-cccccccccccc"


def _make_user(user_id: str, role: str = "client") -> UserEntity:
    now = datetime.now(UTC)
    return UserEntity(
        id=Id.from_str(user_id),
        name="Test User",
        email=Email.create(f"user-{user_id[:8]}@test.com"),
        phone=None,
        password_hash="hashed",
        role=role,  # type: ignore[arg-type]
        created_at=now,
        updated_at=now,
    )


def _make_meal(meal_id: str, price: Decimal = Decimal("10.00"), available: bool = True) -> MealEntity:
    now = datetime.now(UTC)
    return MealEntity(
        id=meal_id,
        name="Test Meal",
        description=None,
        price=price,
        category="main",
        available=available,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def repos():
    sale_repo = InMemorySaleRepository()
    meal_repo = InMemoryMealRepository()
    user_repo = InMemoryUserRepository()
    return sale_repo, meal_repo, user_repo


@pytest.fixture
async def repos_with_data(repos):
    sale_repo, meal_repo, user_repo = repos
    await user_repo.create(_make_user(CLIENT_ID, "client"))
    await user_repo.create(_make_user(ADMIN_ID, "admin"))
    await meal_repo.create(_make_meal(MEAL_ID, price=Decimal("15.00")))
    return sale_repo, meal_repo, user_repo


# ── CreateSale ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_sale_calculates_total(repos_with_data):
    sale_repo, meal_repo, user_repo = repos_with_data
    uc = CreateSale(sale_repo, meal_repo, user_repo, IDGenerator())
    sale = await uc.execute(CreateSaleInput(client_id=CLIENT_ID, meal_id=MEAL_ID, quantity=3))
    assert sale.quantity == 3
    assert sale.unit_price == Decimal("15.00")
    assert sale.total_price == Decimal("45.00")
    assert sale.status == "pending"


@pytest.mark.asyncio
async def test_create_sale_raises_user_not_found(repos_with_data):
    from src.users.domain.errors import UserNotFoundError
    sale_repo, meal_repo, user_repo = repos_with_data
    uc = CreateSale(sale_repo, meal_repo, user_repo, IDGenerator())
    with pytest.raises(UserNotFoundError):
        await uc.execute(CreateSaleInput(client_id="00000000-0000-0000-0000-000000000099", meal_id=MEAL_ID, quantity=1))


@pytest.mark.asyncio
async def test_create_sale_raises_meal_not_found(repos_with_data):
    from src.meals.domain.errors import MealNotFoundError
    sale_repo, meal_repo, user_repo = repos_with_data
    uc = CreateSale(sale_repo, meal_repo, user_repo, IDGenerator())
    with pytest.raises(MealNotFoundError):
        await uc.execute(CreateSaleInput(client_id=CLIENT_ID, meal_id="00000000-0000-0000-0000-000000000099", quantity=1))


@pytest.mark.asyncio
async def test_create_sale_raises_meal_not_available(repos):
    from src.meals.domain.errors import MealNotAvailableError
    sale_repo, meal_repo, user_repo = repos
    unavailable_meal_id = "00000000-0000-0000-0000-eeeeeeeeeeee"
    await user_repo.create(_make_user(CLIENT_ID))
    await meal_repo.create(_make_meal(unavailable_meal_id, available=False))
    uc = CreateSale(sale_repo, meal_repo, user_repo, IDGenerator())
    with pytest.raises(MealNotAvailableError):
        await uc.execute(CreateSaleInput(client_id=CLIENT_ID, meal_id=unavailable_meal_id, quantity=1))


# ── GetSale ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_sale_by_owner(repos_with_data):
    sale_repo, meal_repo, user_repo = repos_with_data
    sale = await CreateSale(sale_repo, meal_repo, user_repo, IDGenerator()).execute(
        CreateSaleInput(client_id=CLIENT_ID, meal_id=MEAL_ID, quantity=1)
    )
    result = await GetSale(sale_repo).execute(GetSaleInput(sale_id=sale.id, requester_id=CLIENT_ID, requester_role="client"))
    assert result.id == sale.id


@pytest.mark.asyncio
async def test_get_sale_by_admin(repos_with_data):
    sale_repo, meal_repo, user_repo = repos_with_data
    sale = await CreateSale(sale_repo, meal_repo, user_repo, IDGenerator()).execute(
        CreateSaleInput(client_id=CLIENT_ID, meal_id=MEAL_ID, quantity=1)
    )
    result = await GetSale(sale_repo).execute(GetSaleInput(sale_id=sale.id, requester_id=ADMIN_ID, requester_role="admin"))
    assert result.id == sale.id


@pytest.mark.asyncio
async def test_get_sale_raises_access_denied(repos_with_data):
    sale_repo, meal_repo, user_repo = repos_with_data
    other_client_id = "00000000-0000-0000-0000-dddddddddddd"
    await user_repo.create(_make_user(other_client_id))
    sale = await CreateSale(sale_repo, meal_repo, user_repo, IDGenerator()).execute(
        CreateSaleInput(client_id=CLIENT_ID, meal_id=MEAL_ID, quantity=1)
    )
    with pytest.raises(SaleAccessDeniedError):
        await GetSale(sale_repo).execute(GetSaleInput(sale_id=sale.id, requester_id=other_client_id, requester_role="client"))


@pytest.mark.asyncio
async def test_get_sale_raises_not_found(repos_with_data):
    sale_repo, _, _ = repos_with_data
    with pytest.raises(SaleNotFoundError):
        await GetSale(sale_repo).execute(GetSaleInput(sale_id="00000000-0000-0000-0000-000000000099", requester_id=CLIENT_ID, requester_role="client"))


# ── ListSales ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_sales_client_sees_only_own(repos_with_data):
    sale_repo, meal_repo, user_repo = repos_with_data
    other_id = "00000000-0000-0000-0000-fffffffffffF"
    await user_repo.create(_make_user(other_id))
    uc = CreateSale(sale_repo, meal_repo, user_repo, IDGenerator())
    await uc.execute(CreateSaleInput(client_id=CLIENT_ID, meal_id=MEAL_ID, quantity=1))
    await uc.execute(CreateSaleInput(client_id=other_id, meal_id=MEAL_ID, quantity=1))
    sales, total = await ListSales(sale_repo).execute(ListSalesInput(requester_id=CLIENT_ID, requester_role="client"))
    assert all(s.client_id == CLIENT_ID for s in sales)


@pytest.mark.asyncio
async def test_list_sales_admin_sees_all(repos_with_data):
    sale_repo, meal_repo, user_repo = repos_with_data
    other_id = "00000000-0000-0000-0000-eeeeeeeeeeef"
    await user_repo.create(_make_user(other_id))
    uc = CreateSale(sale_repo, meal_repo, user_repo, IDGenerator())
    await uc.execute(CreateSaleInput(client_id=CLIENT_ID, meal_id=MEAL_ID, quantity=1))
    await uc.execute(CreateSaleInput(client_id=other_id, meal_id=MEAL_ID, quantity=1))
    sales, total = await ListSales(sale_repo).execute(ListSalesInput(requester_id=ADMIN_ID, requester_role="admin"))
    assert total >= 2


# ── UpdateSale ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_sale_completes(repos_with_data):
    sale_repo, meal_repo, user_repo = repos_with_data
    sale = await CreateSale(sale_repo, meal_repo, user_repo, IDGenerator()).execute(
        CreateSaleInput(client_id=CLIENT_ID, meal_id=MEAL_ID, quantity=1)
    )
    result = await UpdateSale(sale_repo).execute(UpdateSaleInput(sale_id=sale.id, status="completed"))
    assert result.status == "completed"


@pytest.mark.asyncio
async def test_update_sale_cancels_pending(repos_with_data):
    sale_repo, meal_repo, user_repo = repos_with_data
    sale = await CreateSale(sale_repo, meal_repo, user_repo, IDGenerator()).execute(
        CreateSaleInput(client_id=CLIENT_ID, meal_id=MEAL_ID, quantity=1)
    )
    result = await UpdateSale(sale_repo).execute(UpdateSaleInput(sale_id=sale.id, status="cancelled"))
    assert result.status == "cancelled"


@pytest.mark.asyncio
async def test_update_sale_cannot_cancel_completed(repos_with_data):
    sale_repo, meal_repo, user_repo = repos_with_data
    sale = await CreateSale(sale_repo, meal_repo, user_repo, IDGenerator()).execute(
        CreateSaleInput(client_id=CLIENT_ID, meal_id=MEAL_ID, quantity=1)
    )
    await UpdateSale(sale_repo).execute(UpdateSaleInput(sale_id=sale.id, status="completed"))
    with pytest.raises(SaleCannotBeCancelledError):
        await UpdateSale(sale_repo).execute(UpdateSaleInput(sale_id=sale.id, status="cancelled"))


@pytest.mark.asyncio
async def test_update_sale_raises_not_found(repos_with_data):
    sale_repo, _, _ = repos_with_data
    with pytest.raises(SaleNotFoundError):
        await UpdateSale(sale_repo).execute(UpdateSaleInput(sale_id="00000000-0000-0000-0000-000000000099", status="completed"))
