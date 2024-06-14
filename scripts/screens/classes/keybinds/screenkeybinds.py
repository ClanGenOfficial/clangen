from strenum import StrEnum

PRIMARY_NAVBAR = ["events screen", "clan screen", "list screen", "patrol screen"]


class ScreenEnum(StrEnum):
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
    PATROL = "patrol screen"
    CHOOSE_MATE = "choose mate screen"
    CHOOSE_MENTOR = "choose mentor screen"
    CHOOSE_ADOPT_PARENT = "choose adoptive parent screen"
    RELATIONSHIPS = "relationships screen"
    VIEW_CHILDREN = "see kits screen"
    MEDIATION = "mediation screen"
    CHANGE_GENDER = "change gender screen"

    APPRENTICE_DEN = "apprentice den screen"
    NURSERY = "nursery screen"
    ELDER_DEN = "elder den screen"
