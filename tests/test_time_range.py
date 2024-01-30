import pytest
from pendulum import now, time

from src.warden.time_range import TimeRange


def test_start_equal_end_time():
    with pytest.raises(ValueError):
        TimeRange(now(), now())


def test_contains_within_day():
    tested_range = TimeRange(time(8), time(19))

    assert time(12) in tested_range
    assert time(1) not in tested_range
    assert time(20) not in tested_range


def test_contains_over_midnight():
    tested_range = TimeRange(time(19), time(8))

    assert time(12) not in tested_range
    assert time(1) in tested_range
    assert time(20) in tested_range
