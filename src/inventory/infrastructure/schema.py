from sqlalchemy import Column, DateTime, Numeric, String, Table, func
from sqlalchemy.dialects.postgresql import UUID

from src.shared.infrastructure.metadata import metadata

items_table = Table(
    "inventory_items",
    metadata,
    Column("id", UUID(as_uuid=False), primary_key=True),
    Column("name", String, nullable=False),
    Column("quantity", Numeric(precision=14, scale=4), nullable=False),
    Column("unit", String(8), nullable=False, index=True),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)
