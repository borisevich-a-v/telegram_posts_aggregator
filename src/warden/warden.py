from pendulum import datetime, duration, now, time

from .time_range import TimeRange


class Warden:
    def __init__(self):
        self.interactions: list[datetime] = []

        self.forbidden_time = TimeRange(time(0), time(11))
        self.limited_time = TimeRange(time(11), time(18))

    def check_allowance(self) -> bool:
        current_time = now()
        if current_time in self.forbidden_time:
            return False

        if current_time in self.limited_time:
            if len(self.interactions) < 5:
                return True

            # maximum five posts in 30 minutes in limited time
            last_30_min = TimeRange(now().time() - duration(minutes=30), now().time())
            for interaction in self.interactions[-5:]:
                if interaction not in last_30_min:
                    return True

        return False

    def add_new_interaction(self) -> None:
        # TODO clear old interactions more smartly
        if len(self.interactions) > 2_000:
            self.interactions = self.interactions[-500:]
        self.interactions.append(now())


def is_next_post_allowed() -> bool:
    warden = Warden()

    if warden.check_allowance():
        warden.add_new_interaction()
        return True
    return False
