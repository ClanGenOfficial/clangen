from .base_screens import Screens
from .cat_screens import ProfileScreen, ChangeGenderScreen, ChangeNameScreen, CeremonyScreen
from .clan_creation_screens import MakeClanScreen
from .clan_screens import ClanScreen, StarClanScreen, DFScreen, ListScreen, AllegiancesScreen, MedDenScreen
from .event_screens import EventsScreen
from .organizational_screens import\
    StartScreen, SettingsScreen, SwitchClanScreen, StatsScreen
from .patrol_screens import PatrolScreen
from .relation_screens import\
    RelationshipScreen, ChooseMateScreen, ViewChildrenScreen, ChooseMentorScreen
from .world_screens import OutsideClanScreen

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

# SCREENS
screens = Screens()

# ---------------------------------------------------------------------------- #
#                                 cat_screens.py                               #
# ---------------------------------------------------------------------------- #

change_gender_screen = ChangeGenderScreen('change gender screen')
change_name_screen = ChangeNameScreen('change name screen')
profile_screen = ProfileScreen('profile screen')
ceremony_screen = CeremonyScreen('ceremony screen')

# ---------------------------------------------------------------------------- #
#                           clan_creation_screens.py                           #
# ---------------------------------------------------------------------------- #

make_clan_screen = MakeClanScreen('make clan screen')

# ---------------------------------------------------------------------------- #
#                                clan_screens.py                               #
# ---------------------------------------------------------------------------- #

allegiances_screen = AllegiancesScreen('allegiances screen')
clan_screen = ClanScreen('clan screen')
list_screen = ListScreen('list screen')
starclan_screen = StarClanScreen('starclan screen')
df_screen = DFScreen('dark forest screen')
med_den_screen = MedDenScreen('med den screen')

# ---------------------------------------------------------------------------- #
#                               event_screens.py                               #
# ---------------------------------------------------------------------------- #

events_screen = EventsScreen('events screen')

# ---------------------------------------------------------------------------- #
#                           organizational_screens.py                          #
# ---------------------------------------------------------------------------- #

settings_screen = SettingsScreen('settings screen')
stats_screen = StatsScreen('stats screen')
start_screen = StartScreen('start screen')
switch_clan_screen = SwitchClanScreen('switch clan screen')

# ---------------------------------------------------------------------------- #
#                               patrol_screens.py                              #
# ---------------------------------------------------------------------------- #

patrol_screen = PatrolScreen('patrol screen')

# ---------------------------------------------------------------------------- #
#                              relation_screens.py                             #
# ---------------------------------------------------------------------------- #

choose_mate_screen = ChooseMateScreen('choose mate screen')
choose_mentor_screen = ChooseMentorScreen('choose mentor screen')
relationship_screen = RelationshipScreen('relationship screen')
view_children_screen = ViewChildrenScreen('see kits screen')

# ---------------------------------------------------------------------------- #
#                               world_screens.py                               #
# ---------------------------------------------------------------------------- #

outside_clan_screen = OutsideClanScreen('other screen')
# map_screen = MapScreen('map screen')