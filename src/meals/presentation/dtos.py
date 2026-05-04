from decimal import Decimal
from pydantic import BaseModel, Field


class CreateMealDto(BaseModel):
    name: str
    description: str | None = None
    price: Decimal = Field(gt=0)
    category: str
    available: bool = True


class UpdateMealDto(BaseModel):
    name: str | None = None
    description: str | None = None
    price: Decimal | None = Field(default=None, gt=0)
    category: str | None = None
    available: bool | None = None
