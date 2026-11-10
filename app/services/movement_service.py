from sqlalchemy.orm import Session

from app.models.inventory_movement import InventoryMovement
from app.repositories import movement_repository


def get_movements(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[InventoryMovement]:
    return movement_repository.get_movements(
        db,
        skip,
        limit,
    )


def get_movements_by_product(
    db: Session,
    product_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[InventoryMovement]:
    return movement_repository.get_movements_by_product(
        db,
        product_id,
        skip,
        limit,
    )