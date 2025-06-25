from random import choice, randint

from scripts.cat.cats import Cat
from scripts.game_structure.game_essentials import game


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
        kitty
        for kitty in Cat.all_cats.values()
        if not kitty.dead and not kitty.outside
    ]

    for new_role, cat_involved in future_info["involved_cats"].items():
        # grab any cats that need to be newly gathered
        if isinstance(cat_involved, dict):
            gathered_cat_dict[new_role] = _get_constrained_cat(
                cat_involved, possible_cats
            )
            possible_cats.remove(Cat.fetch_cat(gathered_cat_dict[new_role]))
            continue

        # otherwise, assign already involved cats to their new role within the future event
        gathered_cat_dict[new_role] = cat_dict[cat_involved].ID
        if cat_dict[cat_involved] in possible_cats:
            possible_cats.remove(cat_dict[cat_involved])

    return gathered_cat_dict

def _get_constrained_cat(constraint_dict, possible_cats):
    """
    checks the living clan cat list against constraint_dict to find any eligible cats.
    returns a single cat ID chosen from eligible cats
    """

    funct_dict = {
        "age": _check_age,
        "status": _check_status,
        "skill": _check_skill,
        "trait": _check_trait,
        "backstory": _check_backstory,
    }

    allowed_cats = []
    for param in funct_dict:
        allowed_cats = funct_dict[param](possible_cats, constraint_dict.get(param))

        # if the list is emptied, break
        if not allowed_cats:
            break

    if not allowed_cats:
        return None

    return choice(allowed_cats).ID

def _check_age(cat_list: list, ages: list) -> list:
    """
    checks cat_list against required ages and returns qualifying cats
    """
    if not ages or "any" in ages:
        return cat_list

    return [kitty for kitty in cat_list if kitty.age in ages]

def _check_status(cat_list: list, statuses: list) -> list:
    """
    checks cat_list against required statuses and returns qualifying cats
    """
    if not statuses or "any" in statuses:
        return cat_list

    return [kitty for kitty in cat_list if kitty.status in statuses]

def _check_skill(cat_list: list, skills: list) -> list:
    """
    checks cat_list against required skills and returns qualifying cats
    """
    removals = []
    if not skills:
        return cat_list

    for kitty in cat_list:
        has_skill = False
        for _skill in skills:
            split_skill = _skill.split(",")

            if len(split_skill) < 2:
                print("Cat skill incorrectly formatted", _skill)
                continue

            if kitty.skills.meets_skill_requirement(
                split_skill[0], int(split_skill[1])
            ):
                has_skill = True

        if not has_skill:
            removals.append(kitty)

    return [kitty for kitty in cat_list if kitty not in removals]

def _check_trait(cat_list: list, traits: list) -> list:
    """
    checks cat_list against required traits and returns qualifying cats
    """
    if not traits:
        return cat_list

    return [kitty for kitty in cat_list if kitty.trait in traits]

def _check_backstory(cat_list: list, backstories: list) -> list:
    """
    checks cat_list against required backstories and returns qualifying cats
    """
    if not backstories:
        return cat_list

    return [kitty for kitty in cat_list if kitty.backstory in backstories]


future_event = FutureEvent()
