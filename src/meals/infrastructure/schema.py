from sqlalchemy import Boolean, Column, DateTime, Numeric, String, Table, func
from sqlalchemy.dialects.postgresql import UUID

from src.shared.infrastructure.metadata import metadata

meals_table = Table(
    "meals",
    metadata,
    Column("id", UUID(as_uuid=False), primary_key=True),
    Column("name", String, nullable=False),
    Column("description", String, nullable=True),
    Column("price", Numeric(precision=10, scale=2), nullable=False),
    Column("category", String, nullable=False, index=True),
    Column("available", Boolean, nullable=False, default=True),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)
