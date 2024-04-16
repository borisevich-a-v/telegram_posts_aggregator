from unittest.mock import Mock

import pytest
from pendulum import DateTime, Timezone

from bot.warden.warden import (
    NotAllowed,
    Rule8to11EveryDay,
    Rule11to12Workdays,
    RuleLimitAccessInProductiveHours,
    Warden,
)


def get_datetime_with_specific_time(hour, minute=0, second=0) -> DateTime:
    return DateTime(year=2024, month=1, day=1, hour=hour, minute=minute, second=second, tzinfo=Timezone("UTC"))


def test_warden_rules_list():
    expected_rules = {
        Rule8to11EveryDay,
        Rule11to12Workdays,
        RuleLimitAccessInProductiveHours,
    }
    assert expected_rules == set(Warden.RULES)


def test_all_rules_run():
    warden = Warden()
    mocked_rules = [Mock(), Mock(), Mock()]
    warden._rules = mocked_rules

    warden.check_allowance()

    mocked_rules[0].check.assert_called_once()
    mocked_rules[1].check.assert_called_once()
    mocked_rules[2].check.assert_called_once()


def test_rule_raised_an_exception():
    warden = Warden()
    rule_with_exception = Mock()
    rule_with_exception.check = Mock(side_effect=NotAllowed)
    mocked_rules = [Mock(), rule_with_exception, Mock()]
    warden._rules = mocked_rules

    with pytest.raises(NotAllowed):
        warden.check_allowance()


def test_rule_8_to_11_every_day_positive():
    """Check for Rule8to11EveryDay"""
    rule = Rule8to11EveryDay()
    rule.check(get_datetime_with_specific_time(hour=11, second=1))
    rule.check(get_datetime_with_specific_time(hour=12))
    rule.check(get_datetime_with_specific_time(hour=23))
    rule.check(get_datetime_with_specific_time(hour=7, minute=59))


def test_rule_8_to_11_every_day_negative():
    """Check for Rule8to11EveryDay"""
    rule = Rule8to11EveryDay()
    with pytest.raises(NotAllowed):
        rule.check(get_datetime_with_specific_time(hour=8, second=1))

    with pytest.raises(NotAllowed):
        rule.check(get_datetime_with_specific_time(hour=10, minute=59))


def test_rule_11_to_12_workdays_positive_workday():
    """Check for Rule11to12Workdays"""
    rule = Rule11to12Workdays()
    rule.check(DateTime(year=2024, month=4, day=11, hour=12, second=1))
    rule.check(DateTime(year=2024, month=4, day=11, hour=23))
    rule.check(DateTime(year=2024, month=4, day=11, hour=10, second=59))


@pytest.mark.parametrize("day", [13, 14])  # sat and sun
def test_rule_11_to_12_workdays_positive_weekend(day):
    """Check for Rule11to12Workdays"""
    rule = Rule11to12Workdays()
    rule.check(DateTime(year=2024, month=4, day=day, hour=11, minute=30))


@pytest.mark.parametrize("day", [8, 9, 10, 11, 12])  # mon-fri
def test_rule_11_to_12_workdays_negative_workdays(day):
    """Check for Rule11to12Workdays"""
    rule = Rule11to12Workdays()
    with pytest.raises(NotAllowed):
        rule.check(DateTime(year=2024, month=4, day=day, hour=11, minute=30))


def test_rule_11_to_12_workdays_negative():
    """Check for Rule11to12Workdays"""
    rule = Rule11to12Workdays()
    with pytest.raises(NotAllowed):
        rule.check(DateTime(year=2024, month=4, day=11, hour=11, minute=1))

    with pytest.raises(NotAllowed):
        rule.check(DateTime(year=2024, month=4, day=11, hour=11, minute=59))


def test_rule_rule_limit_access_in_working_hours_few_access():
    """Check for RuleLimitAccessInProductiveHours"""
    rule = RuleLimitAccessInProductiveHours()
    allowed_posts_number = 20
    for i in range(allowed_posts_number):
        rule.check(get_datetime_with_specific_time(hour=12, minute=i + 1))


def test_rule_rule_limit_access_in_working_hours_big_delay():
    """Check for RuleLimitAccessInProductiveHours"""
    rule = RuleLimitAccessInProductiveHours()
    allowed_posts_number = 20
    time_period_minutes = 30

    for i in range(allowed_posts_number):
        rule.check(get_datetime_with_specific_time(hour=12, second=i))

    for i in range(allowed_posts_number):
        rule.check(
            get_datetime_with_specific_time(
                hour=12, minute=time_period_minutes + 20, second=i + len(rule.last_access_times)
            )
        )


def test_rule_rule_limit_access_in_working_hours_several_small_delays():
    """Check for RuleLimitAccessInProductiveHours"""
    rule = RuleLimitAccessInProductiveHours()
    allowed_posts_number = 20
    time_period_minutes = 30

    for i in range(allowed_posts_number // 2):
        rule.check(get_datetime_with_specific_time(hour=12, second=i))

    for i in range(allowed_posts_number // 2):
        rule.check(get_datetime_with_specific_time(hour=12, minute=time_period_minutes // 2 + 1, second=i + 1))

    for i in range(allowed_posts_number // 2):
        rule.check(get_datetime_with_specific_time(hour=12, minute=time_period_minutes, second=i + 2))


def test_rule_rule_limit_access_in_working_hours_negative():
    """Check for RuleLimitAccessInProductiveHours"""
    rule = RuleLimitAccessInProductiveHours()
    allowed_posts_number = 20
    with pytest.raises(NotAllowed):
        for i in range(allowed_posts_number + 1):
            rule.check(get_datetime_with_specific_time(hour=12, second=i + 1))
