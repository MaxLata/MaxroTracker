from __future__ import annotations

from collections import OrderedDict
from datetime import date, timedelta

from maxro_tracker.domain.models import WeightLog


def calculate_rolling_average(
    logs: list[WeightLog],
    days: int = 7,
    as_of: date | None = None,
) -> float | None:
    if days <= 0:
        raise ValueError("days must be positive")
    if not logs:
        return None

    latest_by_date = _latest_weight_by_date(logs)
    end_date = as_of or max(latest_by_date)
    start_date = end_date - timedelta(days=days - 1)

    weights = [
        weight
        for log_date, weight in latest_by_date.items()
        if start_date <= log_date <= end_date
    ]

    if len(weights) < days:
        return None
    return sum(weights) / len(weights)


def _latest_weight_by_date(logs: list[WeightLog]) -> OrderedDict[date, float]:
    ordered_logs = sorted(
        logs,
        key=lambda log: (log.log_date, log.updated_at or log.created_at),
    )
    latest_by_date: OrderedDict[date, float] = OrderedDict()
    for log in ordered_logs:
        latest_by_date[log.log_date] = log.weight_lbs
    return latest_by_date

