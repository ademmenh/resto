from decimal import Decimal
from pydantic import BaseModel, Field
from typing import Literal

UnitLiteral = Literal["kg", "l", "m3", "g"]


class CreateItemDto(BaseModel):
    name: str
    quantity: Decimal = Field(ge=Decimal("0"), description="Initial stock (>= 0)")
    unit: UnitLiteral


class UpdateItemDto(BaseModel):
    name: str | None = None
    unit: UnitLiteral | None = None


class QuantityChangeDto(BaseModel):
    amount: Decimal = Field(gt=Decimal("0"), description="Amount to add or remove (> 0)")
