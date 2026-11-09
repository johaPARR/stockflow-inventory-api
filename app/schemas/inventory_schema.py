from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class InventoryBase(BaseModel):
    product_id: int = Field(gt=0)

    quantity: int = Field(
        default=0,
        ge=0,
    )

    min_stock: int = Field(
        default=5,
        ge=0,
    )


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    min_stock: int | None = Field(
        default=None,
        ge=0,
    )


class InventoryResponse(InventoryBase):
    id: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InventoryStockResponse(BaseModel):
    product_id: int
    product_name: str
    sku: str
    quantity: int
    min_stock: int
    is_low_stock: bool