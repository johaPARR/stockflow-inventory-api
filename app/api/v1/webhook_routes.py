
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.webhook_schema import (
    ConfirmedOrderCreate,
    ConfirmedOrderResponse,
)
from app.services import webhook_service


router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post(
    "/orders/confirmed",
    response_model=ConfirmedOrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def confirm_order(
    order_data: ConfirmedOrderCreate,
    db: Session = Depends(get_db),
):
    try:
        movements = webhook_service.process_confirmed_order(
            db,
            order_data,
        )

        return {
            "order_id": order_data.order_id,
            "status": "processed",
            "processed_items": len(movements),
            "movements": movements,
        }

    except webhook_service.OrderAlreadyProcessedError as exc:
        raise HTTPException(status_code=409, detail=str(exc))

    except webhook_service.ProductNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    except webhook_service.InventoryNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    except webhook_service.InactiveProductError as exc:
        raise HTTPException(status_code=409, detail=str(exc))

    except webhook_service.InsufficientStockError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
