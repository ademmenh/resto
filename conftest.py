import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine

from src.app import create_app
from src.config.domain.interface import IConfig
from src.shared.infrastructure.metadata import metadata

# Ensure all schemas are imported so tables are registered in metadata
import src.inventory.infrastructure.schema  # noqa: F401
import src.meals.infrastructure.schema  # noqa: F401
import src.sales.infrastructure.schema  # noqa: F401
import src.users.infrastructure.schema  # noqa: F401


class TestConfig(IConfig):
    @property
    def env(self) -> str: return "test"
    @property
    def app_name(self) -> str: return "resto-test"
    @property
    def api_version(self) -> str: return "1"
    @property
    def port(self) -> int: return 8000
    @property
    def nginx_port(self) -> int: return 443
    @property
    def db_host(self) -> str: return "localhost"
    @property
    def db_port(self) -> int: return 5432
    @property
    def db_user(self) -> str: return "postgres"
    @property
    def db_password(self) -> str: return "postgres"
    @property
    def db_name(self) -> str: return "test_waslini"
    @property
    def logs_dirname(self) -> str: return "logs"
    @property
    def retention_days(self) -> int: return 30
    @property
    def jwt_access_token_secret(self) -> str: return "test-secret"
    @property
    def jwt_refresh_token_secret(self) -> str: return "test-refresh-secret"
    @property
    def jwt_access_token_expiry(self) -> int: return 3600
    @property
    def jwt_refresh_token_expiry(self) -> int: return 604800
    @property
    def jwt_algo(self) -> str: return "HS256"
    @property
    def cookies_secure(self) -> bool: return False
    @property
    def cookies_same_site(self) -> str: return "lax"
    @property
    def database_url(self) -> str: return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    @property
    def async_database_url(self) -> str: return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    @property
    def jwt_secret(self) -> str: return "test-secret"
    @property
    def debug(self) -> bool: return True
    @property
    def cors_origins(self) -> list[str]: return ["*"]
    @property
    def cors_credentials(self) -> bool: return True


@pytest.fixture(scope="session")
def config() -> IConfig:
    return TestConfig()


@pytest_asyncio.fixture(scope="session")
async def engine(config):
    engine = create_async_engine(config.async_database_url)

    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def client(config, engine):
    from src.config.infrastructure.database_adapter import DatabaseAdapter
    from unittest.mock import patch

    async def _noop_create_tables(self):
        pass

    with patch.object(DatabaseAdapter, "__init__", lambda s, c: None), \
         patch.object(DatabaseAdapter, "engine", engine), \
         patch.object(DatabaseAdapter, "create_tables", _noop_create_tables):
        app = create_app(config)
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as ac:
            yield ac
