from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncEngine

from src.meals.domain.entity import MealEntity
from src.meals.domain.ports import IMealRepository, ListMealsFilter
from src.meals.infrastructure.mapper import MealMapper
from src.meals.infrastructure.schema import meals_table


class MealRepository(IMealRepository):
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def find_by_id(self, meal_id: str) -> MealEntity | None:
        async with self._engine.connect() as conn:
            result = await conn.execute(
                select(meals_table).where(meals_table.c.id == meal_id)
            )
            row = result.one_or_none()
            return MealMapper.to_domain(row) if row else None

    async def list(
        self,
        filter: ListMealsFilter | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[MealEntity], int]:
        conditions = []
        if filter is not None:
            if filter.category is not None:
                conditions.append(meals_table.c.category == filter.category)
            if filter.available is not None:
                conditions.append(meals_table.c.available == filter.available)
            if filter.search is not None:
                conditions.append(meals_table.c.name.ilike(f"%{filter.search}%"))

        async with self._engine.connect() as conn:
            count_q = select(func.count()).select_from(meals_table)
            for cond in conditions:
                count_q = count_q.where(cond)
            total: int = (await conn.execute(count_q)).scalar_one()

            data_q = select(meals_table)
            for cond in conditions:
                data_q = data_q.where(cond)
            data_q = data_q.offset((page - 1) * limit).limit(limit)
            rows = (await conn.execute(data_q)).all()

            return [MealMapper.to_domain(r) for r in rows], total

    async def create(self, entity: MealEntity) -> MealEntity:
        values = MealMapper.to_values(entity)
        async with self._engine.begin() as conn:
            result = await conn.execute(
                insert(meals_table).values(**values).returning(meals_table)
            )
            return MealMapper.to_domain(result.one())

    async def update(self, entity: MealEntity) -> MealEntity:
        values = MealMapper.to_values(entity)
        meal_id = values.pop("id")
        async with self._engine.begin() as conn:
            result = await conn.execute(
                update(meals_table)
                .where(meals_table.c.id == meal_id)
                .values(**values)
                .returning(meals_table)
            )
            row = result.one_or_none()
            if row is None:
                raise ValueError(f"Meal with id {meal_id} not found")
            return MealMapper.to_domain(row)

    async def delete(self, meal_id: str) -> None:
        async with self._engine.begin() as conn:
            await conn.execute(
                delete(meals_table).where(meals_table.c.id == meal_id)
            )
