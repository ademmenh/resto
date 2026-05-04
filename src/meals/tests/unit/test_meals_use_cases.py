"""Unit tests for the meals use cases (using InMemoryMealRepository)."""
import pytest
from decimal import Decimal
from unittest.mock import AsyncMock
from src.meals.application.create_meal import CreateMeal, CreateMealInput
from src.meals.application.get_meal import GetMeal, GetMealInput
from src.meals.application.list_meals import ListMeals, ListMealsInput
from src.meals.application.update_meal import UpdateMeal, UpdateMealInput
from src.meals.application.delete_meal import DeleteMeal, DeleteMealInput
from src.meals.domain.errors import MealNotFoundError
from src.meals.infrastructure.in_memory_repository import InMemoryMealRepository
from src.shared.infrastructure.id_generator import IDGenerator


def _make_id_generator() -> IDGenerator:
    return IDGenerator()


@pytest.fixture
def repo() -> InMemoryMealRepository:
    return InMemoryMealRepository()


@pytest.fixture
def id_gen() -> IDGenerator:
    return _make_id_generator()


# ── CreateMeal ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_meal_persists_entity(repo, id_gen):
    use_case = CreateMeal(repo, id_gen)
    result = await use_case.execute(
        CreateMealInput(name="Burger", description=None, price=Decimal("9.99"), category="main")
    )
    assert result.name == "Burger"
    assert result.price == Decimal("9.99")
    assert result.category == "main"
    assert result.available is True
    assert result.id is not None

    stored = await repo.find_by_id(result.id)
    assert stored is not None
    assert stored.name == "Burger"


@pytest.mark.asyncio
async def test_create_meal_strips_whitespace(repo, id_gen):
    use_case = CreateMeal(repo, id_gen)
    result = await use_case.execute(
        CreateMealInput(name="  Pizza  ", description=None, price=Decimal("12.00"), category="  main  ")
    )
    assert result.name == "Pizza"
    assert result.category == "main"


@pytest.mark.asyncio
async def test_create_meal_with_description(repo, id_gen):
    use_case = CreateMeal(repo, id_gen)
    result = await use_case.execute(
        CreateMealInput(name="Salad", description="Fresh salad", price=Decimal("7.00"), category="starter")
    )
    assert result.description == "Fresh salad"


# ── GetMeal ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_meal_returns_entity(repo, id_gen):
    created = await CreateMeal(repo, id_gen).execute(
        CreateMealInput(name="Pasta", description=None, price=Decimal("11.00"), category="main")
    )
    result = await GetMeal(repo).execute(GetMealInput(meal_id=created.id))
    assert result.id == created.id
    assert result.name == "Pasta"


@pytest.mark.asyncio
async def test_get_meal_raises_not_found(repo):
    with pytest.raises(MealNotFoundError):
        await GetMeal(repo).execute(GetMealInput(meal_id="00000000-0000-0000-0000-000000000099"))


# ── ListMeals ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_meals_returns_all(repo, id_gen):
    uc = CreateMeal(repo, id_gen)
    await uc.execute(CreateMealInput(name="A", description=None, price=Decimal("5"), category="main"))
    await uc.execute(CreateMealInput(name="B", description=None, price=Decimal("6"), category="starter"))
    meals, total = await ListMeals(repo).execute(ListMealsInput())
    assert total == 2
    assert len(meals) == 2


@pytest.mark.asyncio
async def test_list_meals_filter_by_category(repo, id_gen):
    uc = CreateMeal(repo, id_gen)
    await uc.execute(CreateMealInput(name="A", description=None, price=Decimal("5"), category="main"))
    await uc.execute(CreateMealInput(name="B", description=None, price=Decimal("6"), category="starter"))
    meals, total = await ListMeals(repo).execute(ListMealsInput(category="main"))
    assert total == 1
    assert meals[0].name == "A"


@pytest.mark.asyncio
async def test_list_meals_filter_by_available(repo, id_gen):
    uc = CreateMeal(repo, id_gen)
    await uc.execute(CreateMealInput(name="Available", description=None, price=Decimal("5"), category="main", available=True))
    await uc.execute(CreateMealInput(name="Unavailable", description=None, price=Decimal("5"), category="main", available=False))
    meals, total = await ListMeals(repo).execute(ListMealsInput(available=False))
    assert total == 1
    assert meals[0].name == "Unavailable"


@pytest.mark.asyncio
async def test_list_meals_filter_by_search(repo, id_gen):
    uc = CreateMeal(repo, id_gen)
    await uc.execute(CreateMealInput(name="Chicken Rice", description=None, price=Decimal("8"), category="main"))
    await uc.execute(CreateMealInput(name="Beef Burger", description=None, price=Decimal("10"), category="main"))
    meals, total = await ListMeals(repo).execute(ListMealsInput(search="chicken"))
    assert total == 1
    assert meals[0].name == "Chicken Rice"


# ── UpdateMeal ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_meal_changes_fields(repo, id_gen):
    created = await CreateMeal(repo, id_gen).execute(
        CreateMealInput(name="Old Name", description=None, price=Decimal("5"), category="main")
    )
    result = await UpdateMeal(repo).execute(
        UpdateMealInput(meal_id=created.id, name="New Name", price=Decimal("15.00"), available=False)
    )
    assert result.name == "New Name"
    assert result.price == Decimal("15.00")
    assert result.available is False


@pytest.mark.asyncio
async def test_update_meal_raises_not_found(repo):
    with pytest.raises(MealNotFoundError):
        await UpdateMeal(repo).execute(
            UpdateMealInput(meal_id="00000000-0000-0000-0000-000000000099", name="X")
        )


@pytest.mark.asyncio
async def test_update_meal_partial_update_preserves_fields(repo, id_gen):
    created = await CreateMeal(repo, id_gen).execute(
        CreateMealInput(name="Pizza", description="Cheesy", price=Decimal("12"), category="main")
    )
    result = await UpdateMeal(repo).execute(
        UpdateMealInput(meal_id=created.id, price=Decimal("14"))
    )
    assert result.name == "Pizza"
    assert result.description == "Cheesy"
    assert result.price == Decimal("14")


# ── DeleteMeal ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delete_meal_removes_entity(repo, id_gen):
    created = await CreateMeal(repo, id_gen).execute(
        CreateMealInput(name="ToDelete", description=None, price=Decimal("5"), category="main")
    )
    await DeleteMeal(repo).execute(DeleteMealInput(meal_id=created.id))
    assert await repo.find_by_id(created.id) is None


@pytest.mark.asyncio
async def test_delete_meal_raises_not_found(repo):
    with pytest.raises(MealNotFoundError):
        await DeleteMeal(repo).execute(DeleteMealInput(meal_id="00000000-0000-0000-0000-000000000099"))
