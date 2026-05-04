from pydantic import BaseModel, Field
from typing import Literal

SaleStatusEnum = Literal["pending", "completed", "cancelled"]


class CreateSaleDto(BaseModel):
    client_id: str
    meal_id: str
    quantity: int = Field(gt=0)


class UpdateSaleDto(BaseModel):
    status: SaleStatusEnum
