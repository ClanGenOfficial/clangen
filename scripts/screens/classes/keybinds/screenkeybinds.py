from strenum import StrEnum

PRIMARY_NAVBAR = ["events screen", "clan screen", "list screen", "patrol screen"]


class ScreensEnum(StrEnum):
    PROFILE = "profile screen"
    CEREMONY = "ceremony screen"
    ROLE = "role screen"
    SPRITE_INSPECT = "sprite inspect screen"
    MAKE_CLAN = "make clan screen"
    ALLEGIANCES = "allegiances screen"
    CAMP = "camp screen"
    CATLIST = "list screen"
    MED_DEN = "med den screen"
    CLEARING = "clearing screen"
    WARRIOR_DEN = "warrior den screen"
    LEADER_DEN = "leader den screen"
    EVENTS = "events screen"
