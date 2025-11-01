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

def rebuild_all_screens():
    global screens, profile_screen, ceremony_screen, role_screen, sprite_inspect_screen, make_clan_screen, allegiances_screen, camp_screen, list_screen, med_den_screen, clearing_screen, warrior_den_screen, leader_den_screen, events_screen, settings_screen, clan_settings_screen, start_screen, switch_clan_screen, patrol_screen, choose_mate_screen, choose_mentor_screen, choose_adoptive_parent_screen, relationship_screen, family_tree_screen, mediation_screen, change_gender_screen, event_edit_screen
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

    event_edit_screen = EventEditScreen(GameScreen.EVENT_EDIT)

rebuild_all_screens()
