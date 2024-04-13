from pendulum import duration, time


class TimeRange:
    """
    This class stores time range, regardless a date.
    So if `start` is 4pm and `end` is 11am, then `__contains__` will return True for 6 pm and 3 am, but False for 1 pm.
    """

    def __init__(self, start: time, end: time) -> None:
        self.start = start
        self.end = end
        if abs(self.end - self.start) < duration(milliseconds=100):
            raise ValueError("The start and the end time are too close.")

    def __contains__(self, checked_time: time) -> bool:
        if self.start < self.end:
            if self.start <= checked_time <= self.end:
                return True
        else:
            if self.start <= checked_time or self.end >= checked_time:
                return True
        return False
