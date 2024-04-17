import abc

from pendulum import DateTime, WeekDay, now, time

from config import USER_TIME_ZONE

from .time_range import TimeRange

WORKING_DAYS = WeekDay.MONDAY, WeekDay.TUESDAY, WeekDay.WEDNESDAY, WeekDay.THURSDAY, WeekDay.FRIDAY


class NotAllowed(Exception):
    """Raised if news check is not allowed to a user."""


class IRule(abc.ABC):
    """Raise an `NotAllowed` exception in case of check has failed"""

    @abc.abstractmethod
    def check(self, current: DateTime) -> None: ...


class Rule8to11EveryDay(IRule):
    FORBIDDEN_TIME = TimeRange(time(8), time(11))

    def check(self, current: DateTime) -> None:
        if current.time() in self.FORBIDDEN_TIME:
            raise NotAllowed("The rule does not allow you to ask for posts. (8am-11am every day)")


class Rule11to12Workdays(IRule):
    FORBIDDEN_TIME = TimeRange(time(11), time(12))
    FORBIDDEN_DAYS: tuple[WeekDay, ...] = WORKING_DAYS

    def check(self, current: DateTime) -> None:
        if current.day_of_week in self.FORBIDDEN_DAYS:
            if current.time() in self.FORBIDDEN_TIME:
                raise NotAllowed("The rule does not allow you to ask for posts. (11am-12pm workdays)")


class RuleSleepTimeMonTue(IRule):
    FORBIDDEN_TIME = TimeRange(time(23), time(8))
    FORBIDDEN_DAYS: tuple[WeekDay, ...] = WORKING_DAYS[:2]

    def check(self, current: DateTime) -> None:
        if current.day_of_week in self.FORBIDDEN_DAYS:
            if current.time() in self.FORBIDDEN_TIME:
                raise NotAllowed("The rule does not allow you to ask for posts. (23pm-8am sleep-time)")


class RuleLimitAccessInProductiveHours(IRule):
    RESTRICTED_TIME = TimeRange(time(12), time(18))

    # No more than 20 posts in 30 minutes
    ALLOWED_POSTS_NUMBER = 20
    TIME_PERIOD = 30 * 60  # 30 minutes

    def __init__(self):
        self.last_access_times: list[DateTime] = []

    def _remove_old_accesses(self, current: DateTime):
        old_times = self.last_access_times
        self.last_access_times = []
        for access_time in old_times:
            if (current.int_timestamp - access_time.int_timestamp) < self.TIME_PERIOD:
                self.last_access_times.append(access_time)

    def check(self, current: DateTime) -> None:
        if current.time() not in self.RESTRICTED_TIME:
            return

        self._remove_old_accesses(current)
        if len(self.last_access_times) >= self.ALLOWED_POSTS_NUMBER:
            raise NotAllowed("You are asking for new posts too often. (12pm-18pm mo more than 20 posts in 30 min)")
        self.last_access_times.append(current)


class Warden:
    RULES = [
        Rule8to11EveryDay,
        Rule11to12Workdays,
        RuleSleepTimeMonTue,
        RuleLimitAccessInProductiveHours,
    ]

    def __init__(self):
        self._rules: list[IRule] = [rule() for rule in self.RULES]

    def check_allowance(self) -> None:
        current_datetime = now(tz=USER_TIME_ZONE)
        for rule in self._rules:
            rule.check(current_datetime)
