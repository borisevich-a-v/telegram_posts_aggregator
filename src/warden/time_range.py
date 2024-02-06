from pendulum import duration, time


class TimeRange:
    def __init__(self, start: time, end: time) -> None:
        self.start = start
        self.end = end
        if abs(self.end - self.start) < duration(milliseconds=100):
            raise ValueError("The start and the end time are too close.")

    def __contains__(self, checked_time: time) -> bool:
        if self.start < self.end:
            if self.start < checked_time < self.end:
                return True
        else:
            if self.start < checked_time or self.end > checked_time:
                return True
        return False
