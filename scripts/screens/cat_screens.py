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
                                                      (200, 24)))
        verdana_black.text(game.switches['naming_text'], (315, 204))
    else:
        pygame.draw.rect(screen, 'white', pygame.Rect((300, 200),
                                                      (200, 24)))
        verdana.text(game.switches['naming_text'], (315, 204))

    text_input_frame = pygame.transform.scale(
        pygame.image.load("resources/images/text_input_frame.png").convert_alpha(), (216, 40))
    screen.blit(text_input_frame, (294, 194))


def draw_back(x_value, y_value):
    buttons.draw_image_button((x_value, y_value),
                              button_name='back',
                              text='Back',
                              size=(105, 30),
                              cur_screen=game.switches['last_screen'],
                              profile_tab_group=None,
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
            bs_display = choice(['disgraced leader', 'disgraced deputy'])
            bs_display = bs_display
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
        the_cat = Cat.all_cats.get(game.switches['cat'], game.clan.instructor)

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

        draw_large(the_cat, (100, 200)) # IMAGE

        # THOUGHT
        if len(the_cat.thought) < 100:
            verdana.text(the_cat.thought, ('center', 180))
        else:
            cut = the_cat.thought.find(' ', int(len(the_cat.thought)/2))
            first_part = the_cat.thought[:cut]
            second_part = the_cat.thought[cut:]
            verdana.text(first_part, ('center', 180))
            verdana.text(second_part, ('center', 200))

        if the_cat.genderalign is None or the_cat.genderalign is True or the_cat.genderalign is False:
            verdana_small.text(str(the_cat.gender), (300, 230 + count * 15))
        else:
            verdana_small.text(str(the_cat.genderalign), (300, 230 + count * 15))
        count += 1  # SEX / GENDER
        if the_cat.exiled:
            verdana_red.text("exiled", (490, 230 + count2 * 15))
        else:
            verdana_small.text(the_cat.status, (490, 230 + count2 * 15))
        if not the_cat.dead and 'leader' in the_cat.status:  # See Lives
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

        # ---------------------------------------------------------------------------- #
        #                                 RELATIONS TAB                                #
        # ---------------------------------------------------------------------------- #
        buttons.draw_image_button((48, 420),
                                  button_name='relations',
                                  text="relations",
                                  size=(176, 30),
                                  profile_tab_group='relations',
                                  available=game.switches['profile_tab_group'] != 'relations'
                                  )
        if game.switches['profile_tab_group'] == 'relations':
            buttons.draw_image_button((50, 450),
                                      button_name='see_family',
                                      text='see family',
                                      size=(172, 36),
                                      cur_screen='see kits screen')
            if not the_cat.dead:
                buttons.draw_image_button((50, 486),
                                          button_name='see_relationships',
                                          text='see relationships',
                                          size=(172, 36),
                                          cur_screen='relationship screen')
            else:
                buttons.draw_image_button((50, 486),
                                          button_name='see_relationships',
                                          text='see relationships',
                                          size=(172, 36),
                                          cur_screen='relationship screen',
                                          available=False)
            if the_cat.age in ['young adult', 'adult', 'senior adult', 'elder'
                               ] and not the_cat.dead:
                buttons.draw_image_button((50, 522),
                                          button_name='choose_mate',
                                          text='choose mate',
                                          size=(172, 36),
                                          cur_screen='choose mate screen')
            else:
                buttons.draw_image_button((50, 522),
                                          button_name='choose_mate',
                                          text='choose mate',
                                          size=(172, 36),
                                          available=False)
            if the_cat.status == 'apprentice' and not the_cat.dead:
                buttons.draw_image_button((50, 558),
                                          button_name='change_mentor',
                                          text='change mentor',
                                          size=(172, 36),
                                          cur_screen='choose mentor screen')
            else:
                buttons.draw_image_button((50, 558),
                                          button_name='change_mentor',
                                          text='change mentor',
                                          size=(172, 36),
                                          available=False)
            buttons.draw_image_button((50, 594),
                                      button_name='close',
                                      text='close',
                                      size=(172, 36),
                                      profile_tab_group=None)

        # ---------------------------------------------------------------------------- #
        #                                 ROLES TAB                                    #
        # ---------------------------------------------------------------------------- #
        buttons.draw_image_button((224, 420),
                                  button_name='roles',
                                  text="roles",
                                  size=(176, 30),
                                  profile_tab_group='roles',
                                  available=game.switches['profile_tab_group'] != 'roles'
                                  )
        if game.switches['profile_tab_group'] == 'roles':
            the_cat = Cat.all_cats.get(game.switches['cat'])
            if game.switches['new_leader'] is not False and game.switches['new_leader'] is not None:
                game.clan.new_leader(game.switches['new_leader'])
            if the_cat.status in ['warrior'
                                  ] and not the_cat.dead and game.clan.leader.dead and not the_cat.exiled:
                buttons.draw_image_button((226, 450),
                                          button_name='promote_leader',
                                          text='promote to leader',
                                          new_leader=the_cat,
                                          size=(172, 36),
                                          )
            else:
                buttons.draw_image_button((226, 450),
                                          button_name='promote_leader',
                                          text='promote to leader',
                                          size=(172, 36),
                                          available=False)
            if the_cat.status in [
                'warrior'
            ] and not the_cat.dead and not the_cat.exiled and game.clan.deputy is None:
                buttons.draw_image_button((226, 486),
                                          button_name='promote_deputy',
                                          text='promote to deputy',
                                          size=(172, 36),
                                          deputy_switch=the_cat
                                          )
            else:
                buttons.draw_image_button((226, 486),
                                          button_name='promote_deputy',
                                          text='promote to deputy',
                                          size=(172, 36),
                                          available=False
                                          )
            if the_cat.status in ['deputy'] and not the_cat.dead and not the_cat.exiled:
                buttons.draw_image_button((226, 486),
                                          button_name='demote_deputy',
                                          text='demote from deputy',
                                          deputy_switch=the_cat,
                                          size=(172, 36),
                                          )
            if the_cat.status in ['apprentice'] and not the_cat.dead and not the_cat.exiled:
                buttons.draw_image_button((226, 522),
                                          button_name='switch_med_app',
                                          text='switch to medicine cat apprentice',
                                          size=(172, 52),
                                          apprentice_switch=the_cat,
                                          )
                buttons.draw_image_button((226, 574),
                                          button_name='close',
                                          text='close',
                                          size=(172, 36),
                                          profile_tab_group=None)
            elif the_cat.status in ['medicine cat apprentice'
                                    ] and not the_cat.dead and not the_cat.exiled:
                buttons.draw_image_button((226, 522),
                                          button_name='switch_warrior_app',
                                          text='switch to warrior apprentice',
                                          size=(172, 52),
                                          apprentice_switch=the_cat,
                                          )
                buttons.draw_image_button((226, 574),
                                          button_name='close',
                                          text='close',
                                          size=(172, 36),
                                          profile_tab_group=None)
            elif the_cat.status == 'warrior' and not the_cat.dead and not the_cat.exiled:
                buttons.draw_image_button((226, 522),
                                          button_name='switch_med_cat',
                                          text='switch to medicine cat',
                                          size=(172, 52),
                                          apprentice_switch=the_cat,
                                          )
                buttons.draw_image_button((226, 574),
                                          button_name='close',
                                          text='close',
                                          size=(172, 36),
                                          profile_tab_group=None)
            elif the_cat.status == 'elder' and not the_cat.dead and not the_cat.exiled:
                buttons.draw_image_button((226, 522),
                                              button_name='switch_med_cat',
                                              text='switch to medicine cat',
                                              size=(172, 52),
                                              apprentice_switch=the_cat,
                                              available=False
                                              )
                buttons.draw_image_button((226, 574),
                                              button_name='close',
                                              text='close',
                                              size=(172, 36),
                                              profile_tab_group=None)
            elif the_cat.status == 'medicine cat' and not the_cat.dead and not the_cat.exiled:
                buttons.draw_image_button((226, 522),
                                          button_name='switch_warrior',
                                          text='switch to warrior',
                                          apprentice_switch=the_cat,
                                          size=(172, 36),
                                          )
                buttons.draw_image_button((226, 558),
                                          button_name='close',
                                          text='close',
                                          size=(172, 36),
                                          profile_tab_group=None)
            else:
                buttons.draw_image_button((226, 522),
                                          button_name='close',
                                          text='close',
                                          size=(172, 36),
                                          profile_tab_group=None)

        #  ROLE SWITCHES
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

        # ---------------------------------------------------------------------------- #
        #                                 PERSONAL TAB                                 #
        # ---------------------------------------------------------------------------- #
        game.switches['gender_align'] = the_cat.genderalign
        buttons.draw_image_button((400, 420),
                                  button_name='personal',
                                  text="personal",
                                  size=(176, 30),
                                  profile_tab_group='personal',
                                  available=game.switches['profile_tab_group'] != 'personal',
                                  )
        if game.switches['profile_tab_group'] == 'personal':
            buttons.draw_image_button((402, 450),
                                      button_name='change_name',
                                      text='change name',
                                      cur_screen='change name screen',
                                      size=(172, 36),
                                      )
            if the_cat.genderalign == "female":
                buttons.draw_image_button((402, 486),
                                          button_name='change_trans_male',
                                          text='change to trans male',
                                          size=(172, 52),
                                          gender_align='trans male'
                                          )
                if game.switches['gender_align'] == 'trans male':
                    the_cat.genderalign = 'trans male'

            elif the_cat.genderalign == "male":
                buttons.draw_image_button((402, 486),
                                          button_name='change_trans_female',
                                          text='change to trans female',
                                          size=(172, 52),
                                          gender_align='trans female',
                                          )
                if game.switches['gender_align'] == 'trans female':
                    the_cat.genderalign = 'trans female'

            elif the_cat.genderalign != "female" and the_cat.genderalign != "male":
                buttons.draw_image_button((402, 486),
                                          button_name='change_cis',
                                          text='change to cisgender',
                                          size=(172, 52),
                                          gender_align=the_cat.gender,
                                          )
                if game.switches['gender_align'] == the_cat.gender:
                    the_cat.genderalign = the_cat.gender

            buttons.draw_image_button((402, 538),
                                      button_name='specify_gender',
                                      text='specify gender',
                                      size=(172, 36),
                                      cat_value=game.switches['cat'],
                                      cur_screen='change gender screen'
                                      )
            if the_cat.age in ['young adult', 'adult', 'senior adult', 'elder'
                               ] and not the_cat.no_kits and not the_cat.dead:
                buttons.draw_image_button((402, 574),
                                          button_name='prevent_kits',
                                          text='Prevent kits',
                                          no_kits=True,
                                          cat_value=the_cat,
                                          size=(172, 36)
                                          )
            elif the_cat.age in ['young adult', 'adult', 'senior adult', 'elder'
                                 ] and the_cat.no_kits and not the_cat.dead:
                buttons.draw_image_button((402, 574),
                                          button_name='allow_kits',
                                          text='Allow kits',
                                          no_kits=False,
                                          cat_value=the_cat,
                                          size=(172, 36)
                                          )
            else:
                buttons.draw_image_button((402, 574),
                                          button_name='prevent_kits',
                                          text='Prevent kits',
                                          no_kits=True,
                                          cat_value=the_cat,
                                          size=(172, 36),
                                          available=False
                                          )
            buttons.draw_image_button((402, 610),
                                      button_name='close',
                                      text='close',
                                      size=(172, 36),
                                      profile_tab_group=None)

            # DISABLED till I make button image and re-establish functionality
            #if the_cat.accessory != None:
            #    buttons.draw_button((x_value, y_value + button_count * y_change),
            #                        text='Remove accessory',
            #                        cat_value=the_cat,
            #                        hotkey=[button_count + 1])

        # ---------------------------------------------------------------------------- #
        #                                 DANGEROUS TAB                                #
        # ---------------------------------------------------------------------------- #
        buttons.draw_image_button((576, 420),
                                  button_name='dangerous',
                                  text="dangerous",
                                  size=(176, 30),
                                  profile_tab_group='dangerous',
                                  available=game.switches['profile_tab_group'] != 'dangerous'
                                  )

        # EXILE BUTTON DISABLED FOR NOW.  remove available=False when functionality is added
        if game.switches['profile_tab_group'] == 'dangerous':
            buttons.draw_image_button((578, 450),
                                      button_name='exile_cat',
                                      text='exile cat',
                                      available=False,
                                      size=(172, 36),
                                      )

            if not the_cat.dead and not the_cat.exiled:
                buttons.draw_image_button((578, 486),
                                          button_name='kill_cat',
                                          text='kill cat',
                                          size=(172, 36),
                                          kill_cat=the_cat,
                                          )
            else:
                buttons.draw_image_button((578, 486),
                                          button_name='kill_cat',
                                          text='kill cat',
                                          size=(172, 36),
                                          kill_cat=the_cat,
                                          available=False
                                          )
            buttons.draw_image_button((578, 522),
                                      button_name='close',
                                      text='close',
                                      size=(172, 36),
                                      profile_tab_group=None)

            # KILL SWITCH
            if game.switches['kill_cat'] is not False and game.switches[
                    'kill_cat'] is not None:
                if game.switches['kill_cat'].status == 'leader':
                    game.clan.leader_lives -= 10
                game.switches['kill_cat'].die()
                game.switches['kill_cat'] = False

        # BACK BUTTON
        draw_back(25, 60)


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
            pygame.image.load(all_platforms[0]).convert_alpha(), (240, 210))
        self.greenleaf_plt = pygame.transform.scale(
            pygame.image.load(all_platforms[1]).convert_alpha(), (240, 210))
        self.leafbare_plt = pygame.transform.scale(
            pygame.image.load(all_platforms[2]).convert_alpha(), (240, 210))
        self.leaffall_plt = pygame.transform.scale(
            pygame.image.load(all_platforms[3]).convert_alpha(), (240, 210))

    def screen_switches(self):
        cat_profiles()
        self.update_platform()


class ChangeNameScreen(Screens):

    def on_use(self):
        the_cat = Cat.all_cats.get(game.switches['cat'])

        draw_text_bar()
        verdana.text('-Change Name-', ('center', 130))
        verdana.text('Add a space between the new prefix and suffix',
                     ('center', 150))
        verdana.text('i.e. Fire heart', ('center', 170))

        buttons.draw_image_button((365, 272),
                                  button_name='done',
                                  text='done',
                                  size=(77, 30),
                                  change_name=['naming_text'],
                                  )

        if game.switches['change_name'] != '':
            name = game.switches['naming_text'].split(' ')
            the_cat.name.prefix = name[0]
            if len(name) > 1:
                # If cat is an apprentice/kit and new suffix is paw/kit, leave hidden suffix unchanged
                if not (the_cat.name.status == "apprentice" and name[1] == "paw") and \
                        not (the_cat.name.status == "kitten" and name[1] == "kit"):
                    the_cat.name.suffix = name[1]
            game.switches['naming_text'] = ''
            game.switches['cur_screen'] = 'name changed screen'
        draw_back(25, 25)


class NameChangedScreen(Screens):
    def on_use(self):
        the_cat = Cat.all_cats.get(game.switches['cat'])

        draw_text_bar()
        verdana.text('-Change Name-', ('center', 130))
        verdana.text('Add a space between the new prefix and suffix',
                     ('center', 150))
        verdana.text('i.e. Fire heart', ('center', 170))

        buttons.draw_image_button((365, 272),
                                  button_name='done',
                                  text='done',
                                  size=(77, 30),
                                  name_cat=['naming_text'],
                                  available=False
                                  )

        game.switches['change_name'] = ''
        verdana.text('Name changed!', ('center', 240))

        buttons.draw_image_button((25, 25),
                                  button_name='back',
                                  text='Back',
                                  size=(105, 30),
                                  cur_screen='profile screen',
                                  profile_tab_group=None,
                                  hotkey=[0])


class ChangeGenderScreen(Screens):

    def on_use(self):
        the_cat = Cat.all_cats.get(game.switches['cat'])
        draw_text_bar()
        verdana.text('-Change Gender-', ('center', 130))
        verdana.text('You can set this to anything.', ('center', 150))
        buttons.draw_image_button((365, 272),
                                  button_name='done',
                                  text='done',
                                  size=(77, 30),
                                  gender_align=game.switches['naming_text'],
                                  )

        if game.switches['gender_align'] == game.switches['naming_text']:
            the_cat.genderalign = game.switches['gender_align']
            game.switches['naming_text'] = ''
            game.switches['cur_screen'] = 'gender changed screen'

        draw_back(25, 25)


class GenderChangedScreen(Screens):

    def on_use(self):
        gender_chosen = False
        the_cat = Cat.all_cats.get(game.switches['cat'])
        draw_text_bar()
        verdana.text('Change Gender', ('center', 130))
        verdana.text('You can set this to anything.', ('center', 150))
        buttons.draw_image_button((365, 272),
                                  button_name='done',
                                  text='done',
                                  size=(77, 30),
                                  gender_align=game.switches['naming_text'],
                                  available=False
                                  )

        verdana.text('Gender changed!', ('center', 240))

        buttons.draw_image_button((25, 25),
                                  button_name='back',
                                  text='Back',
                                  size=(105, 30),
                                  cur_screen='profile screen',
                                  profile_tab_group=None,
                                  hotkey=[0])


