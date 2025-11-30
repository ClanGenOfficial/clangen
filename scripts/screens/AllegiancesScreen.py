import i18n
import pygame
import pygame_gui

from scripts.cat.cats import Cat
from scripts.game_structure import game
from scripts.game_structure.screen_settings import MANAGER
from scripts.utility import (
    get_text_box_theme,
    ui_scale,
    get_alive_clan_queens,
    ui_scale_offset,
    adjust_list_text,
    event_text_adjust,
)
from .Screens import Screens
from ..cat.enums import CatRank
from ..game_structure.ui_elements import UIModifiedScrollingContainer


class AllegiancesScreen(Screens):
    allegiance_list = []

    def __init__(self, name=None):
        super().__init__(name)
        self.names_boxes = None
        self.ranks_boxes = None
        self.scroll_container = None
        self.heading = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.menu_button_pressed(event)
            self.mute_button_pressed(event)

    def on_use(self):
        super().on_use()

    def screen_switches(self):
        super().screen_switches()
        # Heading
        self.heading = pygame_gui.elements.UITextBox(
            "screens.allegiances.heading",
            ui_scale(pygame.Rect((0, 115), (400, 40))),
            text_kwargs={"clan_name": game.clan.displayname},
            object_id=get_text_box_theme("#text_box_34_horizcenter_vertcenter"),
            manager=MANAGER,
            anchors={"centerx": "centerx"},
        )

        # Set Menu Buttons.
        self.show_menu_buttons()
        self.show_mute_buttons()
        self.set_disabled_menu_buttons(["allegiances"])
        self.update_heading_text(f"{game.clan.displayname}Clan")
        allegiance_list = self.get_allegiances_text()

        self.scroll_container = UIModifiedScrollingContainer(
            ui_scale(pygame.Rect((50, 165), (715, 470))),
            allow_scroll_x=False,
            allow_scroll_y=True,
            manager=MANAGER,
        )

        self.ranks_boxes = []
        self.names_boxes = []
        for x in allegiance_list:
            self.ranks_boxes.append(
                pygame_gui.elements.UITextBox(
                    x[0],
                    ui_scale(pygame.Rect((0, 0), (150, -1))),
                    object_id=get_text_box_theme("#text_box_30_horizleft"),
                    container=self.scroll_container,
                    manager=MANAGER,
                    anchors=(
                        {"top_target": self.names_boxes[-1]}
                        if len(self.names_boxes) > 0
                        else None
                    ),
                )
            )
            self.ranks_boxes[-1].disable()

            self.names_boxes.append(
                pygame_gui.elements.UITextBox(
                    x[1],
                    pygame.Rect(
                        (0, -self.ranks_boxes[-1].get_relative_rect()[3]),
                        ui_scale_offset((565, -1)),
                    ),
                    object_id=get_text_box_theme("#text_box_30_horizleft"),
                    container=self.scroll_container,
                    manager=MANAGER,
                    anchors={
                        "top_target": self.ranks_boxes[-1],
                        "left_target": self.ranks_boxes[-1],
                        "left": "left",
                        "right": "right",
                    },
                )
            )
            self.names_boxes[-1].disable()

    def exit_screen(self):
        for x in self.ranks_boxes:
            x.kill()
        del self.ranks_boxes
        for x in self.names_boxes:
            x.kill()
        del self.names_boxes
        self.scroll_container.kill()
        del self.scroll_container
        self.heading.kill()
        del self.heading

    @staticmethod
    def generate_one_entry(cat, extra_details=""):
        """Extra Details will be placed after the cat description, but before the apprentice (if they have one)."""
        output = f"{str(cat.name).upper()} - {cat.describe_cat()} {extra_details}"

        if len(cat.apprentice) == 0:
            return event_text_adjust(Cat, output, main_cat=cat)

        output += f"\n      {i18n.t('general.apprentice', count=len(cat.apprentice)).upper()}: "
        output += adjust_list_text(
            [
                str(Cat.fetch_cat(i).name).upper()
                for i in cat.apprentice
                if Cat.fetch_cat(i)
            ]
        ).upper()

        return event_text_adjust(Cat, output, main_cat=cat)

    def get_allegiances_text(self):
        """Determine Text. Ouputs list of tuples."""

        living_cats = [
            i for i in Cat.all_cats.values() if i.status.alive_in_player_clan
        ]
        living_meds = []
        living_mediators = []
        living_warriors = []
        living_apprentices = []
        living_kits = []
        living_elders = []
        for cat in living_cats:
            if cat.status.rank == CatRank.MEDICINE_CAT:
                living_meds.append(cat)
            elif cat.status.rank == CatRank.WARRIOR:
                living_warriors.append(cat)
            elif cat.status.rank == CatRank.MEDIATOR:
                living_mediators.append(cat)
            elif cat.status.rank.is_any_apprentice_rank():
                living_apprentices.append(cat)
            elif cat.status.rank.is_baby():
                living_kits.append(cat)
            elif cat.status.rank == CatRank.ELDER:
                living_elders.append(cat)

        # Find Queens:
        queen_dict, living_kits = get_alive_clan_queens(living_cats)

        # Remove queens from warrior or elder lists, if they are there.  Let them stay on any other lists.
        for q in queen_dict:
            queen = Cat.fetch_cat(q)
            if not queen:
                continue
            if queen in living_warriors:
                living_warriors.remove(queen)
            elif queen in living_elders:
                living_elders.remove(queen)

        # Clan Leader Box:
        # Pull the Clan leaders
        outputs = []
        if game.clan.leader and game.clan.leader.status.alive_in_player_clan:
            outputs.append(
                [
                    f"<b><u>{i18n.t('general.leader', count=1).upper()}</u></b>",
                    self.generate_one_entry(game.clan.leader),
                ]
            )

        # Deputy Box:
        if game.clan.deputy and game.clan.deputy.status.alive_in_player_clan:
            outputs.append(
                [
                    f"<b><u>{i18n.t('general.deputy', count=1).upper()}</u></b>",
                    self.generate_one_entry(game.clan.deputy),
                ]
            )

        # Medicine Cat Box:
        if living_meds:
            _box = ["", ""]
            _box[
                0
            ] = f"<b><u>{i18n.t('general.medicine cat', count=len(living_meds)).upper()}</u></b>"

            _box[1] = "\n".join([self.generate_one_entry(i) for i in living_meds])
            outputs.append(_box)

        # Mediator Box:
        if living_mediators:
            _box = ["", ""]
            _box[
                0
            ] = f"<b><u>{i18n.t('general.mediator', count=len(living_mediators)).upper()}</u></b>"

            _box[1] = "\n".join([self.generate_one_entry(i) for i in living_mediators])
            outputs.append(_box)

        # Warrior Box:
        if living_warriors:
            _box = ["", ""]
            _box[
                0
            ] = f"<b><u>{i18n.t('general.warrior', count=len(living_warriors)).upper()}</u></b>"

            _box[1] = "\n".join([self.generate_one_entry(i) for i in living_warriors])
            outputs.append(_box)

        # Apprentice Box:
        if living_apprentices:
            _box = ["", ""]
            _box[0] = f"<b><u>{i18n.t('general.apprentice', count=2).upper()}</u></b>"

            _box[1] = "\n".join(
                [self.generate_one_entry(i) for i in living_apprentices]
            )
            outputs.append(_box)

        # Queens and Kits Box:
        if queen_dict or living_kits:
            _box = ["", ""]
            _box[
                0
            ] = f"<b><u>{i18n.t('general.queen', count=2).upper()} AND {i18n.t('general.kit', count=2).upper()}</u></b>"

            # This one is a bit different.  First all the queens, and the kits they are caring for.
            all_entries = []
            for q in queen_dict:
                queen = Cat.fetch_cat(q)
                if not queen:
                    continue
                kittens = []
                for k in queen_dict[q]:
                    kittens += [
                        event_text_adjust(
                            Cat, f"{k.name} - {k.describe_cat(short=True)}", main_cat=k
                        )
                    ]
                if len(kittens) == 1:
                    kittens = i18n.t(
                        "screens.allegiances.caring_for",
                        kitten=kittens[0],
                        count=len(kittens),
                    )
                else:
                    kittens = i18n.t(
                        "screens.allegiances.caring_for",
                        kitten_list=", ".join(kittens[:-1]),
                        last_kitten=kittens[-1],
                        count=len(kittens),
                    )
                all_entries.append(self.generate_one_entry(queen, kittens))

            # Now kittens without carers
            for k in living_kits:
                all_entries.append(
                    event_text_adjust(
                        Cat,
                        f"{str(k.name).upper()} - {k.describe_cat(short=True)}",
                        main_cat=k,
                    )
                )

            _box[1] = "\n".join(all_entries)
            outputs.append(_box)

        # Elder Box:
        if living_elders:
            _box = ["", ""]
            _box[0] = f"<b><u>{i18n.t('general.elder', count=2).upper()}</u></b>"

            _box[1] = "\n".join([self.generate_one_entry(i) for i in living_elders])
            outputs.append(_box)

        return outputs
