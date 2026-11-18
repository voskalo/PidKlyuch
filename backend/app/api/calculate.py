from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_optional_user
from app.api.schemas_calc import (
    CalculationIn, CalculationOut, CarOriginOut, CompareRulesOut, ExciseKindOut, ExciseKindsOut, ParcelIn, RatesOut,
)
from app.customs.rules import CAR_CURRENT, EXCISE_CURRENT
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


@router.get("/car/origins", response_model=list[CarOriginOut])
def car_origins() -> list[CarOriginOut]:
    """Countries of origin the car form offers, with today's duty for a typical (10%) car."""
    r, today = CAR_CURRENT, date.today()
    pct = lambda x: f"{(x * 100).normalize():f}%".replace(".", ",")
    out = []
    for p in r.preferential_origins.values():
        active = today >= p.valid_from
        out.append(CarOriginOut(key=p.key, label=p.label, badge=pct(p.rate_for(r.duty_rate_other) if active else r.duty_rate_other),
                                hint=(f"{p.proof}" if active else f"пільга діє з {p.valid_from:%d.%m.%Y}")))
    out.append(CarOriginOut(key="other", label="США, Японія, Корея, Китай та інші", badge=pct(r.duty_rate_other),
                            hint="звичайна ставка (країни СОТ); нові бензинові понад 3000 см³ — 5%"))
    out.append(CarOriginOut(key="unproven", label="Походження не підтверджено", badge=pct(r.duty_rate_full),
                            hint="повна ставка (ст. 46 МКУ), також для нових понад 3000 см³"))
    return out


@router.get("/excise/kinds", response_model=ExciseKindsOut)
def excise_kinds() -> ExciseKindsOut:
    """What the excise form needs to render: units, duty-free norms, which extra fields each kind needs."""
    r = EXCISE_CURRENT
    return ExciseKindsOut(
        kinds=[
            ExciseKindOut(key=k.key, label=k.label, group=k.group, unit=k.unit, allowance=k.allowance,
                          allowance_note=k.allowance_note, abv_required=k.abv_required, abv_default=k.abv_default,
                          abv_min=k.abv_min, abv_max=k.abv_max, weight_required=k.weight_required)
            for k in r.kinds.values()
        ],
        allowance_groups_24h=list(r.allowance_groups_24h),
        notes=list(r.notes),
    )


@router.get("/rates", response_model=RatesOut)
def rates(rates: RatesService = Depends(get_rates_service)) -> RatesOut:
    t = rates.get_rates()
    return RatesOut(date=t.date, source=t.source, uah_per_unit=t.uah_per_unit)
