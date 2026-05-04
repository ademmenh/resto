from decimal import Decimal

from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncEngine

from src.inventory.domain.entity import ItemEntity
from src.inventory.domain.ports import IItemRepository, ListItemsFilter
from src.inventory.infrastructure.mapper import ItemMapper
from src.inventory.infrastructure.schema import items_table


class ItemRepository(IItemRepository):
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def find_by_id(self, item_id: str) -> ItemEntity | None:
        async with self._engine.connect() as conn:
            result = await conn.execute(select(items_table).where(items_table.c.id == item_id))
            row = result.one_or_none()
            return ItemMapper.to_domain(row) if row else None

    async def list(
        self,
        filter: ListItemsFilter | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[ItemEntity], int]:
        conditions = []
        if filter is not None:
            if filter.unit is not None:
                conditions.append(items_table.c.unit == filter.unit)
            if filter.search is not None:
                conditions.append(items_table.c.name.ilike(f"%{filter.search}%"))

        async with self._engine.connect() as conn:
            count_q = select(func.count()).select_from(items_table)
            for cond in conditions:
                count_q = count_q.where(cond)
            total: int = (await conn.execute(count_q)).scalar_one()
            data_q = select(items_table)
            for cond in conditions:
                data_q = data_q.where(cond)
            data_q = data_q.offset((page - 1) * limit).limit(limit)
            rows = (await conn.execute(data_q)).all()
            return [ItemMapper.to_domain(r) for r in rows], total

    async def create(self, entity: ItemEntity) -> ItemEntity:
        values = ItemMapper.to_values(entity)
        async with self._engine.begin() as conn:
            result = await conn.execute(insert(items_table).values(**values).returning(items_table))
            return ItemMapper.to_domain(result.one())

    async def update(self, entity: ItemEntity) -> ItemEntity:
        values = ItemMapper.to_values(entity)
        item_id = values.pop("id")
        async with self._engine.begin() as conn:
            result = await conn.execute(
                update(items_table)
                .where(items_table.c.id == item_id)
                .values(**values)
                .returning(items_table)
            )
            row = result.one_or_none()
            if row is None:
                raise ValueError(f"Item with id {item_id} not found")
            return ItemMapper.to_domain(row)

    async def update_quantity(self, item_id: str, new_quantity: Decimal) -> ItemEntity:
        async with self._engine.begin() as conn:
            result = await conn.execute(
                update(items_table)
                .where(items_table.c.id == item_id)
                .values(quantity=new_quantity)
                .returning(items_table)
            )
            row = result.one_or_none()
            if row is None:
                raise ValueError(f"Item with id {item_id} not found")
            return ItemMapper.to_domain(row)

    async def delete(self, item_id: str) -> None:
        async with self._engine.begin() as conn:
            await conn.execute(delete(items_table).where(items_table.c.id == item_id))
