"""In-memory implementation of IUserRepository for unit tests."""
from src.users.domain.entity import UserEntity
from src.users.domain.ports import IUserRepository, ListUsersFilter


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
