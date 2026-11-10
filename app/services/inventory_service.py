from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.inventory_movement import MovementType, InventoryMovement
from app.repositories import inventory_repository, movement_repository
from app.schemas.movement_schema import (
    InventoryEntryCreate,
    InventoryExitCreate,
    InventoryAdjustmentCreate,
)


def get_inventory(
    db: Session,
    product_id: int,
) -> Inventory:
    inventory = inventory_repository.get_inventory_by_product_id(
        db,
        product_id,
    )

    if inventory is None:
        raise ValueError("No existe un registro de inventario para este producto")

    return inventory


def get_inventories(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Inventory]:
    return inventory_repository.get_inventories(
        db,
        skip,
        limit,
    )


def register_entry(
    db: Session,
    movement_data: InventoryEntryCreate,
) -> InventoryMovement:
    inventory = inventory_repository.get_inventory_for_update(
        db,
        movement_data.product_id,
    )

    if inventory is None:
        raise ValueError("No existe un registro de inventario para este producto")

    previous_quantity = inventory.quantity
    new_quantity = previous_quantity + movement_data.quantity

    try:
        inventory.quantity = new_quantity

        inventory_repository.update_inventory(db, inventory)

        movement = movement_repository.create_movement(
            db,
            movement_data,
            MovementType.ENTRY,
            previous_quantity,
            new_quantity,
        )

        db.commit()
        db.refresh(movement)

        return movement

    except Exception:
        db.rollback()
        raise


def register_exit(
    db: Session,
    movement_data: InventoryExitCreate,
) -> InventoryMovement:
    inventory = inventory_repository.get_inventory_for_update(
        db,
        movement_data.product_id,
    )

    if inventory is None:
        raise ValueError("No existe un registro de inventario para este producto")

    previous_quantity = inventory.quantity

    if movement_data.quantity > previous_quantity:
        raise ValueError("Stock insuficiente para realizar la salida")

    new_quantity = previous_quantity - movement_data.quantity

    try:
        inventory.quantity = new_quantity

        inventory_repository.update_inventory(db, inventory)

        movement = movement_repository.create_movement(
            db,
            movement_data,
            MovementType.EXIT,
            previous_quantity,
            new_quantity,
        )

        db.commit()
        db.refresh(movement)

        return movement

    except Exception:
        db.rollback()
        raise


def register_adjustment(
    db: Session,
    movement_data: InventoryAdjustmentCreate,
) -> InventoryMovement:
    inventory = inventory_repository.get_inventory_for_update(
        db,
        movement_data.product_id,
    )

    if inventory is None:
        raise ValueError("No existe un registro de inventario para este producto")

    previous_quantity = inventory.quantity
    new_quantity = movement_data.new_quantity

    if previous_quantity == new_quantity:
        raise ValueError("El nuevo stock debe ser diferente al stock actual")

    try:
        inventory.quantity = new_quantity

        inventory_repository.update_inventory(db, inventory)

        movement = movement_repository.create_movement(
            db,
            movement_data,
            MovementType.ADJUSTMENT,
            previous_quantity,
            new_quantity,
        )

        db.commit()
        db.refresh(movement)

        return movement

    except Exception:
        db.rollback()
        raise