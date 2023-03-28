import os
from math import floor
import traceback
from .game_essentials import game
from ..datadir import get_save_dir

try:
    import ujson
except ImportError:
    import json as ujson

from re import sub
from scripts.cat.cats import Cat
from scripts.cat.pelts import choose_pelt, vit, point_markings
from scripts.utility import update_sprite, is_iterable
from random import choice
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
            cat.load_relationship_of_cat()
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

        # initialization of thoughts
        cat.thoughts()
        
        # Save integrety checks
        if game.config["save_load"]["load_integrity_checks"]:
            save_check()
    

def csv_load(all_cats):
    try:
        csvFormat = [
            'ID',
            'name',
            'gender',
            'status',
            'age',
            'trait',
            'parent1',
            'parent2',
            'mentor',
            'pelt_name',
            'pelt_color',
            'pelt_white',
            'pelt_length',
            'spirit_kitten',
            'spirit_adolescent',
            'spirit_adult',
            'spirit_elder',
            'eye_colour',
            'reverse',
            'white_patches',
            'pattern',
            'skin',
            'skill',
            'NULL',
            'specialty',
            'moons',
            'mate',
            'dead',
            'spirit_dead',
            'specialty2',
            'experience',
            'dead_moons',
            'current_apprentice',
            'former_apprentices',
        ]

        id_fields = [
            'parent1',
            'parent2',
            'ID',
            'mate',
            'mentor'
        ]

        tortie_map = {
            'ONE': {
                'tortie_base': 'single',
                'tortie_color': 'BLACK',
                'tortie_pattern': 'tortiesolid',
                'pattern': 'GOLDONE'
            },
            'TWO': {
                'tortie_base': 'single',
                'tortie_color': 'BLACK',
                'tortie_pattern': 'tortiesolid',
                'pattern': 'GOLDTWO'
            },
            'FADEDONE': {
                'tortie_base': 'single',
                'tortie_color': 'BROWN',
                'tortie_pattern': 'tortiesolid',
                'pattern': 'GOLDONE'
            },
            'FADEDTWO': {
                'tortie_base': 'single',
                'tortie_color': 'BROWN',
                'tortie_pattern': 'tortiesolid',
                'pattern': 'GOLDTWO'
            },
            'BLUEONE': {
                'tortie_base': 'single',
                'tortie_color': 'SILVER',
                'tortie_pattern': 'tortiesolid',
                'pattern': 'PALEONE'
            },
            'BLUETWO': {
                'tortie_base': 'single',
                'tortie_color': 'SILVER',
                'tortie_pattern': 'tortiesolid',
                'pattern': 'PALETWO'
            }
        }

        calico_map = {
            'ONE': {
                'tortie_base': 'single',
                'tortie_color': 'BLACK',
                'tortie_pattern': 'tortiesolid',
                'pattern': 'GOLDTHREE'
            },
            'TWO': {
                'tortie_base': 'single',
                'tortie_color': 'BLACK',
                'tortie_pattern': 'tortiesolid',
                'pattern': 'GOLDFOUR'
            },
            'THREE': {
                'tortie_base': 'single',
                'tortie_color': 'BLACK',
                'tortie_pattern': 'tortietabby',
                'pattern': 'GOLDTHREE'
            },
            'FOUR': {
                'tortie_base': 'single',
                'tortie_color': 'BLACK',
                'tortie_pattern': 'tortietabby',
                'pattern': 'GOLDFOUR'
            },
            'FADEDONE': {
                'tortie_base': 'single',
                'tortie_color': 'BROWN',
                'tortie_pattern': 'tortiesolid',
                'pattern': 'GOLDTHREE'
            },
            'FADEDTWO': {
                'tortie_base': 'single',
                'tortie_color': 'BROWN',
                'tortie_pattern': 'tortiesolid',
                'pattern': 'GOLDFOUR'
            },
            'FADEDTHREE': {
                'tortie_base': 'tabby',
                'tortie_color': 'BROWN',
                'tortie_pattern': 'tortietabby',
                'pattern': 'GOLDTHREE'
            },
            'FADEDFOUR': {
                'tortie_base': 'tabby',
                'tortie_color': 'BROWN',
                'tortie_pattern': 'tortietabby',
                'pattern': 'GOLDFOUR'
            },
            'BLUEONE': {
                'tortie_base': 'single',
                'tortie_color': 'SILVER',
                'tortie_pattern': 'tortiesolid',
                'pattern': 'PALETHREE'
            },
            'BLUETWO': {
                'tortie_base': 'single',
                'tortie_color': 'SILVER',
                'tortie_pattern': 'tortiesolid',
                'pattern': 'PALEFOUR'
            },
            'BLUETHREE': {
                'tortie_base': 'tabby',
                'tortie_color': 'SILVER',
                'tortie_pattern': 'tortietabby',
                'pattern': 'PALETHREE'
            },
            'BLUEFOUR': {
                'tortie_base': 'tabby',
                'tortie_color': 'SILVER',
                'tortie_pattern': 'tortietabby',
                'pattern': 'PALEFOUR'
            }
        }

        if os.path.exists(get_save_dir() + '/' + game.switches['clan_list'][0] +
                          'cats.csv'):
            with open(get_save_dir() + '/' + game.switches['clan_list'][0] + 'cats.csv',
                      'r') as read_file:
                rows = read_file.readlines()
        else:
            with open(get_save_dir() + '/' + game.switches['clan_list'][0] + 'cats.txt',
                      'r') as read_file:
                rows = read_file.readlines()
        if len(rows) == 0:
            return

        catData = []

        for row in rows:
            if row == None or row == '' or row.strip() == '':
                continue

            columns = row.split(',')
            cat = {}
            if len(columns) != len(csvFormat):
                game.switches['error_message'] = "Unexpected number of columns in cats"

            i = 0
            for column in columns:
                column = column.strip()
                if column.lower() == 'none':
                    column = None
                elif column.lower() == 'true':
                    column = True
                elif column.lower() == 'false':
                    column = False
                elif column.isnumeric():
                    column = int(column)

                cat[csvFormat[i]] = column
                i += 1

            if not cat['current_apprentice']:
                cat['current_apprentice'] = []
            else:
                cat['current_apprentice'] = str(cat['current_apprentice']).split(';')

            if not cat['former_apprentices']:
                cat['former_apprentices'] = []
            else:
                cat['former_apprentices'] = str(cat['former_apprentices']).split(';')

            catData.append(cat)

        for cat in catData:
            split_name = cat['name'].split(':')
            cat['name_prefix'] = split_name[0]
            if len(split_name) > 1:
                cat['name_suffix'] = split_name[1]
            else:
                cat['name_suffix'] = ''
            
            del cat['name']
            del cat['NULL'] # idfk why this is here but it is

            for id_field in id_fields:
                if cat[id_field]:
                    cat[id_field] = str(cat[id_field])

            cat['gender_align'] = cat['gender']

            cat['paralyzed'] = False
            cat['no_kits'] = False
            cat['exiled'] = False


            if cat['pelt_name'] == 'Tortie':
                tortie_vars = tortie_map[cat['pattern']]
            elif cat['pelt_name'] == 'Calico':
                tortie_vars = calico_map[cat['pattern']]
            else:
                tortie_vars = {
                    'tortie_base': None,
                    'tortie_color': None,
                    'tortie_pattern': None,
                }
            
            if cat['white_patches']:
                cat['white_patches'] = cat['white_patches'].replace('ANY2', 'ANYTWO')
                cat['white_patches'] = cat['white_patches'].replace('CREAMY', '')
            
            if cat['status'] == 'elder':
                cat['status'] = 'senior'
            
            cat.update(tortie_vars)

            cat['eye_colour2'] = cat['eye_colour']
            cat['sprite_young_adult'] = cat['spirit_adult']
            cat['sprite_senior_adult'] = cat['spirit_adult']
            cat['accessory'] = None


        # save the file, then load via the normal method
        try:
            os.mkdir(get_save_dir() + '/' + game.switches['clan_list'][0])
            with open(get_save_dir() + '/' + game.switches['clan_list'][0] + '/clan_cats.json',
                  'w') as write_file:
                write_file.write(ujson.dumps(catData, indent=4))
                load_cats()
        except Exception as e:
            game.switches['error_message'] = "Loading converted save failed"
            game.switches['traceback'] = e
            return
                


    except Exception as e:
        game.switches['error_message'] = "Save conversion failed"
        game.switches['traceback'] = e
        print(e)
        print(traceback.format_exception(e))
        return
    

    

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