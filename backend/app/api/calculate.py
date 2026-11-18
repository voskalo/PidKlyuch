from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_optional_user
from app.api.schemas_calc import CalculationIn, CalculationOut, CompareRulesOut, ParcelIn, RatesOut
from app.core.database import get_db
from app.models import User
from app.services.calculation_service import CalculationService
from app.services.history_service import HistoryService
from app.services.rates_service import RatesService, get_rates_service

router = APIRouter(tags=["calculate"])


@router.post("/calculate", response_model=CalculationOut)
def calculate(
    body: CalculationIn,
    rates: RatesService = Depends(get_rates_service),
    user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
) -> CalculationOut:
    result = CalculationService(rates.get_rates()).calculate(body)
    calc = HistoryService(db).record(
        user, body.delivery_type, body.model_dump(mode="json"), result.model_dump(mode="json")
    )
    if user is not None:
        result.calculation_id = calc.id
    return result


@router.post("/calculate/compare-rules", response_model=CompareRulesOut)
def compare_rules(body: ParcelIn, rates: RatesService = Depends(get_rates_service)) -> CompareRulesOut:
    service = CalculationService(rates.get_rates())
    return CompareRulesOut(
        current=service.calculate(body.model_copy(update={"rules": "current"})),
        july_2027=service.calculate(body.model_copy(update={"rules": "july_2027"})),
    )


@router.get("/rates", response_model=RatesOut)
def rates(rates: RatesService = Depends(get_rates_service)) -> RatesOut:
    t = rates.get_rates()
    return RatesOut(date=t.date, source=t.source, uah_per_unit=t.uah_per_unit)
