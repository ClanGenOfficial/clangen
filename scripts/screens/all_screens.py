from .base_screens import Screens
from .cat_screens import OptionsScreen, ProfileScreen, ChangeGenderScreen, ChangeNameScreen, ExileProfileScreen
from .clan_creation_screens import ClanCreatedScreen, MakeClanScreen
from .clan_screens import ClanScreen, StarClanScreen, ListScreen, AllegiancesScreen
from .event_screens import EventsScreen, SingleEventScreen, PatrolEventScreen, RelationshipEventScreen
from .organizational_screens import\
    StartScreen, SettingsScreen, InfoScreen, SwitchClanScreen, LanguageScreen, RelationshipSettingsScreen, StatsScreen, GameModeScreen
from .patrol_screens import PatrolScreen
from .relation_screens import\
    RelationshipScreen, ChooseMateScreen, ChooseMentorScreen2, ViewChildrenScreen, ChooseMentorScreen
from .world_screens import MapScreen, OutsideClanScreen

# SCREENS
screens = Screens()

# ---------------------------------------------------------------------------- #
#                                 cat_screens.py                               #
# ---------------------------------------------------------------------------- #

change_gender_screen = ChangeGenderScreen('change gender screen')
change_name_screen = ChangeNameScreen('change name screen')
option_screen = OptionsScreen('options screen')
profile_screen = ProfileScreen('profile screen')
exile_profile_screen = ExileProfileScreen('outside profile screen')


# ---------------------------------------------------------------------------- #
#                           clan_creation_screens.py                           #
# ---------------------------------------------------------------------------- #

clan_created_screen = ClanCreatedScreen('clan created screen')
make_clan_screen = MakeClanScreen('make clan screen')

# ---------------------------------------------------------------------------- #
#                                clan_screens.py                               #
# ---------------------------------------------------------------------------- #

allegiances_screen = AllegiancesScreen('allegiances screen')
clan_screen = ClanScreen('clan screen')
list_screen = ListScreen('list screen')
starclan_screen = StarClanScreen('starclan screen')

# ---------------------------------------------------------------------------- #
#                               event_screens.py                               #
# ---------------------------------------------------------------------------- #

events_screen = EventsScreen('events screen')
patrol_event_screen = PatrolEventScreen('patrol event screen')
relationship_event_screen = RelationshipEventScreen('relationship event screen')
single_event_screen = SingleEventScreen('single event screen')

# ---------------------------------------------------------------------------- #
#                           organizational_screens.py                          #
# ---------------------------------------------------------------------------- #

info_screen = InfoScreen('info screen')
language_screen = LanguageScreen('language screen')
relationship_setting_screen = RelationshipSettingsScreen('relationship setting screen')
settings_screen = SettingsScreen('settings screen')
stats_screen = StatsScreen('stats screen')
start_screen = StartScreen('start screen')
switch_clan_screen = SwitchClanScreen('switch clan screen')
game_mode_screen = GameModeScreen('game_mode screen')

# ---------------------------------------------------------------------------- #
#                               patrol_screens.py                              #
# ---------------------------------------------------------------------------- #

patrol_screen = PatrolScreen('patrol screen')

# ---------------------------------------------------------------------------- #
#                              relation_screens.py                             #
# ---------------------------------------------------------------------------- #

choose_mate_screen = ChooseMateScreen('choose mate screen')
choose_mentor_screen = ChooseMentorScreen('choose mentor screen')
choose_mentor_screen2 = ChooseMentorScreen2('choose mentor screen2')
relationship_screen = RelationshipScreen('relationship screen')
view_children_screen = ViewChildrenScreen('see kits screen')

# ---------------------------------------------------------------------------- #
#                               world_screens.py                               #
# ---------------------------------------------------------------------------- #

outside_clan_screen = OutsideClanScreen('other screen')
map_screen = MapScreen('map screen')