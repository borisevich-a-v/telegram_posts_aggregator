from unittest.mock import Mock

import pytest
from pendulum import time

from src.warden.warden import NotAllowed, Rule8to11EveryDay, Rule11to12Workdays, Warden


def test_warden_rules_list():
    expected_rules = {
        Rule8to11EveryDay,
        Rule11to12Workdays,
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
    rule.check(time(hour=11, second=1))
    rule.check(time(hour=12))
    rule.check(time(hour=23))
    rule.check(time(hour=7, minute=59))


def test_rule_8_to_11_every_day_negative():
    """Check for Rule8to11EveryDay"""
    rule = Rule8to11EveryDay()
    with pytest.raises(NotAllowed):
        rule.check(time(hour=8, second=1))

    with pytest.raises(NotAllowed):
        rule.check(time(hour=10, minute=59))


def test_rule_11_to_12_weekdays_positive():
    """Check for Rule11to12Weekdays"""
    rule = Rule11to12Workdays()
    rule.check(time(hour=12, second=1))
    rule.check(time(hour=23))
    rule.check(time(hour=10, minute=59))


def test_rule_11_to_12_weekdays_negative():
    """Check for Rule11to12Weekdays"""
    rule = Rule11to12Workdays()
    with pytest.raises(NotAllowed):
        rule.check(time(hour=11, second=1))

    with pytest.raises(NotAllowed):
        rule.check(time(hour=11, minute=59))
