import random
import ujson

resource_directory = "resources/dicts/thoughts/"

def get_thoughts(cat):
    if cat == None:
        return
    all_cats = cat.all_cats
    # actions or thoughts for all cats. These switch either every moon or every time the game is re-opened
    other_cat = random.choice(list(all_cats.keys()))
    countdown = int(len(all_cats) / 3)
    while other_cat == cat:
        other_cat = random.choice(list(all_cats.keys()))
        countdown -= 1
        if countdown <= 0:
            continue
    other_cat = all_cats.get(other_cat)
    # placeholder thought - should never appear in game
    thoughts = ['Is not thinking about much right now']

    if cat.dead:
        thoughts = get_dead_thoughts(cat, other_cat)

    # general individual thoughts
    thoughts = get_alive_thoughts(cat, other_cat)

    return thoughts

def get_dead_thoughts(cat, other_cat):
        # individual thoughts
        thoughts = GENERAL_DEAD["all"]
        # thoughts with other cats that are dead
        if other_cat.dead:
            thoughts.extend(GENERAL_DEAD["dead"])
        else:
            thoughts.extend(GENERAL_DEAD["alive"])

        # dead young cat thoughts
        if cat.status in ['kitten', 'apprentice', 'medicine cat apprentice']:
            thoughts.extend([
                'Wishes they had more time to grow up',
                'Wonders what their full name would have been',
                'Is bothering older StarClan cats',
                'Is learning about the other cats in StarClan'
            ])
        # dead elder thoughts
        elif cat.status == 'elder':
            thoughts.extend([
                'Is grateful that they lived such a long life',
                'Is happy that their joints no longer ache',
                'Is telling stories to the younger cats of StarClan',
                'Watches over the younger cats of StarClan',
                'Is observing how different the Clan is from when they were alive'
            ])
        # dead leader thoughts
        elif cat.status == 'leader':
            thoughts.extend([
                'Hoped that they were a good leader',
                'Wishes that they had ten lives',
                'Is proud of their clan from StarClan',
                'Is pleased to see the new direction the Clan is heading in',
                'Still frets over their beloved former Clanmates from afar'
            ])
            # checks for specific roles
            if other_cat.status == 'kitten':
                thoughts.extend([
                    'Rejoices with every new kit born to the Clan they still hold so dear'
                ])

        return thoughts

def get_alive_thoughts(cat, other_cat):
    thoughts = GENERAL_ALIVE

    if cat.status == 'kitten':
        thoughts.append(get_kitten_thoughts(cat,other_cat))

    # kitten and warrior apprentice thoughts
    if cat.status != 'medicine cat apprentice' and cat.status != 'warrior' and cat.status != 'deputy' and cat.status != 'medicine cat' and cat.status != 'leader' and cat.status != 'elder' and cat.status != 'queen':
        thoughts.extend([
            'Wonders what their full name will be',
            'Pretends to be a warrior',
            "Practices the hunting crouch",
            'Pretends to fight an enemy warrior',
            'Wants to be a warrior already!',
            'Can\'t wait to be a warrior',
            'Is pretending to be deputy',
        ])
        # checks for specific roles
        if other_cat.status == 'elder':
            thoughts.extend(['Is helping the elders with their ticks'])


    if cat.status == 'apprentice':
        thoughts.append(get_apprentice_thoughts(cat,other_cat))

    if cat.status == 'medicine cat apprentice':
        thoughts.append(get_med_apprentice_thoughts(cat,other_cat))

    if cat.status == 'elder':
        thoughts.append(get_elder_thoughts(cat,other_cat))

    if cat.status == 'medicine cat':
        thoughts.append(get_med_thoughts(cat,other_cat))

    if cat.status == 'deputy':
        thoughts.append(get_deputy_thoughts(cat, other_cat))

    if cat.status == 'leader':
        thoughts.append(get_leader_thoughts(cat, other_cat))

    if cat.status == 'warrior':
        thoughts.append(get_warrior_thoughts(cat, other_cat))
        thoughts.append(get_warrior_trait_role_thoughts(cat, other_cat))

    return thoughts

def get_kitten_thoughts(cat, other_cat):
    thoughts = KITTEN_GENERAL["all"]
    first_key = "alive"
    if other_cat.dead:
        first_key = "dead"
    second_key = other_cat.status
    # checks for specific roles
    thoughts.extend(KITTEN_GENERAL[first_key]["all"])
    thoughts.extend(KITTEN_GENERAL[first_key][second_key])

    # kitten trait thoughts
    trait = cat.trait
    thoughts.extend(KITTEN_TRAITS[trait])
    return thoughts

def get_apprentice_thoughts(cat, other_cat):
    thoughts = []
    thoughts.extend(APPR_GENERAL["all"])
    first_key = "alive"
    if other_cat.dead:
        first_key = "dead"
    second_key = other_cat.status
    # checks for specific roles
    thoughts.extend(APPR_GENERAL[first_key]["all"])
    thoughts.extend(APPR_GENERAL[first_key][second_key])
    
    # checks for specific traits 
    trait = cat.trait
    thoughts.extend(APPR_TRAITS[trait])

    if cat.trait == 'charismatic':
        # checks for specific roles
        if other_cat.status == 'kitten':
            thoughts.extend([
                'Has the kits very engaged in a very, very tall tale'
            ])
        elif cat.status == 'elder':
            thoughts.extend(['Is a favorite among the elders lately'])
    
    thoughts.append(get_apprentice_thoughts(cat, other_cat))
    thoughts.append(get_med_apprentice_thoughts(cat, other_cat))
    return thoughts

def get_med_apprentice_thoughts(cat, other_cat):
    thoughts = []
    thoughts.extend(MED_APPR_GENERAL["all"])
    first_key = "alive"
    if other_cat.dead:
        first_key = "dead"
    second_key = other_cat.status

    # checks for specific roles
    thoughts.extend(MED_APPR_GENERAL[first_key]["all"])
    thoughts.extend(MED_APPR_GENERAL[first_key][second_key])

    # trait specific medicine cat apprentice thoughts    
    trait = cat.trait
    thoughts.extend(MED_APPR_TRAITS[trait])
    
    return thoughts

def get_warrior_thoughts(cat, other_cat):
    thoughts = []
    thoughts.extend(WARRIOR_GENERAL["all"])
    if cat.trait == 'ambitious':
        thoughts.extend([
            'Is asking the Clan leader what they can do to help out around camp',
            'Has been imitating the Clan leader\'s behaviour recently',
            'Envies the deputy\'s position',
        ])
    elif cat.trait == 'fierce':
        thoughts.extend([
            'Was recently chastised by the deputy for reckless behaviour out on patrol'
        ])
    elif cat.trait == 'loyal':
        thoughts.extend([
            'Is listening to the Clan leader intently',
            'Is listening to the deputy intently',
            'Is telling the Clan leader details about the recent patrol',
            'Is telling the deputy details about the recent patrol',
            'Is offering constructive criticism to the deputy',
            'Has agreed to their Clan leader\'s orders recently, despite their own doubts',
            'Proclaimed to the Clan leader their unwavering loyalty'
        ])
    elif cat.trait == 'righteous':
        thoughts.extend([
            'Is refusing to follow the deputy\'s recent orders due to their own morals'
        ])
    thoughts.extend([
            'Caught scent of a fox earlier',
            'Caught scent of an enemy warrior earlier',
            'Is helping to gather herbs', 'Is thinking about love',
            'Is decorating their nest',
            'Is reinforcing the camp with brambles',
            'Caught a huge rabbit',
            'Tries to set a good example for younger cats',
            'Wants to go on a patrol', 'Wants to go on a hunting patrol',
            'Is guarding the camp entrance', 'Is gossiping',
            'Plans to visit the medicine cat', 'Is sharpening their claws',
            'Is helping to escort the medicine cat to gather herbs',
            'Is feeling sore', 'Is being pestered by flies',
            'Feels overworked', 'Is exhausted from yesterday\'s patrol',
            'Wants to have kits', 'Is sparring with some Clanmates',
            'Fell into the nearby creek yesterday and is still feeling damp',
            'Is guarding the camp entrance',
            'Is helping to reinforce the nursery wall with brambles',
            'Is assigned to the dawn patrol tomorrow',
            'Is assigned to the hunting patrol today',
            'Is thinking about kits'
        ])
    # check for specific roles
    if other_cat.status == 'kitten':
        thoughts.extend(['Is watching over the kits'])
        if cat.trait == 'cold':
            thoughts.extend(
                ['Recently snapped at the kits, making them cry'])
        elif cat.trait == 'childish':
            thoughts.extend(['Is teaching new games to the kits'])
        elif cat.trait == 'empathetic':
            thoughts.extend(
                ['Is comforting kits after a scary experience'])
        elif cat.trait == 'fierce':
            thoughts.extend([
                'Is roaring playfully at kits, making them laugh',
                'Has been rough housing with the kits a little too hard lately'
            ])
        elif cat.trait == 'loving':
            thoughts.extend(['Is helping out with kits around camp'])
        elif cat.trait == 'playful':
            thoughts.extend([
                'Is giving kits badger rides on their back!',
                'Is riling up the kits, much to the queens\'s dismay'
            ])
        elif cat.trait == 'shameless':
            thoughts.extend(
                ['Pushed a kit out of their way thoughtlessly'])
        elif cat.trait == 'strict':
            thoughts.extend(['Is grumbling about troublesome kits'])
        elif cat.trait == 'thoughtful':
            thoughts.extend([
                'Is bringing soaked moss to the queens in the nursery',
                'Is promising to take the kits out on a stroll today if they behave',
                'Plucked feathers from their meal for the kits to play with',
                'Is offering to look after the kits while the queens rest'
            ])
        elif cat.trait == 'troublesome':
            thoughts.extend(
                ['Got scolded for telling the kits a naughty joke!'])
    elif other_cat.status == 'elder':
        if cat.trait == 'calm':
            thoughts.extend(
                ['Is politely listening to elders\'s stories'])
        elif cat.trait == 'charismatic':
            thoughts.extend(['Is a favorite among the elders lately'])
        elif cat.trait == 'compassionate':
            thoughts.extend([
                'Helped the elders to rise stiffly from their nests this morning'
            ])
        elif cat.trait == 'empathetic':
            thoughts.extend([
                'Volunteered to gather fresh lining to the elders\' nests'
            ])
        elif cat.trait == 'loyal':
            thoughts.extend([
                'Is checking in on the elder\'s den',
                'Is rambling on to younger cats about the importance of respecting their elders'
            ])
        elif cat.trait == 'thoughtful':
            thoughts.extend([
                'Gave an elder their favorite piece of fresh kill',
                'Is making sure that the elders all have fresh bedding'
            ])
        elif cat.trait == 'troublesome':
            thoughts.extend([
                'Recently was scolded for eating prey before the queens and elders'
            ])
    elif other_cat.status == 'apprentice':
        thoughts.extend([
            'Has the apprentices very engaged in a very, very tall tale'
        ])
        if cat.trait == 'childish':
            thoughts.extend(
                ['Is pouncing on unsuspecting apprentices'])
        elif cat.trait == 'cold':
            thoughts.extend(
                ['Is scolding the apprentices over something slight'])
        elif cat.trait == 'thoughtful':
            thoughts.extend([
                'Is hosting a modified training session for the beginner apprentices'
            ])
    # unused traits: bloodthirsty, calm, charismatic, cold, compassionate, empathetic, lonesome, loyal, patient, righteous, shameless, sneaky, strange, vengeful, wise
    if cat.trait == 'adventurous':
        thoughts.extend([
            'Is itching to explore the land beyond their Clan\'s territory',
            'Wants to go on a journey',
            'Wishes their leader would choose them to go on a quest'
        ])
    elif cat.trait == 'altruistic':
        thoughts.extend([
            'Offered to walk at the front of the patrol',
            'Offered to stick their nose inside a badger set to see if the badger was still there',
            'Offered to stick their nose inside a fox den to see if the fox was still there',
            'Volunteered for extra patrols',
            'Volunteered for extra duties',
            'Volunteered to stand guard of the camp'
        ])
    elif cat.trait == 'ambitious':
        thoughts.extend([
            'Is boasting loudly about having defeated an enemy warrior on patrol the other day',
            'Has been taking on extra patrols lately',
        ])
    elif cat.trait == 'bold':
        thoughts.extend([
            'Is getting some looks after speaking up at the last Clan meeting',
            'Spoke up recently at a Clan meeting'
        ])
    elif cat.trait == 'careful':
        thoughts.extend([
            'Is dutifully standing guard outside of camp',
            'Is helping to reinforce the nursery walls',
            'Is helping to reinforce the camp walls',
            'Is patching up a hole in the camp wall',
            'Is helping to reinforce the walls of the elders\' den',
            'Is going back to check out an old fox burrow they discovered yesterday, just to be safe',
            'Is going back to check out an old badger set they discovered yesterday, just to be safe'
        ])
    elif cat.trait == 'childish':
        thoughts.extend([
            'Splashes in a puddle of water during a patrol',
            'Jumps around while on patrol',
        ])
    elif cat.trait == 'confident':
        thoughts.extend([
            'Boasts about how much fresh kill they intend to bring back to camp today',
            'Thinks that they are the best hunter in the Clan',
            'Thinks that they are the fastest runner in the Clan',
            'Is showing off their battle moves',
            'Thinks that they are the fiercest fighter in the Clan'
        ])
    elif cat.trait == 'daring':
        thoughts.extend([
            'Batted at a snake on a patrol recently and fled',
            'Is leaping from boulder to boulder out in the forest',
            'Is climbing to the top of a very tall tree!',
            'Recently avoided a monster on the Thunderpath by the skin of their teeth!'
        ])
    elif cat.trait == 'faithful':
        thoughts.extend([
            'Is thanking StarClan for their catch out on a hunting patrol today'
        ])
    elif cat.trait == 'fierce':
        thoughts.extend([
            'Is asking with the medicine cat what herbs may help them to be stronger in battle',
            'Is showing off their battle moves',
            'Is offering to lead the patrol today'
        ])
    elif cat.trait == 'insecure':
        thoughts.extend([
            'Almost died of embarrassment after a recent fumble on a patrol'
        ])
    elif cat.trait == 'loving':
        # checks for specific roles
        if other_cat.status == 'kitten':
            thoughts.extend([
                'Is helping out with kits around camp',
                'Is smiling at the antics of the kits',
                'Is offering words of comfort to the kits'
            ])
    elif cat.trait == 'nervous':
        thoughts.extend([
            'Was startled by a shrew while out on patrol!',
            'Was startled by a fluttering bird while out on patrol!',
            'Acted bravely on a recent patrol, despite their anxieties',
        ])
    elif cat.trait == 'playful':
        # checks for specific roles
        if other_cat.status == 'kitten':
            thoughts.extend([
                'Is giving kits badger rides on their back!',
                'Is showing kits a game they used to play when they were that age',
                'Is riling up the kits, much to the queens\' dismay'
            ])
    elif cat.trait == 'responsible':
        thoughts.extend([
            'Is repairing one of the camp walls',
            'Is offering to lead the next patrol out'
        ])
    elif cat.trait == 'strict':
        thoughts.extend([
            'Can\'t stand to watch the younger cats make fools of themselves',
            'Is conducting a rather rigorous training session for the younger warriors',
            'Takes pride in how well-run their patrols always are',
            'Is telling off younger cats for petty dishonesty out on patrol'
        ])
    elif cat.trait == 'thoughtful':
        thoughts.extend([
            'Brought back a much-needed herb to a grateful medicine cat after a hunting patrol'
        ])
    elif cat.trait == 'troublesome':
        thoughts.extend([
            'Is grumbling as they carry out a task for the medicine cat',
            'Climbed up a tree and nearly fell out!'
        ])
    return thoughts

def get_med_thoughts(cat, other_cat):
    thoughts = []
    thoughts.extend(MEDICINE_GENERAL["all"])

    first_key = "alive"
    if other_cat.dead:
        first_key = "dead"
    second_key = other_cat.status

    # checks for specific roles
    thoughts.extend(MEDICINE_GENERAL[first_key]["all"])
    thoughts.extend(MEDICINE_GENERAL[first_key][second_key])

    # trait specific medicine cat apprentice thoughts    
    trait = cat.trait
    thoughts.extend(MEDICINE_TRAITS[trait])
    
    # checks for specific roles + traits
    if cat.status == 'kitten':
        if cat.trait == 'bloodthirsty':
            thoughts.extend(
                ['Encourages kits to eat some strange red berries'])

    return thoughts

def get_deputy_thoughts(cat, other_cat):
    thoughts = []
    thoughts.extend(DEPUTY_GENERAL["all"])

    first_key = "alive"
    if other_cat.dead:
        first_key = "dead"
    second_key = other_cat.status

    # checks for specific roles
    thoughts.extend(DEPUTY_GENERAL[first_key]["all"])
    thoughts.extend(DEPUTY_GENERAL[first_key][second_key])

    # trait specific medicine cat apprentice thoughts    
    trait = cat.trait
    thoughts.extend(DEPUTY_TRAITS[trait])

    # get also the warrior thoughts
    warrior_thoughts = get_warrior_thoughts(cat,other_cat)
    # get all thoughts without "deputy" in it
    warrior_thoughts = list(filter(lambda thought: "deputy" not in thought, warrior_thoughts))
    thoughts.append(warrior_thoughts)

    return thoughts

def get_leader_thoughts(cat, other_cat):
    thoughts = []
    thoughts.extend(LEADER_GENERAL["all"])

    first_key = "alive"
    if other_cat.dead:
        first_key = "dead"
    second_key = other_cat.status

    # checks for specific roles
    thoughts.extend(LEADER_GENERAL[first_key]["all"])
    thoughts.extend(LEADER_GENERAL[first_key][second_key])

    # trait specific medicine cat apprentice thoughts    
    trait = cat.trait
    thoughts.extend(LEADER_TRAITS[trait])

    # get also the warrior thoughts
    warrior_thoughts = get_warrior_thoughts(cat,other_cat)
    # get all thoughts without "deputy" in it
    warrior_thoughts = list(filter(lambda thought: "deputy" not in thought and "leader" not in thought, warrior_thoughts))
    thoughts.append(warrior_thoughts)

    return thoughts

def get_elder_thoughts(cat, other_cat):
    thoughts = ELDER_GENERAL["all"]

    first_key = "alive"
    if other_cat.dead:
        first_key = "dead"
    second_key = other_cat.status

    # checks for specific roles
    thoughts.extend(ELDER_GENERAL[first_key]["all"])
    thoughts.extend(ELDER_GENERAL[first_key][second_key])

    # trait specific medicine cat apprentice thoughts    
    trait = cat.trait
    thoughts.extend(ELDER_TRAITS[trait])

    return thoughts

# ---------------------------------------------------------------------------- #
#                            more in depth thoughts                            #
# ---------------------------------------------------------------------------- #

def get_warrior_trait_role_thoughts(cat, other_cat):
    # nonspecific age trait thoughts (unused traits: bold)
    thoughts = []
    thoughts.extend(WARRIOR_TRAITS[cat.trait])
    if cat.trait == 'altruistic':
        # checks for specific roles
        if other_cat.status == 'elder':
            thoughts.extend([
                'Is taking fresh kill to the elders and queens',
                'Gave their share of fresh kill to the elders',
                'Is putting mousebile on the elder\'s ticks'
            ])
        elif other_cat.status == 'kitten':
            thoughts.extend([
                'Is following the kits around camp, giving the queens a break',
                'Let the kits sleep in their nest with them last night',
                'Is grooming the scruffiest kits around camp dutifully'
            ])
    
    elif cat.trait == 'calm':
        # checks for specific roles
        if other_cat.status == 'elder':
            thoughts.extend(['Is politely listening to elders\'s stories'])
    
    elif cat.trait == 'careful':
        # checks for specific roles
        if other_cat.status == 'kitten':
            thoughts.extend(['Is warning the kits to stay in camp'])
    
    elif cat.trait == 'childish':
        # checks for specific roles
        if other_cat.status == 'kitten':
            thoughts.extend([
                'Is pouncing on unsuspecting kits',
                'Is teaching new games to the kits'
            ])
    
    elif cat.trait == 'cold':
        # checks for specific roles
        if other_cat.status == 'kitten':
            thoughts.extend(
                ['Recently snapped at the kits, making them cry'])
    
    elif cat.trait == 'compassionate':
        if cat.status != 'leader':
            thoughts.extend([
                'Is making sure that the leader has eaten before they dig in to their own meal',
                'Is being scolded for giving their prey away to a starving loner'
            ])
        # checks for specific roles
        if other_cat.status == 'elder':
            thoughts.extend([
                'Helped the elders to rise stiffly from their nests this morning'
            ])
    
    elif cat.trait == 'confident':
        if cat.status != 'deputy' and cat.status != 'leader':
            thoughts.extend([
                'Is letting the Clan leader know their opinion on a rather serious matter',
                'Knows without a doubt that the Clan deputy respects them',
                'Knows without a doubt that the Clan leader must respect them',
                'Is sure to stand tall when the Clan leader walks by'
            ])
    
    elif cat.trait == 'empathetic':
        # checks for specific roles
        if other_cat.status == 'elder':
            thoughts.extend([
                'Volunteered to gather fresh lining to the elders\' nests'
            ])
        elif other_cat.status == 'kitten':
            thoughts.extend(
                ['Is comforting kits after a scary experience'])
    
    elif cat.trait == 'loyal':
        # checks for specific roles
        if other_cat.status == 'kitten':
            thoughts.extend([
                'Is roaring playfully at kits, making them laugh',
                'Has been rough housing with the kits a little to hard lately',
                'Is telling the kits tales about valiant warriors in the thick of epic battles'
            ])
    
    elif cat.trait == 'patient':
        # checks for specific roles
        if other_cat.status == 'kitten':
            thoughts.extend(['Is letting a kit tug on their tail'])
    
    elif cat.trait == 'responsible':
        # checks for specific roles
        if other_cat.status == 'elder':
            thoughts.extend(
                ['Is going to fetch the elders new bedding today'])
        elif other_cat.status == 'kitten':
            thoughts.extend(['Is making sure the kits behave'])
    
    elif cat.trait == 'shameless':
        # checks for specific roles
        if other_cat.status == 'kitten':
            thoughts.extend(
                ['Pushed a kit out of their way thoughtlessly'])
    
    elif cat.trait == 'sneaky':
        if other_cat.status == 'kitten':
            thoughts.extend(
                ['Is teaching kits how to walk without making a sound'])
    
    elif cat.trait == 'strict':
        # checks for specific roles
        if other_cat.status == 'kitten':
            thoughts.extend([
                'Is grumbling about troublesome kits',
                'Can\'t stand to watch the kits make fools of themselves'
            ])
    
    elif cat.trait == 'thoughtful':
        # checks for specific roles
        if other_cat.status == 'elder':
            thoughts.extend([
                'Gave an elder their favorite piece of fresh kill',
                'Is making sure that the elders all have fresh bedding'
            ])
        elif other_cat.status == 'queen':
            thoughts.extend(
                ['Is bringing soaked moss to the queens in the nursery'])
        elif other_cat.status == 'kitten':
            thoughts.extend([
                'Is promising to take the kits out on a stroll today if they behave',
                'Plucked feathers from their meal for the kits to play with',
                'Is hosting a mock training session for the kits',
                'Is offering to look after the kits while the queens rest'
            ])
    
    elif cat.trait == 'troublesome':
        # checks for specific roles
        if other_cat.status == 'elder' or other_cat.status == 'queen':
            thoughts.extend([
                'Recently was scolded for eating prey before the queens and elders'
            ])
        elif other_cat.status == 'kitten':
            thoughts.extend(
                ['Got scolded for telling the kits a naughty joke!'])
    
    elif cat.trait == 'vengeful':
        if cat.status != 'leader':
            thoughts.extend([
                'Thinks that the Clan leader should declare war on a neighboring Clan'
            ])
    
    elif cat.trait == 'wise':
        # checks for specific roles
        if other_cat.status == 'kitten':
            thoughts.extend([
                'Is teaching kits how to identify prey prints in the dirt',
                'Is counseling the kits'
            ])

    # skill specific thoughts
    if cat.skills == 'strong connection to starclan' and cat.status != 'medicine cat' and cat.status != 'medicine cat apprentice':
        thoughts.extend([
            'Is becoming interested in herbs',
            'Volunteers to gather herbs',
            'Has been lending the medicine cat a paw lately'
        ])
    return thoughts

# ---------------------------------------------------------------------------- #
#                             load general thoughts                            #
# ---------------------------------------------------------------------------- #

GENERAL_DEAD = None
with open(f"{resource_directory}cat_dead_general.json", 'r') as read_file:
    GENERAL_DEAD = ujson.loads(read_file.read())

GENERAL_ALIVE = None
with open(f"{resource_directory}cat_alive_general.json", 'r') as read_file:
    GENERAL_ALIVE = ujson.loads(read_file.read())


# ---------------------------------------------------------------------------- #
#                           specific status thoughts                           #
# ---------------------------------------------------------------------------- #

in_depth_path = "alive/"

KITTEN_GENERAL = None
with open(f"{resource_directory}{in_depth_path}kitten_to_other.json", 'r') as read_file:
    KITTEN_GENERAL = ujson.loads(read_file.read())

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

WARRIOR_TRAITS = None
with open(f"{resource_directory}traits.json", 'r') as read_file:
    WARRIOR_TRAITS = ujson.loads(read_file.read())

traits_path = "traits/"

KITTEN_TRAITS = None
with open(f"{resource_directory}{traits_path}kitten.json", 'r') as read_file:
    KITTEN_TRAITS = ujson.loads(read_file.read())

APPR_TRAITS = None
with open(f"{resource_directory}{traits_path}apprentice.json", 'r') as read_file:
    APPR_TRAITS = ujson.loads(read_file.read())

MED_APPR_TRAITS = None
with open(f"{resource_directory}{traits_path}med_apprentice.json", 'r') as read_file:
    MED_APPR_TRAITS = ujson.loads(read_file.read())

MEDICINE_TRAITS = None
with open(f"{resource_directory}{traits_path}medicine.json", 'r') as read_file:
    MEDICINE_TRAITS = ujson.loads(read_file.read())

DEPUTY_TRAITS = None
with open(f"{resource_directory}{traits_path}deputy.json", 'r') as read_file:
    DEPUTY_TRAITS = ujson.loads(read_file.read())

LEADER_TRAITS = None
with open(f"{resource_directory}{traits_path}leader.json", 'r') as read_file:
    LEADER_TRAITS = ujson.loads(read_file.read())

ELDER_TRAITS = None
with open(f"{resource_directory}{traits_path}elder.json", 'r') as read_file:
    ELDER_TRAITS = ujson.loads(read_file.read())