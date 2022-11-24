from random import choice

from .base_screens import Screens, cat_profiles, draw_next_prev_cat_buttons

from scripts.utility import draw_large
from scripts.game_structure.text import *
from scripts.game_structure.buttons import buttons
from scripts.cat.cats import Cat
from scripts.cat.pelts import collars, wild_accessories
import scripts.game_structure.image_cache as image_cache


# ---------------------------------------------------------------------------- #
#                 draw the text bar that the player can input into             #
# ---------------------------------------------------------------------------- #
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
        image_cache.load_image("resources/images/text_input_frame.png").convert_alpha(), (216, 40))
    screen.blit(text_input_frame, (294, 194))


# ---------------------------------------------------------------------------- #
#                               draw back button                               #
# ---------------------------------------------------------------------------- #
def draw_back(x_value, y_value):
    the_cat = Cat.all_cats.get(game.switches['cat'])

    if (the_cat.exiled):
        buttons.draw_image_button((x_value, y_value),
                                  button_name='back',
                                  text='Back',
                                  size=(105, 30),
                                  cur_screen='other screen',
                                  cat_value = the_cat,
                                  profile_tab_group=None,
                                  hotkey=[0])
    elif (the_cat.df):
        buttons.draw_image_button((x_value, y_value),
                                  button_name='back',
                                  text='Back',
                                  size=(105, 30),
                                  cur_screen='dark forest screen',
                                  cat_value = the_cat,
                                  df = True,
                                  profile_tab_group=None,
                                  hotkey=[0])
    else:
        buttons.draw_image_button((x_value, y_value),
                                  button_name='back',
                                  text='Back',
                                  size=(105, 30),
                                  cur_screen=game.switches['last_screen'],
                                  profile_tab_group=None,
                                  hotkey=[0])

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

        # ---------------------------------------------------------------------------- #
        #                                   layout                                     #
        # ---------------------------------------------------------------------------- #
        count = 0
        count2 = 0

        # NAME
        verdana_big.text(cat_name, ('center', 150))

        # CAT PLATFORM
        if game.settings['backgrounds']:
            if game.clan.current_season == 'Newleaf':
                screen.blit(self.newleaf_plt, (55, 200))
            elif game.clan.current_season == 'Greenleaf':
                screen.blit(self.greenleaf_plt, (55, 200))
            elif game.clan.current_season == 'Leaf-bare':
                screen.blit(self.leafbare_plt, (55, 200))
            elif game.clan.current_season == 'Leaf-fall':
                screen.blit(self.leaffall_plt, (55, 200))

        # IMAGE
        draw_large(the_cat, (100, 200))

        # THOUGHT
        if len(the_cat.thought) < 100:
            verdana.text(the_cat.thought, ('center', 180))
        else:
            cut = the_cat.thought.find(' ', int(len(the_cat.thought)/2))
            first_part = the_cat.thought[:cut]
            second_part = the_cat.thought[cut:]
            verdana.text(first_part, ('center', 180))
            verdana.text(second_part, ('center', 200))

        # SEX / GENDER
        if the_cat.genderalign is None or the_cat.genderalign == the_cat.gender:
            verdana_small.text(str(the_cat.gender), (300, 230 + count * 15))

        else:
            verdana_small.text(str(the_cat.genderalign), (300, 230 + count * 15))
        count += 1

        if the_cat.exiled:
            verdana_red.text("exiled", (490, 230 + count2 * 15))

        else:
            verdana_small.text(the_cat.status, (490, 230 + count2 * 15))

        # SEE LEADER LIVES
        if not the_cat.dead and 'leader' in the_cat.status:
            count2 += 1
            verdana_small.text(
                'remaining lives: ' + str(game.clan.leader_lives),
                (490, 230 + count2 * 15))
        count2 += 1

        # MENTOR
        if 'apprentice' in the_cat.status:
            if the_cat.mentor is None:
                the_cat.update_mentor()
            if the_cat.mentor is not None:
                verdana_small.text('mentor: ' + str(the_cat.mentor.name),
                                   (490, 230 + count2 * 15))
                count2 += 1

        # APPRENTICE
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

        # FORMER APPRENTICES
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
                count2 += 1

            elif len(the_cat.former_apprentices) == 4:
                former_apps = 'former apprentices: ' + str(
                    the_cat.former_apprentices[0].name) + ', ' + str(
                        the_cat.former_apprentices[1].name)
                verdana_small.text(former_apps, (490, 230 + count2 * 15))
                count2 += 1

                former_apps2 = str(the_cat.former_apprentices[2].name) + ', ' + str(the_cat.former_apprentices[3].name)
                verdana_small.text(former_apps2, (490, 230 + count2 * 15))
                count2 += 1

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

        # AGE
        if the_cat.age == 'kitten':
            verdana_small.text('young', (300, 230 + count * 15))

        elif the_cat.age == 'elder':
            verdana_small.text('senior', (300, 230 + count * 15))

        else:
            verdana_small.text(the_cat.age, (300, 230 + count * 15))
        count += 1

        # CHARACTER TRAIT
        verdana_small.text(the_cat.trait, (490, 230 + count2 * 15))
        count2 += 1

        # SPECIAL SKILL
        verdana_small.text(the_cat.skill, (490, 230 + count2 * 15))
        count2 += 1

        # EYE COLOR
        verdana_small.text('eyes: ' + the_cat.eye_colour.lower(),
                           (300, 230 + count * 15))
        count += 1

        # PELT TYPE
        verdana_small.text('pelt: ' + the_cat.pelt.name.lower(),
                           (300, 230 + count * 15))
        count += 1

        # PELT LENGTH
        verdana_small.text('fur length: ' + the_cat.pelt.length,
                           (300, 230 + count * 15))
        count += 1

        # ACCESSORY
        verdana_small.text('accessory: ' + str(accessory_display_name(the_cat, the_cat.accessory)),
                           (300, 230 + count * 15))
        count += 1

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
                ).dead:  
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

        # EXPERIENCE
        if not the_cat.dead:
            verdana_small.text('experience: ' + str(the_cat.experience_level),
                               (490, 230 + count2 * 15))
            count2 += 1

        else:
            verdana_small.text('experience: ' + str(the_cat.experience_level),
                               (490, 230 + count2 * 15))
            count2 += 1

        # BACKSTORY
        if the_cat.backstory is not None:
            bs_text = backstory_text(the_cat)
            verdana_small.text('backstory: ' + bs_text, (490, 230 + count2 * 15))
            count2 += 1

        else:
            verdana_small.text('backstory: ' + 'clanborn', (490, 230 + count2 * 15))
            count2 += 1

        the_cat = Cat.all_cats.get(game.switches['cat'])

        # ---------------------------------------------------------------------------- #
        #                                 BACKSTORY TAB                                #
        # ---------------------------------------------------------------------------- #

        # backstory tab and placeholder tabs MUST be above the other tabs in the code so that they blit onto the screen
        # first and display UNDERNEATH the other tabs when the tabs are open

        # closes backstory tab if clicked
        if game.switches['profile_tab_group'] == 'backstory':
            buttons.draw_image_button((48, 622),
                                      button_name='backstory',
                                      text="backstory",
                                      size=(176, 30),
                                      profile_tab_group=None,
                                      )
            screen.blit(ProfileScreen.backstory_tab, (65, 465))

            if game.switches['sub_tab_group'] is None:
                game.switches['sub_tab_group'] = 'life sub tab'

            # this is all a WIP, I'm working on both organizing history into tab categories
            # and saving/displaying history - Scribble
            # ---------------------------------------------------------------------------- #
            #                                 life sub tab                                 #
            # ---------------------------------------------------------------------------- #
            """
            this will hold history related to the cat's life time.  atm i plan for this to be:
            - backstory blurb
            - scar events
            - death event (will need to find a clever way to display leader death events without running out of room)
            """

            buttons.draw_image_button((710, 475),
                                      button_name='sub_tab1',
                                      size=(42, 30),
                                      sub_tab_group='life sub tab'
                                      )

            if game.switches['sub_tab_group'] == 'life sub tab':


                life_history = []

                bs_blurb = bs_blurb_text(the_cat, backstory=the_cat.backstory)

                # append backstory blurb to history
                if bs_blurb is not None:
                    life_history.append(str(bs_blurb))
                else:
                    life_history.append("This cat was born into the clan where they currently reside.")

                # adjust and append scar events to history
                if the_cat.scar_event:
                    scar_text = the_cat.scar_event
                    for x in range(len(the_cat.scar_event)):
                        scar_text[x] = str(the_cat.scar_event[x]).replace(' is ', ' was ', 1)
                        scar_text[x] = str(the_cat.scar_event[x]).replace(' loses ', ' lost ')
                        scar_text[x] = str(the_cat.scar_event[x]).replace(' forces ', ' forced ')

                        not_scarred = ['wounded', 'injured', 'battered', 'hurt', 'punished']
                        for y in not_scarred:
                            scar_text[x] = str(the_cat.scar_event[x]).replace(f' got {y} ', ' was scarred ')
                            scar_text[x] = str(the_cat.scar_event[x]).replace(y, ' scarred ')
                            break
                        if x == 0:
                            scar_text[x] = str(the_cat.scar_event[x]).replace(f'{the_cat.name} ', 'This cat ', 1)
                        elif x == 1:
                            scar_text[x] = str(the_cat.scar_event[x]).replace(f'{the_cat.name} was ', 'They were also ', 1)
                            scar_text[x] = str(the_cat.scar_event[x]).replace(str(the_cat.name), 'They also', 1)
                        elif x >= 3:
                            scar_text[x] = str(the_cat.scar_event[x]).replace(f'{the_cat.name} was ', 'Then they were ', 1)
                            scar_text[x] = str(the_cat.scar_event[x]).replace(str(the_cat.name), 'Then they', 1)
                    scar_history = ' '.join(scar_text)
                    life_history.append(scar_history)

                # join together history list with line breaks
                display_history = '\n'.join(life_history)

                # display cat backstory and blurb in tab
                verdana_small_dark.blit_text(f'{display_history}',
                                             (90, 485),
                                             x_limit=695,
                                             line_break=25,
                                             line_spacing=15
                                             )

            # ---------------------------------------------------------------------------- #
            #                               relation sub tab                               #
            # ---------------------------------------------------------------------------- #
            """
            this will hold history related to relationships with other cats.  atm i plan for this to be:
            - Mentor Influence
            - Former mates and # of kits had with them
            - Current mate and # of kits had with them
            """

            # check if cat has any mentor influence, else assign None
            if len(the_cat.mentor_influence) >= 1:
                influenced_trait = str(the_cat.mentor_influence[0])
                if len(the_cat.mentor_influence) >= 2:
                    influenced_skill = str(the_cat.mentor_influence[1])
                else:
                    influenced_skill = None
            else:
                game.switches['sub_tab_group'] = 'life sub tab'
                influenced_trait = None
                influenced_skill = None

            # if they did have mentor influence, check if skill or trait influence actually happened and assign None
            if influenced_skill in ['None', 'none']:
                influenced_skill = None
            if influenced_trait in ['None', 'none']:
                influenced_trait = None

            if influenced_skill is not None or influenced_trait is not None:
                buttons.draw_image_button((710, 512),
                                          button_name='sub_tab2',
                                          size=(42, 30),
                                          sub_tab_group='relation sub tab'
                                          )
            else:
                buttons.draw_image_button((710, 512),
                                          button_name='sub_tab',
                                          size=(42, 30),
                                          available=False
                                          )

            if game.switches['sub_tab_group'] == 'relation sub tab':
                screen.blit(ProfileScreen.backstory_tab, (65, 465))

                relation_history = []

                # if cat had mentor influence then write history text for those influences and append to history
                    # assign proper grammar to skills
                vowels = ['e', 'a', 'i', 'o', 'u']
                if influenced_skill in Cat.skill_groups.get('special'):
                    adjust_skill = f'unlock their abilities as a {influenced_skill}'
                    for y in vowels:
                        if influenced_skill.startswith(y):
                            adjust_skill = adjust_skill.replace(' a ', ' an ')
                            break
                    influenced_skill = adjust_skill
                elif influenced_skill in Cat.skill_groups.get('star'):
                    adjust_skill = f'grow a {influenced_skill}'
                    influenced_skill = adjust_skill
                elif influenced_skill in Cat.skill_groups.get('smart'):
                    adjust_skill = f'become {influenced_skill}'
                    influenced_skill = adjust_skill
                else:
                    # for loop to assign proper grammar to all these groups
                    become_group = ['heal', 'teach', 'mediate', 'hunt', 'fight', 'speak']
                    for x in become_group:
                        if influenced_skill in Cat.skill_groups.get(x):
                            adjust_skill = f'become a {influenced_skill}'
                            for y in vowels:
                                if influenced_skill.startswith(y):
                                    adjust_skill = adjust_skill.replace(' a ', ' an ')
                                    break
                            influenced_skill = adjust_skill
                            break

                mentor = the_cat.former_mentor[-1].name

                # append influence blurb to history
                if influenced_trait is not None and influenced_skill is None:
                    relation_history.append(f"The influence of their mentor, {mentor}, caused this cat to become more {influenced_trait}.")
                elif influenced_trait is None and influenced_skill is not None:
                    relation_history.append(f"The influence of their mentor, {mentor}, caused this cat to {influenced_skill}.")
                elif influenced_trait is not None and influenced_skill is not None:
                    relation_history.append(f"The influence of their mentor, {mentor}, caused this cat to become more {influenced_trait} as well as {influenced_skill}.")

                # join together history list with line breaks
                display_history = '\n'.join(relation_history)

                # display cat backstory and blurb in tab
                verdana_small_dark.blit_text(f'{display_history}',
                                             (90, 485),
                                             x_limit=695,
                                             line_break=25,
                                             line_spacing=15
                                             )

            # ---------------------------------------------------------------------------- #
            #                              good deeds sub tab                              #
            # ---------------------------------------------------------------------------- #
            """
            this will hold history related to 'good deeds' done by the cat.  atm i plan for this to be:
            - cats that have been saved by this cat
            - cats they have adopted?
            - if we further develop interactions StarClan cats have with living cats, then there is potential for 
            this to hold any important events that a dead cat is included in.
            """

            # commented out until i have info that can be put in this tab
            #buttons.draw_image_button((710, 549),
            #                          button_name='sub_tab3',
            #                          size=(42, 30),
            #                          sub_tab_group='relation sub tab'
            #                          )
            buttons.draw_image_button((710, 549),
                                      button_name='sub_tab',
                                      size=(42, 30),
                                      available=False
                                      )

            # ---------------------------------------------------------------------------- #
            #                              evil deeds sub tab                              #
            # ---------------------------------------------------------------------------- #
            """
            this will hold history related to 'evil deeds' done by the cat.  atm i plan for this to be:
            - cats murdered by this cat
            - if we implement a "corruption" mechanic for living cats targeted by DF then perhaps info on those can
            be included here?
            """
            # commented out until i have info that can be put in this tab
            #buttons.draw_image_button((710, 549),
            #                          button_name='sub_tab3',
            #                          size=(42, 30),
            #                          sub_tab_group='relation sub tab'
            #                          )
            buttons.draw_image_button((710, 586),
                                      button_name='sub_tab',
                                      size=(42, 30),
                                      available=False
                                      )

        # opens backstory tab if clicked
        else:
            buttons.draw_image_button((48, 622),
                                      button_name='backstory',
                                      text="backstory",
                                      size=(176, 30),
                                      profile_tab_group='backstory',
                                      available=game.switches['profile_tab_group'] not in ['backstory', 'relations'],
                                      )

        # ---------------------------------------------------------------------------- #
        #                              PLACEHOLDER TABS                                #
        # ---------------------------------------------------------------------------- #

        # these are only here to balance out the UI, we can replace them later with functional tabs

        buttons.draw_image_button((224, 622),
                                  button_name='cat_tab_3_blank',
                                  text='placeholder',
                                  size=(176, 30),
                                  available=False)
        buttons.draw_image_button((400, 622),
                                  button_name='cat_tab_3_blank',
                                  text='placeholder',
                                  size=(176, 30),
                                  available=False)
        buttons.draw_image_button((576, 622),
                                  button_name='cat_tab_4_blank',
                                  text='placeholder',
                                  size=(176, 30),
                                  available=False)

        # ---------------------------------------------------------------------------- #
        #                                 RELATIONS TAB                                #
        # ---------------------------------------------------------------------------- #

        # open relations tab
        buttons.draw_image_button((48, 420),
                                  button_name='relations',
                                  text="relations",
                                  size=(176, 30),
                                  profile_tab_group='relations',
                                  available=game.switches['profile_tab_group'] != 'relations'
                                  )

        # buttons within the relations tab group
        if game.switches['profile_tab_group'] == 'relations':
            # take to see family screen
            buttons.draw_image_button((50, 450),
                                      button_name='see_family',
                                      text='see family',
                                      size=(172, 36),
                                      cur_screen='see kits screen')

            # take to see the relationship screen
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

            # take to see the choose mate screen (only available if cat is old enough)
            if the_cat.age in ['young adult', 'adult', 'senior adult', 'elder'
                               ] and not the_cat.dead and not the_cat.exiled:
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

            # take to see the change mentor screen (only available if cat is apprentice)
            if the_cat.status in ['apprentice', 'medicine cat apprentice'] and not the_cat.dead:
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

            # close the tab group
            buttons.draw_image_button((50, 594),
                                      button_name='close',
                                      text='close',
                                      size=(172, 36),
                                      profile_tab_group=None)

        # ---------------------------------------------------------------------------- #
        #                                 ROLES TAB                                    #
        # ---------------------------------------------------------------------------- #

        # open roles tab group
        buttons.draw_image_button((224, 420),
                                  button_name='roles',
                                  text="roles",
                                  size=(176, 30),
                                  profile_tab_group='roles',
                                  available=game.switches['profile_tab_group'] != 'roles'
                                  )

        # the buttons within the roles tab group
        if game.switches['profile_tab_group'] == 'roles':
            the_cat = Cat.all_cats.get(game.switches['cat'])

            # promote a cat to new leader if no leader is alive
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

            # promote a cat to deputy if no deputy is alive
            deputy = game.clan.deputy
            if game.clan.deputy is None:
                deputy = None
            elif game.clan.deputy.exiled:
                deputy = None
            elif game.clan.deputy.dead:
                deputy = None

            if the_cat.status in [
                'warrior'
            ] and not the_cat.dead and not the_cat.exiled and deputy is None:
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

            # demote a cat from deputy
            if the_cat.status in ['deputy'] and not the_cat.dead and not the_cat.exiled:
                buttons.draw_image_button((226, 486),
                                          button_name='demote_deputy',
                                          text='demote from deputy',
                                          deputy_switch=the_cat,
                                          size=(172, 36),
                                          )

            # switch an apprentice from warrior to med cat apprentice
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

            # switch an apprentice from med cat apprentice to warrior apprentice
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

            # switch a warrior to med cat
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

            # switch an elder to med cat
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

            # switch a med cat to warrior
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
            # close tab group
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

        # opens personal tab group
        buttons.draw_image_button((400, 420),
                                  button_name='personal',
                                  text="personal",
                                  size=(176, 30),
                                  profile_tab_group='personal',
                                  available=game.switches['profile_tab_group'] != 'personal',
                                  )

        # buttons within tab group
        if game.switches['profile_tab_group'] == 'personal':
            # take to name change screen
            buttons.draw_image_button((402, 450),
                                      button_name='change_name',
                                      text='change name',
                                      cur_screen='change name screen',
                                      size=(172, 36),
                                      )

            # change cat to trans male
            if the_cat.gender == "female" and the_cat.genderalign in ['male', 'female']:
                buttons.draw_image_button((402, 486),
                                          button_name='change_trans_male',
                                          text='change to trans male',
                                          size=(172, 52),
                                          gender_align='trans male'
                                          )
                if game.switches['gender_align'] == 'trans male':
                    the_cat.genderalign = 'trans male'

            # change cat to trans female
            elif the_cat.gender == "male" and the_cat.genderalign in ['male', 'female']:
                buttons.draw_image_button((402, 486),
                                          button_name='change_trans_female',
                                          text='change to trans female',
                                          size=(172, 52),
                                          gender_align='trans female',
                                          )
                if game.switches['gender_align'] == 'trans female':
                    the_cat.genderalign = 'trans female'

            # change cat to cisgender
            elif the_cat.genderalign != "female" and the_cat.genderalign != "male":
                buttons.draw_image_button((402, 486),
                                          button_name='change_cis',
                                          text='change to cisgender',
                                          size=(172, 52),
                                          gender_align=the_cat.gender,
                                          )
                if game.switches['gender_align'] == the_cat.gender:
                    the_cat.genderalign = the_cat.gender

            # take to specify gender screen
            buttons.draw_image_button((402, 538),
                                      button_name='specify_gender',
                                      text='specify gender',
                                      size=(172, 36),
                                      cat_value=game.switches['cat'],
                                      cur_screen='change gender screen'
                                      )

            # prevent kits if kits are allowed
            if the_cat.age in ['young adult', 'adult', 'senior adult', 'elder'
                               ] and not the_cat.no_kits and not the_cat.dead:
                buttons.draw_button((402, 574),
                                          image='buttons/prevent_kits',
                                          text='Prevent kits',
                                          no_kits=True,
                                          cat_value=the_cat,
                                          )

            # allow kits if kits are prevented
            elif the_cat.age in ['young adult', 'adult', 'senior adult', 'elder'
                                 ] and the_cat.no_kits and not the_cat.dead:
                buttons.draw_button((402, 574),
                                          image='buttons/allow_kits',
                                          text='Allow kits',
                                          no_kits=False,
                                          cat_value=the_cat,
                                          )
            else:
                buttons.draw_button((402, 574),
                                          image='buttons/prevent_kits',
                                          text='Prevent kits',
                                          no_kits=True,
                                          cat_value=the_cat,
                                          available=False
                                          )

            # close tab group
            buttons.draw_image_button((402, 610),
                                      button_name='close',
                                      text='close',
                                      size=(172, 36),
                                      profile_tab_group=None)

            # DISABLED till I make button image and re-establish functionality
            if the_cat.accessory != None:
               buttons.draw_button((410,650),
                                   text='Remove accessory',
                                   cat_value=the_cat)

        # ---------------------------------------------------------------------------- #
        #                                 DANGEROUS TAB                                #
        # ---------------------------------------------------------------------------- #

        # open dangerous tab
        buttons.draw_image_button((576, 420),
                                  button_name='dangerous',
                                  text="dangerous",
                                  size=(176, 30),
                                  profile_tab_group='dangerous',
                                  available=game.switches['profile_tab_group'] != 'dangerous'
                                  )


        if game.switches['profile_tab_group'] == 'dangerous':
            # button to kill cat
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
            if not the_cat.dead and not the_cat.exiled:
                buttons.draw_image_button((578, 450),
                                          button_name='exile_cat',
                                          text='exile cat',
                                          available=True,
                                          cat_value=the_cat,
                                          size=(172, 36),
                                          )
            else:
                if not the_cat.df:
                    buttons.draw_image_button((578, 450),
                                              button_name='exile_df',
                                              text='Exile to DF',
                                              available=True,
                                              cat_value=the_cat,
                                              size=(172, 46),
                                              )
                else:
                    buttons.draw_image_button((578, 450),
                                              button_name='exile_df',
                                              text='Exile to DF',
                                              available=False,
                                              cat_value=the_cat,
                                              size=(172, 46),
                                              )


            # close tab group
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

    def screen_switches(self):
        cat_profiles()
        self.update_platform()


# ---------------------------------------------------------------------------- #
#                             change name screen                               #
# ---------------------------------------------------------------------------- #
class ChangeNameScreen(Screens):

    def on_use(self):
        the_cat = Cat.all_cats.get(game.switches['cat'])

        # draw bar for user input
        draw_text_bar()

        # text explanation
        verdana.text('-Change Name-', ('center', 130))
        verdana.text('Add a space between the new prefix and suffix',
                     ('center', 150))
        verdana.text('i.e. Fire heart', ('center', 170))

        # button to switch to Name Changed screen
        buttons.draw_image_button((365, 272),
                                  button_name='done',
                                  text='done',
                                  size=(77, 30),
                                  change_name=['naming_text'],
                                  )

        # changes the name
        if game.switches['change_name'] != '':
            name = game.switches['naming_text'].split(' ')
            if name != ['']:
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

        # draw bar for user input, purely for UI consistency
        draw_text_bar()

        # draw explanation text, purely for UI consistency
        verdana.text('-Change Name-', ('center', 130))
        verdana.text('Add a space between the new prefix and suffix',
                     ('center', 150))
        verdana.text('i.e. Fire heart', ('center', 170))

        # make Done button unavailable
        buttons.draw_image_button((365, 272),
                                  button_name='done',
                                  text='done',
                                  size=(77, 30),
                                  name_cat=['naming_text'],
                                  available=False
                                  )

        # name change confirmation text
        game.switches['change_name'] = ''
        verdana.text('Name changed!', ('center', 240))

        # return to cat profile
        buttons.draw_image_button((25, 25),
                                  button_name='back',
                                  text='Back',
                                  size=(105, 30),
                                  cur_screen='profile screen',
                                  profile_tab_group=None,
                                  hotkey=[0])

# ---------------------------------------------------------------------------- #
#                           change gender screen                               #
# ---------------------------------------------------------------------------- #
class ChangeGenderScreen(Screens):

    def on_use(self):
        the_cat = Cat.all_cats.get(game.switches['cat'])

        # draw bar for user input
        draw_text_bar()

        # draw explanation text
        verdana.text('-Change Gender-', ('center', 130))
        verdana.text('You can set this to anything.', ('center', 150))

        # button to change gender
        buttons.draw_image_button((365, 272),
                                  button_name='done',
                                  text='done',
                                  size=(77, 30),
                                  gender_align=game.switches['naming_text'],
                                  )

        # switch gender
        if game.switches['gender_align'] == game.switches['naming_text']:
            the_cat.genderalign = game.switches['gender_align']
            game.switches['naming_text'] = ''
            game.switches['cur_screen'] = 'gender changed screen'

        draw_back(25, 25)


class GenderChangedScreen(Screens):

    def on_use(self):

        # UI consistency
        draw_text_bar()

        # UI consistency
        verdana.text('Change Gender', ('center', 130))
        verdana.text('You can set this to anything.', ('center', 150))

        # make unavailable
        buttons.draw_image_button((365, 272),
                                  button_name='done',
                                  text='done',
                                  size=(77, 30),
                                  gender_align=game.switches['naming_text'],
                                  available=False
                                  )

        # confirmation text
        verdana.text('Gender changed!', ('center', 240))

        # return to profile screen
        buttons.draw_image_button((25, 25),
                                  button_name='back',
                                  text='Back',
                                  size=(105, 30),
                                  cur_screen='profile screen',
                                  profile_tab_group=None,
                                  hotkey=[0])


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


