"""Integration tests for UserRepository against the in-memory SQLite engine."""
import pytest
from datetime import datetime, UTC
from uuid import uuid4

from src.shared.domain.email import Email
from src.shared.domain.id import Id
from src.users.domain.entity import UserEntity
from src.users.infrastructure.repository import UserRepository
from src.users.domain.ports import ListUsersFilter


def _user(email: str = None, name: str = "Test", role: str = "client") -> UserEntity:
    now = datetime.now(UTC)
    uid = str(uuid4())
    return UserEntity(
        id=Id.from_str(uid),
        name=name,
        email=Email.create(email or f"user-{uid[:8]}@test.com"),
        phone=None,
        password_hash="hashed",
        role=role,  # type: ignore[arg-type]
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_user_repo_create_and_find_by_id(engine):
    repo = UserRepository(engine)
    user = await repo.create(_user())
    found = await repo.find_by_id(user.id.value)
    assert found is not None
    assert found.name == "Test"


@pytest.mark.asyncio
async def test_user_repo_find_by_email(engine):
    repo = UserRepository(engine)
    uid = str(uuid4())
    email = f"unique-{uid[:8]}@find.com"
    await repo.create(_user(email=email))
    found = await repo.find_by_email(email)
    assert found is not None
    assert found.email.value == email


@pytest.mark.asyncio
async def test_user_repo_find_by_id_returns_none(engine):
    repo = UserRepository(engine)
    result = await repo.find_by_id("00000000-0000-0000-0000-000000000000")
    assert result is None


@pytest.mark.asyncio
async def test_user_repo_list_contains_created_users(engine):
    repo = UserRepository(engine)
    uid = str(uuid4())[:8]
    unique_prefix = f"UniqueListUser{uid}"
    u1 = await repo.create(_user(name=f"{unique_prefix}A"))
    u2 = await repo.create(_user(name=f"{unique_prefix}B"))
    # Use search to scope results to what we inserted
    users, total = await repo.list(ListUsersFilter(search=unique_prefix))
    names = [u.name for u in users]
    assert f"{unique_prefix}A" in names
    assert f"{unique_prefix}B" in names
    assert total >= 2


@pytest.mark.asyncio
async def test_user_repo_list_filter_by_role(engine):
    repo = UserRepository(engine)
    uid = str(uuid4())
    await repo.create(_user(email=f"adminrole-{uid[:8]}@test.com", role="admin"))
    admins, _ = await repo.list(ListUsersFilter(role="admin"))
    assert all(u.role == "admin" for u in admins)
    assert len(admins) >= 1


@pytest.mark.asyncio
async def test_user_repo_list_filter_by_search(engine):
    repo = UserRepository(engine)
    uid = str(uuid4())
    unique_name = f"ZzUniqueSrch{uid[:8]}"
    await repo.create(_user(name=unique_name))
    users, _ = await repo.list(ListUsersFilter(search=unique_name[:12]))
    assert len(users) >= 1
    assert any(unique_name in u.name for u in users)


@pytest.mark.asyncio
async def test_user_repo_update(engine):
    repo = UserRepository(engine)
    user = await repo.create(_user(name="OrigName"))
    from dataclasses import replace
    updated = replace(user, name="UpdatedName")
    result = await repo.update(updated)
    assert result.name == "UpdatedName"


@pytest.mark.asyncio
async def test_user_repo_delete(engine):
    repo = UserRepository(engine)
    user = await repo.create(_user())
    await repo.delete(user.id.value)
    assert await repo.find_by_id(user.id.value) is None


@pytest.mark.asyncio
async def test_user_repo_list_pagination(engine):
    repo = UserRepository(engine)
    for _ in range(5):
        await repo.create(_user())
    page1, total = await repo.list(page=1, limit=2)
    assert len(page1) <= 2
    assert total >= 5
