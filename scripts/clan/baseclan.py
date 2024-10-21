
class BaseClan:
    """The base clan in ClanGen, which living Clans derive from."""

    name = ""

    BIOME_TYPES = ["Forest", "Plains", "Mountainous", "Beach"]
    SEASONS = [
        "Newleaf",
        "Newleaf",
        "Newleaf",
        "Greenleaf",
        "Greenleaf",
        "Greenleaf",
        "Leaf-fall",
        "Leaf-fall",
        "Leaf-fall",
        "Leaf-bare",
        "Leaf-bare",
        "Leaf-bare",
    ]

    current_season = "Newleaf"
    starting_season = "Newleaf"
    biome = "Forest"

    # other general stuff (these really need separating out but that'll be another refactor for another day
    all_clans = []
    clan_cats = []

    starclan_cats = []
    darkforest_cats = []
    unknown_cats = []

    temperament_dict = {
        "low_social": ["cunning", "proud", "bloodthirsty"],
        "mid_social": ["amiable", "stoic", "wary"],
        "high_social": ["gracious", "mellow", "logical"],
    }

    def __repr__(self):
        return f"{self.name}Clan"
