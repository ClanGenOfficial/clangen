class OngoingEvent:
    """
    Moon events meant to be spread across multiple moons in a preset order.
    """

    def __init__(
        self,
        event=None,
        camp=None,
        season=None,
        tags=None,
        priority: str = "secondary",
        duration=None,
        current_duration: int = 0,
        rarity: int = 0,
        trigger_events=None,
        progress_events=None,
        conclusion_events=None,
        secondary_disasters=None,
        collateral_damage=None,
    ):
        self.event = event
        self.camp = camp
        self.season = season
        self.tags = tags
        self.priority = priority
        self.duration = duration
        self.current_duration = current_duration
        self.rarity = rarity
        self.trigger_events = trigger_events
        self.progress_events = progress_events
        self.conclusion_events = conclusion_events
        self.secondary_disasters = secondary_disasters
        self.collateral_damage = collateral_damage
