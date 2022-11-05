from .base_screens import Screens, cat_profiles, draw_next_prev_cat_buttons
from random import choice

from scripts.utility import draw_large
from scripts.game_structure.text import *
from scripts.game_structure.buttons import buttons
from scripts.cat.cats import Cat
from scripts.cat.pelts import collars, wild_accessories

def draw_text_bar():
    if game.settings['dark mode']:
        pygame.draw.rect(screen, 'white', pygame.Rect((300, 200),
                                                      (200, 20)))
        verdana_black.text(game.switches['naming_text'], (315, 200))
    else:
        pygame.draw.rect(screen, 'gray', pygame.Rect((300, 200),
                                                     (200, 20)))
        verdana.text(game.switches['naming_text'], (315, 200))

def draw_back(x_value, y_value):
    the_cat = Cat.all_cats.get(game.switches['cat'])
    if (the_cat.exiled):
        buttons.draw_button((x_value, y_value),
        text='Back',
        cur_screen='outside profile screen',
        hotkey=[0])
    else:
        buttons.draw_button((x_value, y_value),
            text='Back',
            cur_screen='profile screen',
            hotkey=[0])

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

def backstory_text(cat, backstory):
    backstory = cat.backstory
    bs_blurb = None
    if backstory is None:
        return ''
    if backstory == 'clanborn':
        bs_blurb = "This cat was born into the clan where they currently reside"
    if backstory == 'half-clan1':
        bs_blurb = "This cat was born into the clan, but one of their parents resides in another clan"
    if backstory == 'half-clan2':
        bs_blurb = "This cat was born in another clan, but chose to come to this clan to be with their other parent"
    if backstory == 'outsider_roots1':
        bs_blurb = "This cat was born into the clan, but one of their parents is an outsider that belongs to no clan"
    if backstory == 'outsider_roots2':
        bs_blurb = "This cat was born outside the clan, but came to live in the clan with their parent at a young age"
    if backstory == 'loner1':
        bs_blurb = "This cat joined the clan by choice after living life as a loner"
    if backstory == 'loner2':
        bs_blurb = "This cat used to live in a barn, but mostly stayed away from twolegs. They decided clanlife might be an interesting change of pace"
    if backstory == 'kittypet1':
        bs_blurb = "This cat joined the clan by choice after living life with twolegs as a kittypet"
    if backstory == 'kittypet2':
        bs_blurb = "This cat used to live on something called a “boat” with twolegs, but decided to join the clan"
    if backstory == 'rogue1':
        bs_blurb = "This cat joined the clan by choice after living life as a rogue"
    if backstory == 'rogue2':
        bs_blurb = "This cat used to live in a twolegplace, scrounging for what they could find. They thought the clan might offer them more security"
    if backstory == 'abandoned1':
        bs_blurb = "This cat was found by the clan as a kit and has been living with them ever since"
    if backstory == 'abandoned2':
        bs_blurb = "This cat was born into a kittypet life, but was brought to the clan as a kit and has lived here ever since"
    if backstory == 'abandoned3':
        bs_blurb = "This cat was born into another clan, but they were left here as a kit for the clan to raise"
    if backstory == 'medicine_cat':
        bs_blurb = "This cat was once a medicine cat in another clan"
    if backstory == 'otherclan':
        bs_blurb = "This cat was born into another clan, but came to this clan by choice"
    if backstory == 'otherclan2':
        bs_blurb = "This cat was unhappy in their old clan and decided to come here instead"
    if backstory == 'ostracized_warrior':
        bs_blurb = "This cat was ostracized from their old clan, but no one really knows why"
    if backstory == 'disgraced':
        bs_blurb = "This cat was cast out of their old clan for some transgression that they’re not keen on talking about"
    if backstory == 'retired_leader':
        bs_blurb = "This cat used to be the leader of another clan before deciding they needed a change of scenery after leadership became too much.\
        They returned their nine lives and let their deputy take over before coming here"
    if backstory == 'refugee':
        bs_blurb = "This cat came to this clan after fleeing from their former clan and the tyrannical leader that had taken over"
    if backstory == 'tragedy_survivor':
        bs_blurb = "Something horrible happened to this cat's previous clan. They refuse to speak about it"
    bs_display = backstory
    if bs_display == 'clanborn':
        bs_display = 'clanborn'
    elif bs_display in ['half-clan1', 'half-clan2']:
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
            bs_display_choice = choice(['disgraced leader', 'disgraced deputy'])
            bs_display = bs_display_choice
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
    if bs_blurb == None:
        bs_blurb = None
    else:
        return bs_blurb
    

class ProfileScreen(Screens):

    def on_use(self):
        # use this variable to point to the cat object in question
        the_cat = Cat.all_cats.get(game.switches['cat'],game.clan.instructor)

        draw_next_prev_cat_buttons(the_cat)
        # use these attributes to create differing profiles for starclan cats etc.
        is_instructor = False
        if the_cat.dead and game.clan.instructor.ID == the_cat.ID:
            is_instructor = True

        # Info in string
        cat_name = str(the_cat.name)  # name
        if the_cat.dead:
            cat_name += " (dead)"  # A dead cat will have the (dead) sign next to their name
        if is_instructor:
            the_cat.thought = "Hello. I am here to guide the dead cats of " + game.clan.name + "Clan into StarClan."

        # LAYOUT
        count = 0
        count2 = 0
        verdana_big.text(cat_name, ('center', 150))  # NAME

        if game.settings['backgrounds']:  # CAT PLATFORM
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

        
        if the_cat.genderalign is None or the_cat.genderalign == the_cat.gender:
            verdana_small.text(str(the_cat.gender), (300, 230 + count * 15))
        else:
            verdana_small.text(str(the_cat.genderalign), (300, 230 + count * 15))
        count += 1  # SEX / GENDER
        if (the_cat.exiled): 
            verdana_red.text("exiled", (490, 230 + count2 * 15))
        else:
            verdana_small.text(the_cat.status, (490, 230 + count2 * 15))
        if not the_cat.dead and 'leader' in the_cat.status:  #See Lives
            count2 += 1
            verdana_small.text(
                'remaining lives: ' + str(game.clan.leader_lives),
                (490, 230 + count2 * 15))
        count2 += 1  # STATUS
        if 'apprentice' in the_cat.status:
            if the_cat.mentor is None:
                the_cat.update_mentor()
            if the_cat.mentor is not None:
                verdana_small.text('mentor: ' + str(the_cat.mentor.name),
                                   (490, 230 + count2 * 15))
                count2 += 1
        if len(the_cat.apprentice) != 0:
            if len(the_cat.apprentice) == 1:
                apps = 'apprentice: ' + str(the_cat.apprentice[0].name)
            else:
                apps = 'apprentices: '
                num = 1
                for cat in the_cat.apprentice:
                    if num % 2 == 0:
                        apps += str(cat.name) + ', '
                    else:
                        apps += str(cat.name) + ', '
                    num += 1
                apps = apps[:len(apps) - 2]
            verdana_small.text(apps, (490, 230 + count2 * 15))
            count2 += 1
        if len(the_cat.former_apprentices
               ) != 0 and the_cat.former_apprentices[0] is not None:
            if len(the_cat.former_apprentices) == 1:
                former_apps = 'former apprentice: ' + str(
                    the_cat.former_apprentices[0].name)
                verdana_small.text(former_apps, (490, 230 + count2 * 15))
                count2 += 1
            elif len(the_cat.former_apprentices) == 2:
                former_apps = 'former apprentices: ' + str(
                    the_cat.former_apprentices[0].name) + ', ' + str(
                        the_cat.former_apprentices[1].name)
                verdana_small.text(former_apps, (490, 230 + count2 * 15))
                count2 += 1
            elif len(the_cat.former_apprentices) == 3:
                former_apps = 'former apprentices: ' + str(
                    the_cat.former_apprentices[0].name) + ', ' + str(
                        the_cat.former_apprentices[1].name)
                verdana_small.text(former_apps, (490, 230 + count2 * 15))
                count2 += 1
                verdana_small.text(str(the_cat.former_apprentices[2].name), (490, 230 + count2 * 15))
                count2+=1
            elif len(the_cat.former_apprentices) == 4:
                former_apps = 'former apprentices: ' + str(
                    the_cat.former_apprentices[0].name) + ', ' + str(
                        the_cat.former_apprentices[1].name)
                verdana_small.text(former_apps, (490, 230 + count2 * 15))
                count2 += 1
                former_apps2 = str(the_cat.former_apprentices[2].name) + ', ' + str(the_cat.former_apprentices[3].name)
                verdana_small.text(former_apps2, (490, 230 + count2 * 15))
                count2+=1
            else:
                num = 1
                rows = []
                name = ''
                for cat in the_cat.former_apprentices:
                    name = name + str(cat.name) + ', '
                    if num == 2:
                        rows.append(name)
                        name = ''
                        num += 1
                    if num % 3 == 0 and name != '':
                        rows.append(name)
                        name = ''
                    num += 1
                for ind in range(len(rows)):
                    if ind == 0:
                        verdana_small.text('former apprentices: ' + rows[ind],
                                           (490, 230 + count2 * 15))
                    elif ind == len(rows) - 1:
                        verdana_small.text(rows[ind][:-2],
                                           (490, 230 + count2 * 15))
                    else:
                        verdana_small.text(rows[ind], (490, 230 + count2 * 15))
                    count2 += 1
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

        # MATE
        if the_cat.mate is not None and not the_cat.dead:
            if the_cat.mate in Cat.all_cats:
                if Cat.all_cats.get(
                        the_cat.mate
                ).dead:  # TODO: fix when mate dies mate becomes none
                    verdana_small.text(
                        'former mate: ' +
                        str(Cat.all_cats[the_cat.mate].name),
                        (300, 230 + count * 15))
                else:
                    verdana_small.text(
                        'mate: ' + str(Cat.all_cats[the_cat.mate].name),
                        (300, 230 + count * 15))
                count += 1
            else:
                verdana_small.text(
                    'Error: mate: ' + str(the_cat.mate) + " not found",
                    ('center', 495))

        # experience
        if not the_cat.dead:
            verdana_small.text('experience: ' + str(the_cat.experience_level),
                               (490, 230 + count2 * 15))
            count2 += 1
        else:
            verdana_small.text('experience: ' + str(the_cat.experience_level),
                               (490, 230 + count2 * 15))
            count2 += 1

        # backstory
        if the_cat.backstory != None:
            bs_text = backstory_text(the_cat, the_cat.backstory)
            verdana_small.text('backstory: ' + bs_text, (490, 230 + count2 * 15))
            count2 += 1
        else:
            verdana_small.text('backstory: ' + 'Clanborn', (490, 230 + count2 * 15))
            count2 += 1

        # buttons
        count = 0
        buttons.draw_button(('center', 400 + count),
                            text="See Family",
                            cur_screen='see kits screen')
        count += 30

        if not the_cat.dead:
            buttons.draw_button(('center', 400 + count),
                                text="See Relationships",
                                cur_screen='relationship screen')
            count += 30

        buttons.draw_button(('center', 400 + count),
                            text='Options',
                            cur_screen='options screen')

        buttons.draw_button(('center', 510),
                            text='Back',
                            cur_screen=game.switches['last_screen'])

    # PLATFORM
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
        if the_cat.dead or game.clan.instructor.ID == the_cat.ID:
            dead_platform = [f'{platform_base_dir}/starclanplatform_{light_dark}.png']
            all_platforms = dead_platform*4
        else:
            for leaf in leaves:
                platform_dir = f'{platform_base_dir}/{biome}/{leaf}_{light_dark}.png'
                all_platforms.append(platform_dir)

        self.newleaf_plt = pygame.transform.scale(
            pygame.image.load(all_platforms[0]).convert(), (240, 210))
        self.greenleaf_plt = pygame.transform.scale(
            pygame.image.load(all_platforms[1]).convert(), (240, 210))
        self.leafbare_plt = pygame.transform.scale(
            pygame.image.load(all_platforms[2]).convert(), (240, 210))
        self.leaffall_plt = pygame.transform.scale(
            pygame.image.load(all_platforms[3]).convert(), (240, 210))

    def screen_switches(self):
        cat_profiles()
        self.update_platform()

class OptionsScreen(Screens):

    def draw_header(self):
        buttons.draw_button((10, 85),
                            text="Relations Tab",
                            options_tab="Relations Tab",
                            hotkey=[11])
        buttons.draw_button((150, 85),
                            text="Roles Tab",
                            options_tab="Roles Tab",
                            hotkey=[12])
        buttons.draw_button((260, 85),
                            text="Personal Tab",
                            options_tab="Personal Tab",
                            hotkey=[13])
        buttons.draw_button((-10, 85),
                            text="Dangerous Tab",
                            options_tab="Dangerous Tab",
                            hotkey=[14])

    def relations_tab(self):
        self.draw_header()

        the_cat = Cat.all_cats.get(game.switches['cat'])
        button_count = 0
        x_value = 'center'
        y_value = 150
        y_change = 50
        buttons.draw_button((x_value, y_value + button_count * y_change),
                            text='See Family',
                            cur_screen='see kits screen',
                            hotkey=[button_count + 1])
        button_count += 1

        # buttons.draw_button((x_value, y_value + button_count * y_change),
        #                     text='Family Tree',
        #                     hotkey=[button_count + 1])
        # button_count += 1
        if not the_cat.dead:
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='See Relationships',
                                cur_screen='relationship screen',
                                hotkey=[button_count + 1])
        button_count += 1

        if the_cat.age in ['young adult', 'adult', 'senior adult', 'elder'
                           ] and not the_cat.dead and not the_cat.exiled:
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Pick mate for ' + str(the_cat.name),
                                cur_screen='choose mate screen',
                                hotkey=[button_count + 1])
            button_count += 1

        if the_cat.status == 'apprentice' and not the_cat.dead:
            game.switches['apprentice'] = the_cat
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Change Mentor',
                                cur_screen='choose mentor screen',
                                hotkey=[button_count + 1])
            button_count += 1

        draw_back(x_value, y_value + button_count * y_change)

    def roles_tab(self):
        self.draw_header()

        the_cat = Cat.all_cats.get(game.switches['cat'])
        button_count = 0
        x_value = 'center'
        y_value = 150
        y_change = 50
        if game.switches['new_leader'] is not False and game.switches[
                'new_leader'] is not None:
            game.clan.new_leader(game.switches['new_leader'])
        if the_cat.status in ['warrior'
                              ] and not the_cat.dead and game.clan.leader.dead and not the_cat.exiled:
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Promote to Leader',
                                new_leader=the_cat,
                                hotkey=[button_count + 1])
            button_count += 1

        elif the_cat.status in [
                'warrior'
        ] and not the_cat.dead and game.clan.deputy is None and not the_cat.exiled:
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Promote to Deputy',
                                deputy_switch=the_cat,
                                hotkey=[button_count + 1])
            button_count += 1

        elif the_cat.status in ['deputy'] and not the_cat.dead and not the_cat.exiled:
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Demote from Deputy',
                                deputy_switch=the_cat,
                                hotkey=[button_count + 1])
            button_count += 1

        elif the_cat.status in ['warrior'
                                ] and not the_cat.dead and game.clan.deputy:
            if game.clan.deputy.dead and not the_cat.exiled:
                buttons.draw_button(
                    (x_value, y_value + button_count * y_change),
                    text='Promote to Deputy',
                    deputy_switch=the_cat,
                    hotkey=[button_count + 1])
                button_count += 1

        if the_cat.status in ['apprentice'] and not the_cat.dead and not the_cat.exiled:
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Switch to medicine cat apprentice',
                                apprentice_switch=the_cat,
                                hotkey=[button_count + 1])
            button_count += 1
        elif the_cat.status in ['medicine cat apprentice'
                                ] and not the_cat.dead and not the_cat.exiled:
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Switch to warrior apprentice',
                                apprentice_switch=the_cat,
                                hotkey=[button_count + 1])
            button_count += 1
        elif the_cat.status == 'warrior' and not the_cat.dead and not the_cat.exiled:
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Switch to medicine cat',
                                apprentice_switch=the_cat,
                                hotkey=[button_count + 1])
            button_count += 1
        elif the_cat.status == 'medicine cat' and not the_cat.dead and not the_cat.exiled:
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Switch to warrior',
                                apprentice_switch=the_cat,
                                hotkey=[button_count + 1])
            button_count += 1

        draw_back(x_value, y_value + button_count * y_change)

    def personal_tab(self):
        self.draw_header()

        the_cat = Cat.all_cats.get(game.switches['cat'])
        button_count = 0
        x_value = 'center'
        y_value = 150
        y_change = 50

        buttons.draw_button((x_value, y_value + button_count * y_change),
                            text='Change Name',
                            cur_screen='change name screen',
                            hotkey=[button_count + 1])
        button_count += 1
        game.switches['name_cat'] = the_cat.ID

        if the_cat.genderalign == "female":
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Change to Trans Male',
                                cat_value=game.switches['cat'],
                                hotkey=[button_count + 1])
            button_count += 1
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Change to Nonbinary/Specify Gender',
                                cat_value=game.switches['cat'],
                                hotkey=[button_count + 1])
            button_count += 1
        elif the_cat.genderalign == "male":
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Change to Trans Female',
                                cat_value=game.switches['cat'],
                                hotkey=[button_count + 1])
            button_count += 1
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Change to Nonbinary/Specify Gender',
                                cat_value=game.switches['cat'],
                                hotkey=[button_count + 1])
            button_count += 1
        elif the_cat.genderalign == "nonbinary":
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Specify Gender',
                                cur_screen='change gender screen',
                                hotkey=[button_count + 1])
            button_count += 1
        if the_cat.genderalign != "female" and the_cat.genderalign != "male":
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Change to Cisgender',
                                cat_value=game.switches['cat'],
                                hotkey=[button_count + 1])
            button_count += 1

        if the_cat.age in ['young adult', 'adult', 'senior adult'
                           ] and not the_cat.no_kits:
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Prevent kits',
                                no_kits=True,
                                cat_value=the_cat,
                                hotkey=[button_count + 1])
            button_count += 1

        elif the_cat.age in ['young adult', 'adult', 'senior adult'
                             ] and the_cat.no_kits:
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Allow kits',
                                no_kits=False,
                                cat_value=the_cat,
                                hotkey=[button_count + 1])
            button_count += 1
            
        if the_cat.accessory is not None:
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Remove accessory',
                                cat_value=the_cat,
                                hotkey=[button_count + 1])
            button_count += 1

        draw_back(x_value, y_value + button_count * y_change)
        
    def dangerous_tab(self):
        self.draw_header()
        the_cat = Cat.all_cats.get(game.switches['cat'])
        button_count = 0
        x_value = 'center'
        y_value = 150
        y_change = 50

        if not the_cat.dead and not the_cat.exiled:
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Exile Cat',
                                cat_value=game.switches['cat'],
                                hotkey=[12],
                                cur_screen='other screen')
            button_count += 1
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Kill Cat',
                                kill_cat=the_cat,
                                hotkey=[11])
            button_count += 1
        # elif the_cat.dead and not the_cat.exiled:
        #     buttons.draw_button((x_value, y_value + button_count * y_change),
        #                         text='Exile to Dark Forest',
        #                         cat_value=game.switches['cat'],
        #                         hotkey=[11])
        #     button_count += 1

        draw_back(x_value, y_value + button_count * y_change)

    def on_use(self):
        the_cat = Cat.all_cats.get(game.switches['cat'])
        verdana_big.text('Options - ' + str(the_cat.name), ('center', 40))
        button_count = 0
        x_value = 'center'
        y_value = 150
        y_change = 50

        if game.switches['options_tab'] == "Relations Tab":
            self.relations_tab()
        elif game.switches['options_tab'] == "Roles Tab":
            self.roles_tab()
        elif game.switches['options_tab'] == "Personal Tab":
            self.personal_tab()
        elif game.switches['options_tab'] == "Dangerous Tab":
            self.dangerous_tab()
        else:
            self.relations_tab()

        if game.switches['deputy_switch'] is not False and game.switches[
                'deputy_switch'] is not None and game.switches[
                    'deputy_switch'].status == 'warrior':
            game.clan.deputy = game.switches['deputy_switch']
            game.switches['deputy_switch'].status_change('deputy')
            game.switches['deputy_switch'] = False
        elif game.switches['deputy_switch'] is not False and game.switches[
                'deputy_switch'] is not None and game.switches[
                    'deputy_switch'].status == 'deputy':
            game.clan.deputy = None
            game.switches['deputy_switch'].status_change('warrior')
            game.switches['deputy_switch'] = False

        if game.switches['apprentice_switch'] is not False and game.switches[
                'apprentice_switch'] is not None and game.switches[
                    'apprentice_switch'].status == 'apprentice':
            game.switches['apprentice_switch'].status_change(
                'medicine cat apprentice')
            game.switches['apprentice_switch'] = False

        if game.switches['apprentice_switch'] is not False and game.switches[
                'apprentice_switch'] is not None and game.switches[
                    'apprentice_switch'].status == 'medicine cat apprentice':
            game.switches['apprentice_switch'].status_change('apprentice')
            game.switches['apprentice_switch'] = False

        if game.switches['apprentice_switch'] is not False and game.switches[
                'apprentice_switch'] is not None and game.switches[
                    'apprentice_switch'].status == 'warrior':
            game.switches['apprentice_switch'].status_change('medicine cat')
            game.switches['apprentice_switch'] = False

        if game.switches['apprentice_switch'] is not False and game.switches[
                'apprentice_switch'] is not None and game.switches[
                    'apprentice_switch'].status == 'medicine cat':
            game.switches['apprentice_switch'].status_change('warrior')
            game.switches['apprentice_switch'] = False

        if game.switches['kill_cat'] is not False and game.switches[
                'kill_cat'] is not None:
            if game.switches['kill_cat'].status == 'leader':
                game.clan.leader_lives -= 10
            game.switches['kill_cat'].die()
            game.switches['kill_cat'] = False

class ChangeNameScreen(Screens):

    def on_use(self):
        draw_text_bar()
        verdana.text('Change Name', ('center', 50))
        verdana.text('Add a space between the new prefix and suffix',
                     ('center', 70))
        verdana.text('i.e. Fire heart', ('center', 90))
        buttons.draw_button(('center', -100),
                            text='Change Name',
                            cur_screen='change name screen',
                            cat_value=game.switches['name_cat'])
        draw_back('center', -50)

class ChangeGenderScreen(Screens):

    def on_use(self):
        draw_text_bar()
        verdana.text('Change Gender', ('center', 50))
        verdana.text('You can set this to anything.', ('center', 70))
        buttons.draw_button(('center', -100),
                            text=' Change Gender ',
                            cur_screen='change gender screen',
                            cat_value=game.switches['name_cat'])
        draw_back('center', -50)


class ExileProfileScreen(Screens):
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

        # if game.settings['backgrounds']:  # CAT PLATFORM
        #     if game.clan.current_season == 'Newleaf':
        #         screen.blit(self.newleaf_plt, (55, 200))
        #     elif game.clan.current_season == 'Greenleaf':
        #         screen.blit(self.greenleaf_plt, (55, 200))
        #     elif game.clan.current_season == 'Leaf-bare':
        #         screen.blit(self.leafbare_plt, (55, 200))
        #     elif game.clan.current_season == 'Leaf-fall':
        #         screen.blit(self.leaffall_plt, (55, 200))

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
        count = 0
        buttons.draw_button(('center', 400 + count),
                            text="See Family",
                            cur_screen='see kits screen')
        count += 30

        if not the_cat.dead:
            buttons.draw_button(('center', 400 + count),
                                text="See Relationships",
                                cur_screen='relationship screen')
            count += 30

        buttons.draw_button(('center', 400 + count),
                            text='Options',
                            cur_screen='options screen')

        buttons.draw_button(('center', 510),
                            text='Back',
                            cur_screen=game.switches['last_screen'])

