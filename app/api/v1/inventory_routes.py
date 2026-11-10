from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.inventory_schema import InventoryResponse
from app.schemas.movement_schema import (
    InventoryEntryCreate,
    InventoryExitCreate,
    InventoryAdjustmentCreate,
    MovementResponse,
)
from app.services import inventory_service


router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
)


@router.get(
    "",
    response_model=list[InventoryResponse],
)
def get_inventories(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return inventory_service.get_inventories(db, skip, limit)


@router.get(
    "/{product_id}",
    response_model=InventoryResponse,
)
def get_inventory(
    product_id: int,
    db: Session = Depends(get_db),
):
    try:
        return inventory_service.get_inventory(db, product_id)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.post(
    "/entries",
    response_model=MovementResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_entry(
    movement_data: InventoryEntryCreate,
    db: Session = Depends(get_db),
):
    try:
        return inventory_service.register_entry(db, movement_data)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.post(
    "/exits",
    response_model=MovementResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_exit(
    movement_data: InventoryExitCreate,
    db: Session = Depends(get_db),
):
    try:
        return inventory_service.register_exit(db, movement_data)
    except ValueError as error:
        message = str(error)

        error_status = (
            status.HTTP_409_CONFLICT
            if "stock insuficiente" in message.lower()
            else status.HTTP_404_NOT_FOUND
        )

        raise HTTPException(
            status_code=error_status,
            detail=message,
        )


@router.post(
    "/adjustments",
    response_model=MovementResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_adjustment(
    movement_data: InventoryAdjustmentCreate,
    db: Session = Depends(get_db),
):
    try:
        return inventory_service.register_adjustment(
            db,
            movement_data,
        )
    except ValueError as error:
        message = str(error)

        error_status = (
            status.HTTP_409_CONFLICT
            if "diferente" in message.lower()
            else status.HTTP_404_NOT_FOUND
        )

        raise HTTPException(
            status_code=error_status,
            detail=message,
        )