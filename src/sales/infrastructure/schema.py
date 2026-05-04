from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Table, func
from sqlalchemy.dialects.postgresql import UUID

from src.shared.infrastructure.metadata import metadata

sales_table = Table(
    "sales",
    metadata,
    Column("id", UUID(as_uuid=False), primary_key=True),
    Column("client_id", UUID(as_uuid=False), ForeignKey("users.id"), nullable=False, index=True),
    Column("meal_id", UUID(as_uuid=False), ForeignKey("meals.id"), nullable=False, index=True),
    Column("quantity", Integer, nullable=False),
    Column("unit_price", Numeric(precision=10, scale=2), nullable=False),
    Column("total_price", Numeric(precision=10, scale=2), nullable=False),
    Column("status", String, nullable=False, default="pending", index=True),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)
