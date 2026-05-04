"""Integration tests for MealRepository against the in-memory SQLite engine."""
import pytest
from decimal import Decimal
from datetime import datetime, UTC
from uuid import uuid4

from src.meals.domain.entity import MealEntity
from src.meals.infrastructure.repository import MealRepository


def _meal(name: str = "Test Meal", category: str = "main", available: bool = True) -> MealEntity:
    now = datetime.now(UTC)
    return MealEntity(
        id=str(uuid4()),
        name=name,
        description="A test meal",
        price=Decimal("10.00"),
        category=category,
        available=available,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_repo_create_and_find_by_id(engine):
    repo = MealRepository(engine)
    meal = await repo.create(_meal())
    found = await repo.find_by_id(meal.id)
    assert found is not None
    assert found.id == meal.id
    assert found.name == "Test Meal"


@pytest.mark.asyncio
async def test_repo_find_by_id_returns_none_for_unknown(engine):
    repo = MealRepository(engine)
    result = await repo.find_by_id("00000000-0000-0000-0000-000000000000")
    assert result is None


@pytest.mark.asyncio
async def test_repo_list_returns_created_meals(engine):
    repo = MealRepository(engine)
    uid = str(uuid4())[:8]
    await repo.create(_meal(name=f"Soup-{uid}"))
    await repo.create(_meal(name=f"Steak-{uid}"))
    meals, total = await repo.list()
    names = [m.name for m in meals]
    assert f"Soup-{uid}" in names
    assert f"Steak-{uid}" in names
    assert total >= 2


@pytest.mark.asyncio
async def test_repo_list_filter_by_category(engine):
    repo = MealRepository(engine)
    uid = str(uuid4())[:8]
    await repo.create(_meal(name=f"Salad-{uid}", category="starter"))
    from src.meals.domain.ports import ListMealsFilter
    meals, _ = await repo.list(ListMealsFilter(category="starter"))
    assert all(m.category == "starter" for m in meals)


@pytest.mark.asyncio
async def test_repo_list_filter_by_available(engine):
    repo = MealRepository(engine)
    uid = str(uuid4())[:8]
    await repo.create(_meal(name=f"NotReady-{uid}", available=False))
    from src.meals.domain.ports import ListMealsFilter
    meals, _ = await repo.list(ListMealsFilter(available=False))
    assert all(m.available is False for m in meals)


@pytest.mark.asyncio
async def test_repo_update_meal(engine):
    repo = MealRepository(engine)
    meal = await repo.create(_meal(name="Old"))
    from dataclasses import replace
    updated_entity = replace(meal, name="Updated", price=Decimal("20.00"))
    result = await repo.update(updated_entity)
    assert result.name == "Updated"
    assert result.price == Decimal("20.00")


@pytest.mark.asyncio
async def test_repo_delete_meal(engine):
    repo = MealRepository(engine)
    meal = await repo.create(_meal())
    await repo.delete(meal.id)
    assert await repo.find_by_id(meal.id) is None


@pytest.mark.asyncio
async def test_repo_list_pagination(engine):
    repo = MealRepository(engine)
    for i in range(5):
        await repo.create(_meal(name=f"PaginMeal{i}-{str(uuid4())[:4]}"))
    page1, total = await repo.list(page=1, limit=3)
    assert len(page1) <= 3
    assert total >= 5
