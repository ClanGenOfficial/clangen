import os
from math import floor
from .game_essentials import game
from ..datadir import get_save_dir

import ujson

from re import sub
from scripts.cat.cats import Cat
from scripts.version import VERSION_NAME
from scripts.cat.pelts import choose_pelt, vit, point_markings
from scripts.utility import update_sprite, is_iterable
from random import choice

from json import JSONDecodeError

def load_cats():
    try:
        json_load()
    except FileNotFoundError:
        try:
            csv_load(Cat.all_cats)
        except FileNotFoundError as e:
            game.switches['error_message'] = 'Can\'t find clan_cats.json!'
            game.switches['traceback'] = e
            raise

def json_load():
    all_cats = []
    cat_data = None
    clanname = game.switches['clan_list'][0]
    clan_cats_json_path = f'{get_save_dir()}/{clanname}/clan_cats.json'
    with open(f"resources/dicts/conversion_dict.json", 'r') as read_file:
        convert = ujson.loads(read_file.read())
    try:
        with open(clan_cats_json_path, 'r') as read_file:
            cat_data = ujson.loads(read_file.read())
    except PermissionError as e:
        game.switches['error_message'] = f'Can\t open {clan_cats_json_path}!'
        game.switches['traceback'] = e
        raise
    except JSONDecodeError as e:
        game.switches['error_message'] = f'{clan_cats_json_path} is malformed!'
        game.switches['traceback'] = e
        raise

    old_creamy_patches = convert["old_creamy_patches"]
    old_tortie_patches = convert["old_tortie_patches"]
    no_tint_patches = ['SEPIAPOINT', 'MINKPOINT', 'SEALPOINT']

    # create new cat objects
    for i, cat in enumerate(cat_data):
        try:
            new_pelt = choose_pelt(cat["pelt_color"],
                                cat["pelt_white"], cat["pelt_name"],
                                cat["pelt_length"], True)
            if cat["eye_colour"] == "BLUE2":
                cat["eye_colour"] = "COBALT"
            if cat["eye_colour"] in ["BLUEYELLOW", "BLUEGREEN"]:
                if cat["eye_colour"] == "BLUEYELLOW":
                    cat["eye_colour2"] = "YELLOW"
                elif cat["eye_colour"] == "BLUEGREEN":
                    cat["eye_colour2"] = "GREEN"
                cat["eye_colour"] = "BLUE"
            if cat["eye_colour2"] == "BLUE2":
                new_cat.eye_colour2 = "COBALT"
            new_cat = Cat(ID=cat["ID"],
                        prefix=cat["name_prefix"],
                        suffix=cat["name_suffix"],
                        specsuffix_hidden=(cat["specsuffix_hidden"] if 'specsuffix_hidden' in cat else False),
                        gender=cat["gender"],
                        status=cat["status"],
                        parent1=cat["parent1"],
                        parent2=cat["parent2"],
                        moons=cat["moons"],
                        eye_colour=cat["eye_colour"],
                        pelt=new_pelt,
                        loading_cat=True)
            new_cat.eye_colour2 = cat["eye_colour2"] if "eye_colour2" in cat else None
            new_cat.age = cat["age"]
            if new_cat.age == 'elder':
                new_cat.age = 'senior'
            new_cat.genderalign = cat["gender_align"]
            new_cat.backstory = cat["backstory"] if "backstory" in cat else None
            new_cat.birth_cooldown = cat["birth_cooldown"] if "birth_cooldown" in cat else 0
            new_cat.moons = cat["moons"]
            if cat["trait"] in ["clever", "patient", "empathetic", "altruistic"]:
                new_cat.trait = "compassionate"
            else:
                new_cat.trait = cat["trait"]
            new_cat.mentor = cat["mentor"]
            new_cat.former_mentor = cat["former_mentor"] if "former_mentor" in cat else []
            new_cat.patrol_with_mentor = cat["patrol_with_mentor"] if "patrol_with_mentor" in cat else 0
            new_cat.mentor_influence = cat["mentor_influence"] if "mentor_influence" in cat else []
            new_cat.paralyzed = cat["paralyzed"]
            new_cat.no_kits = cat["no_kits"]
            new_cat.exiled = cat["exiled"]
            new_cat.cat_sprites['kitten'] = cat["sprite_kitten"] if "sprite_kitten" in cat else cat["spirit_kitten"]
            new_cat.cat_sprites['adolescent'] = cat["sprite_adolescent"] if "sprite_adolescent" in cat else cat["spirit_adolescent"]
            new_cat.cat_sprites['young adult'] = cat["sprite_young_adult"] if "sprite_young_adult" in cat else cat["spirit_young_adult"]
            new_cat.cat_sprites['adult'] = cat["sprite_adult"] if "sprite_adult" in cat else cat["spirit_adult"]
            new_cat.cat_sprites['senior adult'] = cat["sprite_senior_adult"] if "sprite_senior_adult" in cat else cat["spirit_senior_adult"]
            new_cat.cat_sprites['senior'] = cat["sprite_senior"] if "sprite_senior" in cat else cat["spirit_elder"]
            new_cat.cat_sprites['para_adult'] = cat["sprite_para_adult"] if "sprite_para_adult" in cat else None
            # setting up sprites that might not be correct
            if new_cat.pelt is not None:
                if new_cat.pelt.length == 'long':
                    if new_cat.cat_sprites['adult'] not in [9, 10, 11]:
                        if new_cat.cat_sprites['adult'] == 0:
                            new_cat.cat_sprites['adult'] = 9
                        elif new_cat.cat_sprites['adult'] == 1:
                            new_cat.cat_sprites['adult'] = 10
                        elif new_cat.cat_sprites['adult'] == 2:
                            new_cat.cat_sprites['adult'] = 11
                        new_cat.cat_sprites['young adult'] = new_cat.cat_sprites['adult']
                        new_cat.cat_sprites['senior adult'] = new_cat.cat_sprites['adult']
                        new_cat.cat_sprites['para_adult'] = 16
                else:
                    new_cat.cat_sprites['para_adult'] = 15
                if new_cat.cat_sprites['senior'] not in [12, 13, 14]:
                    if new_cat.cat_sprites['senior'] == 3:
                        new_cat.cat_sprites['senior'] = 12
                    elif new_cat.cat_sprites['senior'] == 4:
                        new_cat.cat_sprites['senior'] = 13
                    elif new_cat.cat_sprites['senior'] == 5:
                        new_cat.cat_sprites['senior'] = 14
            new_cat.eye_colour = cat["eye_colour"]
            new_cat.reverse = cat["reverse"]
            if cat["white_patches"] in old_creamy_patches:
                new_cat.white_patches = convert["old_creamy_patches"][str(cat['white_patches'])]
                new_cat.white_patches_tint = "darkcream"
            else:
                new_cat.white_patches = cat["white_patches"]
                if 'white_patches_tint' in cat:
                    new_cat.white_patches_tint = cat['white_patches_tint']
                else:
                    if new_cat.white_patches in no_tint_patches:
                        new_cat.white_patches_tint = "none"
                    else:
                        new_cat.white_patches_tint = "offwhite"
            if cat["white_patches"] == 'POINTMARK':
                new_cat.white_patches = "SEALPOINT"
            if cat["white_patches"] == 'PANTS2':
                new_cat.white_patches = 'PANTSTWO'
            if cat["white_patches"] == 'ANY2':
                new_cat.white_patches = 'ANYTWO'
            if cat["white_patches"] == "VITILIGO2":
                cat["white_patches"] = "VITILIGOTWO"
            new_cat.vitiligo = cat["vitiligo"] if "vitiligo" in cat else None
            new_cat.points = cat["points"] if "points" in cat else None
            if cat["white_patches"] in vit:
                new_cat.vitiligo = cat["white_patches"]
                new_cat.white_patches = None
            if "vitiligo" in cat and cat["vitiligo"] == "VITILIGO2":
                new_cat.vitiligo = "VITILIGOTWO"
            elif cat["white_patches"] in point_markings:
                new_cat.points = cat["white_patches"]
                new_cat.white_patches = None
            new_cat.tortiebase = cat["tortie_base"]
            if cat["tortie_pattern"] and "tortie" in cat["tortie_pattern"]:
                new_cat.tortiepattern = sub("tortie", "", cat["tortie_pattern"]).lower()
                if new_cat.tortiepattern == "solid":
                    new_cat.tortiepattern = "single"
            else:
                new_cat.tortiepattern = cat["tortie_pattern"]

            if cat["pattern"] in old_tortie_patches:
                # Convert old torties
                new_cat.pattern = convert["old_tortie_patches"][cat["pattern"]][1]
                new_cat.tortiecolour = convert["old_tortie_patches"][cat["pattern"]][0]
                # If the pattern is old, there is also a change the base color is stored in
                # tortiecolour, and that may be different from the pelt color (main for torties
                # generated before the "ginger-on-ginger" update. If it was generated after that update,
                # tortiecolour and pelt_colour will be the same. Therefore, lets also re-set the pelt color
                new_cat.pelt.colour = cat["tortie_color"]
            else:
                new_cat.pattern = cat["pattern"]
                new_cat.tortiecolour = cat["tortie_color"]
            if cat["pattern"] == "MINIMAL1":
                new_cat.pattern = "MINIMALONE"
            elif cat["pattern"] == "MINIMAL2":
                new_cat.pattern = "MINIMALTWO"
            elif cat["pattern"] == "MINIMAL3":
                new_cat.pattern = "MINIMALTHREE"
            elif cat["pattern"] == "MINIMAL4":
                new_cat.pattern = "MINIMALFOUR"
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
            new_cat.previous_mates = cat["previous_mates"] if "previous_mates" in cat else []
            new_cat.dead = cat["dead"]
            new_cat.died_by = cat["died_by"] if "died_by" in cat else []
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
            new_cat.favourite = cat["favourite"] if "favourite" in cat else False
            new_cat.tint = cat["tint"] if "tint" in cat else "none"
            all_cats.append(new_cat)
        except KeyError as e:
            if "ID" in cat:
                key = f" ID #{cat['ID']} "
            else: 
                key = f" at index {i} "
            game.switches['error_message'] = f'Cat{key}in clan_cats.json is missing {e}!'
            game.switches['traceback'] = e
            raise

    # replace cat ids with cat objects and add other needed variables
    for cat in all_cats:
        cat.load_conditions()

        # this is here to handle paralyzed cats in old saves
        if cat.paralyzed and "paralyzed" not in cat.permanent_condition:
            cat.get_permanent_condition("paralyzed")
        elif "paralyzed" in cat.permanent_condition and not cat.paralyzed:
            cat.paralyzed = True

        # load the relationships
        if not cat.dead:
            game.switches[
                'error_message'] = 'There was an error loading this clan\'s relationships. Last cat read was ' + str(
                    cat)
            cat.load_relationship_of_cat()
            game.switches[
                'error_message'] = f'There was an error when relationships for cat #{cat} are created.'
            if cat.relationships is not None and len(cat.relationships) < 1:
                cat.init_all_relationships()
        else:
            cat.relationships = {}

        # get all the siblings ids and save them
        siblings = list(
            filter(lambda inter_cat: cat.is_sibling(inter_cat), all_cats))
        cat.siblings = [sibling.ID for sibling in siblings]

        # Add faded siblings:
        for parent in cat.get_parents():
            try:
                cat_ob = Cat.fetch_cat(parent)
                cat.siblings.extend(cat_ob.faded_offspring)
            except:
                if parent == cat.parent1:
                    cat.parent1 = None
                elif parent == cat.parent2:
                    cat.parent2 = None

        # Remove duplicates
        cat.siblings = list(set(cat.siblings))

        # get all the children ids and save them
        children = list(
            filter(lambda inter_cat: cat.is_parent(inter_cat), all_cats))
        cat.children = [child.ID for child in children]

        # Add faded children
        cat.children.extend(cat.faded_offspring)
        
        game.switches['error_message'] = f'There was an error when thoughts for cat #{cat} are created.'
        # initialization of thoughts
        cat.thoughts()
        
        # Save integrety checks
        if game.config["save_load"]["load_integrity_checks"]:
            save_check()
    

def csv_load(all_cats):
    if game.switches['clan_list'][0].strip() == '':
        cat_data = ''
    else:
        if os.path.exists(get_save_dir() + '/' + game.switches['clan_list'][0] +
                          'cats.csv'):
            with open(get_save_dir() + '/' + game.switches['clan_list'][0] + 'cats.csv',
                      'r') as read_file:
                cat_data = read_file.read()
        else:
            with open(get_save_dir() + '/' + game.switches['clan_list'][0] + 'cats.txt',
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
                the_cat.cat_sprites['kitten'], the_cat.cat_sprites[
                    'adolescent'] = int(attr[13]), int(attr[14])
                game.switches[
                    'error_message'] = '5There was an error loading cat # ' + str(
                        attr[0])
                the_cat.cat_sprites['adult'], the_cat.cat_sprites[
                    'elder'] = int(attr[15]), int(attr[16])
                game.switches[
                    'error_message'] = '6There was an error loading cat # ' + str(
                        attr[0])
                the_cat.cat_sprites['young adult'], the_cat.cat_sprites[
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
                        the_cat.cat_sprites['dead'] = attr[33]
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

def save_check():
    """Checks through loaded cats, checks and attempts to fix issues """
    
    for cat in Cat.all_cats:
        cat_ob = Cat.all_cats[cat]
        
        # Not-mutural mate relations
        if cat_ob.mate:
            _temp_ob = Cat.all_cats.get(cat_ob.mate)
            if _temp_ob:
                # Check if the mate's mate feild is set to none
                if not _temp_ob.mate:
                    _temp_ob.mate = cat_ob.ID 
            else:
                # Invalid mate
                cat_ob.mate = None
                
def version_convert(version_info):
    """Does all save-convertion that require referencing the saved version number.
    This is a seperate function, since the version info is stored in clan.json, but most converson needs to be 
    done on the cats. Clan data is loaded in after cats, however. """
    
    if version_info is None:
        return
    
    if version_info["version_name"] == VERSION_NAME:
        # Save was made on current version
        return
    
    if version_info["version_name"] is None:
        # Save was made before version number stoage was implemented. 
        # This means the EXP must be adjusted. 
        for c in Cat.all_cats.values():
            c.experience = c.experience * 3.2
    