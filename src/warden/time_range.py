from pendulum import time, duration


class TimeRange:
    """TimeRange for humans"""

    def __init__(self, start: time, end: time):
        self.start = start
        self.end = end
        if abs(self.end - self.start) < duration(milliseconds=50):
            raise ValueError("Start and end time should be different")

    def __contains__(self, checked_time):
        if self.start < self.end:
            if self.start < checked_time < self.end:
                return True
        else:
            if self.start < checked_time or self.end > checked_time:
                return True
        return False
