import abc

from pendulum import WeekDay, datetime, now, time, today

from src.warden.time_range import TimeRange

WORKING_DAYS = WeekDay.MONDAY, WeekDay.TUESDAY, WeekDay.WEDNESDAY, WeekDay.THURSDAY, WeekDay.FRIDAY


class NotAllowed(Exception):
    """Raised if news check is not allowed to a user."""


class IRule(abc.ABC):
    """Raise an `NotAllowed` exception in case of check has failed"""

    @abc.abstractmethod
    def check(self, checked_time: datetime) -> None: ...


class Rule8to11EveryDay(IRule):
    FORBIDDEN_TIME = TimeRange(time(8), time(11))

    def check(self, checked_time: datetime) -> None:
        if checked_time in self.FORBIDDEN_TIME:
            raise NotAllowed("The rule does not allow you to ask for posts. (8am-11am every day)")


class Rule11to12Workdays(IRule):
    FORBIDDEN_TIME: TimeRange = TimeRange(time(11), time(12))
    FORBIDDEN_DAYS: tuple[WeekDay, ...] = WORKING_DAYS

    def check(self, checked_time: datetime) -> None:
        if today().day_of_week in self.FORBIDDEN_DAYS:
            if checked_time in self.FORBIDDEN_TIME:
                raise NotAllowed("The rule does not allow you to ask for posts. (11am-12pm workdays)")


class RuleSleepTimeMonTue(IRule):
    # To be implemented
    def check(self, checked_time: datetime) -> None: ...


class RuleLimitAccessInWorkingHours(IRule):
    # To be implemented
    def check(self, checked_time: datetime) -> None: ...


class Warden:
    RULES = [
        Rule8to11EveryDay,
        Rule11to12Workdays,
    ]

    def __init__(self):
        self._rules: list[IRule] = [rule() for rule in self.RULES]

    def check_allowance(self) -> None:
        current_time = now().time()
        for rule in self._rules:
            rule.check(current_time)
