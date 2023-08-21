import pygame
import pygame_gui

from .Screens import Screens

from scripts.cat.cats import Cat
from scripts.game_structure.image_button import UISpriteButton, UIImageButton, UITextBoxTweaked
from scripts.utility import get_text_box_theme, scale, get_med_cats, shorten_text_to_fit
from scripts.game_structure.game_essentials import game, screen_x, screen_y, MANAGER
from ..conditions import get_amount_cat_for_one_medic, medical_cats_condition_fulfilled


class AllegiancesScreen(Screens):
    allegiance_list = []

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.menu_button_pressed(event)

    def on_use(self):
        pass

    def screen_switches(self):
        # Heading
        self.heading = pygame_gui.elements.UITextBox(f'{game.clan.name}Clan Allegiances',
                                                     scale(pygame.Rect((390, 230), (800, 80))),
                                                     object_id=get_text_box_theme("#text_box_34_horizcenter")
                                                     , manager=MANAGER)

        # Set Menu Buttons.
        self.show_menu_buttons()
        self.set_disabled_menu_buttons(["allegiances"])
        self.update_heading_text(f'{game.clan.name}Clan')
        allegiance_list = self.get_allegiances_text()


        self.scroll_container = pygame_gui.elements.UIScrollingContainer(scale(pygame.Rect((100, 330), (1430, 1000)))
                                                                         , manager=MANAGER)
        
        self.ranks_boxes = []
        self.names_boxes = []
        y_pos = 0
        for x in allegiance_list:
            self.ranks_boxes.append(pygame_gui.elements.UITextBox(x[0],
                                   scale(pygame.Rect((0, y_pos), (300, -1))),
                                   object_id=get_text_box_theme("#text_box_30_horizleft"),
                                   container=self.scroll_container, manager=MANAGER))
            self.ranks_boxes[-1].disable()

            self.names_boxes.append(pygame_gui.elements.UITextBox(x[1],
                                    scale(pygame.Rect((300, y_pos), (1060, -1))),
                                    object_id=get_text_box_theme("#text_box_30_horizleft"),
                                    container=self.scroll_container, manager=MANAGER))
            self.names_boxes[-1].disable()
            
            y_pos += 1400 * self.names_boxes[-1].get_relative_rect()[3] / screen_y 

        
        self.scroll_container.set_scrollable_area_dimensions((1360 / 1600 * screen_x, y_pos / 1400 * screen_y))

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
    
    def generate_one_entry(self, cat, extra_details = ""):
            """ Extra Details will be placed after the cat description, but before the apprentice (if they have one. )"""
            output = f"{str(cat.name).upper()} - {cat.describe_cat()} {extra_details}"

            if len(cat.apprentice) > 0:
                if len(cat.apprentice) == 1:
                    output += "\n      APPRENTICE: "
                else:
                    output += "\n      APPRENTICES: "     
                output += ", ".join([str(Cat.fetch_cat(i).name).upper() for i in cat.apprentice if Cat.fetch_cat(i)])

            return output

    def get_allegiances_text(self):
        """Determine Text. Ouputs list of tuples. """

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
            elif cat.status in ["apprentice", "medicine cat apprentice", "mediator apprentice"]:
                living_apprentices.append(cat)
            elif cat.status in ["kitten", "newborn"]:
                living_kits.append(cat)
            elif cat.status == "elder":
                living_elders.append(cat)

        # Find Queens:
        queen_dict = {}
        for cat in living_kits.copy():
            parents = cat.get_parents()
            #Fetch parent object, only alive and not outside. 
            parents = [Cat.fetch_cat(i) for i in parents if Cat.fetch_cat(i) and not(Cat.fetch_cat(i).dead or Cat.fetch_cat(i).outside)]
            if not parents:
                continue
            
            if len(parents) == 1 or all(i.gender == "male" for i in parents) or parents[0].gender == "female":
                if parents[0].ID in queen_dict:
                    queen_dict[parents[0].ID].append(cat)
                    living_kits.remove(cat)
                else:
                    queen_dict[parents[0].ID] = [cat]
                    living_kits.remove(cat) 
            elif len(parents) == 2:
                if parents[1].ID in queen_dict:
                    queen_dict[parents[1].ID].append(cat)
                    living_kits.remove(cat)
                else:
                    queen_dict[parents[1].ID] = [cat]
                    living_kits.remove(cat) 

        # Remove queens from warrior or elder lists, if they are there.  Let them stay on any other lists. 
        for q in queen_dict:
            queen = Cat.fetch_cat(q)
            if not queen:
                continue
            if queen in living_warriors:
                living_warriors.remove(queen)
            elif queen in living_elders:
                living_elders.remove(queen)
            
        #Clan Leader Box:
        # Pull the Clan leaders
        outputs = []
        if game.clan.leader and not (game.clan.leader.dead or game.clan.leader.outside):
                outputs.append([
                    '<b><u>LEADER</u></b>',
                    self.generate_one_entry(game.clan.leader)
                ])

        # Deputy Box:
        if game.clan.deputy and not (game.clan.deputy.dead or game.clan.deputy.outside):
            outputs.append([
                '<b><u>DEPUTY</u></b>',
                self.generate_one_entry(game.clan.deputy)
            ])
        
        # Medicine Cat Box:
        if living_meds:
            _box = ["", ""]
            if len(living_meds) == 1:
                _box[0] = '<b><u>MEDICINE CAT</u></b>'
            else:
                _box[0] = '<b><u>MEDICINE CATS</u></b>'
            
            _box[1] = "\n".join([self.generate_one_entry(i) for i in living_meds])
            outputs.append(_box)
        
        # Mediator Box:
        if living_mediators:
            _box = ["", ""]
            if len(living_mediators) == 1:
                _box[0] = '<b><u>MEDIATOR</u></b>'
            else:
                _box[0] = '<b><u>MEDIATORS</u></b>'
            
            _box[1] = "\n".join([self.generate_one_entry(i) for i in living_mediators])
            outputs.append(_box)

         # Warrior Box:
        if living_warriors:
            _box = ["", ""]
            if len(living_warriors) == 1:
                _box[0] = '<b><u>WARRIOR</u></b>'
            else:
                _box[0] = '<b><u>WARRIORS</u></b>'
            
            _box[1] = "\n".join([self.generate_one_entry(i) for i in living_warriors])
            outputs.append(_box)
        
         # Apprentice Box:
        if living_apprentices:
            _box = ["", ""]
            if len(living_apprentices) == 1:
                _box[0] = '<b><u>APPRENTICE</u></b>'
            else:
                _box[0] = '<b><u>APPRENTICES</u></b>'
            
            _box[1] = "\n".join([self.generate_one_entry(i) for i in living_apprentices])
            outputs.append(_box)
        
         # Queens and Kits Box:
        if queen_dict or living_kits:
            _box = ["", ""]
            _box[0] = '<b><u>QUEENS AND KITS</u></b>'
            
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

            #Now kittens without carers
            for k in living_kits:
                all_entries.append(f"{str(k.name).upper()} - {k.describe_cat(short=True)}")

            _box[1] = "\n".join(all_entries)
            outputs.append(_box)

        # Elder Box:
        if living_elders:
            _box = ["", ""]
            if len(living_elders) == 1:
                _box[0] = '<b><u>ELDER</u></b>'
            else:
                _box[0] = '<b><u>ELDERS</u></b>'
            
            _box[1] = "\n".join([self.generate_one_entry(i) for i in living_elders])
            outputs.append(_box)

        return outputs

            
class MedDenScreen(Screens):
    cat_buttons = {}
    conditions_hover = {}
    cat_names = []

    def __init__(self, name=None):
        super().__init__(name)
        self.help_button = None
        self.log_box = None
        self.log_title = None
        self.log_tab = None
        self.cats_tab = None
        self.hurt_sick_title = None
        self.display_med = None
        self.med_cat = None
        self.minor_tab = None
        self.out_den_tab = None
        self.in_den_tab = None
        self.injured_and_sick_cats = None
        self.minor_cats = None
        self.out_den_cats = None
        self.in_den_cats = None
        self.meds_messages = None
        self.current_med = None
        self.cat_bg = None
        self.last_page = None
        self.next_page = None
        self.last_med = None
        self.next_med = None
        self.den_base = None
        self.med_info = None
        self.med_name = None
        self.current_page = None
        self.meds = None
        self.back_button = None

        self.tab_showing = self.in_den_tab
        self.tab_list = self.in_den_cats

        self.herbs = {}

        self.open_tab = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen('camp screen')
            elif event.ui_element == self.next_med:
                self.current_med += 1
                self.update_med_cat()
            elif event.ui_element == self.last_med:
                self.current_med -= 1
                self.update_med_cat()
            elif event.ui_element == self.next_page:
                self.current_page += 1
                self.update_sick_cats()
            elif event.ui_element == self.last_page:
                self.current_page -= 1
                self.update_sick_cats()
            elif event.ui_element == self.in_den_tab:
                self.in_den_tab.disable()
                self.tab_showing.enable()
                self.tab_list = self.in_den_cats
                self.tab_showing = self.in_den_tab
                self.update_sick_cats()
            elif event.ui_element == self.out_den_tab:
                self.tab_showing.enable()
                self.tab_list = self.out_den_cats
                self.tab_showing = self.out_den_tab
                self.out_den_tab.disable()
                self.update_sick_cats()
            elif event.ui_element == self.minor_tab:
                self.tab_showing.enable()
                self.tab_list = self.minor_cats
                self.tab_showing = self.minor_tab
                self.minor_tab.disable()
                self.update_sick_cats()
            elif event.ui_element in self.cat_buttons.values():
                cat = event.ui_element.return_cat_object()
                game.switches["cat"] = cat.ID
                self.change_screen('profile screen')
            elif event.ui_element == self.med_cat:
                cat = event.ui_element.return_cat_object()
                game.switches["cat"] = cat.ID
                self.change_screen('profile screen')
            elif event.ui_element == self.cats_tab:
                self.open_tab = "cats"
                self.cats_tab.disable()
                self.log_tab.enable()
                self.handle_tab_toggles()
            elif event.ui_element == self.log_tab:
                self.open_tab = "log"
                self.log_tab.disable()
                self.cats_tab.enable()
                self.handle_tab_toggles()

    def screen_switches(self):
        self.hide_menu_buttons()
        self.back_button = UIImageButton(scale(pygame.Rect((50, 50), (210, 60))), "", object_id="#back_button"
                                         , manager=MANAGER)
        self.next_med = UIImageButton(scale(pygame.Rect((1290, 556), (68, 68))), "", object_id="#arrow_right_button"
                                      , manager=MANAGER)
        self.last_med = UIImageButton(scale(pygame.Rect((1200, 556), (68, 68))), "", object_id="#arrow_left_button"
                                      , manager=MANAGER)

        if game.clan.game_mode != 'classic':
            self.help_button = UIImageButton(scale(pygame.Rect(
                (1450, 50), (68, 68))),
                "",
                object_id="#help_button", manager=MANAGER,
                tool_tip_text="Your medicine cats will gather herbs over each timeskip and during any patrols you send "
                              "them on. You can see what was gathered in the Log below! Your medicine cats will give"
                              " these to any hurt or sick cats that need them, helping those cats to heal quicker."
                              "<br><br>"
                              "Hover your mouse over the medicine den image to see what herbs your Clan has!",

            )
            self.last_page = UIImageButton(scale(pygame.Rect((660, 1272), (68, 68))), "", object_id="#arrow_left_button"
                                           , manager=MANAGER)
            self.next_page = UIImageButton(scale(pygame.Rect((952, 1272), (68, 68))), "",
                                           object_id="#arrow_right_button"
                                           , manager=MANAGER)

            self.hurt_sick_title = pygame_gui.elements.UITextBox(
                "Hurt & Sick Cats",
                scale(pygame.Rect((281, 820), (400, 60))),
                object_id=get_text_box_theme("#text_box_40_horizcenter"), manager=MANAGER
            )
            self.log_title = pygame_gui.elements.UITextBox(
                "Medicine Den Log",
                scale(pygame.Rect((281, 820), (400, 60))),
                object_id=get_text_box_theme("#text_box_40_horizcenter"), manager=MANAGER
            )
            self.log_title.hide()
            self.cat_bg = pygame_gui.elements.UIImage(scale(pygame.Rect
                                                            ((280, 880), (1120, 400))),
                                                      pygame.image.load(
                                                          "resources/images/sick_hurt_bg.png").convert_alpha()
                                                      , manager=MANAGER)
            self.cat_bg.disable()
            log_text = game.herb_events_list.copy()
            """if game.settings["fullscreen"]:
                img_path = "resources/images/spacer.png"
            else:
                img_path = "resources/images/spacer_small.png"""
            self.log_box = pygame_gui.elements.UITextBox(
                f"{f'<br>-------------------------------<br>'.join(log_text)}<br>",
                scale(pygame.Rect
                      ((300, 900), (1080, 360))),
                object_id="#text_box_26_horizleft_verttop_pad_14_0_10", manager=MANAGER
            )
            self.log_box.hide()
            self.cats_tab = UIImageButton(scale(pygame.Rect
                                                ((218, 924), (68, 150))),
                                          "",
                                          object_id="#hurt_sick_cats_button", manager=MANAGER
                                          )
            self.cats_tab.disable()
            self.log_tab = UIImageButton(scale(pygame.Rect
                                               ((218, 1104), (68, 128))),
                                         "",
                                         object_id="#med_den_log_button", manager=MANAGER
                                         )
            self.in_den_tab = UIImageButton(scale(pygame.Rect
                                                  ((740, 818), (150, 70))),
                                            "",
                                            object_id="#in_den_tab", manager=MANAGER)
            self.in_den_tab.disable()
            self.out_den_tab = UIImageButton(scale(pygame.Rect
                                                   ((920, 818), (224, 70))),
                                             "",
                                             object_id="#out_den_tab", manager=MANAGER)
            self.minor_tab = UIImageButton(scale(pygame.Rect
                                                 ((1174, 818), (140, 70))),
                                           "",
                                           object_id="#minor_tab", manager=MANAGER)
            self.tab_showing = self.in_den_tab

            self.in_den_cats = []
            self.out_den_cats = []
            self.minor_cats = []
            self.injured_and_sick_cats = []
            for the_cat in Cat.all_cats_list:
                if not the_cat.dead and not the_cat.outside and (the_cat.injuries or the_cat.illnesses):
                    self.injured_and_sick_cats.append(the_cat)
            for cat in self.injured_and_sick_cats:
                if cat.injuries:
                    for injury in cat.injuries:
                        if cat.injuries[injury]["severity"] != 'minor' and injury not in ["pregnant", 'recovering from birth',
                                                                                          "sprain", "lingering shock"]:
                            if cat not in self.in_den_cats:
                                self.in_den_cats.append(cat)
                            if cat in self.out_den_cats:
                                self.out_den_cats.remove(cat)
                            elif cat in self.minor_cats:
                                self.minor_cats.remove(cat)
                            break
                        elif injury in ['recovering from birth', "sprain", "lingering shock", "pregnant"] and cat not in self.in_den_cats:
                            if cat not in self.out_den_cats:
                                self.out_den_cats.append(cat)
                            if cat in self.minor_cats:
                                self.minor_cats.remove(cat)
                            break
                        elif cat not in (self.in_den_cats or self.out_den_cats):
                            if cat not in self.minor_cats:
                                self.minor_cats.append(cat)
                if cat.illnesses:
                    for illness in cat.illnesses:
                        if cat.illnesses[illness]["severity"] != 'minor' and illness != 'grief stricken':
                            if cat not in self.in_den_cats:
                                self.in_den_cats.append(cat)
                            if cat in self.out_den_cats:
                                self.out_den_cats.remove(cat)
                            elif cat in self.minor_cats:
                                self.minor_cats.remove(cat)
                            break
                        elif illness == 'grief stricken':
                            if cat not in self.in_den_cats:
                                if cat not in self.out_den_cats:
                                    self.out_den_cats.append(cat)
                            if cat in self.minor_cats:
                                self.minor_cats.remove(cat)
                            break
                        else:
                            if cat not in (self.in_den_cats and self.out_den_cats and self.minor_cats):
                                self.minor_cats.append(cat)
            self.tab_list = self.in_den_cats
            self.current_page = 1
            self.update_sick_cats()

        self.current_med = 1

        self.draw_med_den()
        self.update_med_cat()

        self.meds_messages = UITextBoxTweaked(
            "",
            scale(pygame.Rect((216, 620), (1200, 160))),
            object_id=get_text_box_theme("#text_box_30_horizcenter_vertcenter"),
            line_spacing=1
        )

        if self.meds:
            med_messages = []

            amount_per_med = get_amount_cat_for_one_medic(game.clan)
            number = medical_cats_condition_fulfilled(Cat.all_cats.values(), amount_per_med,
                                                      give_clanmembers_covered=True)
            if len(self.meds) == 1:
                insert = 'medicine cat'
            else:
                insert = 'medicine cats'
            meds_cover = f"Your {insert} can care for a Clan of up to {number} members, including themselves."

            if len(self.meds) >= 1 and number == 0:
                meds_cover = f"You have no medicine cats who are able to work. Your Clan will be at a higher risk of death and disease."

            herb_amount = sum(game.clan.herbs.values())
            med_concern = f"This should not appear."
            if herb_amount == 0:
                med_concern = f"The herb stores are empty and bare, this does not bode well."
            elif 0 < herb_amount <= 8:
                if len(self.meds) == 1:
                    med_concern = f"The medicine cat worries over the herb stores, they don't have nearly enough for the Clan."
                else:
                    med_concern = f"The medicine cats worry over the herb stores, they don't have nearly enough for the Clan."
            elif 8 < herb_amount <= 20:
                med_concern = f"The herb stores are small, but it's enough for now."
            elif 20 < herb_amount <= 30:
                if len(self.meds) == 1:
                    med_concern = f"The medicine cat is content with how many herbs they have stocked up."
                else:
                    med_concern = f"The medicine cats are content with how many herbs they have stocked up."
            elif 30 < herb_amount <= 50:
                if len(self.meds) == 1:
                    med_concern = f"The herb stores are overflowing and the medicine cat has little worry."
                else:
                    med_concern = f"The herb stores are overflowing and the medicine cats have little worry."
            elif 50 < herb_amount:
                if len(self.meds) == 1:
                    med_concern = f"StarClan has blessed them with plentiful herbs and the medicine cat sends their thanks to Silverpelt."
                else:
                    med_concern = f"StarClan has blessed them with plentiful herbs and the medicine cats send their thanks to Silverpelt."

            med_messages.append(meds_cover)
            med_messages.append(med_concern)
            self.meds_messages.set_text("<br>".join(med_messages))

        else:
            meds_cover = f"You have no medicine cats, your clan will be at higher risk of death and sickness."
            self.meds_messages.set_text(meds_cover)

    def handle_tab_toggles(self):
        if self.open_tab == "cats":
            self.log_title.hide()
            self.log_box.hide()

            self.hurt_sick_title.show()
            self.last_page.show()
            self.next_page.show()
            self.in_den_tab.show()
            self.out_den_tab.show()
            self.minor_tab.show()
            for cat in self.cat_buttons:
                self.cat_buttons[cat].show()
            for x in range(len(self.cat_names)):
                self.cat_names[x].show()
            for button in self.conditions_hover:
                self.conditions_hover[button].show()
        elif self.open_tab == "log":
            self.hurt_sick_title.hide()
            self.last_page.hide()
            self.next_page.hide()
            self.in_den_tab.hide()
            self.out_den_tab.hide()
            self.minor_tab.hide()
            for cat in self.cat_buttons:
                self.cat_buttons[cat].hide()
            for x in range(len(self.cat_names)):
                self.cat_names[x].hide()
            for button in self.conditions_hover:
                self.conditions_hover[button].hide()

            self.log_title.show()
            self.log_box.show()

    def update_med_cat(self):
        if self.med_cat:
            self.med_cat.kill()
        if self.med_info:
            self.med_info.kill()
        if self.med_name:
            self.med_name.kill()

        # get the med cats
        self.meds = get_med_cats(Cat, working=False)

        if not self.meds:
            all_pages = []
        else:
            all_pages = self.chunks(self.meds, 1)

        if self.current_med > len(all_pages):
            if len(all_pages) == 0:
                self.current_med = 1
            else:
                self.current_med = len(all_pages)

        if all_pages:
            self.display_med = all_pages[self.current_med - 1]
        else:
            self.display_med = []

        if len(all_pages) <= 1:
            self.next_med.disable()
            self.last_med.disable()
        else:
            if self.current_med >= len(all_pages):
                self.next_med.disable()
            else:
                self.next_med.enable()

            if self.current_med <= 1:
                self.last_med.disable()
            else:
                self.last_med.enable()

        for cat in self.display_med:
            self.med_cat = UISpriteButton(scale(pygame.Rect
                                                ((870, 330), (300, 300))),
                                          cat.sprite,
                                          cat_object=cat, manager=MANAGER)
            name = str(cat.name)
            short_name = shorten_text_to_fit(name, 275, 30)
            self.med_name = pygame_gui.elements.ui_label.UILabel(scale(pygame.Rect
                                                                       ((1050, 310), (450, 60))),
                                                                 short_name,
                                                                 object_id=get_text_box_theme("#text_box_30_horizcenter"), manager=MANAGER
                                                                 )
            self.med_info = UITextBoxTweaked(
                "",
                scale(pygame.Rect((1160, 370), (240, 240))),
                object_id=get_text_box_theme("#text_box_22_horizcenter"),
                line_spacing=1, manager=MANAGER
            )
            med_skill = cat.skills.skill_string(short=True)
            med_exp = f"exp: {cat.experience_level}"
            med_working = True
            if cat.not_working():
                med_working = False
            if med_working is True:
                work_status = "This cat can work"
            else:
                work_status = "This cat isn't able to work"
            info_list = [med_skill, med_exp, work_status]
            self.med_info.set_text("<br>".join(info_list))

    def update_sick_cats(self):
        """
        set tab showing as either self.in_den_cats, self.out_den_cats, or self.minor_cats; whichever one you want to
        display and update
        """
        self.clear_cat_buttons()

        tab_list = self.tab_list

        if not tab_list:
            all_pages = []
        else:
            all_pages = self.chunks(tab_list, 10)

        if self.current_page > len(all_pages):
            if len(all_pages) == 0:
                self.current_page = 1
            else:
                self.current_page = len(all_pages)

        # Check for empty list (no cats)
        if all_pages:
            self.display_cats = all_pages[self.current_page - 1]
        else:
            self.display_cats = []

        # Update next and previous page buttons
        if len(all_pages) <= 1:
            self.next_page.disable()
            self.last_page.disable()
        else:
            if self.current_page >= len(all_pages):
                self.next_page.disable()
            else:
                self.next_page.enable()

            if self.current_page <= 1:
                self.last_page.disable()
            else:
                self.last_page.enable()

        pos_x = 350
        pos_y = 920
        i = 0
        for cat in self.display_cats:
            condition_list = []
            if cat.injuries:
                condition_list.extend(cat.injuries.keys())
            if cat.illnesses:
                condition_list.extend(cat.illnesses.keys())
            if cat.permanent_condition:
                for condition in cat.permanent_condition:
                    if cat.permanent_condition[condition]["moons_until"] == -2:
                        condition_list.extend(cat.permanent_condition.keys())
            conditions = ",<br>".join(condition_list)

            self.cat_buttons["able_cat" + str(i)] = UISpriteButton(scale(pygame.Rect
                                                                         ((pos_x, pos_y), (100, 100))),
                                                                   cat.sprite,
                                                                   cat_object=cat,
                                                                   manager=MANAGER,
                                                                   tool_tip_text=conditions,
                                                                   starting_height=2)


            name = str(cat.name)
            short_name = shorten_text_to_fit(name, 185, 30)
            self.cat_names.append(pygame_gui.elements.UITextBox(short_name,
                                                                scale(
                                                                    pygame.Rect((pos_x - 60, pos_y + 100), (220, 60))),
                                                                object_id="#text_box_30_horizcenter", manager=MANAGER))

            pos_x += 200
            if pos_x >= 1340:
                pos_x = 350
                pos_y += 160
            i += 1

    def draw_med_den(self):
        sorted_dict = dict(sorted(game.clan.herbs.items()))
        herbs_stored = sorted_dict.items()
        herb_list = []
        for herb in herbs_stored:
            amount = str(herb[1])
            type = str(herb[0].replace("_", " "))
            herb_list.append(f"{amount} {type}")
        if not herbs_stored:
            herb_list.append("Empty")
        if len(herb_list) <= 10:
            herb_display = "<br>".join(sorted(herb_list))

            self.den_base = UIImageButton(scale(pygame.Rect
                                                ((216, 190), (792, 448))),
                                          "",
                                          object_id="#med_cat_den_hover",
                                          tool_tip_text=herb_display, manager=MANAGER
                                          )
        else:
            count = 1
            holding_pairs = []
            pair = []
            added = False
            for y in range(len(herb_list)):
                if (count % 2) == 0:  # checking if count is an even number
                    count += 1
                    pair.append(herb_list[y])
                    holding_pairs.append("   -   ".join(pair))
                    pair.clear()
                    added = True
                    continue
                else:
                    pair.append(herb_list[y])
                    count += 1
                    added = False
            if added is False:
                holding_pairs.extend(pair)

            herb_display = "<br>".join(holding_pairs)
            self.den_base = UIImageButton(scale(pygame.Rect
                                                ((216, 190), (792, 448))),
                                          "",
                                          object_id="#med_cat_den_hover_big",
                                          tool_tip_text=herb_display, manager=MANAGER
                                          )

        herbs = game.clan.herbs
        for herb in herbs:
            if herb == 'cobwebs':
                self.herbs["cobweb1"] = pygame_gui.elements.UIImage(scale(pygame.Rect
                                                                          ((216, 190), (792, 448))),
                                                                    pygame.transform.scale(
                                                                        pygame.image.load(
                                                                            "resources/images/med_cat_den/cobweb1.png").convert_alpha(),
                                                                        (792, 448)
                                                                    ), manager=MANAGER)
                if herbs["cobwebs"] > 1:
                    self.herbs["cobweb2"] = pygame_gui.elements.UIImage(scale(pygame.Rect
                                                                              ((216, 190), (792, 448))),
                                                                        pygame.transform.scale(
                                                                            pygame.image.load(
                                                                                "resources/images/med_cat_den/cobweb2.png").convert_alpha(),
                                                                            (792, 448)
                                                                        ), manager=MANAGER)
                continue
            self.herbs[herb] = pygame_gui.elements.UIImage(scale(pygame.Rect
                                                                 ((216, 190), (792, 448))),
                                                           pygame.transform.scale(
                                                               pygame.image.load(
                                                                   f"resources/images/med_cat_den/{herb}.png").convert_alpha(),
                                                               (792, 448)
                                                           ), manager=MANAGER)

    def exit_screen(self):
        self.meds_messages.kill()
        self.last_med.kill()
        self.next_med.kill()
        self.den_base.kill()
        for herb in self.herbs:
            self.herbs[herb].kill()
        self.herbs = {}
        if self.med_info:
            self.med_info.kill()
        if self.med_name:
            self.med_name.kill()
        self.back_button.kill()
        if game.clan.game_mode != 'classic':
            self.help_button.kill()
            self.cat_bg.kill()
            self.last_page.kill()
            self.next_page.kill()
            self.in_den_tab.kill()
            self.out_den_tab.kill()
            self.minor_tab.kill()
            self.clear_cat_buttons()
            self.hurt_sick_title.kill()
            self.cats_tab.kill()
            self.log_tab.kill()
            self.log_title.kill()
            self.log_box.kill()
        if self.med_cat:
            self.med_cat.kill()

    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]

    def clear_cat_buttons(self):
        for cat in self.cat_buttons:
            self.cat_buttons[cat].kill()
        for button in self.conditions_hover:
            self.conditions_hover[button].kill()
        for x in range(len(self.cat_names)):
            self.cat_names[x].kill()

        self.cat_names = []
        self.cat_buttons = {}
