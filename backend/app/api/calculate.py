from fastapi import APIRouter, Body, Depends

from app.api.schemas_calc import CalculationIn, CalculationOut, CompareRulesOut, ParcelIn, RatesOut
from app.services.calculation_service import CalculationService
from app.services.rates_service import RatesService, get_rates_service

router = APIRouter(tags=["calculate"])


@router.post("/calculate", response_model=CalculationOut)
def calculate(
    body: CalculationIn = Body(...),
    rates: RatesService = Depends(get_rates_service),
) -> CalculationOut:
    return CalculationService(rates.get_rates()).calculate(body)


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
