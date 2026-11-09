from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.inventory_movement import MovementType


class MovementBase(BaseModel):
    product_id: int = Field(gt=0)

    quantity: int = Field(
        gt=0,
        description="Cantidad del movimiento",
    )

    reason: str = Field(
        min_length=3,
        max_length=255,
    )

    reference: str | None = Field(
        default=None,
        max_length=100,
    )

    notes: str | None = None


class InventoryEntryCreate(MovementBase):
    pass


class InventoryExitCreate(MovementBase):
    pass


class InventoryAdjustmentCreate(BaseModel):
    product_id: int = Field(gt=0)

    new_quantity: int = Field(
        ge=0,
        description="Nueva cantidad total de stock",
    )

    reason: str = Field(
        min_length=3,
        max_length=255,
    )

    reference: str | None = Field(
        default=None,
        max_length=100,
    )

    notes: str | None = None


class MovementResponse(BaseModel):
    id: int
    product_id: int
    movement_type: MovementType
    quantity: int
    previous_quantity: int
    new_quantity: int
    reason: str
    reference: str | None
    notes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)