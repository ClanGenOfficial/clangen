import random
import traceback
from copy import deepcopy

import pygame
import pygame_gui
from pygame_gui.core import ObjectID

from scripts.cat.cats import Cat
from scripts.game_structure import image_cache, constants
from scripts.game_structure.game.settings import game_settings_save, game_setting_get
from scripts.game_structure.game_essentials import (
    game,
)
from scripts.game_structure.ui_elements import (
    UISpriteButton,
    UIImageButton,
    UISurfaceImageButton,
)
from scripts.game_structure.windows import SaveError
from scripts.utility import (
    ui_scale,
    ui_scale_dimensions,
    get_current_season,
    ui_scale_value,
)
from .Screens import Screens
from ..cat.save_load import save_cats
from ..clan_package.settings import get_clan_setting
from ..clan_package.settings.clan_settings import set_clan_setting
from ..game_structure.game.switches import switch_set_value, switch_get_value, Switch
from ..cat.enums import CatRank
from ..ui.generate_button import ButtonStyles, get_button_dict


class ClanScreen(Screens):
    max_sprites_displayed = (
        400  # we don't want 100,000 sprites rendering at once. 400 is enough.
    )
    cat_buttons = []

    def __init__(self, name=None):
        super().__init__(name)
        self.cats_in_camp = []
        self.taken_spaces = {}
        self.show_den_labels_text = None
        self.show_den_labels = None
        self.show_den_text = None
        self.label_toggle = None
        self.app_den_label = None
        self.clearing_label = None
        self.nursery_label = None
        self.elder_den_label = None
        self.med_den_label = None
        self.leader_den_label = None
        self.warrior_den_label = None
        self.layout = None

    def on_use(self):
        if not get_clan_setting("backgrounds"):
            self.set_bg(None)
        super().on_use()

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)
            if event.ui_element == self.save_button:
                try:
                    self.save_button_saving_state.show()
                    self.save_button.disable()
                    save_cats(switch_get_value(Switch.clan_name), Cat, game)
                    game.clan.save_clan()
                    game.clan.save_pregnancy(game.clan)
                    game.save_events()
                    game_settings_save(self)
                    switch_set_value(Switch.saved_clan, True)
                    self.update_buttons_and_text()
                except RuntimeError:
                    SaveError(traceback.format_exc())
                    self.change_screen("start screen")
            if event.ui_element in self.cat_buttons:
                switch_set_value(Switch.cat, event.ui_element.return_cat_id())
                self.change_screen("profile screen")
            if event.ui_element == self.label_toggle:
                set_clan_setting("den labels", not get_clan_setting("den_labels"))
                self.update_buttons_and_text()
            if event.ui_element == self.med_den_label:
                self.change_screen("med den screen")
            if event.ui_element == self.clearing_label:
                self.change_screen("clearing screen")
            if event.ui_element == self.warrior_den_label:
                self.change_screen("warrior den screen")
            if event.ui_element == self.leader_den_label:
                self.change_screen("leader den screen")
            else:
                self.menu_button_pressed(event)

        elif event.type == pygame.KEYDOWN and game_setting_get("keybinds"):
            if event.key == pygame.K_RIGHT:
                self.change_screen("list screen")
            elif event.key == pygame.K_LEFT:
                self.change_screen("events screen")
            elif event.key == pygame.K_SPACE:
                self.save_button_saving_state.show()
                self.save_button.disable()
                save_cats(switch_get_value(Switch.clan_name), Cat, game)
                game.clan.save_clan()
                game.clan.save_pregnancy(game.clan)
                game.save_events()
                game_settings_save(self)
                switch_set_value(Switch.saved_clan, True)
                self.update_buttons_and_text()

    def screen_switches(self):
        super().screen_switches()
        self.show_mute_buttons()
        self.update_camp_bg()
        switch_set_value(Switch.cat, None)
        if game.clan.biome + game.clan.camp_bg in constants.LAYOUTS:
            self.layout = constants.LAYOUTS[game.clan.biome + game.clan.camp_bg]
        else:
            self.layout = constants.LAYOUTS["default"]

        if "cat_shading" not in self.layout:
            self.layout["cat_shading"] = constants.LAYOUTS["default"]["cat_shading"]

        self.choose_cat_positions()

        self.set_disabled_menu_buttons(["camp_screen"])
        self.update_heading_text(f"{game.clan.name}Clan")
        self.show_menu_buttons()

        # Creates and places the cat sprites.
        self.cat_buttons = []  # To contain all the buttons.

        # We have to convert the positions to something pygame_gui buttons will understand
        # This should be a temp solution. We should change the code that determines positions.
        i = 0
        all_positions = list(self.taken_spaces.values())
        used_positions = all_positions.copy()

        layers = []
        for x in self.cats_in_camp:
            layers.append(2)
            place = self.taken_spaces[x.ID]
            layers[-1] += all_positions.count(place) - used_positions.count(place)
            used_positions.remove(place)

            try:
                image = x.sprite.convert_alpha()
                try:
                    blend_layer = (
                        self.game_bgs[self.active_bg]
                        .subsurface(ui_scale(pygame.Rect(tuple(x.placement), (50, 50))))
                        .convert_alpha()
                    )
                    blend_layer = pygame.transform.box_blur(
                        blend_layer, self.layout["cat_shading"]["blur"]
                    )
                except ValueError:
                    x_diff = ui_scale_value(
                        50 + (x.placement[0] if x.placement[0] < 0 else 0)
                    )
                    y_diff = ui_scale_value(
                        50 + (x.placement[1] if x.placement[1] < 0 else 0)
                    )
                    avg_layer = self.game_bgs[self.active_bg].subsurface(
                        ui_scale(
                            pygame.Rect(
                                (
                                    x.placement[0] if x.placement[0] > 0 else 0,
                                    x.placement[1] if x.placement[1] > 0 else 0,
                                ),
                                (x_diff, y_diff),
                            )
                        )
                    )
                    blend_layer = pygame.Surface(ui_scale_dimensions((50, 50)))
                    blend_layer.fill(pygame.transform.average_color(avg_layer))

                sprite = image.copy()
                sprite.fill((255, 255, 255, 255), special_flags=pygame.BLEND_RGB_MAX)
                sprite.blit(blend_layer, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                image.set_alpha(self.layout["cat_shading"]["blend_strength"])
                sprite.blit(image, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
                sprite.set_alpha(255)

                self.cat_buttons.append(
                    UISpriteButton(
                        ui_scale(pygame.Rect(tuple(x.placement), (50, 50))),
                        sprite,
                        mask=x.sprite_mask,
                        cat_id=x.ID,
                        starting_height=layers[-1],
                    )
                )
            except:
                traceback.print_exc()
                print(f"ERROR: placing {x.name}'s sprite on Clan page")

        # Den Labels
        # Redo the locations, so that it uses layout on the Clan page
        self.warrior_den_label = UISurfaceImageButton(
            ui_scale(pygame.Rect(self.layout["warrior den"], (121, 28))),
            "screens.core.warriors_den",
            get_button_dict(ButtonStyles.ROUNDED_RECT, (121, 28)),
            object_id=ObjectID(class_id="@buttonstyles_rounded_rect", object_id=None),
            starting_height=2,
        )
        self.leader_den_label = UISurfaceImageButton(
            ui_scale(pygame.Rect(self.layout["leader den"], (112, 28))),
            "screens.core.leader_den",
            get_button_dict(ButtonStyles.ROUNDED_RECT, (112, 28)),
            object_id=ObjectID(class_id="@buttonstyles_rounded_rect", object_id=None),
            starting_height=2,
        )
        self.med_den_label = UISurfaceImageButton(
            ui_scale(pygame.Rect(self.layout["medicine den"], (151, 28))),
            "screens.core.medicine_cat_den",
            get_button_dict(ButtonStyles.ROUNDED_RECT, (151, 28)),
            object_id=ObjectID(class_id="@buttonstyles_rounded_rect", object_id=None),
            starting_height=2,
        )
        self.elder_den_label = UISurfaceImageButton(
            ui_scale(pygame.Rect(self.layout["elder den"], (103, 28))),
            "screens.core.elders_den",
            get_button_dict(ButtonStyles.ROUNDED_RECT, (103, 28)),
            object_id=ObjectID(class_id="@buttonstyles_rounded_rect", object_id=None),
        )
        self.elder_den_label.disable()
        self.nursery_label = UISurfaceImageButton(
            ui_scale(pygame.Rect(self.layout["nursery"], (80, 28))),
            "screens.core.nursery",
            get_button_dict(ButtonStyles.ROUNDED_RECT, (80, 28)),
            object_id=ObjectID(class_id="@buttonstyles_rounded_rect", object_id=None),
        )
        self.nursery_label.disable()

        self.clearing_label = UISurfaceImageButton(
            ui_scale(pygame.Rect(self.layout["clearing"], (81, 28))),
            "screens.core.clearing",
            get_button_dict(ButtonStyles.ROUNDED_RECT, (81, 28)),
            object_id=ObjectID(class_id="@buttonstyles_rounded_rect", object_id=None),
        )
        if game.clan.game_mode == "classic":
            self.clearing_label.disable()

        self.app_den_label = UISurfaceImageButton(
            ui_scale(pygame.Rect(self.layout["apprentice den"], (147, 28))),
            "screens.core.apprentices_den",
            get_button_dict(ButtonStyles.ROUNDED_RECT, (147, 28)),
            object_id=ObjectID(class_id="@buttonstyles_rounded_rect", object_id=None),
        )
        self.app_den_label.disable()

        # Draw the toggle and text
        self.show_den_labels = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((25, 641), (167, 34))),
            pygame.transform.scale(
                image_cache.load_image("resources/images/show_den_labels.png"),
                ui_scale_dimensions((167, 34)),
            ),
        )
        self.show_den_labels_text = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((60, 641), (130, 34))),
            "screens.clan.show_dens",
            object_id="@buttonstyles_rounded_rect",
        )
        self.show_den_labels.disable()
        self.label_toggle = UIImageButton(
            ui_scale(pygame.Rect((25, 641), (32, 32))),
            "",
            object_id="@checked_checkbox",
        )

        save_buttons = get_button_dict(ButtonStyles.SQUOVAL, (114, 30))
        save_buttons["normal"] = image_cache.load_image(
            "resources/images/buttons/save_clan.png"
        )
        self.save_button = UISurfaceImageButton(
            ui_scale(pygame.Rect(((343, 643), (114, 30)))),
            "buttons.save_clan",
            save_buttons,
            object_id="@buttonstyles_squoval",
            sound_id="save",
        )
        self.save_button.enable()
        self.save_button_saved_state = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 643), (114, 30))),
            "buttons.clan_saved",
            {
                "normal": pygame.transform.scale(
                    image_cache.load_image("resources/images/save_clan_saved.png"),
                    ui_scale_dimensions((114, 30)),
                )
            },
            object_id="@buttonstyles_squoval",
            anchors={"centerx": "centerx"},
        )
        self.save_button_saved_state.hide()
        self.save_button_saving_state = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 643), (114, 30))),
            "buttons.saving",
            {"normal": get_button_dict(ButtonStyles.SQUOVAL, (114, 30))["normal"]},
            object_id="@buttonstyles_squoval",
            anchors={"centerx": "centerx"},
        )
        self.save_button_saving_state.disable()
        self.save_button_saving_state.hide()

        self.update_buttons_and_text()

    def exit_screen(self):
        # removes the cat sprites.
        for button in self.cat_buttons:
            button.kill()
        self.cat_buttons = []

        self.taken_spaces.clear()
        self.cats_in_camp.clear()

        # Kill all other elements, and destroy the reference so they aren't hanging around
        self.save_button.kill()
        del self.save_button
        self.save_button_saved_state.kill()
        del self.save_button_saved_state
        self.save_button_saving_state.kill()
        del self.save_button_saving_state
        self.warrior_den_label.kill()
        del self.warrior_den_label
        self.leader_den_label.kill()
        del self.leader_den_label
        self.med_den_label.kill()
        del self.med_den_label
        self.elder_den_label.kill()
        del self.elder_den_label
        self.nursery_label.kill()
        del self.nursery_label
        self.clearing_label.kill()
        del self.clearing_label
        self.app_den_label.kill()
        del self.app_den_label
        self.label_toggle.kill()
        del self.label_toggle
        self.show_den_labels.kill()
        del self.show_den_labels
        self.show_den_labels_text.kill()
        del self.show_den_labels_text

        # reset save status
        switch_set_value(Switch.saved_clan, False)

    def update_camp_bg(self):
        light_dark = "dark" if game_setting_get("dark mode") else "light"

        camp_bg_base_dir = "resources/images/camp_bg/"
        leaves = ["newleaf", "greenleaf", "leafbare", "leaffall"]
        camp_nr = game.clan.camp_bg

        if camp_nr is None:
            camp_nr = "camp1"
            game.clan.camp_bg = camp_nr

        available_biome = ["Forest", "Mountainous", "Plains", "Beach"]
        biome = game.clan.biome
        if biome not in available_biome:
            biome = available_biome[0]
            game.clan.biome = biome
        biome = biome.lower()

        all_backgrounds = []
        for leaf in leaves:
            platform_dir = (
                f"{camp_bg_base_dir}/{biome}/{leaf}_{camp_nr}_{light_dark}.png"
            )
            all_backgrounds.append(platform_dir)

        self.add_bgs(
            {
                "Newleaf": pygame.transform.scale(
                    pygame.image.load(all_backgrounds[0]).convert(),
                    ui_scale_dimensions((800, 700)),
                ),
                "Greenleaf": pygame.transform.scale(
                    pygame.image.load(all_backgrounds[1]).convert(),
                    ui_scale_dimensions((800, 700)),
                ),
                "Leaf-bare": pygame.transform.scale(
                    pygame.image.load(all_backgrounds[2]).convert(),
                    ui_scale_dimensions((800, 700)),
                ),
                "Leaf-fall": pygame.transform.scale(
                    pygame.image.load(all_backgrounds[3]).convert(),
                    ui_scale_dimensions((800, 700)),
                ),
            },
            {
                "Newleaf": None,
                "Greenleaf": None,
                "Leaf-bare": None,
                "Leaf-fall": None,
            },
        )

        self.set_bg(get_current_season())

    def choose_nonoverlapping_positions(self, first_choices, dens, weights=None):
        if not weights:
            weights = [1] * len(dens)

        dens = dens.copy()

        chosen_index = random.choices(range(0, len(dens)), weights=weights, k=1)[0]
        first_chosen_den = dens[chosen_index]
        while True:
            chosen_den = dens[chosen_index]
            if first_choices[chosen_den]:
                pos = random.choice(first_choices[chosen_den])
                first_choices[chosen_den].remove(pos)
                just_pos = pos[0].copy()
                if pos not in first_choices[chosen_den]:
                    # Then this is the second cat to be places here, given an offset

                    # Offset based on the "tag" in pos[1]. If "y" is in the tag,
                    # the cat will be offset down. If "x" is in the tag, the behavior depends on
                    # the presence of the "y" tag. If "y" is not present, always shift the cat left or right
                    # if it is present, shift the cat left or right 3/4 of the time.
                    if "x" in pos[1] and ("y" not in pos[1] or random.getrandbits(2)):
                        just_pos[0] += 15 * random.choice([-1, 1])
                    if "y" in pos[1]:
                        just_pos[1] += 15
                return tuple(just_pos), pos[0]
            dens.pop(chosen_index)
            weights.pop(chosen_index)
            if not dens:
                break
            # Put finding the next index after the break condition, so it won't be done unless needed
            chosen_index = random.choices(range(0, len(dens)), weights=weights, k=1)[0]

        return None, None

    def choose_cat_positions(self):
        """Determines the positions of cat on the clan screen."""
        # These are the first choices. As positions are chosen, they are removed from the options to indicate they are
        # taken.
        first_choices = deepcopy(self.layout)

        all_dens = [
            "nursery place",
            "leader place",
            "elder place",
            "medicine place",
            "apprentice place",
            "clearing place",
            "warrior place",
        ]

        # Allow two cat in the same position.
        for x in all_dens:
            first_choices[x].extend(first_choices[x])

        for x in game.clan.clan_cats:
            if not Cat.all_cats[x].status.alive_in_player_clan:
                continue

            base_pos = None
            # Newborns are not meant to be placed. They are hiding.
            if (
                Cat.all_cats[x].status.rank == CatRank.NEWBORN
                or constants.CONFIG["fun"]["all_cats_are_newborn"]
            ):
                if (
                    constants.CONFIG["fun"]["all_cats_are_newborn"]
                    or constants.CONFIG["fun"]["newborns_can_roam"]
                ):
                    # Free them
                    [
                        Cat.all_cats[x].placement,
                        base_pos,
                    ] = self.choose_nonoverlapping_positions(
                        first_choices, all_dens, [1, 100, 1, 1, 1, 100, 50]
                    )
                else:
                    continue

            if Cat.all_cats[x].status.rank in (
                CatRank.APPRENTICE,
                CatRank.MEDIATOR_APPRENTICE,
            ):
                [
                    Cat.all_cats[x].placement,
                    base_pos,
                ] = self.choose_nonoverlapping_positions(
                    first_choices, all_dens, [1, 50, 1, 1, 100, 100, 1]
                )
            elif Cat.all_cats[x].status.rank == CatRank.DEPUTY:
                [
                    Cat.all_cats[x].placement,
                    base_pos,
                ] = self.choose_nonoverlapping_positions(
                    first_choices, all_dens, [1, 50, 1, 1, 1, 50, 1]
                )

            elif Cat.all_cats[x].status.rank == CatRank.ELDER:
                [
                    Cat.all_cats[x].placement,
                    base_pos,
                ] = self.choose_nonoverlapping_positions(
                    first_choices, all_dens, [1, 1, 2000, 1, 1, 1, 1]
                )
            elif Cat.all_cats[x].status.rank == CatRank.KITTEN:
                [
                    Cat.all_cats[x].placement,
                    base_pos,
                ] = self.choose_nonoverlapping_positions(
                    first_choices, all_dens, [60, 8, 1, 1, 1, 1, 1]
                )
            elif Cat.all_cats[x].status.rank.is_any_medicine_rank():
                [
                    Cat.all_cats[x].placement,
                    base_pos,
                ] = self.choose_nonoverlapping_positions(
                    first_choices, all_dens, [20, 20, 20, 400, 1, 1, 1]
                )
            elif Cat.all_cats[x].status.rank in (CatRank.WARRIOR, CatRank.MEDIATOR):
                [
                    Cat.all_cats[x].placement,
                    base_pos,
                ] = self.choose_nonoverlapping_positions(
                    first_choices, all_dens, [1, 1, 1, 1, 1, 60, 60]
                )
            elif Cat.all_cats[x].status.is_leader:
                [
                    Cat.all_cats[x].placement,
                    base_pos,
                ] = self.choose_nonoverlapping_positions(
                    first_choices, all_dens, [1, 200, 1, 1, 1, 1, 1]
                )
            if not Cat.all_cats[x].placement:
                # if a cat wasn't placed, it's because no spots remain
                break

            self.taken_spaces[Cat.all_cats[x].ID] = base_pos
            self.cats_in_camp.append(Cat.all_cats[x])

    def update_buttons_and_text(self):
        if switch_get_value(Switch.saved_clan):
            self.save_button_saving_state.hide()
            self.save_button_saved_state.show()
            self.save_button.disable()
        else:
            self.save_button.enable()

        self.label_toggle.kill()
        if get_clan_setting("den labels"):
            self.label_toggle = UIImageButton(
                ui_scale(pygame.Rect((25, 641), (34, 34))),
                "",
                starting_height=2,
                object_id="@checked_checkbox",
            )
            self.warrior_den_label.show()
            self.clearing_label.show()
            self.nursery_label.show()
            self.app_den_label.show()
            self.leader_den_label.show()
            self.med_den_label.show()
            self.elder_den_label.show()
        else:
            self.label_toggle = UIImageButton(
                ui_scale(pygame.Rect((25, 641), (34, 34))),
                "",
                starting_height=2,
                object_id="@unchecked_checkbox",
            )
            self.warrior_den_label.hide()
            self.clearing_label.hide()
            self.nursery_label.hide()
            self.app_den_label.hide()
            self.leader_den_label.hide()
            self.med_den_label.hide()
            self.elder_den_label.hide()
