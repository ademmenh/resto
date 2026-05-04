"""Integration tests for ItemRepository against the in-memory SQLite engine."""
import pytest
from decimal import Decimal
from datetime import datetime, UTC
from uuid import uuid4

from src.inventory.domain.entity import ItemEntity
from src.inventory.domain.ports import ListItemsFilter
from src.inventory.domain.unit import Unit
from src.inventory.infrastructure.repository import ItemRepository
from src.shared.domain.id import Id


def _item(name: str = "Flour", unit: str = "kg", quantity: str = "10") -> ItemEntity:
    now = datetime.now(UTC)
    return ItemEntity(
        id=Id.from_str(str(uuid4())),
        name=name,
        quantity=Decimal(quantity),
        unit=Unit.create(unit),
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_item_repo_create_and_find(engine):
    repo = ItemRepository(engine)
    item = await repo.create(_item())
    found = await repo.find_by_id(item.id.value)
    assert found is not None
    assert found.name == "Flour"


@pytest.mark.asyncio
async def test_item_repo_find_returns_none_for_unknown(engine):
    repo = ItemRepository(engine)
    result = await repo.find_by_id("00000000-0000-0000-0000-000000000000")
    assert result is None


@pytest.mark.asyncio
async def test_item_repo_list_all(engine):
    repo = ItemRepository(engine)
    uid = str(uuid4())[:8]
    await repo.create(_item(name=f"Sugar-{uid}"))
    await repo.create(_item(name=f"Salt-{uid}"))
    items, total = await repo.list()
    names = [i.name for i in items]
    assert f"Sugar-{uid}" in names
    assert f"Salt-{uid}" in names
    assert total >= 2


@pytest.mark.asyncio
async def test_item_repo_list_filter_by_unit(engine):
    repo = ItemRepository(engine)
    uid = str(uuid4())[:8]
    await repo.create(_item(name=f"Milk-{uid}", unit="l"))
    await repo.create(_item(name=f"Cheese-{uid}", unit="kg"))
    items, _ = await repo.list(ListItemsFilter(unit="l"))  # type: ignore[arg-type]
    assert all(i.unit.value == "l" for i in items)
    assert len(items) >= 1


@pytest.mark.asyncio
async def test_item_repo_list_filter_by_search(engine):
    repo = ItemRepository(engine)
    uid = str(uuid4())[:8]
    await repo.create(_item(name=f"ZzOlive-{uid}"))
    items, _ = await repo.list(ListItemsFilter(search=f"ZzOlive-{uid}"))
    assert len(items) >= 1
    assert any("ZzOlive" in i.name for i in items)


@pytest.mark.asyncio
async def test_item_repo_update(engine):
    repo = ItemRepository(engine)
    item = await repo.create(_item(name="OldItem"))
    from dataclasses import replace
    updated_entity = replace(item, name="NewItem", quantity=Decimal("50"))
    result = await repo.update(updated_entity)
    assert result.name == "NewItem"
    assert result.quantity == Decimal("50")


@pytest.mark.asyncio
async def test_item_repo_update_quantity(engine):
    repo = ItemRepository(engine)
    item = await repo.create(_item(quantity="5"))
    result = await repo.update_quantity(item.id.value, Decimal("99"))
    assert result.quantity == Decimal("99")


@pytest.mark.asyncio
async def test_item_repo_delete(engine):
    repo = ItemRepository(engine)
    item = await repo.create(_item())
    await repo.delete(item.id.value)
    assert await repo.find_by_id(item.id.value) is None


@pytest.mark.asyncio
async def test_item_repo_list_pagination(engine):
    repo = ItemRepository(engine)
    for i in range(5):
        await repo.create(_item(name=f"PaginItem{i}-{str(uuid4())[:4]}"))
    page1, total = await repo.list(page=1, limit=2)
    assert len(page1) <= 2
    assert total >= 5
