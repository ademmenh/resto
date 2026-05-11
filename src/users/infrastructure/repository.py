from sqlalchemy import delete, func, insert, or_, select, update
from sqlalchemy.ext.asyncio import AsyncEngine

from src.users.domain.entity import UserEntity
from src.users.domain.ports import IUserRepository, ListUsersFilter
from src.users.infrastructure.mapper import UserMapper
from src.users.infrastructure.schema import users_table


class UserRepository(IUserRepository):
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def find_by_id(self, user_id: str) -> UserEntity | None:
        async with self._engine.connect() as conn:
            result = await conn.execute(select(users_table).where(users_table.c.id == user_id))
            row = result.one_or_none()
            return UserMapper.to_domain(row) if row else None

    async def find_by_email(self, email: str) -> UserEntity | None:
        async with self._engine.connect() as conn:
            result = await conn.execute(select(users_table).where(users_table.c.email == email))
            row = result.one_or_none()
            return UserMapper.to_domain(row) if row else None

    async def list(
        self,
        filter: ListUsersFilter | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[UserEntity], int]:
        conditions = []
        if filter is not None:
            if filter.role is not None:
                conditions.append(users_table.c.role == filter.role)
            if filter.search is not None:
                term = f"%{filter.search}%"
                conditions.append(
                    or_(users_table.c.name.ilike(term), users_table.c.email.ilike(term))
                )

        async with self._engine.connect() as conn:
            count_q = select(func.count()).select_from(users_table)
            for cond in conditions:
                count_q = count_q.where(cond)
            total: int = (await conn.execute(count_q)).scalar_one()
            data_q = select(users_table)
            for cond in conditions:
                data_q = data_q.where(cond)
            data_q = data_q.offset((page - 1) * limit).limit(limit)
            rows = (await conn.execute(data_q)).all()
            return [UserMapper.to_domain(r) for r in rows], total

    async def create(self, entity: UserEntity) -> UserEntity:
        values = UserMapper.to_values(entity)
        async with self._engine.begin() as conn:
            result = await conn.execute(insert(users_table).values(**values).returning(users_table))
            return UserMapper.to_domain(result.one())

    async def update(self, entity: UserEntity) -> UserEntity:
        values = UserMapper.to_values(entity)
        user_id = values.pop("id")
        async with self._engine.begin() as conn:
            result = await conn.execute(
                update(users_table).where(users_table.c.id == user_id).values(**values)
            )
            if result.rowcount == 0:
                raise ValueError(f"User with id {user_id} not found")

            result = await conn.execute(
                select(users_table).where(users_table.c.id == user_id)
            )
            row = result.one()
            return UserMapper.to_domain(row)

    async def delete(self, user_id: str) -> None:
        async with self._engine.begin() as conn:
            await conn.execute(delete(users_table).where(users_table.c.id == user_id))

class InMemoryUserRepository(IUserRepository):
    def __init__(self) -> None:
        self._store: dict[str, UserEntity] = {}

    async def find_by_id(self, user_id: str) -> UserEntity | None:
        return self._store.get(user_id)

    async def find_by_email(self, email: str) -> UserEntity | None:
        return next((u for u in self._store.values() if u.email.value == email), None)

    async def list(
        self,
        filter: ListUsersFilter | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[UserEntity], int]:
        items = list(self._store.values())
        if filter is not None:
            if filter.role is not None:
                items = [u for u in items if u.role == filter.role]
            if filter.search is not None:
                term = filter.search.lower()
                items = [
                    u for u in items
                    if term in u.name.lower() or term in u.email.value.lower()
                ]
        total = len(items)
        start = (page - 1) * limit
        return items[start : start + limit], total

    async def create(self, entity: UserEntity) -> UserEntity:
        self._store[entity.id.value] = entity
        return entity

    async def update(self, entity: UserEntity) -> UserEntity:
        self._store[entity.id.value] = entity
        return entity

    async def delete(self, user_id: str) -> None:
        self._store.pop(user_id, None)