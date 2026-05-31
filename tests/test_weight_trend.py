from datetime import date, datetime

import pytest

from maxro_tracker.domain.models import WeightLog
from maxro_tracker.services.weight_trend import calculate_rolling_average


def test_calculate_rolling_average_returns_seven_day_average() -> None:
    logs = [
        WeightLog(log_date=date(2026, 5, day), weight_lbs=150 + day)
        for day in range(1, 8)
    ]

    assert calculate_rolling_average(logs, as_of=date(2026, 5, 7)) == 154


def test_calculate_rolling_average_returns_none_with_fewer_than_days() -> None:
    logs = [
        WeightLog(log_date=date(2026, 5, day), weight_lbs=150 + day)
        for day in range(1, 6)
    ]

    assert calculate_rolling_average(logs, as_of=date(2026, 5, 7)) is None


def test_calculate_rolling_average_uses_latest_entry_for_duplicate_date() -> None:
    logs = [
        WeightLog(log_date=date(2026, 5, 1), weight_lbs=151, updated_at=datetime(2026, 5, 1, 7)),
        WeightLog(log_date=date(2026, 5, 1), weight_lbs=152, updated_at=datetime(2026, 5, 1, 8)),
        WeightLog(log_date=date(2026, 5, 2), weight_lbs=153),
    ]

    assert calculate_rolling_average(logs, days=2, as_of=date(2026, 5, 2)) == 152.5


def test_calculate_rolling_average_rejects_invalid_window() -> None:
    with pytest.raises(ValueError, match="days must be positive"):
        calculate_rolling_average([], days=0)

