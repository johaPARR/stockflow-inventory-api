
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory_movement import (
    InventoryMovement,
    MovementType,
)
from app.schemas.movement_schema import (
    InventoryEntryCreate,
    InventoryExitCreate,
    InventoryAdjustmentCreate,
)


def create_movement(
    db: Session,
    movement_data: (
        InventoryEntryCreate
        | InventoryExitCreate
        | InventoryAdjustmentCreate
    ),
    movement_type: MovementType,
    previous_quantity: int,
    new_quantity: int,
) -> InventoryMovement:
    movement = InventoryMovement(
        product_id=movement_data.product_id,
        movement_type=movement_type,
        quantity=abs(new_quantity - previous_quantity),
        previous_quantity=previous_quantity,
        new_quantity=new_quantity,
        reason=movement_data.reason,
        reference=movement_data.reference,
        notes=movement_data.notes,
    )

    db.add(movement)
    db.flush()

    return movement


def get_movement_by_id(
    db: Session,
    movement_id: int,
) -> InventoryMovement | None:
    return db.get(InventoryMovement, movement_id)


def get_movements(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[InventoryMovement]:
    statement = (
        select(InventoryMovement)
        .order_by(InventoryMovement.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def get_movements_by_product(
    db: Session,
    product_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[InventoryMovement]:
    statement = (
        select(InventoryMovement)
        .where(InventoryMovement.product_id == product_id)
        .order_by(InventoryMovement.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(statement).all())
