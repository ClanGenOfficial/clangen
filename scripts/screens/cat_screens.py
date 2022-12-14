from random import choice
from scripts.utility import update_sprite

from .base_screens import Screens, cat_profiles, draw_next_prev_cat_buttons

from scripts.utility import draw_large, get_text_box_theme
from scripts.game_structure.text import *
from scripts.game_structure.buttons import buttons
from scripts.cat.cats import Cat
from scripts.cat.pelts import collars, wild_accessories
import scripts.game_structure.image_cache as image_cache
import pygame_gui
from scripts.game_structure.image_button import UIImageButton, UISpriteButton, UITextBoxTweaked, UIImageTextBox

# ---------------------------------------------------------------------------- #
#             change how accessory info displays on cat profiles               #
# ---------------------------------------------------------------------------- #
def accessory_display_name(cat, accessory):
    accessory = cat.accessory

    if accessory is None:
        return ''
    acc_display = accessory.lower()

    if accessory is not None:
        if accessory in collars:
            collar_color = None
            if acc_display.startswith('crimson'):
                collar_color = 'red'
            elif acc_display.startswith('blue'):
                collar_color = 'blue'
            elif acc_display.startswith('yellow'):
                collar_color = 'yellow'
            elif acc_display.startswith('cyan'):
                collar_color = 'cyan'
            elif acc_display.startswith('red'):
                collar_color = 'orange'
            elif acc_display.startswith('lime'):
                collar_color = 'lime'
            elif acc_display.startswith('green'):
                collar_color = 'green'
            elif acc_display.startswith('rainbow'):
                collar_color = 'rainbow'
            elif acc_display.startswith('black'):
                collar_color = 'black'
            elif acc_display.startswith('spikes'):
                collar_color = 'spiky'
            elif acc_display.startswith('pink'):
                collar_color = 'pink'
            elif acc_display.startswith('purple'):
                collar_color = 'purple'
            elif acc_display.startswith('multi'):
                collar_color = 'multi'
            if acc_display.endswith('bow') and not acc_display == 'rainbow':
                acc_display = collar_color + ' bow'
            elif acc_display.endswith('bell'):
                acc_display = collar_color + ' bell collar'
            else:
                acc_display = collar_color + ' collar'

    elif accessory in wild_accessories:
        if acc_display == 'blue feathers':
            acc_display = 'crow feathers'
        elif acc_display == 'red feathers':
            acc_display = 'cardinal feathers'
        else:
            acc_display = acc_display
    else:
        acc_display = acc_display
    if accessory is None:
        acc_display = None
    return acc_display


# ---------------------------------------------------------------------------- #
#               assigns backstory blurbs to the backstory                      #
# ---------------------------------------------------------------------------- #
def bs_blurb_text(cat, backstory=None):
    backstory = cat.backstory
    bs_blurb = None
    if backstory is None:
        bs_blurb = "This cat was born into the clan where they currently reside."
    if backstory == 'clan_founder':
        bs_blurb = "This cat is one of the founding members of the clan."
    if backstory == 'clanborn':
        bs_blurb = "This cat was born into the clan where they currently reside."
    if backstory == 'halfclan1':
        bs_blurb = "This cat was born into the clan, but one of their parents resides in another clan."
    if backstory == 'halfclan2':
        bs_blurb = "This cat was born in another clan, but chose to come to this clan to be with their other parent."
    if backstory == 'outsider_roots1':
        bs_blurb = "This cat was born into the clan, but one of their parents is an outsider that belongs to no clan."
    if backstory == 'outsider_roots2':
        bs_blurb = "This cat was born outside the clan, but came to live in the clan with their parent at a young age."
    if backstory == 'loner1':
        bs_blurb = "This cat joined the clan by choice after living life as a loner."
    if backstory == 'loner2':
        bs_blurb = "This cat used to live in a barn, but mostly stayed away from twolegs. They decided clanlife " \
                   "might be an interesting change of pace."
    if backstory == 'kittypet1':
        bs_blurb = "This cat joined the clan by choice after living life with twolegs as a kittypet."
    if backstory == 'kittypet2':
        bs_blurb = "This cat used to live on something called a “boat” with twolegs, but decided to join the clan."
    if backstory == 'rogue1':
        bs_blurb = "This cat joined the clan by choice after living life as a rogue."
    if backstory == 'rogue2':
        bs_blurb = "This cat used to live in a twolegplace, scrounging for what they could find. They thought " \
                   "the clan might offer them more security."
    if backstory == 'abandoned1':
        bs_blurb = "This cat was found by the clan as a kit and has been living with them ever since."
    if backstory == 'abandoned2':
        bs_blurb = "This cat was born into a kittypet life, but was brought to the clan as a kit and has lived " \
                   "here ever since."
    if backstory == 'abandoned3':
        bs_blurb = "This cat was born into another clan, but they were left here as a kit for the clan to raise."
    if backstory == 'medicine_cat':
        bs_blurb = "This cat was once a medicine cat in another clan."
    if backstory == 'otherclan':
        bs_blurb = "This cat was born into another clan, but came to this clan by choice."
    if backstory == 'otherclan2':
        bs_blurb = "This cat was unhappy in their old clan and decided to come here instead."
    if backstory == 'ostracized_warrior':
        bs_blurb = "This cat was ostracized from their old clan, but no one really knows why."
    if backstory == 'disgraced':
        bs_blurb = "This cat was cast out of their old clan for some transgression that they’re not keen on " \
                   "talking about."
    if backstory == 'retired_leader':
        bs_blurb = "This cat used to be the leader of another clan before deciding they needed a change of scenery " \
                   "after leadership became too much.  They returned their nine lives and let their deputy " \
                   "take over before coming here."
    if backstory == 'refugee':
        bs_blurb = "This cat came to this clan after fleeing from their former clan and the tyrannical " \
                   "leader that had taken over."
    if backstory == 'tragedy_survivor':
        bs_blurb = "Something horrible happened to this cat's previous clan. They refuse to speak about it."
    return bs_blurb


# ---------------------------------------------------------------------------- #
#             change how backstory info displays on cat profiles               #
# ---------------------------------------------------------------------------- #
def backstory_text(cat):
    backstory = cat.backstory
    if backstory is None:
        return ''
    bs_display = backstory
    if bs_display == 'clanborn':
        bs_display = 'clanborn'
    elif bs_display == 'clan_founder':
        bs_display = 'clan founder'
    elif bs_display in ['halfclan1', 'halfclan2']:
        bs_display = 'half-clan'
    elif bs_display in ['outsider_roots1', 'outsider_roots2']:
        bs_display = 'outsider roots'
    elif bs_display in ['loner1', 'loner2']:
        bs_display = 'formerly a loner'
    elif bs_display in ['kittypet1', 'kittypet2']:
        bs_display = 'formerly a kittypet'
    elif bs_display in ['rogue1', 'rogue2']:
        bs_display = 'formerly a rogue'
    elif bs_display in ['abandoned1', 'abandoned2', 'abandoned3']:
        bs_display = 'formerly abandoned'
    elif bs_display == 'medicine_cat':
        bs_display = 'formerly a medicine cat'
    elif bs_display in ['otherclan', 'otherclan2']:
        bs_display = 'formerly from another clan'
    elif bs_display == 'ostracized_warrior':
        bs_display = 'ostracized warrior'
    elif bs_display == 'disgraced':
        if cat.status == 'medicine cat':
            bs_display = 'disgraced medicine cat'
        elif cat.status in ['warrior', 'elder']:
            bs_display = 'disgraced deputy'
    elif bs_display == 'retired_leader':
        bs_display = 'retired leader'
    elif bs_display == 'refugee':
        bs_display = 'refugee'
    elif bs_display == 'tragedy_survivor':
        bs_display = 'survivor of a tragedy'
    if bs_display == None:
        bs_display = None
    else:
        return bs_display


# ---------------------------------------------------------------------------- #
#                               Profile Screen                                 #
# ---------------------------------------------------------------------------- #
class ProfileScreen(Screens):
    # UI Images
    backstory_tab = image_cache.load_image("resources/images/backstory_bg.png").convert_alpha()

    # Keep track of current tabs open. Can be used to keep tabs open when pages are switched, and
    #   helps with exiting the screen
    default_sub_tab = 'relation'
    open_tab = None
    open_sub_tab = default_sub_tab

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen(game.last_screen_forProfile)
            elif event.ui_element == self.previous_cat_button:
                self.clear_profile()
                game.switches['cat'] = self.previous_cat
                self.build_profile()
                self.update_disabled_buttons_and_text()
            elif event.ui_element == self.next_cat_button:
                self.clear_profile()
                game.switches['cat'] = self.next_cat
                self.build_profile()
                self.update_disabled_buttons_and_text()
            elif event.ui_element == self.relations_tab_button:
                self.toggle_relations_tab()
            elif event.ui_element == self.roles_tab_button:
                self.toggle_roles_tab()
            elif event.ui_element == self.personal_tab_button:
                self.toggle_personal_tab()
            elif event.ui_element == self.dangerous_tab_button:
                self.toggle_dangerous_tab()
            elif event.ui_element == self.backstory_tab_button:
                self.toggle_backstory_tab()
            else:
                self.handle_tab_events(event)
                    
    def handle_tab_events(self, event):
        '''Handles buttons presses on the tabs'''
        if self.open_tab != None and self.open_tab != 'backstory':
            if event.ui_element == self.close_tab_button:
                self.close_current_tab()
        elif self.open_tab == None:
            #If no tab is open, don't check any further. 
            return
        
        #Relations Tab
        if self.open_tab == 'relations':
            if event.ui_element == self.see_family_button:
                self.change_screen('see kits screen')
            elif event.ui_element == self.see_relationships_button:
                self.change_screen('relationship screen')
            elif event.ui_element == self.choose_mate_button:
                self.change_screen('choose mate screen')
            elif event.ui_element == self.change_mentor_button:
                self.change_screen('choose mentor screen')
        #Roles Tab
        elif self.open_tab == 'roles':
            if event.ui_element == self.promote_leader_button:
                game.clan.new_leader(self.the_cat)
                self.clear_profile()
                self.build_profile()
                self.update_disabled_buttons_and_text()
            elif event.ui_element == self.toggle_deputy_button:
                if self.the_cat.status == 'warrior':
                    self.the_cat.status_change('deputy')
                    game.clan.deputy = self.the_cat
                elif self.the_cat.status == 'deputy':
                    self.the_cat.status_change('warrior')
                    game.clan.deputy = None
                self.clear_profile()
                self.build_profile()
                self.update_disabled_buttons_and_text()
            elif event.ui_element == self.toggle_med_button:
                if self.the_cat.status == 'medicine cat apprentice':
                    self.the_cat.status_change('apprentice')
                elif self.the_cat.status == "apprentice":
                    self.the_cat.status_change('medicine cat apprentice')
                elif self.the_cat.status == 'medicine cat':
                    self.the_cat.status_change('warrior')
                elif self.the_cat.status in ['warrior', 'elder']:
                    self.the_cat.status_change('medicine cat')
                self.clear_profile()
                self.build_profile()
                self.update_disabled_buttons_and_text()
        #Personal Tab
        elif self.open_tab == 'personal':
            if event.ui_element == self.change_name_button:
                self.change_screen('change name screen')
            elif event.ui_element == self.specify_gender_button:
                self.change_screen('change gender screen')
            elif event.ui_element == self.cis_trans_button:
                if self.the_cat.genderalign != "female" and self.the_cat.genderalign != "male":
                    self.the_cat.genderalign = self.the_cat.gender
                elif self.the_cat.gender == "male" and self.the_cat.genderalign in ['male', 'female']:
                    self.the_cat.genderalign = 'trans female'
                elif self.the_cat.gender == "female" and self.the_cat.genderalign in ['male', 'female']:
                    self.the_cat.genderalign = 'trans male'
                self.clear_profile()
                self.build_profile()
                self.update_disabled_buttons_and_text()
            elif event.ui_element == self.toggle_kits:
                if self.the_cat.no_kits:
                    self.the_cat.no_kits = False
                else:
                    self.the_cat.no_kits = True
                self.update_disabled_buttons_and_text()
        #Dangerous Tab
        elif self.open_tab == 'dangerous':
            if event.ui_element == self.kill_cat_button:
                if self.the_cat.status == 'leader':
                    game.clan.leader_lives -= 10
                self.the_cat.die()
                update_sprite(self.the_cat)
                self.clear_profile()
                self.build_profile()
                self.update_disabled_buttons_and_text()
            elif event.ui_element == self.exile_cat_button:
                if not self.the_cat.dead and not self.the_cat.exiled:
                    self.the_cat.exiled = True
                    self.the_cat.thought = "Is shocked that they have been exiled"
                    self.clear_profile()
                    self.build_profile()
                    self.update_disabled_buttons_and_text()
                if self.the_cat.dead:
                    self.the_cat.df = True
                    self.the_cat.thought = "Is distraught after being sent to the Place of No Stars"
                    update_sprite(self.the_cat)
                self.clear_profile()
                self.build_profile()
                self.update_disabled_buttons_and_text()             
    
    def screen_switches(self):
        self.the_cat = Cat.all_cats.get(game.switches['cat'])

        #Set-up the menu buttons, which appear on all cat profile images. 
        self.next_cat_button = UIImageButton(pygame.Rect((622,25),(153,30)), "", object_id = "#next_cat_button")
        self.previous_cat_button = UIImageButton(pygame.Rect((25,25),(153,30)), "", object_id = "#previous_cat_button")
        self.back_button = UIImageButton(pygame.Rect((25,60),(105, 30)), "", object_id = "#back_button")
        self.relations_tab_button = UIImageButton(pygame.Rect((48, 420),(176, 30)), "", object_id = "#relations_tab_button")
        self.roles_tab_button = UIImageButton(pygame.Rect((224,420),(176,30)),"", object_id = "#roles_tab_button")
        self.personal_tab_button = UIImageButton(pygame.Rect((400,420),(176,30)), "", object_id = "#personal_tab_button")
        self.dangerous_tab_button =  UIImageButton(pygame.Rect((576, 420),(176,30)), "", object_id = "#dangerous_tab_button")

        self.backstory_tab_button = UIImageButton(pygame.Rect((48, 622),(176, 30)), "", object_id = "#backstory_tab_button")
        self.placeholder_tab_2 = UIImageButton(pygame.Rect((224, 622),(176, 30)), "" , object_id = "#cat_tab_3_blank_button")
        self.placeholder_tab_2.disable()
        self.placeholder_tab_3 = UIImageButton(pygame.Rect((400, 622),(176, 30)), "", object_id = "#cat_tab_3_blank_button")
        self.placeholder_tab_3.disable()
        self.placeholder_tab_4 = UIImageButton(pygame.Rect((576, 622),(176, 30)), "", object_id = "#cat_tab_4_blank_button")
        self.placeholder_tab_4.disable()

        self.build_profile()

        self.hide_menu_buttons() #Menu buttons don't appear on the profile screen
        cat_profiles() 
        self.update_platform()

    def clear_profile(self):
        '''Clears all profile objects. '''
        self.cat_info_column1.kill()
        self.cat_info_column2.kill()
        self.cat_thought.kill()
        self.cat_name.kill()
        self.cat_image.kill()
        if self.background != None:
            self.background.kill()

    def exit_screen(self):
        self.clear_profile()
        self.back_button.kill()
        self.next_cat_button.kill()
        self.previous_cat_button.kill()
        self.relations_tab_button.kill()
        self.roles_tab_button.kill()
        self.personal_tab_button.kill()
        self.dangerous_tab_button.kill()
        self.backstory_tab_button.kill()
        self.placeholder_tab_2.kill()
        self.placeholder_tab_3.kill()
        self.placeholder_tab_4.kill()
        self.close_current_tab()

    def build_profile(self):
        '''Rebuild builds the cat profile. Run when you switch cats
            or for changes in the profile. 
            the_cat should be a Cat object. '''
        self.the_cat = Cat.all_cats.get(game.switches['cat'])
        # use these attributes to create differing profiles for starclan cats etc.
        is_sc_instructor = False
        is_df_instructor = False
        if self.the_cat.dead and game.clan.instructor.ID == self.the_cat.ID and self.the_cat.df is False:
            is_sc_instructor = True
        elif self.the_cat.dead and game.clan.instructor.ID == self.the_cat.ID and self.the_cat.df is True:
            is_df_instructor = True


        # Info in string
        cat_name = str(self.the_cat.name)  # name
        if self.the_cat.dead:
            cat_name += " (dead)"  # A dead cat will have the (dead) sign next to their name
        if is_sc_instructor:
            self.the_cat.thought = "Hello. I am here to guide the dead cats of " + game.clan.name + "Clan into StarClan."
        if is_df_instructor:
            self.the_cat.thought = "Hello. I am here to drag the dead cats of " + game.clan.name + "Clan into the Dark Forest."

        #Write cat name
        self.cat_name = pygame_gui.elements.UITextBox(cat_name, pygame.Rect((200,140),(400,40)),
                                                      object_id=get_text_box_theme("#cat_profile_name_box"))

        #Write cat thought
        self.cat_thought = pygame_gui.elements.UITextBox(self.the_cat.thought, pygame.Rect((100,170),(600,40)),
                                                         wrap_to_height=True,
                                                         object_id=get_text_box_theme("#cat_profile_thoughts_box"))

        self.cat_info_column1 = UITextBoxTweaked(self.generate_column1(self.the_cat), pygame.Rect((300, 230),(180,180)),
                                                 object_id= get_text_box_theme("#cat_profile_info_box"),
                                                 line_spacing = 0.95)
        self.cat_info_column2 = UITextBoxTweaked(self.generate_column2(self.the_cat), pygame.Rect((490, 230),(230,180)),
                                                 object_id= get_text_box_theme("#cat_profile_info_box"),
                                                 line_spacing = 0.95)

        #Set the cat backgrounds. 
        self.update_platform()
        if game.settings['backgrounds']:
            if game.clan.current_season == 'Newleaf':
                self.background = pygame_gui.elements.UIImage(pygame.Rect((55,200),(240, 210)) ,self.newleaf_plt)
            elif game.clan.current_season == 'Greenleaf':
                self.background = pygame_gui.elements.UIImage(pygame.Rect((55,200),(240, 210)) ,self.greenleaf_plt)
            elif game.clan.current_season == 'Leaf-bare':
                self.background = pygame_gui.elements.UIImage(pygame.Rect((55,200),(240, 210)) ,self.leafbare_plt)
            elif game.clan.current_season == 'Leaf-fall':
                self.background = pygame_gui.elements.UIImage(pygame.Rect((55,200),(240, 210)) ,self.leaffall_plt)
        else: 
            self.background = None

          #Create cat image object 
        self.cat_image = pygame_gui.elements.UIImage(pygame.Rect((100, 200),(150,150)), self.the_cat.large_sprite)

        #Determine where the next and previous cat buttons lead
        self.determine_previous_and_next_cat()

        #Disable and enable next and previous cat buttons as needed. 
        if self.next_cat == 0:
            self.next_cat_button.disable()
        else:
            self.next_cat_button.enable()

        if self.previous_cat == 0:
            self.previous_cat_button.disable()
        else:
            self.previous_cat_button.enable()
    
    def determine_previous_and_next_cat(self):
        ''''Determines where the next and previous buttons point too.'''
        
        is_instructor = False
        if self.the_cat.dead and game.clan.instructor.ID == self.the_cat.ID:
            is_instructor = True

        previous_cat = 0
        next_cat = 0
        if self.the_cat.dead and not is_instructor and not self.the_cat.df:
            previous_cat = game.clan.instructor.ID

        if is_instructor:
            next_cat = 1

        for check_cat in Cat.all_cats:
            if Cat.all_cats[check_cat].ID == self.the_cat.ID:
                next_cat = 1
            else:
                if next_cat == 0 and Cat.all_cats[
                        check_cat].ID != self.the_cat.ID and Cat.all_cats[
                            check_cat].dead == self.the_cat.dead and Cat.all_cats[
                                check_cat].ID != game.clan.instructor.ID and not Cat.all_cats[
                                    check_cat].exiled and Cat.all_cats[
                        check_cat].df == self.the_cat.df:
                    previous_cat = Cat.all_cats[check_cat].ID

                elif next_cat == 1 and Cat.all_cats[
                        check_cat].ID != self.the_cat.ID and Cat.all_cats[
                            check_cat].dead == self.the_cat.dead and Cat.all_cats[
                                check_cat].ID != game.clan.instructor.ID and not Cat.all_cats[
                                    check_cat].exiled and Cat.all_cats[
                        check_cat].df == self.the_cat.df:
                    next_cat = Cat.all_cats[check_cat].ID

                elif int(next_cat) > 1:
                    break

        if next_cat == 1:
            next_cat = 0

        self.next_cat = next_cat
        self.previous_cat = previous_cat

    def generate_column1(self, the_cat):
        '''Generate the left column information'''
        output = ""

        #SEX/GENDER
        if the_cat.genderalign is None or the_cat.genderalign == the_cat.gender:
            output += str(the_cat.gender)
        else:
            output += str(the_cat.genderalign)
        #NEWLINE ----------
        output += "\n"

         # AGE
        if the_cat.age == 'kitten':
            output += 'young'
        elif the_cat.age == 'elder':
            output += 'senior'
        else:
            output += the_cat.age
        #NEWLINE ----------
        output += "\n"

        # EYE COLOR
        output += 'eyes: ' + the_cat.eye_colour.lower()
        #NEWLINE ----------
        output += "\n"

        # PELT TYPE
        output += 'pelt: ' + the_cat.pelt.name.lower()
        #NEWLINE ----------
        output += "\n"

        # PELT LENGTH
        output += 'fur length: ' + the_cat.pelt.length
        #NEWLINE ----------
        output += "\n"

        #ACCESSORY
        output += 'accessory: ' + str(accessory_display_name(the_cat, the_cat.accessory))
        #NEWLINE ----------
        output += "\n"

        # PARENTS
        if the_cat.parent1 is None:
            output += 'parents: unknown'
        elif the_cat.parent2 is None and the_cat.parent1 in the_cat.all_cats:
            par1 = str(the_cat.all_cats[the_cat.parent1].name)
            output += 'parents: ' + par1 + ', unknown'
        elif the_cat.parent2 is None:
            par2 = "unknown"
            par1 = "Error: Cat#" + the_cat.parent1 + " not found"
            output += 'parents: ' + par1 + ', unknown'
        else:
            if the_cat.parent1 in the_cat.all_cats and the_cat.parent2 in the_cat.all_cats:
                par1 = str(the_cat.all_cats[the_cat.parent1].name)
                par2 = str(the_cat.all_cats[the_cat.parent2].name)

            elif the_cat.parent1 in the_cat.all_cats:
                par2 = "Error: Cat#" + the_cat.parent2 + " not found"
                par1 = str(the_cat.all_cats[the_cat.parent1].name)

            elif the_cat.parent2 in the_cat.all_cats:
                par1 = "Error: Cat#" + the_cat.parent1 + " not found"
                par2 = str(the_cat.all_cats[the_cat.parent2].name)

            else:
                par1 = "Error: Cat#" + the_cat.parent1 + " not found"
                par2 = "Error: Cat#" + the_cat.parent2 + " not found"

            output += 'parents: ' + par1 + ' and ' + par2
        #NEWLINE ----------
        output += "\n"

         # MOONS
        if the_cat.dead:
            output += str(the_cat.moons) 
            if the_cat.moons == 1:
                output += ' moon (in life)\n'
            elif the_cat.moons != 1:
                output += ' moons (in life)\n'

            output += str(the_cat.dead_for)
            if the_cat.dead_for == 1:
                output +=' moon (in death)'
            elif the_cat.dead_for != 1:
                output += ' moons (in death)'
        else:
            output += str(the_cat.moons)
            if the_cat.moons == 1:
                output += ' moon'
            elif the_cat.moons != 1:
                output += ' moons'
        #NEWLINE ----------
        output += "\n"

        # CONDITIONS (temporary)
        injury_list = []
        permanent_conditions_list = []
        illness_list = []
        injury_string = None
        permanent_conditions_string = None
        illness_string = None

        if the_cat.is_injured():
            for y in the_cat.injuries:
                injury_list.append(y)
            injury_string = ", ".join(injury_list)
        if the_cat.is_disabled():
            for y in the_cat.permanent_condition:
                if the_cat.permanent_condition[y]["moons_until"] == -2 and the_cat.permanent_condition[y]["born_with"] is True:
                    permanent_conditions_list.append(y)
                elif the_cat.permanent_condition[y]["born_with"] is False:
                    permanent_conditions_list.append(y)

            if len(permanent_conditions_list) > 0:
                permanent_conditions_string = ", ".join(permanent_conditions_list)
        if the_cat.is_ill():
            for y in the_cat.illnesses:
                illness_list.append(y)
            illness_string = ', '.join(illness_list)

        if the_cat.is_ill() and the_cat.is_injured():
            verdana_small.text(
                f"condition: {illness_string}, {injury_string}", (300, 230 + count * 15))
            count += 1
        elif the_cat.is_ill():
            verdana_small.text(
                f"condition: {illness_string}", (300, 230 + count * 15))
            count += 1
        elif the_cat.is_injured():
            verdana_small.text(
                f"condition: {injury_string}", (300, 230 + count * 15))
            count += 1

        if the_cat.is_disabled():
            if permanent_conditions_string is not None:
                verdana_small.text(
                    f"permanent conditions: {permanent_conditions_string}", (300, 230 + count * 15))
                count += 1

        # MATE
        if the_cat.mate is not None and not the_cat.dead:
            if the_cat.mate in Cat.all_cats:
                if Cat.all_cats.get(
                        the_cat.mate
                ).dead:  
                    output += 'former mate: ' + str(Cat.all_cats[the_cat.mate].name)
                else:
                    output += 'mate: ' + str(Cat.all_cats[the_cat.mate].name)
            else:
                output += 'Error: mate: ' + str(the_cat.mate) + " not found"

        return output

    def generate_column2(self, the_cat):
        '''Generate the right column information'''
        output = ""

        #STATUS
        if the_cat.exiled:
            output += "<font color='#FF0000'>exiled</font>"
        else:
            output += the_cat.status

        #NEWLINE ----------
        output += "\n"

        #LEADER LIVES:
        #Optional - Only shows up for leaders
        if not the_cat.dead and 'leader' in the_cat.status:
            output += 'remaining lives: ' + str(game.clan.leader_lives)
            #NEWLINE ----------
            output += "\n"

        #MENTOR
        #Only shows up if the cat has a mentor.
        if the_cat.mentor is not None:
            output += "mentor: " + str(the_cat.mentor.name) + "\n"

        #FORMER APPRENTICES
        #Optional - Only shows up if the cat has previous apprentice(s)
        # FORMER APPRENTICES
        if len(the_cat.former_apprentices
               ) != 0 and the_cat.former_apprentices[0] is not None:

            if len(the_cat.former_apprentices) == 1:
                output += 'former apprentice: ' + str(
                    the_cat.former_apprentices[0].name)

            elif len(the_cat.former_apprentices) > 1:
                output += 'former apprentices: ' + ", ".join([str(i.name) for i in the_cat.former_apprentices])
            
            #NEWLINE ----------
            output += "\n"


        # CHARACTER TRAIT
        output += the_cat.trait
        #NEWLINE ----------
        output += "\n"

        # SPECIAL SKILL
        output += the_cat.skill
        #NEWLINE ----------
        output += "\n"

        # EXPERIENCE
        output += 'experience: ' + str(the_cat.experience_level)
        #NEWLINE ----------
        output += "\n"

        # BACKSTORY
        if the_cat.backstory is not None:
            bs_text = backstory_text(the_cat)
            output += 'backstory: ' + bs_text
        else:
            output += 'backstory: ' + 'clanborn'

        return output

    def toggle_backstory_tab(self):
        '''Opens the backstory tab'''
        previous_open_tab = self.open_tab

        #This closes the current tab, so only one can be open as a time
        self.close_current_tab()

        if previous_open_tab == 'backstory':
            '''If the current open tab is relations, just close the tab and do nothing else. '''
            pass
        else:
            self.open_tab = 'backstory'
            self.backstory_background = pygame_gui.elements.UIImage(pygame.Rect((64,465),(645, 157)), self.backstory_tab)
            self.sub_tab_1 = UIImageButton(pygame.Rect((710, 475),(42, 30)), "", object_id = "#sub_tab_1_button")
            self.sub_tab_1.disable()
            self.sub_tab_2 = UIImageButton(pygame.Rect((710, 512),(42, 30)), "", object_id = "#sub_tab_2_button")
            self.sub_tab_2.disable()
            self.sub_tab_3 = UIImageButton(pygame.Rect((710, 549),(42, 30)), "", object_id = "#sub_tab_3_button")
            self.sub_tab_3.disable()
            self.sub_tab_4 = UIImageButton(pygame.Rect((710, 586),(42, 30)), "", object_id = "#sub_tab_4_button")
            self.sub_tab_4.disable()

            #This will be overwritten in update_disabled_buttons_and_text()
            self.history_text_box = pygame_gui.elements.UITextBox("", pygame.Rect((80,480),(615, 142)))
            self.update_disabled_buttons_and_text()

    def toggle_history_sub_tab(self):
        '''To toggle the sub-tab, when that's added'''

    def get_history_text(self):
        output = ""
        if self.open_sub_tab == 'relation':
            life_history = []
            bs_blurb = bs_blurb_text(self.the_cat, backstory=self.the_cat.backstory)
            if bs_blurb is not None:
                life_history.append(str(bs_blurb))
            else:
                life_history.append("This cat was born into the clan where they currently reside.")
            
            if self.the_cat.scar_event:
                scar_text = self.the_cat.scar_event
                for x in range(len(self.the_cat.scar_event)):
                    scar_text[x] = str(self.the_cat.scar_event[x]).replace(' is ', ' was ', 1)
                    scar_text[x] = str(self.the_cat.scar_event[x]).replace(' loses ', ' lost ')
                    scar_text[x] = str(self.the_cat.scar_event[x]).replace(' forces ', ' forced ')

                    not_scarred = ['wounded', 'injured', 'battered', 'hurt', 'punished']
                    for y in not_scarred:
                        scar_text[x] = str(self.the_cat.scar_event[x]).replace(f' got {y} ', ' was scarred ')
                        scar_text[x] = str(self.the_cat.scar_event[x]).replace(y, ' scarred ')
                        break
                    if x == 0:
                        scar_text[x] = str(self.the_cat.scar_event[x]).replace(f'{self.the_cat.name} ', 'This cat ', 1)
                    elif x == 1:
                        scar_text[x] = str(self.the_cat.scar_event[x]).replace(f'{self.the_cat.name} was ', 'They were also ', 1)
                        scar_text[x] = str(self.the_cat.scar_event[x]).replace(str(self.the_cat.name), 'They also', 1)
                    elif x >= 3:
                        scar_text[x] = str(self.the_cat.scar_event[x]).replace(f'{self.the_cat.name} was ', 'Then they were ', 1)
                        scar_text[x] = str(self.the_cat.scar_event[x]).replace(str(self.the_cat.name), 'Then they', 1)
                scar_history = ' '.join(scar_text)
                life_history.append(scar_history)

            # join together history list with line breaks
            output = '\n'.join(life_history)
        return output

    def toggle_relations_tab(self):
        '''Opens relations tab'''
        #Save what is previously open, for toggle purposes. 
        previous_open_tab = self.open_tab

        #This closes the current tab, so only one can be open as a time
        self.close_current_tab()

        if previous_open_tab == 'relations':
            '''If the current open tab is relations, just close the tab and do nothing else. '''
            pass
        else:
            self.open_tab = 'relations'
            self.see_family_button =  UIImageButton(pygame.Rect((50,450),(172,36)), "", object_id = "#see_family_button")
            self.see_relationships_button = UIImageButton(pygame.Rect((50,486),(172,36)),"", object_id = "#see_relationships_button")
            self.choose_mate_button = UIImageButton(pygame.Rect((50,522),(172,36)), "", object_id = "#choose_mate_button")
            self.change_mentor_button = UIImageButton(pygame.Rect((50,558),(172,36)),"", object_id = "#change_mentor_button")
            #This button is another option to close the tab, although I've made the opening button also close the tab
            self.close_tab_button = UIImageButton(pygame.Rect((50,594),(172,36)),"", object_id = "#close_tab_button")
            self.update_disabled_buttons_and_text()

    def toggle_roles_tab(self):
        #Save what is previously open, for toggle purposes. 
        previous_open_tab = self.open_tab

        #This closes the current tab, so only one can be open as a time
        self.close_current_tab()

        if previous_open_tab == 'roles':
            '''If the current open tab is roles, just close the tab and do nothing else. '''
            pass
        else:
            self.open_tab = 'roles'
            self.promote_leader_button = UIImageButton(pygame.Rect((226,450),(172,36)),"", object_id = "#promote_leader_button")
            
            #These are a placeholders, to be killed and recreated in self.update_disabled_buttons(). 
            #   This it due to the image switch depending on the cat's status, and the location switch the close button
            #    If you can think of a better way to do this, please fix! 
            self.toggle_deputy_button = UIImageButton(pygame.Rect((226,486),(172,36)), "", visible = False)
            self.toggle_med_button = UIImageButton(pygame.Rect((226,522),(172,52)), "", visible = False)
            self.close_tab_button = UIImageButton(pygame.Rect((226, 574),(172,36)), "", visible = False)
            self.update_disabled_buttons_and_text()
        
    def toggle_personal_tab(self):
        #Save what is previously open, for toggle purposes. 
        previous_open_tab = self.open_tab

        #This closes the current tab, so only one can be open as a time
        self.close_current_tab()

        if previous_open_tab == 'personal':
            '''If the current open tab is personal, just close the tab and do nothing else. '''
            pass
        else:
            self.open_tab = 'personal'
            self.change_name_button = UIImageButton(pygame.Rect((402,450), (172,36)), "", object_id = "#change_name_button")
            self.specify_gender_button = UIImageButton(pygame.Rect((402, 538),(172, 36)), "", object_id = "#specify_gender_button")
            self.close_tab_button = UIImageButton(pygame.Rect((402, 610),(172, 36)), "", object_id = "#close_tab_button")

            #These are a placeholders, to be killed and recreated in self.update_disabled_buttons(). 
            #   This it due to the image switch depending on the cat's status, and the location switch the close button
            #    If you can think of a better way to do this, please fix! 
            self.cis_trans_button = UIImageButton(pygame.Rect((402, 486),(0,0)), "", visible = False)
            self.toggle_kits = UIImageButton(pygame.Rect(((402, 574)),(0,0)), "", visible = False)
            self.update_disabled_buttons_and_text()

    def toggle_dangerous_tab(self):
        #Save what is previously open, for toggle purposes. 
        previous_open_tab = self.open_tab

        #This closes the current tab, so only one can be open as a time
        self.close_current_tab()

        if previous_open_tab == 'dangerous':
            '''If the current open tab is dangerous, just close the tab and do nothing else. '''
            pass
        else:
            self.open_tab = 'dangerous'
            self.kill_cat_button = UIImageButton(pygame.Rect((578, 486),(172, 36)), "" , object_id = "#kill_cat_button")
            self.close_tab_button = UIImageButton(pygame.Rect((578, 522),(172, 36)), "", object_id = "#close_tab_button")

            #These are a placeholders, to be killed and recreated in self.update_disabled_buttons_and_text(). 
            #   This it due to the image switch depending on the cat's status, and the location switch the close button
            #    If you can think of a better way to do this, please fix! 
            self.exile_cat_button = UIImageButton(pygame.Rect((578, 486),(172, 36)),"", visible = False)
            self.update_disabled_buttons_and_text()

    def update_disabled_buttons_and_text(self):
        '''Sets which tab buttons should be disabled. This is run when the cat is switched. '''
        if self.open_tab == None:
            pass
        elif self.open_tab == 'relations':
            if self.the_cat.dead:
                self.see_relationships_button.disable()
            else:
                self.see_relationships_button.enable()

            if self.the_cat.age not in ['young adult', 'adult', 'senior adult', 'elder'
                               ] or self.the_cat.dead or self.the_cat.exiled:
                self.choose_mate_button.disable()
            else:
                self.choose_mate_button.enable()

            if self.the_cat.status not in  ['apprentice', 'medicine cat apprentice'] or self.the_cat.dead:
                self.change_mentor_button.disable()
            else:
                self.change_mentor_button.enable()
        #Roles Tab
        elif self.open_tab == 'roles':
            if self.the_cat.status not in ['warrior'] or self.the_cat.dead or not game.clan.leader.dead or self.the_cat.exiled:
                self.promote_leader_button.disable()
            else:
                self.promote_leader_button.enable()
            
            #Promote to deputy button
            deputy = game.clan.deputy
            if game.clan.deputy is None:
                deputy = None
            elif game.clan.deputy.exiled:
                deputy = None
            elif game.clan.deputy.dead:
                deputy = None
    
            #This one is bit different. Since the image on the tab depends on the cat's status, we have to 
            #   recreate the button.
            self.toggle_deputy_button.kill()
            if self.the_cat.status in [
                'warrior'
            ] and not self.the_cat.dead and not self.the_cat.exiled and deputy is None:
                self.toggle_deputy_button = UIImageButton(pygame.Rect((226,486),(172,36)), "", object_id = "#promote_deputy_button")
            elif self.the_cat.status in ['deputy'] and not self.the_cat.dead and not self.the_cat.exiled:
                self.toggle_deputy_button = UIImageButton(pygame.Rect((226,486),(172,36)), "", object_id = "#demote_deputy_button")
            else:
                self.toggle_deputy_button = UIImageButton(pygame.Rect((226,486),(172,36)), "", object_id = "#promote_deputy_button")
                self.toggle_deputy_button.disable()
            
            #This one is also different, same reasons. This also handles the exit close tab button for this tab
            close_button_location = (0,0)
            self.close_tab_button.kill()
            self.toggle_med_button.kill()
            #Switch apprentice to medicine cat apprentice
            if self.the_cat.status in ['apprentice'] and not self.the_cat.dead and not self.the_cat.exiled:
                self.toggle_med_button = UIImageButton(pygame.Rect((226, 522),(172, 52)), "", object_id = "#switch_med_app_button")
                close_button_location = (226, 574)
            #Switch med apprentice to warrior apprentice
            elif self.the_cat.status in ['medicine cat apprentice'] and not self.the_cat.dead and not self.the_cat.exiled:
                self.toggle_med_button = UIImageButton(pygame.Rect((226, 522),(172, 52)),"",object_id = "#switch_warrior_app_button")
                close_button_location = (226, 574)
            #Switch warrior or elder to med cat. 
            elif self.the_cat.status in ['warrior','elder'] and not self.the_cat.dead and not self.the_cat.exiled:
                self.toggle_med_button =  UIImageButton(pygame.Rect((226, 522),(172, 52)),"",object_id = "#switch_med_cat_button")
                close_button_location = (226, 574)
            #Switch med cat to warrior 
            elif self.the_cat.status == 'medicine cat' and not self.the_cat.dead and not self.the_cat.exiled:
                self.toggle_med_button = UIImageButton(pygame.Rect((226, 522),(172,36)),"",object_id = "#switch_warrior_button")
                close_button_location = (226, 558)
            else:
                #Dummy button so .kill() calls don't fail
                self.toggle_med_button = pygame_gui.elements.UIButton(pygame.Rect((0,0),(0,0)),"", visible=False)
                close_button_location = (226, 522)

            #Draw close button
            self.close_tab_button = UIImageButton(pygame.Rect(close_button_location,(172,36)), "", object_id = "#close_tab_button")
        elif self.open_tab == "personal":

            #Button to trans or cis the cats. 
            self.cis_trans_button.kill()
            if self.the_cat.gender == "female" and self.the_cat.genderalign in ['male', 'female']:
                self.cis_trans_button = UIImageButton(pygame.Rect((402, 486),(172, 52)),"", object_id = "#change_trans_male_button")
            elif self.the_cat.gender == "male" and self.the_cat.genderalign in ['male', 'female']:
                self.cis_trans_button = UIImageButton(pygame.Rect((402, 486),(172, 52)),"", object_id = "#change_trans_female_button")
            elif self.the_cat.genderalign != "female" and self.the_cat.genderalign != "male":
                self.cis_trans_button = UIImageButton(pygame.Rect((402, 486),(172, 52)), "", object_id = "#change_cis_button")
            else:
                self.cis_trans_button = UIImageButton(pygame.Rect((402, 486),(172, 52)), "", object_id = "#change_cis_button")
                self.cis_trans_button.disable()

            #Button to prevent kits:
            self.toggle_kits.kill()
            if self.the_cat.age in ['young adult', 'adult', 'senior adult', 'elder'] and not self.the_cat.dead:
                    if self.the_cat.no_kits:
                        self.toggle_kits = UIImageButton(pygame.Rect((402, 574),(172, 36)),"", object_id = "#prevent_kits_button")
                    else:
                        self.toggle_kits = UIImageButton(pygame.Rect((402, 574),(172, 36)),"", object_id = "#allow_kits_button")
            else:
                self.toggle_kits = UIImageButton(pygame.Rect((402, 574),(172, 36)), "",  object_id = "#prevent_kits_button")
                self.toggle_kits.disable()
        #Dangerous Tab
        elif self.open_tab == 'dangerous':

            #Button to exile cat
            self.exile_cat_button.kill()
            if not self.the_cat.dead:
                self.exile_cat_button = UIImageButton(pygame.Rect((578, 450),(172, 36)), "", object_id = "#exile_cat_button")
                if self.the_cat.exiled:
                    self.exile_cat_button.disable()
            elif self.the_cat.dead:
                self.exile_cat_button = UIImageButton(pygame.Rect((578, 450),(172, 46)), "", object_id = "#exile_df_button")
                if self.the_cat.df:
                    self.exile_cat_button.disable()
            else:
                self.exile_cat_button = UIImageButton(pygame.Rect((578, 450),(172, 36)), "", object_id = "#exile_cat_button")
                self.exile_cat_button.disable()

            if not self.the_cat.dead:
                self.kill_cat_button.enable()
            else:
                self.kill_cat_button.disable()
        #Backstory_tab:
        elif self.open_tab == 'backstory':
            self.history_text_box.kill()
            self.history_text_box = pygame_gui.elements.UITextBox(self.get_history_text(), 
                                                        pygame.Rect((80,480),(615, 142)), object_id= "#history_tab_text_box") 

    def close_current_tab(self):
        '''Closes current tab. '''
        if self.open_tab == None:
            pass
        elif self.open_tab == 'relations':
            self.see_family_button.kill()
            self.see_relationships_button.kill()
            self.choose_mate_button.kill()
            self.change_mentor_button.kill()
            self.close_tab_button.kill()
        elif self.open_tab == 'roles':
            self.promote_leader_button.kill()
            self.toggle_deputy_button.kill()
            self.toggle_med_button.kill()
            self.close_tab_button.kill()
        elif self.open_tab == 'personal':
            self.change_name_button.kill()
            self.specify_gender_button.kill()
            self.close_tab_button.kill()
            self.cis_trans_button.kill()
            self.toggle_kits.kill()
        elif self.open_tab == 'dangerous':
            self.kill_cat_button.kill()
            self.exile_cat_button.kill()
            self.close_tab_button.kill()
        elif self.open_tab == 'backstory':
            self.backstory_background.kill()
            self.sub_tab_1.kill()
            self.sub_tab_2.kill()
            self.sub_tab_3.kill()
            self.sub_tab_4.kill()
            self.history_text_box.kill()

        self.open_tab = None

    # ---------------------------------------------------------------------------- #
    #                               cat platforms                                  #
    # ---------------------------------------------------------------------------- #
    def update_platform(self):
        the_cat = Cat.all_cats.get(game.switches['cat'],
                                         game.clan.instructor)
        
        light_dark = "light"
        if game.settings["dark mode"]:
            light_dark = "dark"

        platform_base_dir = 'resources/images/platforms/'
        leaves = ["newleaf", "greenleaf", "leafbare", "leaffall"]
        
        available_biome = ['Forest', 'Mountainous', 'Plains', 'Beach']
        biome = game.clan.biome

        if biome not in available_biome:
            biome = available_biome[0]

        biome = biome.lower()

        all_platforms = []
        if the_cat.df:
            dead_platform = [f'{platform_base_dir}darkforestplatform_{light_dark}.png']
            all_platforms = dead_platform*4
        elif the_cat.dead or game.clan.instructor.ID == the_cat.ID:
            dead_platform = [f'{platform_base_dir}/starclanplatform_{light_dark}.png']
            all_platforms = dead_platform*4
        else:
            for leaf in leaves:
                platform_dir = f'{platform_base_dir}/{biome}/{leaf}_{light_dark}.png'
                all_platforms.append(platform_dir)

        self.newleaf_plt = pygame.transform.scale(
            pygame.image.load(all_platforms[0]).convert_alpha(), (240, 210))
        self.greenleaf_plt = pygame.transform.scale(
            pygame.image.load(all_platforms[1]).convert_alpha(), (240, 210))
        self.leafbare_plt = pygame.transform.scale(
            pygame.image.load(all_platforms[2]).convert_alpha(), (240, 210))
        self.leaffall_plt = pygame.transform.scale(
            pygame.image.load(all_platforms[3]).convert_alpha(), (240, 210))
    
    def on_use(self):
       pass
# ---------------------------------------------------------------------------- #
#                             change name screen                               #
# ---------------------------------------------------------------------------- #
class ChangeNameScreen(Screens):
    the_cat = ''

    def screen_switches(self):
        self.hide_menu_buttons()

        self.the_cat = Cat.all_cats.get(game.switches['cat'])

        self.heading = pygame_gui.elements.UITextBox("-Change Name-", pygame.Rect((100, 130), (600, 40)),
                                                     object_id=get_text_box_theme())

        self.name_changed = pygame_gui.elements.UITextBox("Named Changed!", pygame.Rect((100, 350),(600, 40)),
                                                          visible=False,
                                                          object_id=get_text_box_theme())

        self.done_button = UIImageButton(pygame.Rect((365, 282),(77, 30)),"", object_id= pygame_gui.core.ObjectID(object_id="#done_button"))
        self.back_button = UIImageButton(pygame.Rect((25, 25),(105, 30)),"", object_id= pygame_gui.core.ObjectID(object_id="#back_button"))

        self.test_button = UIImageButton(pygame.Rect((350, 350),(180, 180)),"", object_id= pygame_gui.core.ObjectID(object_id="#image_button"),visible =False)

        self.prefix_entry_box = pygame_gui.elements.UITextEntryLine(pygame.Rect((220,200),(180,30)),
                                                                    placeholder_text=self.the_cat.name.prefix)
        if self.the_cat.name.status in ["apprentice", "leader", "medicine cat apprentice", "leader"]:
            self.suffix_entry_box = pygame_gui.elements.UITextEntryLine(pygame.Rect((400, 200),(180,30)),
                                                                        placeholder_text=self.the_cat.name.special_suffixes[self.the_cat.name.status])
            self.suffix_entry_box.disable() #You can't change a special suffix
        else:
            self.suffix_entry_box = pygame_gui.elements.UITextEntryLine(pygame.Rect((400,200),(180,30)),
                                                                        placeholder_text=self.the_cat.name.suffix)
    
    def exit_screen(self):
        self.prefix_entry_box.kill()
        del self.prefix_entry_box
        self.suffix_entry_box.kill()
        del self.suffix_entry_box
        self.done_button.kill()
        del self.done_button
        self.back_button.kill()
        del self.back_button
        self.heading.kill()
        del self.heading
        self.name_changed.kill()
        del self.name_changed

    def on_use(self):
        pass
        
    def handle_event(self,event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.done_button:
                if self.prefix_entry_box.get_text() != '':
                    self.the_cat.name.prefix = self.prefix_entry_box.get_text()
                    self.name_changed.show()
                if self.suffix_entry_box.get_text() != '':
                    self.the_cat.name.suffix = self.suffix_entry_box.get_text()
                    self.name_changed.show()
            elif event.ui_element == self.back_button:
                self.change_screen('profile screen')

# ---------------------------------------------------------------------------- #
#                           change gender screen                               #
# ---------------------------------------------------------------------------- #
class ChangeGenderScreen(Screens):
    gender_changed = False

    def screen_switches(self):
        self.hide_menu_buttons()

        self.header = pygame_gui.elements.UITextBox("-Change Gender-\nYou can set this to anything. "
                                                    "Gender alignment does not effect gameplay",
                                                    pygame.Rect((100, 130), (600, 100)),
                                                    object_id=get_text_box_theme())
        self.gender_changed = pygame_gui.elements.UITextBox("Gender Changed!",
                                                            pygame.Rect((100, 240), (600, 40)),
                                                            object_id=get_text_box_theme(),
                                                            visible=False)
        self.the_cat = Cat.all_cats.get(game.switches['cat'])
        self.gender_changed = False
    
        self.gender_entry_box = pygame_gui.elements.UITextEntryLine(pygame.Rect((300, 200),(200, 24)),
                                                                    placeholder_text=self.the_cat.genderalign)
        self.done_button = UIImageButton(pygame.Rect((365, 282),(77, 30)), "",
                                        object_id="#done_button")
        self.back_button = UIImageButton(pygame.Rect((25, 25),(105, 30)), "",
                                         object_id="#back_button")
        
    def exit_screen(self):
        self.header.kill()
        del self.header
        self.gender_changed.kill()
        del self.header
        self.gender_entry_box.kill()
        del self.gender_entry_box
        self.done_button.kill()
        del self.done_button
        self.back_button.kill()
        del self.back_button

    def on_use(self):
        pass

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.done_button:
                if self.gender_entry_box.get_text() != "":
                    self.the_cat.genderalign = self.gender_entry_box.get_text()
                    self.gender_changed.show()
            elif event.ui_element == self.back_button:
                self.change_screen('profile screen')
        return 


class ExileProfileScreen(Screens):
    def update_platform(self):
        the_cat = Cat.all_cats.get(game.switches['cat'],
                                         game.clan.instructor)
        
        light_dark = "light"
        if game.settings["dark mode"]:
            light_dark = "dark"

        platform_base_dir = 'resources/images/platforms/'
        leaves = ["newleaf", "greenleaf", "leafbare", "leaffall"]
        
        available_biome = ['Forest', 'Mountainous', 'Plains', 'Beach']
        biome = game.clan.biome

        if biome not in available_biome:
            biome = available_biome[0]

        biome = biome.lower()

        all_platforms = []
        if the_cat.df:
            dead_platform = [f'{platform_base_dir}darkforestplatform_{light_dark}.png']
            all_platforms = dead_platform*4
        elif the_cat.dead or game.clan.instructor.ID == the_cat.ID:
            dead_platform = [f'{platform_base_dir}/starclanplatform_{light_dark}.png']
            all_platforms = dead_platform*4
        else:
            for leaf in leaves:
                platform_dir = f'{platform_base_dir}/{biome}/{leaf}_{light_dark}.png'
                all_platforms.append(platform_dir)

        self.newleaf_plt = pygame.transform.scale(
            pygame.image.load(all_platforms[0]).convert_alpha(), (240, 210))
        self.greenleaf_plt = pygame.transform.scale(
            pygame.image.load(all_platforms[1]).convert_alpha(), (240, 210))
        self.leafbare_plt = pygame.transform.scale(
            pygame.image.load(all_platforms[2]).convert_alpha(), (240, 210))
        self.leaffall_plt = pygame.transform.scale(
            pygame.image.load(all_platforms[3]).convert_alpha(), (240, 210))
        
    def on_use(self):
        # use this variable to point to the cat object in question
        the_cat = Cat.all_cats.get(game.switches['cat'],game.clan.instructor)

        # draw_next_prev_cat_buttons(the_cat)
        # use these attributes to create differing profiles for starclan cats etc.

        # Info in string
        cat_name = str(the_cat.name)  # name

        # LAYOUT
        count = 0
        count2 = 0
        verdana_big.text(cat_name, ('center', 150))  # NAME

        if game.settings['backgrounds']:  # CAT PLATFORM
            self.update_platform()
            if game.clan.current_season == 'Newleaf':
                screen.blit(self.newleaf_plt, (55, 200))
            elif game.clan.current_season == 'Greenleaf':
                screen.blit(self.greenleaf_plt, (55, 200))
            elif game.clan.current_season == 'Leaf-bare':
                screen.blit(self.leafbare_plt, (55, 200))
            elif game.clan.current_season == 'Leaf-fall':
                screen.blit(self.leaffall_plt, (55, 200))

        draw_large(the_cat,(100, 200)) # IMAGE

        # THOUGHT
        if len(the_cat.thought) < 100:
            verdana.text(the_cat.thought, ('center', 180))
        else:
            cut = the_cat.thought.find(' ', int(len(the_cat.thought)/2))
            first_part = the_cat.thought[:cut]
            second_part = the_cat.thought[cut:]
            verdana.text(first_part, ('center', 180))
            verdana.text(second_part, ('center', 200))

        if the_cat.genderalign == None or the_cat.genderalign == True or the_cat.genderalign == False:
            verdana_small.text(str(the_cat.gender), (300, 230 + count * 15))
        else:
            verdana_small.text(str(the_cat.genderalign), (300, 230 + count * 15))
        count += 1  # SEX / GENDER
        verdana_small.text("exiled", (490, 230 + count2 * 15))
        count2+=1
        if the_cat.age == 'kitten':
            verdana_small.text('young', (300, 230 + count * 15))
        elif the_cat.age == 'elder':
            verdana_small.text('senior', (300, 230 + count * 15))
        else:
            verdana_small.text(the_cat.age, (300, 230 + count * 15))
        count += 1  # AGE
        verdana_small.text(the_cat.trait, (490, 230 + count2 * 15))
        count2 += 1  # CHARACTER TRAIT
        verdana_small.text(the_cat.skill, (490, 230 + count2 * 15))
        count2 += 1  # SPECIAL SKILL
        verdana_small.text('eyes: ' + the_cat.eye_colour.lower(),
                           (300, 230 + count * 15))
        count += 1  # EYE COLOR
        verdana_small.text('pelt: ' + the_cat.pelt.name.lower(),
                           (300, 230 + count * 15))
        count += 1  # PELT TYPE
        verdana_small.text('fur length: ' + the_cat.pelt.length,
                           (300, 230 + count * 15))
        count += 1  # PELT LENGTH
        verdana_small.text('accessory: ' + str(accessory_display_name(the_cat, the_cat.accessory)),
                           (300, 230 + count * 15))
        count += 1  # accessory

        # PARENTS
        if the_cat.parent1 is None:
            verdana_small.text('parents: unknown', (300, 230 + count * 15))
            count += 1
        elif the_cat.parent2 is None and the_cat.parent1 in the_cat.all_cats:
            par1 = str(the_cat.all_cats[the_cat.parent1].name)
            verdana_small.text('parents: ' + par1 + ', unknown',
                               (300, 230 + count * 15))
            count += 1
        elif the_cat.parent2 is None:
            par2 = "unknown"
            par1 = "Error: Cat#" + the_cat.parent1 + " not found"
            verdana_small.text('parents: ' + par1 + ', unknown',
                               (300, 230 + count * 15))
            count += 1
        else:
            if the_cat.parent1 in the_cat.all_cats and the_cat.parent2 in the_cat.all_cats:
                par1 = str(the_cat.all_cats[the_cat.parent1].name)
                par2 = str(the_cat.all_cats[the_cat.parent2].name)
            elif the_cat.parent1 in the_cat.all_cats:
                par2 = "Error: Cat#" + the_cat.parent2 + " not found"
                par1 = str(the_cat.all_cats[the_cat.parent1].name)
            elif the_cat.parent2 in the_cat.all_cats:
                par1 = "Error: Cat#" + the_cat.parent1 + " not found"
                par2 = str(the_cat.all_cats[the_cat.parent2].name)
            else:
                par1 = "Error: Cat#" + the_cat.parent1 + " not found"
                par2 = "Error: Cat#" + the_cat.parent2 + " not found"

            verdana_small.text('parents: ' + par1 + ' and ' + par2,
                               (300, 230 + count * 15))
            count += 1

        # MOONS
        if the_cat.dead:
            if the_cat.moons == 1:
                verdana_small.text(
                    str(the_cat.moons) + ' moon (in life)',
                    (300, 230 + count * 15))
                count += 1
            elif the_cat.moons != 1:
                verdana_small.text(
                    str(the_cat.moons) + ' moons (in life)',
                    (300, 230 + count * 15))
                count += 1
            if the_cat.dead_for == 1:
                verdana_small.text(
                    str(the_cat.dead_for) + ' moon (in death)',
                    (300, 230 + count * 15))
                count += 1
            elif the_cat.dead_for != 1:
                verdana_small.text(
                    str(the_cat.dead_for) + ' moons (in death)',
                    (300, 230 + count * 15))
                count += 1
        else:
            if the_cat.moons == 1:
                verdana_small.text(
                    str(the_cat.moons) + ' moon', (300, 230 + count * 15))
                count += 1
            elif the_cat.moons != 1:
                verdana_small.text(
                    str(the_cat.moons) + ' moons', (300, 230 + count * 15))
                count += 1

        # buttons

        buttons.draw_image_button((48, 420),
                                  button_name='relations',
                                  text="relations",
                                  size=(176, 30),
                                  profile_tab_group='relations',
                                  available=False
                                  )
        buttons.draw_image_button((224, 420),
                                  button_name='roles',
                                  text="roles",
                                  size=(176, 30),
                                  profile_tab_group='roles',
                                  available=False
                                  )
        buttons.draw_image_button((400, 420),
                                  button_name='personal',
                                  text="personal",
                                  size=(176, 30),
                                  profile_tab_group='personal',
                                  available=True,
                                  )
        buttons.draw_image_button((576, 420),
                                  button_name='dangerous',
                                  text="dangerous",
                                  size=(176, 30),
                                  profile_tab_group='dangerous',
                                  available=False
                                  )
        draw_back(25, 60)

