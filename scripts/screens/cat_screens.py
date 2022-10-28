from .base_screens import Screens, cat_profiles, draw_next_prev_cat_buttons

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
    buttons.draw_image_button((x_value, y_value),
                              button_name='back',
                              text='Back',
                              size=(105, 30),
                              cur_screen='profile screen',
                              hotkey=[0])

def accessory_display_name(accessory):
    if not accessory:
        return ''
    accessory = accessory.lower()
    acc_display = accessory
    if accessory != None:
        if accessory in collars:
            collar_color = None
            if accessory.startswith('crimson'):
                collar_color = 'crimson'
            elif accessory.startswith('blue'):
                collar_color = 'blue'
            elif accessory.startswith('yellow'):
                collar_color = 'yellow'
            elif accessory.startswith('cyan'):
                collar_color = 'cyan'
            elif accessory.startswith('red'):
                collar_color = 'red'
            elif accessory.startswith('lime'):
                collar_color = 'lime'
            elif accessory.startswith('green'):
                collar_color = 'green'
            elif accessory.startswith('rainbow'):
                collar_color = 'rainbow'
            elif accessory.startswith('black'):
                collar_color = 'black'
            elif accessory.startswith('spikes'):
                collar_color = 'spiky'
            elif accessory.startswith('pink'):
                collar_color = 'pink'
            elif accessory.startswith('purple'):
                collar_color = 'purple'
            elif accessory.startswith('multi'):
                collar_color = 'multi'
            if accessory.endswith('bow') and not accessory == 'rainbow':
                acc_display = collar_color + ' bow'
            elif accessory.endswith('bell'):
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
    if accessory == None:
        acc_display = None
    return acc_display

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


        if the_cat.genderalign == None or the_cat.genderalign == True or the_cat.genderalign == False:
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
        verdana_small.text('accessory: ' + str(accessory_display_name(the_cat.accessory)),
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

        # buttons
        count = 0

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
                                      cur_screen='relationship screen')
            if not the_cat.dead:
                buttons.draw_image_button((50, 486),
                                          button_name='see_relationships',
                                          text='see relationships',
                                          size=(172, 36),
                                          cur_screen='see kits screen')
            else:
                buttons.draw_image_button((50, 486),
                                          button_name='see_relationships',
                                          text='see relationships',
                                          size=(172, 36),
                                          cur_screen='see kits screen',
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
                game.switches['apprentice'] = the_cat
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
                               ] and not the_cat.no_kits:
                buttons.draw_image_button((402, 574),
                                          button_name='prevent_kits',
                                          text='Prevent kits',
                                          no_kits=True,
                                          cat_value=the_cat,
                                          size=(172, 36)
                                          )
            elif the_cat.age in ['young adult', 'adult', 'senior adult', 'elder'
                                 ] and the_cat.no_kits:
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

        # BACK BUTTON
        buttons.draw_image_button((25, 60),
                                  button_name='back',
                                  text='Back',
                                  size=(105, 30),
                                  cur_screen=game.switches['last_screen'])


        if game.switches['kill_cat'] is not False and game.switches[
                'kill_cat'] is not None:
            if game.switches['kill_cat'].status == 'leader':
                game.clan.leader_lives -= 10
            game.switches['kill_cat'].die()
            game.switches['kill_cat'] = False

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
        biome.lower()

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
                           ] and not the_cat.dead:
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

        draw_back(25, 25)

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

        draw_back(25, 25)

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

        draw_back(25, 25)
        
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

        draw_back(25, 25)

    def on_use(self):
        the_cat = Cat.all_cats.get(game.switches['cat'])
        verdana_big.text('Options - ' + str(the_cat.name), ('center', 40))
        button_count = 0
        x_value = 'center'
        y_value = 150
        y_change = 50


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
        draw_back(25, 25)

class ChangeGenderScreen(Screens):

    def on_use(self):
        the_cat = Cat.all_cats.get(game.switches['cat'])
        draw_text_bar()
        verdana.text('Change Gender', ('center', 50))
        verdana.text('You can set this to anything.', ('center', 70))
        buttons.draw_button(('center', -100),
                            text=' Change Gender ',
                            cur_screen='change gender screen',
                            gender_align=game.switches['naming_text'])
        draw_back(25, 25)

        if game.switches['gender_align'] == game.switches['naming_text']:
            the_cat.genderalign = game.switches['gender_align']
            game.save_cats()
            game.switches['naming_text'] = ''
