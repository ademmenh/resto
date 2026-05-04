"""Unit tests for users use cases (using InMemoryUserRepository)."""
import pytest
from datetime import datetime, UTC
from unittest.mock import AsyncMock

from src.shared.domain.email import Email
from src.shared.domain.id import Id
from src.users.application.get_user import GetUser, GetUserInput
from src.users.application.list_users import ListUsers, ListUsersInput
from src.users.application.update_user import UpdateUser, UpdateUserInput
from src.users.application.delete_user import DeleteUser, DeleteUserInput
from src.users.domain.entity import UserEntity
from src.users.domain.errors import UserEmailAlreadyExistsError, UserNotFoundError
from src.users.infrastructure.in_memory_repository import InMemoryUserRepository


def _make_user(user_id: str, name: str = "Alice", email: str = "alice@example.com", role: str = "client") -> UserEntity:
    now = datetime.now(UTC)
    return UserEntity(
        id=Id.from_str(user_id),
        name=name,
        email=Email.create(email),
        phone=None,
        password_hash="hashed",
        role=role,  # type: ignore[arg-type]
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def repo() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def password_adapter():
    mock = AsyncMock()
    mock.hash = AsyncMock(return_value="new_hash")
    mock.compare = AsyncMock(return_value=True)
    return mock


# ── GetUser ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_user_returns_entity(repo):
    user = _make_user("00000000-0000-0000-0000-000000000001")
    await repo.create(user)
    result = await GetUser(repo).execute(GetUserInput(user_id=user.id.value))
    assert result.id == user.id


@pytest.mark.asyncio
async def test_get_user_raises_not_found(repo):
    with pytest.raises(UserNotFoundError):
        await GetUser(repo).execute(GetUserInput(user_id="00000000-0000-0000-0000-000000000099"))


# ── ListUsers ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_users_returns_all(repo):
    await repo.create(_make_user("00000000-0000-0000-0000-000000000001", "Alice", "a@e.com", "client"))
    await repo.create(_make_user("00000000-0000-0000-0000-000000000002", "Bob", "b@e.com", "admin"))
    users, total = await ListUsers(repo).execute(ListUsersInput())
    assert total == 2


@pytest.mark.asyncio
async def test_list_users_filter_by_role(repo):
    await repo.create(_make_user("00000000-0000-0000-0000-000000000001", "Alice", "a@e.com", "client"))
    await repo.create(_make_user("00000000-0000-0000-0000-000000000002", "Bob", "b@e.com", "admin"))
    users, total = await ListUsers(repo).execute(ListUsersInput(role="admin"))
    assert total == 1
    assert users[0].name == "Bob"


@pytest.mark.asyncio
async def test_list_users_filter_by_search(repo):
    await repo.create(_make_user("00000000-0000-0000-0000-000000000001", "Alice Smith", "alice@e.com"))
    await repo.create(_make_user("00000000-0000-0000-0000-000000000002", "Bob Jones", "bob@e.com"))
    users, total = await ListUsers(repo).execute(ListUsersInput(search="alice"))
    assert total == 1
    assert users[0].name == "Alice Smith"


# ── UpdateUser ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_user_changes_name(repo, password_adapter):
    user = _make_user("00000000-0000-0000-0000-000000000001")
    await repo.create(user)
    result = await UpdateUser(repo, password_adapter).execute(
        UpdateUserInput(user_id=user.id.value, name="New Name")
    )
    assert result.name == "New Name"


@pytest.mark.asyncio
async def test_update_user_raises_not_found(repo, password_adapter):
    with pytest.raises(UserNotFoundError):
        await UpdateUser(repo, password_adapter).execute(
            UpdateUserInput(user_id="00000000-0000-0000-0000-000000000099", name="X")
        )


@pytest.mark.asyncio
async def test_update_user_raises_email_conflict(repo, password_adapter):
    await repo.create(_make_user("00000000-0000-0000-0000-000000000001", email="user1@e.com"))
    await repo.create(_make_user("00000000-0000-0000-0000-000000000002", email="user2@e.com"))
    with pytest.raises(UserEmailAlreadyExistsError):
        await UpdateUser(repo, password_adapter).execute(
            UpdateUserInput(user_id="00000000-0000-0000-0000-000000000001", email="user2@e.com")
        )


@pytest.mark.asyncio
async def test_update_user_hashes_password(repo, password_adapter):
    user = _make_user("00000000-0000-0000-0000-000000000001")
    await repo.create(user)
    result = await UpdateUser(repo, password_adapter).execute(
        UpdateUserInput(user_id=user.id.value, password="newpassword")
    )
    assert result.password_hash == "new_hash"


# ── DeleteUser ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delete_user_removes_entity(repo):
    user = _make_user("00000000-0000-0000-0000-000000000001")
    await repo.create(user)
    await DeleteUser(repo).execute(DeleteUserInput(user_id=user.id.value))
    assert await repo.find_by_id(user.id.value) is None


@pytest.mark.asyncio
async def test_delete_user_raises_not_found(repo):
    with pytest.raises(UserNotFoundError):
        await DeleteUser(repo).execute(DeleteUserInput(user_id="00000000-0000-0000-0000-000000000099"))
