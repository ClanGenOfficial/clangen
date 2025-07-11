from typing import List


class ShortEvent:
    """
    A moon event that only affects the moon it was triggered on.  Can involve two cats directly and be restricted by various constraints.
    - full documentation available on GitHub wiki
    """

    def __init__(
        self,
        event_id: str = "",
        location: List[str] = None,
        season: List[str] = None,
        sub_type: List[str] = None,
        tags: List[str] = None,
        weight: int = 0,
        text: str = "",
        new_accessory: List[str] = None,
        m_c=None,
        r_c=None,
        new_cat: List[list] = None,
        injury: list = None,
        exclude_involved: list = None,
        history: list = None,
        relationships: list = None,
        outsider: dict = None,
        other_clan: dict = None,
        supplies: list = None,
        new_gender: List[str] = None,
        future_event: dict = None,
    ):
        if not event_id:
            print("WARNING: moon event has no event_id")
        self.event_id = event_id
        self.location = location if location else ["any"]
        self.season = season if season else ["any"]
        self.sub_type = sub_type if sub_type else []
        self.tags = tags if tags else []
        self.weight = weight
        self.text = text
        self.new_accessory = new_accessory if new_accessory else []
        self.m_c = m_c if m_c else {"age": ["any"]}
        if self.m_c:
            if "age" not in self.m_c:
                self.m_c["age"] = ["any"]
            if "status" not in self.m_c:
                self.m_c["status"] = ["any"]
            if "relationship_status" not in self.m_c:
                self.m_c["relationship_status"] = []
            if "skill" not in self.m_c:
                self.m_c["skill"] = []
            if "not_skill" not in self.m_c:
                self.m_c["not_skill"] = []
            if "trait" not in self.m_c:
                self.m_c["trait"] = []
            if "not_trait" not in self.m_c:
                self.m_c["not_trait"] = []
            if "age" not in self.m_c:
                self.m_c["age"] = []
            if "backstory" not in self.m_c:
                self.m_c["backstory"] = []
            if "dies" not in self.m_c:
                self.m_c["dies"] = False
            if "gender" not in self.m_c:
                self.m_c["gender"] = []

        self.r_c = r_c if r_c else {}
        if self.r_c:
            if "age" not in self.r_c:
                self.r_c["age"] = ["any"]
            if "status" not in self.r_c:
                self.r_c["status"] = ["any"]
            if "relationship_status" not in self.r_c:
                self.r_c["relationship_status"] = []
            if "skill" not in self.r_c:
                self.r_c["skill"] = []
            if "not_skill" not in self.r_c:
                self.r_c["not_skill"] = []
            if "trait" not in self.r_c:
                self.r_c["trait"] = []
            if "not_trait" not in self.r_c:
                self.r_c["not_trait"] = []
            if "age" not in self.r_c:
                self.r_c["age"] = []
            if "backstory" not in self.r_c:
                self.r_c["backstory"] = []
            if "dies" not in self.r_c:
                self.r_c["dies"] = False
            if "gender" not in self.r_c:
                self.r_c["gender"] = []

        self.new_cat = new_cat if new_cat else []
        self.exclude_involved = exclude_involved if exclude_involved else []
        self.injury = injury if injury else []
        self.history = history if history else []
        self.relationships = relationships if relationships else []
        self.outsider = outsider if outsider else {}
        if self.outsider:
            if "current_rep" not in self.outsider:
                self.outsider["current_rep"] = []
            if "changed" not in self.outsider:
                self.outsider["changed"] = 0
        self.other_clan = other_clan if other_clan else {}
        if self.other_clan:
            if "current_rep" not in self.other_clan:
                self.other_clan["current_rep"] = []
            if "changed" not in self.other_clan:
                self.other_clan["changed"] = 0
        self.supplies = supplies if supplies else []
        self.new_gender = new_gender
        self.future_event = future_event if future_event else {}

    def __repr__(self):
        return f"{self.event_id} ({self.sub_type})"
