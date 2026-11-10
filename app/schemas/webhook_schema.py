
from pydantic import BaseModel, Field, field_validator

from app.schemas.movement_schema import MovementResponse


class ConfirmedOrderItem(BaseModel):
    sku: str = Field(min_length=2, max_length=50)
    quantity: int = Field(gt=0)


class ConfirmedOrderCreate(BaseModel):
    order_id: str = Field(min_length=1, max_length=100)
    items: list[ConfirmedOrderItem] = Field(min_length=1)

    @field_validator("items")
    @classmethod
    def validate_unique_skus(cls, items):
        skus = [item.sku for item in items]

        if len(skus) != len(set(skus)):
            raise ValueError(
                "La orden no puede contener SKU duplicados"
            )

        return items


class ConfirmedOrderResponse(BaseModel):
    order_id: str
    status: str
    processed_items: int
    movements: list[MovementResponse]
