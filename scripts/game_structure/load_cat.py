import os
from math import floor
from .game_essentials import game

try:
    import ujson
except ImportError:
    import json as ujson

from scripts.cat.cats import Cat
from scripts.cat.pelts import choose_pelt
from scripts.utility import update_sprite
try:
    from ujson import JSONDecodeError
except ImportError:
    from json import JSONDecodeError

def load_cats():
    try:
        json_load()
    except FileNotFoundError:
        try:
            csv_load(Cat.all_cats)
        except FileNotFoundError:
            game.switches['error_message'] = 'Can\'t find clan_cats.json!'
            raise

def json_load():
    all_cats = []
    cat_data = None
    clanname = game.switches['clan_list'][0]
    try:
        with open('saves/' + clanname + '/clan_cats.json', 'r') as read_file:
            cat_data = ujson.loads(read_file.read())
    except PermissionError:
        game.switches['error_message'] = f'Can\t open saves/{clanname}/clan_cats.json!'
        raise
    except JSONDecodeError:
        game.switches['error_message'] = f'saves/{clanname}/clan_cats.json is malformed!'
        raise
        
    # create new cat objects
    for i, cat in enumerate(cat_data):
        try:
            new_pelt = choose_pelt(cat["pelt_color"],
                                cat["pelt_white"], cat["pelt_name"],
                                cat["pelt_length"], True)
            new_cat = Cat(ID=cat["ID"],
                        prefix=cat["name_prefix"],
                        suffix=cat["name_suffix"],
                        gender=cat["gender"],
                        status=cat["status"],
                        parent1=cat["parent1"],
                        parent2=cat["parent2"],
                        moons=cat["moons"],
                        eye_colour=cat["eye_colour"] if cat["eye_colour"] not in ["BLUEYELLOW", "BLUEGREEN"] else "BLUE",
                        pelt=new_pelt,
                        loading_cat=True)
            new_cat.eye_colour2 = cat["eye_colour2"] if "eye_colour2" in cat else None
            new_cat.age = cat["age"]
            new_cat.genderalign = cat["gender_align"]
            new_cat.backstory = cat["backstory"] if "backstory" in cat else None
            new_cat.birth_cooldown = cat[
                "birth_cooldown"] if "birth_cooldown" in cat else 0
            new_cat.moons = cat["moons"]
            new_cat.trait = cat["trait"]
            new_cat.mentor = cat["mentor"]
            new_cat.former_mentor = cat["former_mentor"] if "former_mentor" in cat else []
            new_cat.patrol_with_mentor = cat["patrol_with_mentor"] if "patrol_with_mentor" in cat else 0
            new_cat.mentor_influence = cat["mentor_influence"] if "mentor_influence" in cat else []
            new_cat.paralyzed = cat["paralyzed"]
            new_cat.no_kits = cat["no_kits"]
            new_cat.exiled = cat["exiled"]
            new_cat.age_sprites['kitten'] = cat["spirit_kitten"]
            new_cat.age_sprites['adolescent'] = cat["spirit_adolescent"]
            new_cat.age_sprites['young adult'] = cat["spirit_young_adult"]
            new_cat.age_sprites['adult'] = cat["spirit_adult"]
            new_cat.age_sprites['senior adult'] = cat["spirit_senior_adult"]
            new_cat.age_sprites['elder'] = cat["spirit_elder"]
            new_cat.eye_colour = cat["eye_colour"]
            new_cat.reverse = cat["reverse"]
            new_cat.white_patches = cat["white_patches"]
            new_cat.pattern = cat["pattern"]
            new_cat.tortiebase = cat["tortie_base"]
            new_cat.tortiecolour = cat["tortie_color"]
            new_cat.tortiepattern = cat["tortie_pattern"]
            new_cat.skin = cat["skin"]
            new_cat.skill = cat["skill"]
            new_cat.scars = cat["scars"] if "scars" in cat else []

            # converting old specialty saves into new scar parameter
            if "specialty" in cat or "specialty2" in cat:
                if cat["specialty"] is not None:
                    new_cat.scars.append(cat["specialty"])
                if cat["specialty2"] is not None:
                    new_cat.scars.append(cat["specialty2"])

            new_cat.accessory = cat["accessory"]
            new_cat.mate = cat["mate"]
            new_cat.dead = cat["dead"]
            new_cat.died_by = cat["died_by"] if "died_by" in cat else []
            new_cat.age_sprites['dead'] = cat["spirit_dead"]
            new_cat.experience = cat["experience"]
            new_cat.dead_for = cat["dead_moons"]
            new_cat.apprentice = cat["current_apprentice"]
            new_cat.former_apprentices = cat["former_apprentices"]
            new_cat.possible_scar = cat["possible_scar"] if "possible_scar" in cat else None
            new_cat.scar_event = cat["scar_event"] if "scar_event" in cat else []
            new_cat.death_event = cat["death_event"] if "death_event" in cat else []
            new_cat.df = cat["df"] if "df" in cat else False
            new_cat.corruption = cat["corruption"] if "corruption" in cat else 0
            new_cat.life_givers = cat["life_givers"] if "life_givers" in cat else []
            new_cat.known_life_givers = cat["known_life_givers"] if "known_life_givers" in cat else []
            new_cat.virtues = cat["virtues"] if "virtues" in cat else []
            new_cat.outside = cat["outside"] if "outside" in cat else False
            new_cat.retired = cat["retired"] if "retired" in cat else False
            new_cat.faded_offspring = cat["faded_offspring"] if "faded_offspring" in cat else []
            new_cat.opacity = cat["opacity"] if "opacity" in cat else 100
            new_cat.prevent_fading = cat["prevent_fading"] if "prevent_fading" in cat else False
            new_cat.tint = cat["tint"] if "tint" in cat else "none"
            all_cats.append(new_cat)
        except KeyError as e:
            if "ID" in cat:
                key = f" ID #{cat['ID']} "
            else: 
                key = f" at index {i} "
            game.switches['error_message'] = f'Cat{key}in clan_cats.json is missing {e}!'
            raise

    # replace cat ids with cat objects and add other needed variables
    for cat in all_cats:
        cat.load_conditions()
        # load the relationships
        if not cat.dead:
            game.switches[
                'error_message'] = 'There was an error loading this clan\'s relationships. Last cat read was ' + str(
                    cat)
            cat.load_relationship_of_cat()
            game.switches[
                'error_message'] = f'There was an error when relationships for cat #{cat} are created.'
            if cat.relationships is not None and len(cat.relationships) < 1:
                cat.create_all_relationships()
        else:
            cat.relationships = {}

        """# replace mentor id with cat instance
        mentor_relevant = list(
            filter(lambda inter_cat: inter_cat.ID == cat.mentor, all_cats))
        cat.mentor = None
        if len(mentor_relevant) == 1:
            cat.mentor = mentor_relevant[0]

        if len(cat.former_mentor) > 0:
            old_mentors = []
            for cat_id in cat.former_mentor:
                relevant_list = list(
                    filter(lambda cat: cat.ID == cat_id, all_cats)
                )
                if len(relevant_list) > 0:
                    old_mentors.append(relevant_list[0])
            cat.former_mentor = old_mentors

        # update the apprentice
        if len(cat.apprentice) > 0:
            new_apprentices = []
            for cat_id in cat.apprentice:
                relevant_list = list(
                    filter(lambda cat: cat.ID == cat_id, all_cats))
                if len(relevant_list) > 0:
                    # if the cat can't be found, drop the cat_id
                    new_apprentices.append(relevant_list[0])
            cat.apprentice = new_apprentices

        # update the apprentice
        if len(cat.former_apprentices) > 0:
            new_apprentices = []
            for cat_id in cat.former_apprentices:
                relevant_list = list(
                    filter(lambda cat: cat.ID == cat_id, all_cats))
                if len(relevant_list) > 0:
                    # if the cat can't be found, drop the cat_id
                    new_apprentices.append(relevant_list[0])
            cat.former_apprentices = new_apprentices"""

        # get all the siblings ids and save them
        siblings = list(
            filter(lambda inter_cat: cat.is_sibling(inter_cat), all_cats))
        cat.siblings = [sibling.ID for sibling in siblings]

        # Add faded siblings:
        for parent in cat.get_parents():
            cat_ob = Cat.fetch_cat(parent)
            cat.siblings.extend(cat_ob.faded_offspring)
        # Remove duplicates
        cat.siblings = list(set(cat.siblings))

        # get all the children ids and save them
        children = list(
            filter(lambda inter_cat: cat.is_parent(inter_cat), all_cats))
        cat.children = [child.ID for child in children]

        # Add faded children
        cat.children.extend(cat.faded_offspring)

        # initialization of thoughts
        cat.thoughts()

def csv_load(all_cats):
    if game.switches['clan_list'][0].strip() == '':
        cat_data = ''
    else:
        if os.path.exists('saves/' + game.switches['clan_list'][0] +
                          'cats.csv'):
            with open('saves/' + game.switches['clan_list'][0] + 'cats.csv',
                      'r') as read_file:
                cat_data = read_file.read()
        else:
            with open('saves/' + game.switches['clan_list'][0] + 'cats.txt',
                      'r') as read_file:
                cat_data = read_file.read()
    if len(cat_data) > 0:
        cat_data = cat_data.replace('\t', ',')
        for i in cat_data.split('\n'):
            # CAT: ID(0) - prefix:suffix(1) - gender(2) - status(3) - age(4) - trait(5) - parent1(6) - parent2(7) - mentor(8)
            # PELT: pelt(9) - colour(10) - white(11) - length(12)
            # SPRITE: kitten(13) - apprentice(14) - warrior(15) - elder(16) - eye colour(17) - reverse(18)
            # - white patches(19) - pattern(20) - tortiebase(21) - tortiepattern(22) - tortiecolour(23) - skin(24) - skill(25) - NONE(26) - spec(27) - accessory(28) -
            # spec2(29) - moons(30) - mate(31)
            # dead(32) - SPRITE:dead(33) - exp(34) - dead for _ moons(35) - current apprentice(36)
            # (BOOLS, either TRUE OR FALSE) paralyzed(37) - no kits(38) - exiled(39)
            # genderalign(40) - former apprentices list (41)[FORMER APPS SHOULD ALWAYS BE MOVED TO THE END]
            if i.strip() != '':
                attr = i.split(',')
                for x in range(len(attr)):
                    attr[x] = attr[x].strip()
                    if attr[x] in ['None', 'None ']:
                        attr[x] = None
                    elif attr[x].upper() == 'TRUE':
                        attr[x] = True
                    elif attr[x].upper() == 'FALSE':
                        attr[x] = False
                game.switches[
                    'error_message'] = '1There was an error loading cat # ' + str(
                        attr[0])
                the_pelt = choose_pelt(attr[2], attr[10], attr[11], attr[9],
                                       attr[12], True)
                game.switches[
                    'error_message'] = '2There was an error loading cat # ' + str(
                        attr[0])
                the_cat = Cat(ID=attr[0],
                              prefix=attr[1].split(':')[0],
                              suffix=attr[1].split(':')[1],
                              gender=attr[2],
                              status=attr[3],
                              pelt=the_pelt,
                              parent1=attr[6],
                              parent2=attr[7],
                              eye_colour=attr[17])
                game.switches[
                    'error_message'] = '3There was an error loading cat # ' + str(
                        attr[0])
                the_cat.age, the_cat.mentor = attr[4], attr[8]
                game.switches[
                    'error_message'] = '4There was an error loading cat # ' + str(
                        attr[0])
                the_cat.age_sprites['kitten'], the_cat.age_sprites[
                    'adolescent'] = int(attr[13]), int(attr[14])
                game.switches[
                    'error_message'] = '5There was an error loading cat # ' + str(
                        attr[0])
                the_cat.age_sprites['adult'], the_cat.age_sprites[
                    'elder'] = int(attr[15]), int(attr[16])
                game.switches[
                    'error_message'] = '6There was an error loading cat # ' + str(
                        attr[0])
                the_cat.age_sprites['young adult'], the_cat.age_sprites[
                    'senior adult'] = int(attr[15]), int(attr[15])
                game.switches[
                    'error_message'] = '7There was an error loading cat # ' + str(
                        attr[0])
                the_cat.reverse, the_cat.white_patches, the_cat.pattern = attr[
                    18], attr[19], attr[20]
                game.switches[
                    'error_message'] = '8There was an error loading cat # ' + str(
                        attr[0])
                the_cat.tortiebase, the_cat.tortiepattern, the_cat.tortiecolour = attr[
                    21], attr[22], attr[23]
                game.switches[
                    'error_message'] = '9There was an error loading cat # ' + str(
                        attr[0])
                the_cat.trait, the_cat.skin, the_cat.specialty = attr[5], attr[
                    24], attr[27]
                game.switches[
                    'error_message'] = '10There was an error loading cat # ' + str(
                        attr[0])
                the_cat.skill = attr[25]
                if len(attr) > 28:
                    the_cat.accessory = attr[28]
                if len(attr) > 29:
                    the_cat.specialty2 = attr[29]
                else:
                    the_cat.specialty2 = None
                game.switches[
                    'error_message'] = '11There was an error loading cat # ' + str(
                        attr[0])
                if len(attr) > 34:
                    the_cat.experience = int(attr[34])
                    experiencelevels = [
                        'very low', 'low', 'slightly low', 'average',
                        'somewhat high', 'high', 'very high', 'master', 'max'
                    ]
                    the_cat.experience_level = experiencelevels[floor(
                        int(the_cat.experience) / 10)]
                else:
                    the_cat.experience = 0
                game.switches[
                    'error_message'] = '12There was an error loading cat # ' + str(
                        attr[0])
                if len(attr) > 30:
                    # Attributes that are to be added after the update
                    the_cat.moons = int(attr[30])
                    if len(attr) >= 31:
                        # assigning mate to cat, if any
                        the_cat.mate = attr[31]
                    if len(attr) >= 32:
                        # Is the cat dead
                        the_cat.dead = attr[32]
                        the_cat.age_sprites['dead'] = attr[33]
                game.switches[
                    'error_message'] = '13There was an error loading cat # ' + str(
                        attr[0])
                if len(attr) > 35:
                    the_cat.dead_for = int(attr[35])
                game.switches[
                    'error_message'] = '14There was an error loading cat # ' + str(
                        attr[0])
                if len(attr) > 36 and attr[36] is not None:
                    the_cat.apprentice = attr[36].split(';')
                game.switches[
                    'error_message'] = '15There was an error loading cat # ' + str(
                        attr[0])
                if len(attr) > 37:
                    the_cat.paralyzed = bool(attr[37])
                if len(attr) > 38:
                    the_cat.no_kits = bool(attr[38])
                if len(attr) > 39:
                    the_cat.exiled = bool(attr[39])
                if len(attr) > 40:
                    the_cat.genderalign = attr[40]
                if len(attr
                       ) > 41 and attr[41] is not None:  #KEEP THIS AT THE END
                    the_cat.former_apprentices = attr[41].split(';')
        game.switches[
            'error_message'] = 'There was an error loading this clan\'s mentors, apprentices, relationships, or sprite info.'
        for inter_cat in all_cats.values():
            # Load the mentors and apprentices after all cats have been loaded
            game.switches[
                'error_message'] = 'There was an error loading this clan\'s mentors/apprentices. Last cat read was ' + str(
                    inter_cat)
            inter_cat.mentor = Cat.all_cats.get(inter_cat.mentor)
            apps = []
            former_apps = []
            for app_id in inter_cat.apprentice:
                app = Cat.all_cats.get(app_id)
                # Make sure if cat isn't an apprentice, they're a former apprentice
                if 'apprentice' in app.status:
                    apps.append(app)
                else:
                    former_apps.append(app)
            for f_app_id in inter_cat.former_apprentices:
                f_app = Cat.all_cats.get(f_app_id)
                former_apps.append(f_app)
            inter_cat.apprentice = [a.ID for a in apps] #Switch back to IDs. I don't want to risk breaking everything.
            inter_cat.former_apprentices = [a.ID for a in former_apps]
            if not inter_cat.dead:
                game.switches[
                    'error_message'] = 'There was an error loading this clan\'s relationships. Last cat read was ' + str(
                        inter_cat)
                inter_cat.load_relationship_of_cat()
            game.switches[
                'error_message'] = 'There was an error loading a cat\'s sprite info. Last cat read was ' + str(
                    inter_cat)
            update_sprite(inter_cat)
        # generate the relationship if some is missing
        if not the_cat.dead:
            game.switches[
                'error_message'] = 'There was an error when relationships where created.'
            for id in all_cats.keys():
                the_cat = all_cats.get(id)
                game.switches[
                    'error_message'] = f'There was an error when relationships for cat #{the_cat} are created.'
                if the_cat.relationships is not None and len(the_cat.relationships) < 1:
                    the_cat.create_all_relationships()
        game.switches['error_message'] = ''
