"""Unit tests for auth use cases using in-memory repositories."""
import pytest
from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock

from src.auth.application.login import Login, LoginInput
from src.auth.application.register import Register, RegisterInput
from src.auth.domain.errors import InvalidCredentialsError
from src.auth.domain.ports import IJwtAdapter, IPasswordAdapter, TokenPayload
from src.shared.domain.email import Email
from src.shared.domain.id import Id
from src.users.domain.entity import UserEntity
from src.users.domain.errors import UserEmailAlreadyExistsError
from src.users.infrastructure.repository import InMemoryUserRepository
from src.shared.infrastructure.id_generator import IDGenerator
from src.auth.application.refresh import RefreshToken
from src.auth.domain.errors import InvalidRefreshTokenError


def _make_user(user_id: str = "00000000-0000-0000-0000-000000000001", email: str = "test@example.com") -> UserEntity:
    now = datetime.now(UTC)
    return UserEntity(
        id=Id.from_str(user_id),
        name="Test User",
        email=Email.create(email),
        phone=None,
        password_hash="hashed_password",
        role="client",
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def user_repo() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def id_gen() -> IDGenerator:
    return IDGenerator()


@pytest.fixture
def password_adapter():
    mock = AsyncMock(spec=IPasswordAdapter)
    mock.hash = AsyncMock(return_value="hashed_password")
    mock.compare = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def jwt_adapter():
    mock = MagicMock(spec=IJwtAdapter)
    mock.sign = MagicMock(return_value="access_token_value")
    mock.sign_refresh = MagicMock(return_value="refresh_token_value")
    mock.verify_refresh = MagicMock(return_value=TokenPayload(sub="00000000-0000-0000-0000-000000000001", email="test@example.com", role="client"))
    return mock


# ── Register ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_creates_user_and_returns_tokens(user_repo, id_gen, password_adapter, jwt_adapter):
    uc = Register(user_repo, password_adapter, id_gen, jwt_adapter)
    result = await uc.execute(RegisterInput(name="Alice", email="alice@e.com", password="pass123", phone=None))
    assert result.user.name == "Alice"
    assert result.user.email.value == "alice@e.com"
    assert result.tokens.access_token == "access_token_value"
    assert result.tokens.refresh_token == "refresh_token_value"


@pytest.mark.asyncio
async def test_register_raises_email_conflict(user_repo, id_gen, password_adapter, jwt_adapter):
    await user_repo.create(_make_user(email="alice@e.com"))
    uc = Register(user_repo, password_adapter, id_gen, jwt_adapter)
    with pytest.raises(UserEmailAlreadyExistsError):
        await uc.execute(RegisterInput(name="Alice", email="alice@e.com", password="pass123", phone=None))


# ── Login ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_login_returns_user_and_tokens(user_repo, password_adapter, jwt_adapter):
    await user_repo.create(_make_user(email="test@example.com"))
    uc = Login(user_repo, password_adapter, jwt_adapter)
    result = await uc.execute(LoginInput(email="test@example.com", password="correct_pass"))
    assert result.user.email.value == "test@example.com"
    assert result.tokens.access_token == "access_token_value"


@pytest.mark.asyncio
async def test_login_raises_invalid_credentials_for_unknown_email(user_repo, password_adapter, jwt_adapter):
    uc = Login(user_repo, password_adapter, jwt_adapter)
    with pytest.raises(InvalidCredentialsError):
        await uc.execute(LoginInput(email="nobody@example.com", password="pass"))


@pytest.mark.asyncio
async def test_login_raises_invalid_credentials_for_wrong_password(user_repo, password_adapter, jwt_adapter):
    password_adapter.compare = AsyncMock(return_value=False)
    await user_repo.create(_make_user(email="test@example.com"))
    uc = Login(user_repo, password_adapter, jwt_adapter)
    with pytest.raises(InvalidCredentialsError):
        await uc.execute(LoginInput(email="test@example.com", password="wrong_pass"))

# ── Refresh ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_refresh_returns_new_tokens(user_repo, jwt_adapter):
    user = _make_user()
    await user_repo.create(user)
    
    payload = TokenPayload(sub=user.id.value, email=user.email.value, role=user.role)
    uc = RefreshToken(user_repo, jwt_adapter)
    
    result = await uc.execute(payload)
    
    assert result.access_token == "access_token_value"
    assert result.refresh_token == "refresh_token_value"
    jwt_adapter.sign.assert_called_once()
    jwt_adapter.sign_refresh.assert_called_once()


@pytest.mark.asyncio
async def test_refresh_raises_invalid_token_if_user_not_found(user_repo, jwt_adapter):
    payload = TokenPayload(sub="non-existent", email="test@e.com", role="client")
    uc = RefreshToken(user_repo, jwt_adapter)
    
    with pytest.raises(InvalidRefreshTokenError):
        await uc.execute(payload)
