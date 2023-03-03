from random import choice

try:
    import ujson
except ImportError:
    import json as ujson

def get_thoughts(cat, other_cat):
    # placeholder thought - should only appear in game, when there is only one cat left
    thoughts = ['Is not thinking about much right now']

    if cat is None or other_cat is None:
        return thoughts

    # actions or thoughts for all cats. These switch either every moon or every time the game is re-opened
    if cat.is_alive() and not cat.outside:
        thoughts = get_alive_thoughts(cat, other_cat)
    elif cat.is_alive() and cat.outside and not cat.exiled:
        thoughts = get_outside_thoughts(cat, other_cat)
    elif cat.is_alive() and cat.exiled:
        thoughts = get_exile_thoughts(cat, other_cat)
    elif cat.df:
        thoughts = get_df_thoughts(cat, other_cat)
    elif cat.outside:
        thoughts = get_ur_thoughts(cat, other_cat)
    else:
        thoughts = get_dead_thoughts(cat, other_cat)


    return thoughts

def get_dead_thoughts(cat, other_cat):
        # individual thoughts
        thoughts = []
        thoughts += GENERAL_DEAD["all"]
        # thoughts with other cats that are dead
        if other_cat.dead:
            thoughts += GENERAL_DEAD["dead"]
        else:
            thoughts += GENERAL_DEAD["alive"]

        # dead young cat thoughts
        if cat.status in ['kitten', 'apprentice', 'medicine cat apprentice']:
            thoughts += [
                'Wishes they had more time to grow up',
                'Wonders what their full name would have been',
                'Is bothering older StarClan cats',
                'Is learning about the other cats in StarClan'
            ]
        # dead elder thoughts
        elif cat.status == 'elder':
            thoughts += [
                'Is grateful that they lived such a long life',
                'Is happy that their joints no longer ache',
                'Is telling stories to the younger cats of StarClan',
                'Watches over the younger cats of StarClan',
                'Is observing how different the Clan is from when they were alive'
            ]
        # dead leader thoughts
        elif cat.status == 'leader':
            thoughts += [
                'Hoped that they were a good leader',
                'Wishes that they had ten lives',
                'Is proud of their Clan from StarClan',
                'Is pleased to see the new direction the Clan is heading in',
                'Still frets over their beloved former Clanmates from afar'
            ]
            # checks for specific roles
            if other_cat.status == 'kitten':
                thoughts += [
                    'Rejoices with every new kit born to the Clan they still hold so dear'
                ]

        return thoughts

def get_alive_thoughts(cat, other_cat):
    thoughts = []
    thoughts += GENERAL_ALIVE
    thoughts += GENERAL_TO_OTHER["all"]

    if other_cat.dead:
        first_key = "dead"
    else:
        first_key = "alive"

    thoughts += get_family_thoughts(cat, other_cat)
    thoughts += GENERAL_TO_OTHER[first_key]["all"]

    try:
        if other_cat.status not in ['kittypet', 'loner', 'rogue']:
            thoughts += GENERAL_TO_OTHER["alive"][other_cat.status]
    except KeyError:
        print("GENERAL_TO_OTHER does not have key " + other_cat.status)

    try:
        if cat.status == 'kitten':
            thoughts += get_kitten_thoughts(cat,other_cat)

        elif cat.status == 'apprentice':
            thoughts += get_apprentice_thoughts(cat,other_cat)

        elif cat.status == 'medicine cat apprentice':
            thoughts += get_med_apprentice_thoughts(cat, other_cat)

        elif cat.status == "mediator apprentice":
            thoughts += get_mediator_app_thoughts(cat, other_cat)

        elif cat.status == 'mediator':
            thoughts += get_mediator_thoughts(cat, other_cat)

        elif cat.status == 'elder':
            thoughts += get_elder_thoughts(cat,other_cat)

        elif cat.status == 'medicine cat':
            thoughts += get_med_thoughts(cat,other_cat)

        elif cat.status == 'deputy':
            thoughts += get_deputy_thoughts(cat, other_cat)

        elif cat.status == 'leader':
            thoughts += get_leader_thoughts(cat, other_cat)

        elif cat.status == 'warrior':
            thoughts += get_warrior_thoughts(cat, other_cat)
            thoughts += get_warrior_trait_role_thoughts(cat, other_cat)
                                             
    except Exception as e:
        print("Error loading rank thoughts. ")
        print(e)


    return thoughts

def get_kitten_thoughts(cat, other_cat):
    thoughts = []
    thoughts += KITTEN_GENERAL["all"]

    first_key = "alive"
    if other_cat.dead:
        first_key = "dead"

    second_key = other_cat.status
    # checks for specific roles
    thoughts += KITTEN_GENERAL[first_key]["all"]
    thoughts += KITTEN_GENERAL[first_key][second_key]

    # kitten trait thoughts
    trait = cat.trait
    thoughts += KITTEN_TRAITS[trait]
    return thoughts

def get_mediator_thoughts(cat, other_cat):
    thoughts = []
    thoughts += MEDIATOR_GENERAL["all"]

    if other_cat.dead:
        first_key = "dead"
    else:
        first_key = "alive"


    second_key = other_cat.status
    # checks for specific roles
    thoughts += MEDIATOR_GENERAL[first_key]["all"]
    thoughts += MEDIATOR_GENERAL[first_key][second_key]

    trait = cat.trait
    thoughts += MEDIATOR_TRAITS[trait]

    return thoughts

def get_mediator_app_thoughts(cat, other_cat):
    thoughts = []
    thoughts += MEDIATOR_APP_GENERAL["all"]

    if other_cat.dead:
        first_key = "dead"
    else:
        first_key = "alive"


    second_key = other_cat.status
    # checks for specific roles
    thoughts += MEDIATOR_APP_GENERAL[first_key]["all"]
    thoughts += MEDIATOR_APP_GENERAL[first_key][second_key]

    trait = cat.trait
    thoughts += MEDIATOR_APP_TRAITS[trait]

    return thoughts

def get_apprentice_thoughts(cat, other_cat):
    thoughts = []
    thoughts += APPR_GENERAL["all"]
    first_key = "alive"
    if other_cat.dead:
        first_key = "dead"

    second_key = other_cat.status
    # checks for specific roles
    thoughts += APPR_GENERAL[first_key]["all"]
    thoughts += APPR_GENERAL[first_key][second_key]

    # checks for specific traits
    trait = cat.trait
    thoughts += APPR_TRAITS[trait]

    if trait == 'charismatic':
        # checks for specific roles
        if other_cat.status == 'kitten':
            thoughts += [
                'Has the kits very engaged in a very, very tall tale'
            ]
        elif cat.status == 'elder':
            thoughts += ['Is a favorite among the elders lately']

    return thoughts

def get_med_apprentice_thoughts(cat, other_cat):
    thoughts = []
    thoughts += MED_APPR_GENERAL["all"]
    first_key = "alive"
    if other_cat.dead:
        first_key = "dead"
    second_key = other_cat.status

    # checks for specific roles
    thoughts += MED_APPR_GENERAL[first_key]["all"]
    thoughts += MED_APPR_GENERAL[first_key][second_key]

    # trait specific medicine cat apprentice thoughts    
    trait = cat.trait
    thoughts += MED_APPR_TRAITS[trait]
    
    return thoughts

def get_warrior_thoughts(cat, other_cat):
    thoughts = []
    thoughts += WARRIOR_GENERAL["all"]

    first_key = "alive"
    if other_cat.dead:
        first_key = "dead"
    second_key = other_cat.status

    # checks for specific roles
    thoughts += WARRIOR_GENERAL[first_key]["all"]
    thoughts += WARRIOR_GENERAL[first_key][second_key]

    # trait specific medicine cat apprentice thoughts    
    trait = cat.trait
    thoughts += WARRIOR_TRAITS[trait]

    # check for specific roles
    if other_cat.status == 'kitten':
        if cat.trait == 'cold':
            thoughts += ['Recently snapped at the kits, making them cry']
        elif cat.trait == 'childish':
            thoughts += ['Is teaching new games to the kits']
        elif cat.trait == 'empathetic':
            thoughts += ['Is comforting kits after a scary experience']
        elif cat.trait == 'fierce':
            thoughts += [
                'Is roaring playfully at kits, making them laugh',
                'Has been rough-housing with the kits a little too hard lately'
            ]
        elif cat.trait == 'loving':
            thoughts += [
                'Is helping out with kits around camp',
                'Is smiling at the antics of the kits',
                'Is offering words of comfort to the kits']
        elif cat.trait == 'playful':
            thoughts += [
                'Is showing kits a game they used to play when they were that age',
                'Is giving kits badger rides on their back!',
                'Is riling up the kits, much to the queens\'s dismay'
            ]
        elif cat.trait == 'shameless':
            thoughts += ['Pushed a kit out of their way thoughtlessly']
        elif cat.trait == 'strict':
            thoughts += ['Is grumbling about troublesome kits']
        elif cat.trait == 'thoughtful':
            thoughts += [
                'Is bringing soaked moss to the queens in the nursery',
                'Is promising to take the kits out on a stroll today if they behave',
                'Plucked feathers from their meal for the kits to play with',
                'Is offering to look after the kits while the queens rest'
            ]
        elif cat.trait == 'troublesome':
            thoughts += ['Got scolded for telling the kits a naughty joke!']
    elif other_cat.status == 'elder':
        if cat.trait == 'calm':
            thoughts += ['Is politely listening to elders\'s stories']
        elif cat.trait == 'charismatic':
            thoughts += ['Is a favorite among the elders lately']
        elif cat.trait == 'compassionate':
            thoughts += [
                'Helped the elders to rise stiffly from their nests this morning'
            ]
        elif cat.trait == 'empathetic':
            thoughts += [
                'Volunteered to gather fresh lining to the elders\' nests'
            ]
        elif cat.trait == 'loyal':
            thoughts += [
                'Is checking in on the elder\'s den',
                'Is rambling on to younger cats about the importance of respecting their elders'
            ]
        elif cat.trait == 'thoughtful':
            thoughts += [
                'Gave an elder their favorite piece of fresh-kill',
                'Is making sure that the elders all have fresh bedding'
            ]
        elif cat.trait == 'troublesome':
            thoughts += [
                'Recently was scolded for eating prey before the queens and elders'
            ]
    elif other_cat.status == 'apprentice':
        if cat.trait == 'childish':
            thoughts += ['Is pouncing on unsuspecting apprentices']
        elif cat.trait == 'cold':
            thoughts += ['Is scolding the apprentices over something slight']
        elif cat.trait == 'thoughtful':
            thoughts += [
                'Is hosting a modified training session for the beginner apprentices'
            ]

    return thoughts

def get_med_thoughts(cat, other_cat):
    thoughts = []
    thoughts += MEDICINE_GENERAL["all"]

    first_key = "alive"
    if other_cat.dead:
        first_key = "dead"
    second_key = other_cat.status

    # checks for specific roles
    thoughts += MEDICINE_GENERAL[first_key]["all"]
    thoughts += MEDICINE_GENERAL[first_key][second_key]

    # trait specific medicine cat apprentice thoughts    
    trait = cat.trait
    thoughts += MEDICINE_TRAITS[trait]
    
    # checks for specific roles + traits
    if cat.status == 'kitten':
        if cat.trait == 'bloodthirsty':
            thoughts += ['Encourages kits to eat some strange red berries']

    return thoughts

def get_deputy_thoughts(cat, other_cat):
    thoughts = []
    thoughts += DEPUTY_GENERAL["all"]

    first_key = "alive"
    if other_cat.dead:
        first_key = "dead"
    second_key = other_cat.status

    # checks for specific roles
    thoughts += DEPUTY_GENERAL[first_key]["all"]
    thoughts += DEPUTY_GENERAL[first_key][second_key]

    # trait specific medicine cat apprentice thoughts    
    trait = cat.trait
    thoughts += DEPUTY_TRAITS[trait]

    # get also the warrior thoughts
    warrior_thoughts = get_warrior_thoughts(cat,other_cat)
    # get all thoughts without "deputy" in it
    warrior_thoughts = list(filter(lambda thought: "deputy" not in thought, warrior_thoughts))
    thoughts += warrior_thoughts

    return thoughts

def get_leader_thoughts(cat, other_cat):
    thoughts = []
    thoughts += LEADER_GENERAL["all"]

    first_key = "alive"
    if other_cat.dead:
        first_key = "dead"
    second_key = other_cat.status

    # checks for specific roles
    thoughts += LEADER_GENERAL[first_key]["all"]
    thoughts += LEADER_GENERAL[first_key][second_key]

    # trait specific medicine cat apprentice thoughts    
    trait = cat.trait
    thoughts += LEADER_TRAITS[trait]

    # get also the warrior thoughts
    warrior_thoughts = get_warrior_thoughts(cat,other_cat)
    # get all thoughts without "deputy" in it
    warrior_thoughts = list(filter(lambda thought: "deputy" not in thought and "leader" not in thought, warrior_thoughts))
    thoughts += warrior_thoughts

    return thoughts

def get_elder_thoughts(cat, other_cat):
    thoughts = []
    thoughts += ELDER_GENERAL["all"]

    first_key = "alive"
    if other_cat.dead:
        first_key = "dead"
    second_key = other_cat.status

    # checks for specific roles
    thoughts += ELDER_GENERAL[first_key]["all"]
    thoughts += ELDER_GENERAL[first_key][second_key]

    # trait specific medicine cat apprentice thoughts    
    trait = cat.trait
    if trait in cat.kit_traits:
        cat.trait = choice(cat.traits)
    thoughts += ELDER_TRAITS[trait]

    return thoughts

def get_family_thoughts(cat, other_cat):
    """Returns a list of thoughts, if the other cat is a kit from cat."""
    thoughts = []
    if cat.children is None or len(cat.children) <= 0:
        return thoughts

    # children
    all_children = list(filter(lambda inter_cat: inter_cat.ID in cat.children and inter_cat.is_alive(), cat.all_cats.values()))
    if all_children is None or len(all_children) <= 0:
        return thoughts
    
    thoughts += get_adult_children_thoughts(cat,other_cat,all_children)

    # young kitten
    kitten = list(filter(lambda inter_cat: inter_cat.moons < 6 and inter_cat.is_alive(), all_children))
    if kitten is None or len(kitten) <= 0:
        return thoughts
    thoughts += get_young_children_thoughts(cat,other_cat,kitten)

    return thoughts

# ---------------------------------------------------------------------------- #
#                            more in depth thoughts                            #
# ---------------------------------------------------------------------------- #

def get_adult_children_thoughts(cat, other_cat, all_children):
    thoughts = []
    if all_children is None and len(all_children) <= 0:
        return thoughts

    thoughts += FAMILY["has_children"]
    if other_cat.ID in all_children and other_cat.moons > 11:
        thoughts += [
            "Is remembering how cute r_c was when they were little",
            "Is feeling proud of r_c",
            "Thinks how fast time can go when looking at r_c"
        ]

    return thoughts

def get_young_children_thoughts(cat, other_cat, young_children):
    thoughts = []
    if young_children is None and len(young_children) <= 0:
        return thoughts

    if len(young_children) == 1:
        thoughts += FAMILY["has_young_children"]["single"]
    else:
        thoughts += FAMILY["has_young_children"]["multiple"]

    if other_cat.ID in young_children:
        thoughts += [
            "Can't stop gazing at r_c with wonder",
            "Worries that r_c may not be safe",
            "Is grooming r_c"
        ]

    return thoughts

def get_warrior_trait_role_thoughts(cat, other_cat):
    # nonspecific age trait thoughts (unused traits: bold)
    thoughts = []
    thoughts += WARRIOR_TRAITS[cat.trait]
    if cat.trait == 'altruistic':
        # checks for specific roles
        if other_cat.status == 'elder':
            thoughts += [
                'Is taking fresh-kill to the elders and queens',
                'Gave their share of fresh-kill to the elders',
                'Is putting mousebile on the elder\'s ticks'
            ]
        elif other_cat.status == 'kitten':
            thoughts += [
                'Is following the kits around camp, giving the queens a break',
                'Let the kits sleep in their nest with them last night',
                'Is grooming the scruffiest kits around camp dutifully'
            ]
    
    elif cat.trait == 'calm':
        # checks for specific roles
        if other_cat.status == 'elder':
            thoughts += ['Is politely listening to elders\'s stories']
    
    elif cat.trait == 'careful':
        # checks for specific roles
        if other_cat.status == 'kitten':
            thoughts += ['Is warning the kits to stay in camp']
    
    elif cat.trait == 'childish':
        # checks for specific roles
        if other_cat.status == 'kitten':
            thoughts += [
                'Is pouncing on unsuspecting kits',
                'Is teaching new games to the kits'
            ]
    
    elif cat.trait == 'cold':
        # checks for specific roles
        if other_cat.status == 'kitten':
            thoughts += ['Recently snapped at the kits, making them cry']
    
    elif cat.trait == 'compassionate':
        if cat.status != 'leader':
            thoughts += [
                'Is making sure that the leader has eaten before they dig in to their own meal',
                'Is being scolded for giving their prey away to a starving loner'
            ]
        # checks for specific roles
        if other_cat.status == 'elder':
            thoughts += [
                'Helped the elders to rise stiffly from their nests this morning'
            ]
    
    elif cat.trait == 'confident':
        if cat.status != 'deputy' and cat.status != 'leader':
            thoughts += [
                'Is letting the Clan leader know their opinion on a rather serious matter',
                'Knows without a doubt that the Clan deputy respects them',
                'Knows without a doubt that the Clan leader must respect them',
                'Is sure to stand tall when the Clan leader walks by'
            ]
    
    elif cat.trait == 'empathetic':
        # checks for specific roles
        if other_cat.status == 'elder':
            thoughts += [
                'Volunteered to gather fresh lining to the elders\' nests'
            ]
        elif other_cat.status == 'kitten':
            thoughts += ['Is comforting kits after a scary experience']
    
    elif cat.trait == 'loyal':
        # checks for specific roles
        if other_cat.status == 'kitten':
            thoughts += [
                'Is roaring playfully at kits, making them laugh',
                'Has been rogue housing with the kits a little to hard lately',
                'Is telling the kits tales about valiant warriors in the thick of epic battles'
            ]
    
    elif cat.trait == 'patient':
        # checks for specific roles
        if other_cat.status == 'kitten':
            thoughts += ['Is letting a kit tug on their tail']
    
    elif cat.trait == 'responsible':
        # checks for specific roles
        if other_cat.status == 'elder':
            thoughts += ['Is going to fetch the elders new bedding today']
        elif other_cat.status == 'kitten':
            thoughts += ['Is making sure the kits behave']
    
    elif cat.trait == 'shameless':
        # checks for specific roles
        if other_cat.status == 'kitten':
            thoughts += ['Pushed a kit out of their way thoughtlessly']
    
    elif cat.trait == 'sneaky':
        if other_cat.status == 'kitten':
            thoughts += ['Is teaching kits how to walk without making a sound']
    
    elif cat.trait == 'strict':
        # checks for specific roles
        if other_cat.status == 'kitten':
            thoughts += [
                'Is grumbling about troublesome kits',
                'Can\'t stand to watch the kits make fools of themselves'
            ]
    
    elif cat.trait == 'thoughtful':
        # checks for specific roles
        if other_cat.status == 'elder':
            thoughts += [
                'Gave an elder their favorite piece of fresh-kill',
                'Is making sure that the elders all have fresh bedding'
            ]
        elif other_cat.status == 'queen':
            thoughts += ['Is bringing soaked moss to the queens in the nursery']
        elif other_cat.status == 'kitten':
            thoughts += [
                'Is promising to take the kits out on a stroll today if they behave',
                'Plucked feathers from their meal for the kits to play with',
                'Is hosting a mock training session for the kits',
                'Is offering to look after the kits while the queens rest'
            ]
    
    elif cat.trait == 'troublesome':
        # checks for specific roles
        if other_cat.status == 'elder' or other_cat.status == 'queen':
            thoughts += [
                'Recently was scolded for eating prey before the queens and elders'
            ]
        elif other_cat.status == 'kitten':
            thoughts += ['Got scolded for telling the kits a naughty joke!']
    
    elif cat.trait == 'vengeful':
        if cat.status != 'leader':
            thoughts += [
                'Thinks that the Clan leader should declare war on a neighboring Clan'
            ]
    
    elif cat.trait == 'wise':
        # checks for specific roles
        if other_cat.status == 'kitten':
            thoughts += [
                'Is teaching kits how to identify prey prints in the dirt',
                'Is counseling the kits'
            ]

    # skill specific thoughts
    if cat.skills == 'strong connection to starclan' and cat.status != 'medicine cat' and cat.status != 'medicine cat apprentice':
        thoughts += [
            'Is becoming interested in herbs',
            'Volunteers to gather herbs',
            'Has been lending the medicine cat a paw lately'
        ]
    return thoughts

def get_df_thoughts(cat, other_cat):
    thoughts = []
    thoughts+= GENERAL_DEAD["df"]
    
    return thoughts

def get_exile_thoughts(cat, other_cat):
    thoughts = []
    thoughts += EXILE
    
    return thoughts

def get_ur_thoughts(cat, other_cat):
    thoughts = []
    thoughts+= GENERAL_DEAD["ur"]

    return thoughts

def get_outside_thoughts(cat, other_cat):
    thoughts = []
    if cat.status in ["kittypet", "loner", "rogue"]:
        thoughts += OUTSIDE[cat.status]['general']
        if cat.age == 'kitten':
            thoughts += OUTSIDE[cat.status]['kitten']
        elif cat.age == 'adolescent':
            thoughts += OUTSIDE[cat.status]['adolescent']
        elif cat.age in ['young adult', 'adult', 'senior adult']:
            thoughts += OUTSIDE[cat.status]['adult']
        elif cat.age == 'elder':
            thoughts += OUTSIDE[cat.status]['elder']
        return thoughts
    thoughts += OUTSIDE['lost']['general']
    if cat.age == 'kitten':
        thoughts += OUTSIDE['lost']['kitten']
    elif cat.age == 'adolescent':
        thoughts += OUTSIDE['lost']['apprentice']
    elif cat.age in ['young adult', 'adult', 'senior adult']:
        thoughts += OUTSIDE['lost']['warrior']
    elif cat.status == 'medicine cat' or cat.status == 'medicine cat apprentice':
        thoughts += OUTSIDE['lost']['med']
    elif cat.status == 'deputy':
        thoughts += OUTSIDE['lost']['deputy']
    elif cat.status == 'leader':
        thoughts += OUTSIDE['lost']['leader']
    elif cat.age == 'elder':
        thoughts += OUTSIDE['lost']['elder']
    return thoughts

# ---------------------------------------------------------------------------- #
#                             load general thoughts                            #
# ---------------------------------------------------------------------------- #

resource_directory = "resources/dicts/thoughts/"

GENERAL_DEAD = None
with open(f"{resource_directory}cat_dead_general.json", 'r', encoding='ascii') as read_file:
    GENERAL_DEAD = ujson.loads(read_file.read())

GENERAL_ALIVE = None
with open(f"{resource_directory}cat_alive_general.json", 'r', encoding='ascii') as read_file:
    GENERAL_ALIVE = ujson.loads(read_file.read())
    
EXILE = None
with open(f"{resource_directory}exile.json", 'r', encoding='ascii') as read_file:
    EXILE = ujson.loads(read_file.read())
    
OUTSIDE = None
with open(f"{resource_directory}other.json", 'r', encoding='ascii') as read_file:
    OUTSIDE = ujson.loads(read_file.read())

FAMILY = None
with open(f"{resource_directory}family.json", 'r', encoding='ascii') as read_file:
    FAMILY = ujson.loads(read_file.read())

# ---------------------------------------------------------------------------- #
#                           specific status thoughts                           #
# ---------------------------------------------------------------------------- #

in_depth_path = "alive/"

GENERAL_TO_OTHER = None
with open(f"{resource_directory}{in_depth_path}1_all_to_other.json", 'r') as read_file:
    GENERAL_TO_OTHER = ujson.loads(read_file.read())

KITTEN_GENERAL = None
with open(f"{resource_directory}{in_depth_path}kitten_to_other.json", 'r') as read_file:
    KITTEN_GENERAL = ujson.loads(read_file.read())

MEDIATOR_GENERAL = None
with open(f"{resource_directory}{in_depth_path}mediator_to_other.json", 'r') as read_file:
    MEDIATOR_GENERAL = ujson.loads(read_file.read())

MEDIATOR_APP_GENERAL = None
with open(f"{resource_directory}{in_depth_path}mediator_apprentice_to_other.json", 'r') as read_file:
    MEDIATOR_APP_GENERAL = ujson.loads(read_file.read())

APPR_GENERAL = None
with open(f"{resource_directory}{in_depth_path}apprentice_to_other.json", 'r') as read_file:
    APPR_GENERAL = ujson.loads(read_file.read())

MED_APPR_GENERAL = None
with open(f"{resource_directory}{in_depth_path}medicine_app_to_other.json", 'r') as read_file:
    MED_APPR_GENERAL = ujson.loads(read_file.read())

WARRIOR_GENERAL = None
with open(f"{resource_directory}{in_depth_path}warrior_to_other.json", 'r') as read_file:
    WARRIOR_GENERAL = ujson.loads(read_file.read())

MEDICINE_GENERAL = None
with open(f"{resource_directory}{in_depth_path}medicine_to_other.json", 'r') as read_file:
    MEDICINE_GENERAL = ujson.loads(read_file.read())

DEPUTY_GENERAL = None
with open(f"{resource_directory}{in_depth_path}deputy_to_other.json", 'r') as read_file:
    DEPUTY_GENERAL = ujson.loads(read_file.read())

LEADER_GENERAL = None
with open(f"{resource_directory}{in_depth_path}leader_to_other.json", 'r') as read_file:
    LEADER_GENERAL = ujson.loads(read_file.read())

ELDER_GENERAL = None
with open(f"{resource_directory}{in_depth_path}elder_to_other.json", 'r') as read_file:
    ELDER_GENERAL = ujson.loads(read_file.read())

# ---------------------------------------------------------------------------- #
#                            specific trait thoughts                           #
# ---------------------------------------------------------------------------- #

traits_path = "traits/"

KITTEN_TRAITS = None
with open(f"{resource_directory}{traits_path}kitten.json", 'r', encoding='ascii') as read_file:
    KITTEN_TRAITS = ujson.loads(read_file.read())

APPR_TRAITS = None
with open(f"{resource_directory}{traits_path}apprentice.json", 'r', encoding='ascii') as read_file:
    APPR_TRAITS = ujson.loads(read_file.read())

MED_APPR_TRAITS = None
with open(f"{resource_directory}{traits_path}med_apprentice.json", 'r', encoding='ascii') as read_file:
    MED_APPR_TRAITS = ujson.loads(read_file.read())

WARRIOR_TRAITS = None
with open(f"{resource_directory}{traits_path}warrior.json", 'r', encoding='ascii') as read_file:
    WARRIOR_TRAITS = ujson.loads(read_file.read())

MEDICINE_TRAITS = None
with open(f"{resource_directory}{traits_path}medicine.json", 'r', encoding='ascii') as read_file:
    MEDICINE_TRAITS = ujson.loads(read_file.read())

DEPUTY_TRAITS = None
with open(f"{resource_directory}{traits_path}deputy.json", 'r', encoding='ascii') as read_file:
    DEPUTY_TRAITS = ujson.loads(read_file.read())

LEADER_TRAITS = None
with open(f"{resource_directory}{traits_path}leader.json", 'r', encoding='ascii') as read_file:
    LEADER_TRAITS = ujson.loads(read_file.read())

ELDER_TRAITS = None
with open(f"{resource_directory}{traits_path}elder.json", 'r', encoding='ascii') as read_file:
    ELDER_TRAITS = ujson.loads(read_file.read())

MEDIATOR_TRAITS = None
with open(f"{resource_directory}{traits_path}mediator.json", 'r', encoding='ascii') as read_file:
    MEDIATOR_TRAITS = ujson.loads(read_file.read())

MEDIATOR_APP_RAITS = None
with open(f"{resource_directory}{traits_path}mediator_apprentice.json", 'r', encoding='ascii') as read_file:
    MEDIATOR_APP_TRAITS = ujson.loads(read_file.read())
