
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.product import Product
from app.schemas.inventory_schema import InventoryCreate


def create_inventory(
    db: Session,
    inventory_data: InventoryCreate,
) -> Inventory:
    inventory = Inventory(**inventory_data.model_dump())

    db.add(inventory)
    db.flush()

    return inventory


def get_inventory_by_id(
    db: Session,
    inventory_id: int,
) -> Inventory | None:
    return db.get(Inventory, inventory_id)


def get_inventory_by_product_id(
    db: Session,
    product_id: int,
) -> Inventory | None:
    statement = select(Inventory).where(
        Inventory.product_id == product_id
    )

    return db.scalar(statement)


def get_inventory_for_update(
    db: Session,
    product_id: int,
) -> Inventory | None:
    statement = (
        select(Inventory)
        .where(Inventory.product_id == product_id)
        .with_for_update()
    )

    return db.scalar(statement)


def get_inventories(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Inventory]:
    statement = (
        select(Inventory)
        .order_by(Inventory.id)
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def get_inventory_with_product(
    db: Session,
    product_id: int,
) -> tuple[Inventory, Product] | None:
    statement = (
        select(Inventory, Product)
        .join(Product, Inventory.product_id == Product.id)
        .where(Inventory.product_id == product_id)
    )

    result = db.execute(statement).first()

    if result is None:
        return None

    return result


def update_inventory(
    db: Session,
    inventory: Inventory,
) -> Inventory:
    db.flush()

    return inventory


    