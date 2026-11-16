"""Persistence of calculations: per-user history and aggregate usage stats for the report."""
from collections import defaultdict

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models import Calculation, User


class HistoryService:
    def __init__(self, db: Session):
        self.db = db

    def record(self, user: User | None, delivery_type: str, input_: dict, result: dict) -> Calculation:
        calc = Calculation(
            user_id=user.id if user else None, delivery_type=delivery_type, input=input_, result=result
        )
        self.db.add(calc)
        self.db.commit()
        self.db.refresh(calc)
        return calc

    def list_for(self, user: User, limit: int = 100) -> list[Calculation]:
        stmt = (
            select(Calculation)
            .where(Calculation.user_id == user.id)
            .order_by(Calculation.created_at.desc(), Calculation.id.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt))

    def delete_for(self, user: User, calc_id: int) -> bool:
        res = self.db.execute(
            delete(Calculation).where(Calculation.id == calc_id, Calculation.user_id == user.id)
        )
        self.db.commit()
        return res.rowcount > 0

    def stats(self) -> dict[str, int]:
        users = self.db.scalar(select(func.count(User.id))) or 0
        total = self.db.scalar(select(func.count(Calculation.id))) or 0
        rows = self.db.execute(
            select(Calculation.user_id, Calculation.created_at).where(Calculation.user_id.is_not(None))
        ).all()
        days_by_user: dict[int, set] = defaultdict(set)
        for user_id, created_at in rows:
            days_by_user[user_id].add(created_at.date())
        return {
            "users": users,
            "calculations": total,
            "calculations_by_signed_in": len(rows),
            "returning_users": sum(1 for days in days_by_user.values() if len(days) >= 2),
        }
