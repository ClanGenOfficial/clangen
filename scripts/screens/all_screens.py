from .AllegiancesScreen import AllegiancesScreen
from .CeremonyScreen import CeremonyScreen
from .ChangeGenderScreen import ChangeGenderScreen
from .ChooseAdoptiveParentScreen import ChooseAdoptiveParentScreen
from .ChooseMateScreen import ChooseMateScreen
from .ChooseMentorScreen import ChooseMentorScreen
from .ClanScreen import ClanScreen
from .ClanSettingsScreen import ClanSettingsScreen
from .ClearingScreen import ClearingScreen
from .EventEditScreen import EventEditScreen
from .EventsScreen import EventsScreen
from .FamilyTreeScreen import FamilyTreeScreen
from .LeaderDenScreen import LeaderDenScreen
from .ListScreen import ListScreen
from .MakeClanScreen import MakeClanScreen
from .MedDenScreen import MedDenScreen
from .MediationScreen import MediationScreen
from .PatrolScreen import PatrolScreen
from .ProfileScreen import ProfileScreen
from .RelationshipScreen import RelationshipScreen
from .RoleScreen import RoleScreen
from .Screens import Screens
from .SettingsScreen import SettingsScreen
from .SpriteInspectScreen import SpriteInspectScreen
from .StartScreen import StartScreen
from .SwitchClanScreen import SwitchClanScreen
from .WarriorDenScreen import WarriorDenScreen
from .enums import GameScreen

# ---------------------------------------------------------------------------- #
#                                  UI RULES                                    #
# ---------------------------------------------------------------------------- #
"""
SCREEN: 700 height x 800 width

MARGINS: 25px on all sides
    ~Any new buttons or text MUST be within these margins.
    ~Buttons on the edge of the screen should butt up right against the margin. 
    (i.e. the <<Main Menu button is placed 25px x 25px on most screens) 
    
BUTTONS:
    ~Buttons are 30px in height. Width can be anything, though generally try to keep to even numbers.
    ~Square icons are 34px x 34px.
    ~Generally keep text at least 5px away from the right and left /straight/ (do not count the rounded ends) edge 
    of the button (this rule is sometimes broken. the goal is to be consistent across the entire screen or button type)
    ~Generally, the vertical gap between buttons should be 5px
"""


class AllScreens:
    screens = Screens()
    profile_screen = ProfileScreen(GameScreen.PROFILE)
    ceremony_screen = CeremonyScreen(GameScreen.CEREMONY)
    role_screen = RoleScreen(GameScreen.CHANGE_ROLE)
    sprite_inspect_screen = SpriteInspectScreen(GameScreen.SPRITE_INSPECT)

    make_clan_screen = MakeClanScreen(GameScreen.MAKE_CLAN)

    allegiances_screen = AllegiancesScreen(GameScreen.ALLEGIANCES)
    camp_screen = ClanScreen(GameScreen.CAMP)
    list_screen = ListScreen(GameScreen.LIST)
    med_den_screen = MedDenScreen(GameScreen.MED_DEN)
    clearing_screen = ClearingScreen(GameScreen.CLEARING)
    warrior_den_screen = WarriorDenScreen(GameScreen.WARRIOR_DEN)
    leader_den_screen = LeaderDenScreen(GameScreen.LEADER_DEN)

    events_screen = EventsScreen(GameScreen.EVENTS)

    settings_screen = SettingsScreen(GameScreen.SETTINGS)
    clan_settings_screen = ClanSettingsScreen(GameScreen.CLAN_SETTINGS)
    start_screen = StartScreen(GameScreen.START)
    event_edit_screen = EventEditScreen(GameScreen.EVENT_EDIT)
    switch_clan_screen = SwitchClanScreen(GameScreen.SWITCH_CLAN)

    patrol_screen = PatrolScreen(GameScreen.PATROL)

    choose_mate_screen = ChooseMateScreen(GameScreen.CHOOSE_MATE)
    choose_mentor_screen = ChooseMentorScreen(GameScreen.CHOOSE_MENTOR)
    choose_adoptive_parent_screen = ChooseAdoptiveParentScreen(
        GameScreen.CHOOSE_ADOPTIVE_PARENT
    )
    relationship_screen = RelationshipScreen(GameScreen.RELATIONSHIP)
    family_tree_screen = FamilyTreeScreen(GameScreen.FAMILY_TREE)
    mediation_screen = MediationScreen(GameScreen.MEDIATION)
    change_gender_screen = ChangeGenderScreen(GameScreen.CHANGE_GENDER)

    @classmethod
    def rebuild_all_screens(cls):
        cls.screens = Screens()
        cls.profile_screen = ProfileScreen(GameScreen.PROFILE)
        cls.ceremony_screen = CeremonyScreen(GameScreen.CEREMONY)
        cls.role_screen = RoleScreen(GameScreen.CHANGE_ROLE)
        cls.sprite_inspect_screen = SpriteInspectScreen(GameScreen.SPRITE_INSPECT)

        cls.make_clan_screen = MakeClanScreen(GameScreen.MAKE_CLAN)

        cls.allegiances_screen = AllegiancesScreen(GameScreen.ALLEGIANCES)
        cls.camp_screen = ClanScreen(GameScreen.CAMP)
        cls.list_screen = ListScreen(GameScreen.LIST)
        cls.med_den_screen = MedDenScreen(GameScreen.MED_DEN)
        cls.clearing_screen = ClearingScreen(GameScreen.CLEARING)
        cls.warrior_den_screen = WarriorDenScreen(GameScreen.WARRIOR_DEN)
        cls.leader_den_screen = LeaderDenScreen(GameScreen.LEADER_DEN)

        cls.events_screen = EventsScreen(GameScreen.EVENTS)

        cls.settings_screen = SettingsScreen(GameScreen.SETTINGS)
        cls.clan_settings_screen = ClanSettingsScreen(GameScreen.CLAN_SETTINGS)
        cls.start_screen = StartScreen(GameScreen.START)
        cls.switch_clan_screen = SwitchClanScreen(GameScreen.SWITCH_CLAN)

        cls.patrol_screen = PatrolScreen(GameScreen.PATROL)

        cls.choose_mate_screen = ChooseMateScreen(GameScreen.CHOOSE_MATE)
        cls.choose_mentor_screen = ChooseMentorScreen(GameScreen.CHOOSE_MENTOR)
        cls.choose_adoptive_parent_screen = ChooseAdoptiveParentScreen(
            GameScreen.CHOOSE_ADOPTIVE_PARENT
        )
        cls.relationship_screen = RelationshipScreen(GameScreen.RELATIONSHIP)
        cls.family_tree_screen = FamilyTreeScreen(GameScreen.FAMILY_TREE)
        cls.mediation_screen = MediationScreen(GameScreen.MEDIATION)
        cls.change_gender_screen = ChangeGenderScreen(GameScreen.CHANGE_GENDER)
