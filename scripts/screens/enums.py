from enum import StrEnum


class GameScreen(StrEnum):
    START = "start_screen"
    # screens access through start screen
    MAKE_CLAN = "make_clan_screen"
    SWITCH_CLAN = "switch_clan_screen"
    SETTINGS = "settings_screen"
    EVENT_EDIT = "event_edit_screen"

    # screens accessed through top menu
    CAMP = "camp_screen"
    LIST = "list_screen"
    EVENTS = "events_screen"
    PATROL = "patrol_screen"
    ALLEGIANCES = "allegiances_screen"
    CLAN_SETTINGS = "clan_settings_screen"

    # den/work screens
    LEADER_DEN = "leader_den_screen"
    MED_DEN = "med_den_screen"
    WARRIOR_DEN = "warrior_den_screen"
    CLEARING = "clearing_screen"
    MEDIATION = "mediation_screen"

    PROFILE = "profile_screen"
    # screens accessed through profile
    CEREMONY = "ceremony_screen"
    SPRITE_INSPECT = "sprite_inspect_screen"
    RELATIONSHIP = "relationship_screen"
    FAMILY_TREE = "family_tree_screen"
    CHANGE_GENDER = "change_gender_screen"
    CHANGE_ROLE = "role_screen"
    CHOOSE_MATE = "choose_mate_screen"
    CHOOSE_MENTOR = "choose_mentor_screen"
    CHOOSE_ADOPTIVE_PARENT = "choose_adoptive_parent_screen"
