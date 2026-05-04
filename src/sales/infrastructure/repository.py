from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncEngine

from src.sales.domain.entity import SaleEntity, SaleStatus
from src.sales.domain.ports import ISaleRepository, ListSalesFilter
from src.sales.infrastructure.mapper import SaleMapper
from src.sales.infrastructure.schema import sales_table


class SaleRepository(ISaleRepository):
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def find_by_id(self, sale_id: str) -> SaleEntity | None:
        async with self._engine.connect() as conn:
            result = await conn.execute(
                select(sales_table).where(sales_table.c.id == sale_id)
            )
            row = result.one_or_none()
            return SaleMapper.to_domain(row) if row else None

    async def list(
        self,
        filter: ListSalesFilter | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[SaleEntity], int]:
        conditions = []
        if filter is not None:
            if filter.client_id is not None:
                conditions.append(sales_table.c.client_id == filter.client_id)
            if filter.status is not None:
                conditions.append(sales_table.c.status == filter.status)

        async with self._engine.connect() as conn:
            count_q = select(func.count()).select_from(sales_table)
            for cond in conditions:
                count_q = count_q.where(cond)
            total: int = (await conn.execute(count_q)).scalar_one()

            data_q = select(sales_table)
            for cond in conditions:
                data_q = data_q.where(cond)
            data_q = data_q.offset((page - 1) * limit).limit(limit)
            rows = (await conn.execute(data_q)).all()

            return [SaleMapper.to_domain(r) for r in rows], total

    async def create(self, entity: SaleEntity) -> SaleEntity:
        values = SaleMapper.to_values(entity)
        async with self._engine.begin() as conn:
            result = await conn.execute(
                insert(sales_table).values(**values).returning(sales_table)
            )
            return SaleMapper.to_domain(result.one())

    async def update_status(self, sale_id: str, status: SaleStatus) -> SaleEntity:
        async with self._engine.begin() as conn:
            result = await conn.execute(
                update(sales_table)
                .where(sales_table.c.id == sale_id)
                .values(status=status)
                .returning(sales_table)
            )
            row = result.one_or_none()
            if row is None:
                raise ValueError(f"Sale with id {sale_id} not found")
            return SaleMapper.to_domain(row)

    async def delete(self, sale_id: str) -> None:
        async with self._engine.begin() as conn:
            await conn.execute(
                delete(sales_table).where(sales_table.c.id == sale_id)
            )
