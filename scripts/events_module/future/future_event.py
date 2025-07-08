from random import randint

from scripts.cat.cats import Cat
from scripts.events_module.event_filters import cat_for_event
from scripts.events_module.generate_events import GenerateEvents
from scripts.game_structure.game_essentials import game


def prep_event(event, event_id: str, possible_cats: dict):
    """
    Checks if the given event has a future event attached, then creates the future event
    :param event: the class object for the event
    :param event_id: the ID for the event
    :param possible_cats: a dict of all cats involved in the event. This should provide the cat
    abbreviation as the key and the cat object as the value.
    """
    if not event.future_event:
        return

    for event_info in event.future_event:
        # create dict of all cats that need to be involved in future event
        gathered_cat_dict = _collect_involved_cats(possible_cats, event_info)

        # create future event and add it to the future event list
        game.clan.future_events.append(
            FutureEvent(
                parent_event=event_id,
                event_type=event_info["event_type"],
                pool=event_info["pool"],
                moon_delay=randint(
                    event_info["moon_delay"][0], event_info["moon_delay"][1]
                ),
                involved_cats=gathered_cat_dict,
            )
        )


def _collect_involved_cats(cat_dict: dict, future_info: dict) -> dict:
    """
    collects involved cats and assigns their roles for the future event, then
    returns a dict associating their new role (key) with their cat ID (value)

    :param cat_dict: a dict of cats already present with the parent event of the future event. Key should be abbr
    string and value should be cat object.
    :param future_info: the future_info dict from the parent event
    """
    gathered_cat_dict = {}

    # we always need an m_c and an r_c, so if they weren't specified at all then we need to find them
    if not future_info["involved_cats"].get("m_c"):
        future_info["involved_cats"]["m_c"] = {}
    if not future_info["involved_cats"].get("r_c"):
        future_info["involved_cats"]["r_c"] = {}

    # we're just keeping this to living cats within the clan for now, more complexity can come later
    possible_cats = [
        kitty for kitty in Cat.all_cats.values() if kitty.status.alive_in_player_clan
    ]

    for new_role, cat_involved in future_info["involved_cats"].items():
        # grab any cats that need to be newly gathered
        if isinstance(cat_involved, dict):
            gathered_cat_dict[new_role] = cat_for_event(cat_involved, possible_cats)
            possible_cats.remove(Cat.fetch_cat(gathered_cat_dict[new_role]))
            continue

        # otherwise, assign already involved cats to their new role within the future event
        gathered_cat_dict[new_role] = cat_dict[cat_involved].ID
        if cat_dict[cat_involved] in possible_cats:
            possible_cats.remove(cat_dict[cat_involved])

    return gathered_cat_dict


def check_for_triggered_future_event():
    """
    Handles aging future events and triggering them.
    """
    removals = []

    for event in game.clan.future_events:
        event.moon_delay -= 1
        # we give events a buffer of 12 moons to allow any season-locked events a chance to trigger, then we remove
        if event.moon_delay <= -12:
            removals.append(event)
        # attempt to trigger event
        if event.moon_delay <= 0:
            event.trigger()
            if event.triggered:
                removals.append(event)

    for event in removals:
        if event in game.clan.future_events:
            game.clan.future_events.remove(event)


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
        self.allowed_events = [self.pool.get("event_id")]
        self.excluded_events = [self.pool.get("excluded_event_id")]
        self.negate_subtyping = ("subtype" not in self.pool,)

    def to_dict(self):
        return {
            "parent_event": self.parent_event,
            "event_type": self.event_type,
            "pool": self.pool,
            "moon_delay": self.moon_delay,
            "involved_cats": self.involved_cats,
        }

    def trigger(self):
        GenerateEvents.create_short_event(
            event_type=self.event_type,
            main_cat=Cat.fetch_cat(self.involved_cats.get("m_c")),
            random_cat=Cat.fetch_cat(self.involved_cats.get("r_c")),
            freshkill_pile=game.clan.freshkill_pile,
            victim_cat=Cat.fetch_cat(self.involved_cats.get("mur_c")),
            sub_type=self.pool.get("subtype"),
            future_event=self,
        )
