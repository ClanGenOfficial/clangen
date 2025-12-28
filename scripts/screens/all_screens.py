import warnings

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

screens = None
screen_dict = {}


def rebuild_all_screens():
    global screens
    screens = Screens()

    enum_to_class = {
        GameScreen.PROFILE: ProfileScreen,
        GameScreen.CEREMONY: CeremonyScreen,
        GameScreen.CHANGE_ROLE: RoleScreen,
        GameScreen.SPRITE_INSPECT: SpriteInspectScreen,
        GameScreen.MAKE_CLAN: MakeClanScreen,
        GameScreen.ALLEGIANCES: AllegiancesScreen,
        GameScreen.CAMP: ClanScreen,
        GameScreen.LIST: ListScreen,
        GameScreen.MED_DEN: MedDenScreen,
        GameScreen.CLEARING: ClearingScreen,
        GameScreen.WARRIOR_DEN: WarriorDenScreen,
        GameScreen.LEADER_DEN: LeaderDenScreen,
        GameScreen.EVENTS: EventsScreen,
        GameScreen.SETTINGS: SettingsScreen,
        GameScreen.CLAN_SETTINGS: ClanSettingsScreen,
        GameScreen.START: StartScreen,
        GameScreen.SWITCH_CLAN: SwitchClanScreen,
        GameScreen.PATROL: PatrolScreen,
        GameScreen.CHOOSE_MATE: ChooseMateScreen,
        GameScreen.CHOOSE_MENTOR: ChooseMentorScreen,
        GameScreen.CHOOSE_ADOPTIVE_PARENT: ChooseAdoptiveParentScreen,
        GameScreen.RELATIONSHIP: RelationshipScreen,
        GameScreen.FAMILY_TREE: FamilyTreeScreen,
        GameScreen.MEDIATION: MediationScreen,
        GameScreen.CHANGE_GENDER: ChangeGenderScreen,
        GameScreen.EVENT_EDIT: EventEditScreen,
    }

    for enum, classobj in enum_to_class.items():
        screen_dict[enum] = classobj(enum)


def get_screen(screen: GameScreen):
    return screen_dict[screen]


rebuild_all_screens()
