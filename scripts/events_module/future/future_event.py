class FutureEvent:
    def __init__(
        self,
        parent_event: str = None,
        event_type: str = None,
        pool: dict = None,
        moon_delay: int = 0,
        involved_cats: dict = None,
    ):
        self.parent_event = parent_event
        self.event_type = event_type
        self.pool = pool
        self.moon_delay = moon_delay

        self.involved_cats = involved_cats

        self.triggered = False
        self.allowed_events = self.pool.get("event_id")
        self.excluded_events = self.pool.get("excluded_event_id")
        self.negate_subtyping = "sub_type" not in self.pool

    def to_dict(self):
        return {
            "parent_event": self.parent_event,
            "event_type": self.event_type,
            "pool": self.pool,
            "moon_delay": self.moon_delay,
            "involved_cats": self.involved_cats,
        }
