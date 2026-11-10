from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories import (
    category_repository,
    inventory_repository,
    product_repository,
)
from app.schemas.inventory_schema import InventoryCreate
from app.schemas.product_schema import ProductCreate, ProductUpdate


def create_product(
    db: Session,
    product_data: ProductCreate,
) -> Product:
    existing_product = product_repository.get_product_by_sku(
        db,
        product_data.sku,
    )

    if existing_product:
        raise ValueError("Ya existe un producto con ese SKU")

    category = category_repository.get_category_by_id(
        db,
        product_data.category_id,
    )

    if category is None:
        raise ValueError("La categoría no existe")

    if not category.is_active:
        raise ValueError("No se pueden crear productos en una categoría inactiva")

    try:
        product = product_repository.create_product(
            db,
            product_data,
        )

        inventory_repository.create_inventory(
            db,
            InventoryCreate(
                product_id=product.id,
                quantity=0,
                min_stock=5,
            ),
        )

        db.commit()
        db.refresh(product)

        return product

    except Exception:
        db.rollback()
        raise


def get_product(
    db: Session,
    product_id: int,
) -> Product:
    product = product_repository.get_product_by_id(
        db,
        product_id,
    )

    if product is None:
        raise ValueError("Producto no encontrado")

    return product


def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Product]:
    return product_repository.get_products(
        db,
        skip,
        limit,
    )


def update_product(
    db: Session,
    product_id: int,
    product_data: ProductUpdate,
) -> Product:
    product = get_product(db, product_id)

    update_data = product_data.model_dump(exclude_unset=True)

    required_fields = ["sku", "name", "price", "category_id"]

    for field in required_fields:
        if field in update_data and update_data[field] is None:
            raise ValueError(f"El campo {field} no puede ser nulo")

    if "sku" in update_data:
        existing_product = product_repository.get_product_by_sku(
            db,
            update_data["sku"],
        )

        if existing_product and existing_product.id != product_id:
            raise ValueError("Ya existe un producto con ese SKU")

    if "category_id" in update_data:
        category = category_repository.get_category_by_id(
            db,
            update_data["category_id"],
        )

        if category is None:
            raise ValueError("La categoría no existe")

        if not category.is_active:
            raise ValueError("No se puede asignar un producto a una categoría inactiva")

    try:
        product = product_repository.update_product(
            db,
            product,
            product_data,
        )

        db.commit()
        db.refresh(product)

        return product

    except Exception:
        db.rollback()
        raise