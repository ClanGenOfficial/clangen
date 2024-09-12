import pygame
import pygame_gui

from scripts.cat.cats import Cat

from scripts.game_structure.game_essentials import game, screen_x, screen_y, MANAGER
from scripts.game_structure.ui_elements import (
    UISpriteButton,
    UIImageButton,
    UITextBoxTweaked
)
from scripts.utility import (
    get_text_box_theme,
    scale,
    get_alive_status_cats,
    shorten_text_to_fit,
    get_alive_clan_queens,
)
from .Screens import Screens
from ..conditions import get_amount_cat_for_one_medic, medical_cats_condition_fulfilled


class AllegiancesScreen(Screens):
    allegiance_list = []

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.menu_button_pressed(event)
            self.mute_button_pressed(event)


    def on_use(self):
        pass

    def screen_switches(self):
        # Heading
        self.heading = pygame_gui.elements.UITextBox(
            f"{game.clan.name}Clan Allegiances",
            scale(pygame.Rect((390, 230), (800, 80))),
            object_id=get_text_box_theme("#text_box_34_horizcenter"),
            manager=MANAGER,
        )

        # Set Menu Buttons.
        self.show_menu_buttons()
        self.show_mute_buttons()
        self.set_disabled_menu_buttons(["allegiances"])
        self.update_heading_text(f"{game.clan.name}Clan")
        allegiance_list = self.get_allegiances_text()

        self.scroll_container = pygame_gui.elements.UIScrollingContainer(
            scale(pygame.Rect((100, 330), (1430, 1000))),
            allow_scroll_x=False,
            manager=MANAGER,
        )

        self.ranks_boxes = []
        self.names_boxes = []
        y_pos = 0
        for x in allegiance_list:
            self.ranks_boxes.append(
                pygame_gui.elements.UITextBox(
                    x[0],
                    scale(pygame.Rect((0, y_pos), (300, -1))),
                    object_id=get_text_box_theme("#text_box_30_horizleft"),
                    container=self.scroll_container,
                    manager=MANAGER,
                )
            )
            self.ranks_boxes[-1].disable()

            self.names_boxes.append(
                pygame_gui.elements.UITextBox(
                    x[1],
                    scale(pygame.Rect((300, y_pos), (1060, -1))),
                    object_id=get_text_box_theme("#text_box_30_horizleft"),
                    container=self.scroll_container,
                    manager=MANAGER,
                )
            )
            self.names_boxes[-1].disable()

            y_pos += 1400 * self.names_boxes[-1].get_relative_rect()[3] / screen_y

        self.scroll_container.set_scrollable_area_dimensions(
            (1360 / 1600 * screen_x, y_pos / 1400 * screen_y)
        )

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

    def generate_one_entry(self, cat, extra_details=""):
        """Extra Details will be placed after the cat description, but before the apprentice (if they have one. )"""
        output = f"{str(cat.name).upper()} - {cat.describe_cat()} {extra_details}"

        if len(cat.apprentice) > 0:
            if len(cat.apprentice) == 1:
                output += "\n      APPRENTICE: "
            else:
                output += "\n      APPRENTICES: "
            output += ", ".join(
                [
                    str(Cat.fetch_cat(i).name).upper()
                    for i in cat.apprentice
                    if Cat.fetch_cat(i)
                ]
            )

        return output

    def get_allegiances_text(self):
        """Determine Text. Ouputs list of tuples."""

        living_cats = [i for i in Cat.all_cats.values() if not (i.dead or i.outside)]
        living_meds = []
        living_mediators = []
        living_warriors = []
        living_apprentices = []
        living_kits = []
        living_elders = []
        for cat in living_cats:
            if cat.status == "medicine cat":
                living_meds.append(cat)
            elif cat.status == "warrior":
                living_warriors.append(cat)
            elif cat.status == "mediator":
                living_mediators.append(cat)
            elif cat.status in [
                "apprentice",
                "medicine cat apprentice",
                "mediator apprentice",
            ]:
                living_apprentices.append(cat)
            elif cat.status in ["kitten", "newborn"]:
                living_kits.append(cat)
            elif cat.status == "elder":
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
        if game.clan.leader and not (game.clan.leader.dead or game.clan.leader.outside):
            outputs.append(
                ["<b><u>LEADER</u></b>", self.generate_one_entry(game.clan.leader)]
            )

        # Deputy Box:
        if game.clan.deputy and not (game.clan.deputy.dead or game.clan.deputy.outside):
            outputs.append(
                ["<b><u>DEPUTY</u></b>", self.generate_one_entry(game.clan.deputy)]
            )

        # Medicine Cat Box:
        if living_meds:
            _box = ["", ""]
            if len(living_meds) == 1:
                _box[0] = "<b><u>MEDICINE CAT</u></b>"
            else:
                _box[0] = "<b><u>MEDICINE CATS</u></b>"

            _box[1] = "\n".join([self.generate_one_entry(i) for i in living_meds])
            outputs.append(_box)

        # Mediator Box:
        if living_mediators:
            _box = ["", ""]
            if len(living_mediators) == 1:
                _box[0] = "<b><u>MEDIATOR</u></b>"
            else:
                _box[0] = "<b><u>MEDIATORS</u></b>"

            _box[1] = "\n".join([self.generate_one_entry(i) for i in living_mediators])
            outputs.append(_box)

        # Warrior Box:
        if living_warriors:
            _box = ["", ""]
            if len(living_warriors) == 1:
                _box[0] = "<b><u>WARRIOR</u></b>"
            else:
                _box[0] = "<b><u>WARRIORS</u></b>"

            _box[1] = "\n".join([self.generate_one_entry(i) for i in living_warriors])
            outputs.append(_box)

        # Apprentice Box:
        if living_apprentices:
            _box = ["", ""]
            if len(living_apprentices) == 1:
                _box[0] = "<b><u>APPRENTICE</u></b>"
            else:
                _box[0] = "<b><u>APPRENTICES</u></b>"

            _box[1] = "\n".join(
                [self.generate_one_entry(i) for i in living_apprentices]
            )
            outputs.append(_box)

        # Queens and Kits Box:
        if queen_dict or living_kits:
            _box = ["", ""]
            _box[0] = "<b><u>QUEENS AND KITS</u></b>"

            # This one is a bit different.  First all the queens, and the kits they are caring for.
            all_entries = []
            for q in queen_dict:
                queen = Cat.fetch_cat(q)
                if not queen:
                    continue
                kittens = []
                for k in queen_dict[q]:
                    kittens += [f"{k.name} - {k.describe_cat(short=True)}"]
                if len(kittens) == 1:
                    kittens = f" <i>(caring for {kittens[0]})</i>"
                else:
                    kittens = f" <i>(caring for {', '.join(kittens[:-1])}, and {kittens[-1]})</i>"

                all_entries.append(self.generate_one_entry(queen, kittens))

            # Now kittens without carers
            for k in living_kits:
                all_entries.append(
                    f"{str(k.name).upper()} - {k.describe_cat(short=True)}"
                )

            _box[1] = "\n".join(all_entries)
            outputs.append(_box)

        # Elder Box:
        if living_elders:
            _box = ["", ""]
            if len(living_elders) == 1:
                _box[0] = "<b><u>ELDER</u></b>"
            else:
                _box[0] = "<b><u>ELDERS</u></b>"

            _box[1] = "\n".join([self.generate_one_entry(i) for i in living_elders])
            outputs.append(_box)

        return outputs
