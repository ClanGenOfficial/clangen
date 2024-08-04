from .AllegiancesScreen import AllegiancesScreen
from .CeremonyScreen import CeremonyScreen
from .ChangeGenderScreen import ChangeGenderScreen
from .ChooseAdoptiveParentScreen import ChooseAdoptiveParentScreen
from .ChooseMateScreen import ChooseMateScreen
from .ChooseMentorScreen import ChooseMentorScreen
from .ClanScreen import ClanScreen
from .ClanSettingsScreen import ClanSettingsScreen
from .ClearingScreen import ClearingScreen
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

    profile_screen = ProfileScreen("profile screen")
    ceremony_screen = CeremonyScreen("ceremony screen")
    role_screen = RoleScreen("role screen")
    sprite_inspect_screen = SpriteInspectScreen("sprite inspect screen")

    make_clan_screen = MakeClanScreen("make clan screen")

    allegiances_screen = AllegiancesScreen("allegiances screen")
    camp_screen = ClanScreen("camp screen")
    list_screen = ListScreen("list screen")
    med_den_screen = MedDenScreen("med den screen")
    clearing_screen = ClearingScreen("clearing screen")
    warrior_den_screen = WarriorDenScreen("warrior den screen")
    leader_den_screen = LeaderDenScreen("leader den screen")

    events_screen = EventsScreen("events screen")

    settings_screen = SettingsScreen("settings screen")
    clan_settings_screen = ClanSettingsScreen("clan settings screen")
    start_screen = StartScreen("start screen")
    switch_clan_screen = SwitchClanScreen("switch clan screen")

    patrol_screen = PatrolScreen("patrol screen")

    choose_mate_screen = ChooseMateScreen("choose mate screen")
    choose_mentor_screen = ChooseMentorScreen("choose mentor screen")
    choose_adoptive_parent_screen = ChooseAdoptiveParentScreen(
        "choose adoptive parent screen"
    )
    relationship_screen = RelationshipScreen("relationship screen")
    family_tree_screen = FamilyTreeScreen("family tree screen")
    mediation_screen = MediationScreen("mediation screen")
    change_gender_screen = ChangeGenderScreen("change gender screen")

    @classmethod
    def rebuild_all_screens(cls):
        cls.screens = Screens()
        cls.profile_screen = ProfileScreen("profile screen")
        cls.ceremony_screen = CeremonyScreen("ceremony screen")
        cls.role_screen = RoleScreen("role screen")
        cls.sprite_inspect_screen = SpriteInspectScreen("sprite inspect screen")

        cls.make_clan_screen = MakeClanScreen("make clan screen")

        cls.allegiances_screen = AllegiancesScreen("allegiances screen")
        cls.camp_screen = ClanScreen("camp screen")
        cls.list_screen = ListScreen("list screen")
        cls.med_den_screen = MedDenScreen("med den screen")
        cls.clearing_screen = ClearingScreen("clearing screen")
        cls.warrior_den_screen = WarriorDenScreen("warrior den screen")
        cls.leader_den_screen = LeaderDenScreen("leader den screen")

        cls.events_screen = EventsScreen("events screen")

        cls.settings_screen = SettingsScreen("settings screen")
        cls.clan_settings_screen = ClanSettingsScreen("clan settings screen")
        cls.start_screen = StartScreen("start screen")
        cls.switch_clan_screen = SwitchClanScreen("switch clan screen")

        cls.patrol_screen = PatrolScreen("patrol screen")

        cls.choose_mate_screen = ChooseMateScreen("choose mate screen")
        cls.choose_mentor_screen = ChooseMentorScreen("choose mentor screen")
        cls.choose_adoptive_parent_screen = ChooseAdoptiveParentScreen(
            "choose adoptive parent screen"
        )
        cls.relationship_screen = RelationshipScreen("relationship screen")
        cls.family_tree_screen = FamilyTreeScreen("family tree screen")
        cls.mediation_screen = MediationScreen("mediation screen")
        cls.change_gender_screen = ChangeGenderScreen("change gender screen")
