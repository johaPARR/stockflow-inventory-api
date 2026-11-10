from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.movement_schema import MovementResponse
from app.services import movement_service


router = APIRouter(
    prefix="/movements",
    tags=["Movements"],
)


@router.get(
    "",
    response_model=list[MovementResponse],
)
def get_movements(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return movement_service.get_movements(
        db,
        skip,
        limit,
    )


@router.get(
    "/product/{product_id}",
    response_model=list[MovementResponse],
)
def get_movements_by_product(
    product_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return movement_service.get_movements_by_product(
        db,
        product_id,
        skip,
        limit,
    )