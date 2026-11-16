from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.services.history_service import HistoryService

router = APIRouter(tags=["history"])


class HistoryItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    delivery_type: str
    input: dict
    result: dict


class StatsOut(BaseModel):
    users: int
    calculations: int
    calculations_by_signed_in: int
    returning_users: int


@router.get("/history", response_model=list[HistoryItemOut])
def list_history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return HistoryService(db).list_for(user)


@router.delete("/history/{calc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_history_item(calc_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not HistoryService(db).delete_for(user, calc_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Calculation not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/stats", response_model=StatsOut)
def stats(db: Session = Depends(get_db)) -> dict[str, int]:
    return HistoryService(db).stats()
