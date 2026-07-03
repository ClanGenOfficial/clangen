from enum import StrEnum


class GameScreen(StrEnum):
    START = "start_screen"
    # screens access through start screen
    SWITCH_CLAN = "switch_clan_screen"
    SETTINGS = "settings_screen"
    EVENT_EDIT = "event_edit_screen"

    # make clan screens
    MAKE_CLAN_CHOOSE_MODE = "choose_mode_screen"
    MAKE_CLAN_CHOOSE_CARDS = "choose_cards_screen"
    MAKE_CLAN_CHOOSE_NAME = "choose_name_screen"
    MAKE_CLAN_CHOOSE_CATS = "choose_cats_screen"
    MAKE_CLAN_CHOOSE_CAMP = "choose_camp_screen"
    MAKE_CLAN_CHOOSE_SYMBOL = "choose_symbol_screen"
    MAKE_CLAN_CLAN_CREATED = "clan_created_screen"

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
