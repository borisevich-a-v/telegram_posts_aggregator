from pendulum import datetime, duration, now, time

from .time_range import TimeRange


class NotAllowed(Exception):  # Choose better name
    ...


class Warden:
    def __init__(self):
        self.interactions: list[datetime] = []

        # Pay attention for time zones
        self.forbidden_time = TimeRange(time(8), time(11))  # it's okay to set up Warden in the init for now
        self.limited_time = TimeRange(time(11), time(18))

    def check_allowance(self) -> None:
        self.add_new_interaction()

        current_time = now()

        # You are right! Make checks as a separate classes with a standardized interface. Let's do it proper
        self.check_1(current_time)
        self.check_2(current_time)

    def check_1(self, current_time):  # todo choose better name
        if current_time in self.forbidden_time:
            # raise NotAllowed("Forbidden time")
            ...

    def check_2(self, current_time):
        # maximum five posts in 30 minutes in limited time
        if current_time in self.limited_time:
            if len(self.interactions) < 5:
                ...

            last_30_min = TimeRange(now().time() - duration(minutes=30), now().time())
            for interaction in self.interactions[-5:]:
                if interaction not in last_30_min:
                    ...

    def add_new_interaction(self) -> None:
        # TODO: do it somehow smartly
        if len(self.interactions) > 2_000:
            self.interactions = self.interactions[-500:]
        self.interactions.append(now())
