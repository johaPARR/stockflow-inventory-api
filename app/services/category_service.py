
from sqlalchemy.orm import Session

from app.models.category import Category
from app.repositories import category_repository
from app.schemas.category_schema import CategoryCreate, CategoryUpdate


def create_category(
    db: Session,
    category_data: CategoryCreate,
) -> Category:
    existing_category = category_repository.get_category_by_name(
        db,
        category_data.name,
    )

    if existing_category:
        raise ValueError("Ya existe una categoría con ese nombre")

    try:
        category = category_repository.create_category(
            db,
            category_data,
        )

        db.commit()
        db.refresh(category)

        return category

    except Exception:
        db.rollback()
        raise


def get_category(
    db: Session,
    category_id: int,
) -> Category:
    category = category_repository.get_category_by_id(
        db,
        category_id,
    )

    if category is None:
        raise ValueError("Categoría no encontrada")

    return category


def get_categories(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Category]:
    return category_repository.get_categories(
        db,
        skip,
        limit,
    )


def update_category(
    db: Session,
    category_id: int,
    category_data: CategoryUpdate,
) -> Category:
    category = get_category(db, category_id)

    update_data = category_data.model_dump(exclude_unset=True)

    # Validar que el nombre no sea nulo.
    if "name" in update_data and update_data["name"] is None:
        raise ValueError(
            "El nombre de la categoría no puede ser nulo"
        )

    # Validar que no exista otra categoría con el mismo nombre.
    if "name" in update_data:
        existing_category = category_repository.get_category_by_name(
            db,
            update_data["name"],
        )

        if existing_category and existing_category.id != category_id:
            raise ValueError("Ya existe una categoría con ese nombre")

    try:
        category = category_repository.update_category(
            db,
            category,
            category_data,
        )

        db.commit()
        db.refresh(category)

        return category

    except Exception:
        db.rollback()
        raise
