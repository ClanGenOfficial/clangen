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
    #thoughts = get_alive_thoughts(cat, other_cat)

    return thoughts

def get_dead_thoughts(cat, other_cat):
        # individual thoughts
        thoughts = GENERAL_DEAD
        other_name = str(other_cat.name)
        # thoughts with other cats that are dead
        if other_cat.dead:
            thoughts.extend([
                'Is sharing tongues with ' + other_name,
                'Has been spending time with ' + other_name + ' lately',
                'Is acting huffy at ' + other_name,
                'Is sharing a freshkill with ' + other_name,
                'Is curious about ' + other_name, 'Is talking with ' +
                other_name, 'Doesn\'t want to talk to ' + other_name,
                'Is having a serious fight with ' + other_name,
                'Wants to spend more time with ' + other_name + '!',
                'Is thinking about future prophecies with ' + other_name,
                'Is watching over the Clan with ' + other_name,
                'Is listening to long-forgotten stories about the Clan'
            ])
        # thoughts with other cats that are alive
        elif not other_cat.dead:
            thoughts.extend([
                'Is watching over ' + other_name,
                'Is curious about what ' + other_name + ' is doing',
                'Wants to send a message to ' + other_name,
                'Is currently walking in the dreams of ' + other_name,
                'Is proud of ' + other_name, 'Is disappointed in ' +
                other_name, 'Wants to warn ' + other_name,
                'Has been following the growth of ' + other_name,
                'Has seen ' + other_name + '\'s future demise',
                'Is looking to visit ' + other_name + ' in a dream soon',
                'Accidentally found themselves in ' + other_name +
                '\'s dreams the other night', 'Wants to warn ' + other_name +
                ' about something that will happen soon', 'Knows what ' +
                other_name + '\'s secret is and wants to tell some cat'
            ])
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
    thoughts = GENERAL
    other_name = other_cat.name
    # thoughts with other cats who are dead
    if other_cat.dead:
        # young cat thoughts about dead cat
        if cat.status in ['kitten', 'apprentice', 'medicine cat apprentice']:
            thoughts.extend([
                'Is listening to stories about ' + other_name,
                'Is learning more about ' + other_name,
                'Is sad they couldn\'t spend time with ' + other_name,
                'Is wondering if ' + other_name +
                ' would have been their friend'
            ])
        # ADDED
        # older cat thoughts about dead cat
        elif cat.status in ['warrior', 'medicine cat', 'deputy', 'leader']:
            thoughts.extend([
                'Is listening to stories about ' + other_name,
                'Is learning more about ' + other_name,
                'Is sad they couldn\'t spend more time with ' + other_name,
                'Wishes they could visit ' + other_name + ' in StarClan',
                'Is remembering ' + other_name
            ])
        # ADDED
        # elder thoughts about dead cat
        elif cat.status == 'elder':
            thoughts.extend([
                'Is telling stories about ' + other_name,
                'Is sad they couldn\'t spend more time with ' + other_name,
                'Wishes they could visit ' + other_name + ' in StarClan',
                'Is remembering ' + other_name,
                'Wishes that ' + other_name + ' were still alive',
                'Found a trinket that used to belong to ' + other_name,
                'Is forgetting who ' + other_name + ' was',
                'Is thinking fondly of ' + other_name,
                'Sometimes feels like ' + other_name +
                " is still right there next to them"
            ])
        #ADDED
        elif cat.status == 'medicine cat' or cat.status == 'medicine cat apprentice' or cat.skill == 'strong connection to StarClan':  # medicine cat/strong connection
            # thoughts about dead cat
            thoughts.extend([
                'Was given a prophecy by ' + other_name,
                'Was sent an omen by ' + other_name, 'Is dreaming about ' +
                other_name + ' who gives them a message', 
                'Is visited by ' +
                other_name, 'Senses ' + other_name + ' is nearby', 
                'Saw ' +
                other_name + ' in a dream, warning them about... something',
                'Is asking for guidance from ' + other_name,
                'Is wondering desperately why ' + other_name +
                ' wasn\'t there when they needed them',
                'Is sure that they saw ' + other_name +
                ' appear in the forest today... why?',
                'Blames themselves for ' + other_name + '\'s death...'
            ])
        # ADDED but trait is not considered

    # thoughts with other cat who is alive
    elif not other_cat.dead and not other_cat.exiled:
        if cat.status in [
                'apprentice', 'medicine cat apprentice', 'warrior',
                'medicine cat', 'deputy', 'leader'
        ]:
            # older cat thoughts about kit
            if other_cat.status == 'kitten':
                thoughts.extend([
                    'Trips over ' + other_name,
                    'Is giving advice to ' + other_name, 
                    'Is giving ' +
                    other_name + ' a badger ride on their back!',
                    'Had to nip ' + other_name +
                    ' on the rump because they were being naughty',
                    'Is promising to take ' + other_name +
                    ' outside of camp if they behave', 'Is watching ' +
                    other_name + ' perform an almost-decent hunting crouch',
                    'Can\'t take their eyes off of ' + other_name +
                    ' for more than a few seconds', 'Gave ' + other_name +
                    ' a trinket they found while out on patrol today'
                ])
                if cat.ID not in [other_cat.parent1, other_cat.parent2]:
                    thoughts.append(
                        'Hopes that their own kits are as cute as ' +
                        other_name + ' someday')
            else:
                thoughts.extend([
                    'Is fighting with ' + other_name,
                    'Is talking with ' + other_name,
                    'Is sharing prey with ' + other_name,
                    'Heard a rumor about ' + other_name,
                    'Just told ' + other_name + ' a hilarious joke'
                ])

        if other_cat.is_potential_mate(cat, for_love_interest=True):
            thoughts.extend([
                'Is developing a crush on ' + other_name,
                'Is spending a lot of time with ' + other_name,
                'Feels guilty about hurting ' + other_name + '\'s feelings',
                'Can\'t seem to stop talking about ' + other_name,
                'Would spend the entire day with ' + other_name +
                ' if they could',
                'Was caught enjoying a moonlit stroll with ' + other_name +
                ' last night...', 'Keeps shyly glancing over at ' +
                other_name + ' as the Clan talks about kits',
                'Gave a pretty flower they found to ' + other_name,
                'Is admiring ' + other_name + ' from afar...',
                'Is thinking of the best ways to impress ' + other_name,
                'Doesn\'t want ' + other_name + ' to overwork themselves',
                'Is rolling around a little too playfully with ' + other_name +
                '...', 'Is wondering what it would be like to grow old with ' +
                other_name
            ])

    # kitten specific thoughts
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

    # general apprentice thoughts
    if cat.status == 'apprentice' or cat.status == 'medicine cat apprentice':
        thoughts.append(get_all_apprentice_thoughts(cat,other_cat))

    # elder specific thoughts
    if cat.status == 'elder':
        thoughts.append(get_elder_thoughts(cat,other_cat))
    # no trait specific elder thoughts yet

    # medicine cat specific thoughts
    if cat.status == 'medicine cat' or cat.status == 'medicine cat apprentice':
        thoughts.append(get_med_thoughts(cat,other_cat))

    # deputy specific thoughts
    if cat.status == 'deputy':
        thoughts.append(get_deputy_thoughts(cat, other_cat))

    # leader specific thoughts
    if cat.status == 'leader':
        thoughts.append(get_leader_thoughts(cat, other_cat))

    # warrior specific thoughts
    if cat.status == 'warrior':
        thoughts.append(get_warrior_thoughts(cat, other_cat))
        thoughts.append(get_trait_thoughts(cat, other_cat))

    return thoughts

def get_kitten_thoughts(cat, other_cat):
    thoughts = KITTEN_GENERAL
    if other_cat.status == 'elder':
        thoughts.extend(
            ['Was nipped on the rump by an elder for being naughty'])
    # kitten trait thoughts
    if cat.trait == 'charming':
        thoughts.extend([
            'Is rolling around cutely while warriors look upon them',
            'Is rubbing up against the warriors\' legs',
            'Is hoping the patrol will come back with a special gift for them like usual',
            'Is trying to purr their way out of trouble with the medicine cat'
        ])
    elif cat.trait == 'impulsive':
        thoughts.extend([
            'Keeps streaking across the clearing',
            'Is stuck in a tree... again',
            'Is complaining of a tummy ache after eating too much',
            'Is awfully close to getting a nip on the rump for misbehaving',
            'Is waiting for an opportunity to sprint out of sight'
        ])
    elif cat.trait == 'nervous':
        thoughts.extend([
            'Was startled by a croaking frog',
            'Is doing their best not to get stepped on by the bigger cats'
        ])
    # kitten and skill specific thoughts
    elif cat.skills == 'strong connection to starclan':
        thoughts.extend([
            'Thinks they saw a StarClan cat in their dreams',
            'Is scrambling the medicine cat\'s herbs!',
            'Is pretending to be the medicine cat'
        ])
    return thoughts

def get_all_apprentice_thoughts(cat, other_cat):
    thoughts = []
    thoughts.extend([
            'Is gathering moss',
            'Is gossiping',
            'Is acting angsty',
            'Is dreading their apprentice duties',
            'Fell into the nearby creek yesterday and is still feeling damp',
            'Is making their mentor laugh',
            'Is really bonding with their mentor',
            'Is having a hard time keeping up with their training',
            'Was tasked with lining nests with fresh moss today',
            'Is dreaming of someday making their Clan proud',
        ])
        # checks for specific roles
    if other_cat.status == 'kitten':
        thoughts.extend([
            'Is awkwardly deflecting kits\' questions about where kits come from',
            'Was put on kit-sitting duty',
            'Is showing off to the kits',
            'Is telling off kits for being immature',
            'Is rambling on to kits about the importance of respecting their elders'
        ])
    elif other_cat.status == 'elder':
        thoughts.extend([
            'Was asked to gather fresh moss for the elders\' bedding',
            'Plans to visit the elders soon',
            'Is checking in on the elder\'s den',
            'Plans to help the elders with their ticks'
        ])
    # checks for specific traits  (unused traits: 'calm', 'compassionate', 'faithful', 'cold', childish, confident, fierce, patient, sneaky, strange, thoughtful
    if cat.trait == 'adventurous':
        thoughts.extend([
            'Is quietly trying to recruit other apprentices for a quick adventure'
        ])
    elif cat.trait == 'altruistic':
        thoughts.extend([
            'Is thinking of giving their mentor a gift for their hard work',
            'Made a keen suggestion to their mentor the other day'
        ])
    elif cat.trait == 'ambitious':
        thoughts.extend([
            'Is asking the Clan leader what they can do to help out around camp',
            'Has been asking their mentor for more training',
            'Tries to put on a brave face for their fellow apprentices',
            'Is feeling proud of themselves',
            'Made sure to wake up early to train',
            'Is daydreaming about a Clan celebration in their honor someday'
        ])
    elif cat.trait == 'bloodthirsty':
        thoughts.extend([
            'Starts a fight with another apprentice',
            'Is hoping their warrior name will end in -claw'
        ])
    elif cat.trait == 'bold':
        thoughts.extend(['Winked cheekily at another apprentice'])
    elif cat.trait == 'careful':
        thoughts.extend(['Is asking if they need more training'])
    elif cat.trait == 'charismatic':
        thoughts.extend([
            'Winked playfully at another apprentice from across the clearing!',
            'Is this moon\'s heartthrob to the other apprentices',
            'Has recently given a wonderful speech to fellow apprentices, boosting morale'
        ])
        # checks for specific roles
        if other_cat.status == 'kitten':
            thoughts.extend([
                'Has the kits very engaged in a very, very tall tale'
            ])
        elif cat.status == 'elder':
            thoughts.extend(['Is a favorite among the elders lately'])
    elif cat.trait == 'daring':
        thoughts.extend(['Is itching to go out and train'])
    elif cat.trait == 'empathetic':
        thoughts.extend([
            'Is doing extra apprentice tasks around camp, to help lighten the load'
        ])
    elif cat.trait == 'insecure':
        thoughts.extend([
            'Doesn\'t think that they have performing up to their mentor\'s standards lately...',
        ])
    elif cat.trait == 'lonesome':
        thoughts.extend(
            ['Is feeling cramped in the apprentice\'s den'])
    elif cat.trait == 'loving':
        thoughts.extend([
            'Is listening to another apprentice\'s troubles sympathetically'
        ])
    elif cat.trait == 'loyal':
        thoughts.extend([
            'Is listening to their mentor intently',
            'Proclaimed to their mentor their unwavering loyalty'
        ])
    elif cat.trait == 'nervous':
        thoughts.extend([
            'Is hoping to not train with their mentor today...',
            'Wishes they were back in the nursery',
            'Has agreed to their mentor\'s orders recently, despite their own doubts',
        ])
    elif cat.trait == 'playful':
        thoughts.extend([
            'Won\'t stop making funny faces when their mentor\'s back is turned',
            'Annoyed their mentor on accident the other day',
            'Successfully lightened a dreary mood while out training the other day',
        ])
    elif cat.trait == 'responsible':
        thoughts.extend([
            'Is licking their chest in embarrassment after being praised by their mentor',
            'Is asking their mentor what they can do to be helpful around camp today'
        ])
    elif cat.trait == 'righteous':
        thoughts.extend([
            'Is refusing to follow their mentor\'s recent orders due to their own morals'
        ])
    elif cat.trait == 'shameless':
        thoughts.extend(['Was found napping in the warrior\'s den!'])
    elif cat.trait == 'strict':
        thoughts.extend([
            'Is busy chastising fellow apprentices... but no cat is sure what for',
            'Is participating in a rather rigorous training session'
        ])
    elif cat.trait == 'troublesome':
        thoughts.extend([
            'Is ignoring their mentor\'s orders',
            'Is making other apprentices laugh',
            'Got in trouble for shirking their training the other day...'
        ])
    elif cat.trait == 'vengeful':
        thoughts.extend(['Snaps at another apprentice'])
    elif cat.trait == 'wise':
        thoughts.extend([
            'Is giving somber advice to a fellow apprentice',
            'Was sought out by another apprentice recently for their wisdom'
        ])
    thoughts.append(get_apprentice_thoughts(cat, other_cat))
    thoughts.append(get_med_apprentice_thoughts(cat, other_cat))
    return thoughts

def get_apprentice_thoughts(cat, other_cat):
    thoughts = []
    thoughts.extend([
        'Is thinking about the time they caught a huge rabbit',
        'Practices some battle moves',
        'Is helping to reinforce the camp wall with brambles',
        'Is daydreaming about having a mate and kits someday',
        'Had quite the adventure today'
    ])
    # role specific apprentice thoughts
    # unused traits: adventurous, altruistic, calm, careful, charismatic, childish, cold, compassionate, empathetic, faithful, lonesome, loving, loyal,
    # patient, playful, responsible, righteous, shameless, sneaky, strange, strict, troublesome, vengeful, wise
    if other_cat.status == 'elder':
        thoughts.extend(['Is helping to repair the elder\'s den'])
    # trait specific apprentice thoughts
    if cat.trait == 'ambitious':
        thoughts.extend([
            'Begs to be made a warrior early',
            'Seems to be ordering their fellow apprentices around',
            'Has been catching the most prey out of all the apprentices'
        ])
    elif cat.trait == 'bloodthirsty':
        thoughts.extend([
            'Pesters their mentor about doing battle training',
            'Is thinking about murder',
            'Draws blood during their battle training',
        ])
    elif cat.trait == 'cold':
        thoughts.extend(
            ['Is hoping their warrior name will end in -claw'])
    elif cat.trait == 'bold':
        thoughts.extend([
            'Is criticizing their mentor',
            'Taunted rival Clan apprentices at the border the other day',
            'Is looking to challenge a warrior to a sparring match'
        ])
    elif cat.trait == 'confident':
        thoughts.extend(
            ['Is sure that they\'ll be made into a warrior today'])
    elif cat.trait == 'daring':
        thoughts.extend([
            'Is being scolded by the deputy for reckless behavior while out training'
        ])
    elif cat.trait == 'fierce':
        thoughts.extend([
            'Is showing off their new battle moves',
            'Is pushing hard for more battle training',
            'Was recently chastised by their mentor for reckless behaviour out on patrol',
            'Practiced battle moves with their claws out'
        ])
    elif cat.trait == 'insecure':
        thoughts.extend([
            'Is wondering if they are good enough to be a warrior...',
            'Wonders if the medicine cat life would have better suited them...',
            'Is reluctant to spar with their mentor today',
            'Doesn\'t think their hauls on hunting patrols have been substantial enough as of late'
        ])
    elif cat.trait == 'nervous':
        thoughts.extend([
            'Hopes that they will be a strong enough warrior...',
            'Is wondering if they are more suited for life as a medicine cat...',
            'Was startled by a squirrel while out training!',
        ])
    elif cat.trait == 'thoughtful':
        thoughts.extend(
            ['Offered to go on the dawn patrol with their mentor'])

def get_med_apprentice_thoughts(cat, other_cat):
    thoughts.extend([
        'Is wondering if they are good enough to become a medicine cat',
        'Wishes the other apprentices could understand how they feel',
        'Helps apply a poultice to a small wound',
        'Is enjoying learning all of the herbs a medicine cat needs!'
    ])
    # checks for specific roles
    if other_cat.status == 'kitten':
        thoughts.extend([])
    elif other_cat.status == 'elder':
        thoughts.extend([])
    # trait specific medicine cat apprentice thoughts
    # unused traits: adventurous, altruistic, ambitious, bloodthirsty, bold, calm, careful, charismatic, childish, compassionate, confident, daring, empathetic,
    # faithful, fierce, lonesome, loving, loyal, patient, playful, responsible, righteous, shameless, sneaky, strange, strict, thoughtful, troublesome, vengeful, wise
    if cat.trait == 'cold':
        thoughts.extend([
            'Is hoping their medicine cat name will end in -claw'
        ])
    elif cat.trait == 'insecure':
        thoughts.extend([
            'Is wondering if they are good enough to be a medicine cat...',
            'Wonders if the warrior life would have better suited them...'
        ])
    elif cat.trait == 'nervous':
        thoughts.extend([
            'Is wondering if they are more suited for life as a warrior...'
        ])

def get_warrior_thoughts(cat, other_cat):
    thoughts = []
    thoughts.extend(['Wants to be chosen as the new deputy'])
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
    thoughts.extend([
        'Is looking for herbs', 'Is organizing the herb stores',
        'Is drying some herbs', 'Is counting the poppy seeds',
        'Is gathering cobwebs', 'Is interpreting an omen',
        'Is interpreting a prophecy',
        'Hopes for a message from StarClan soon',
        'Is checking up on the warriors',
        'Is feeling stressed taking care of the Clan',
        'Is wondering if they could borrow some catmint from the other Clans',
        'Is wrapping a wound with cobwebs',
        'Is clearing out old herbs', 'Is tending growing herbs',
        'Is making new nests', 'Wishes they had an extra set of paws',
        'Is carefully picking up spilled poppy seeds',
        'Is out gathering more cobwebs',
        'Is reciting the names of herbs aloud',
        'Was startled awake in the wee hours by a vivid dream',
        'Is running low on catmint', 'Is running low on marigold',
        'Is running low on burdock root',
        'Is running low on poppy seeds', 'Is running low on cobwebs',
        'Is running low on feverfew',
        'Is running low on borage leaves', 'Is running low on tansy',
        'Is running low on mouse bile',
        'Plans to go out gathering herbs today',
        'Is looking forward to the half-moon meeting',
        'Is struggling to remember all of the names of herbs',
        'Is helping organize the herb stores',
        'Is proud of their ability to care for their Clanmates',
        'Made a mess of the herbs and is panicking',
        'Has been hearing the voices of StarClan cats...',
        'Has the foul taste of bitter herbs in their mouth',
        'Is happy that they chose life as a medicine cat',
        'Is lining nests with fresh moss and feathers'
    ])
    # medicine cat only thoughts no apprentices allowed
    if cat.status != 'medicine cat apprentice':
        thoughts.extend(
            ['Is thinking about taking on a new apprentice'])
    # checks for specific roles
    if cat.status == 'kitten':
        thoughts.extend([
            'Is teaching kits about what plants to stay away from',
            'Chased kits out of their den',
        ])
        # roles + traits
        if cat.trait == 'bloodthirsty':
            thoughts.extend(
                ['Encourages kits to eat some strange red berries'])
    # trait specific medicine cat thoughts
    if cat.trait == 'adventurous':
        thoughts.extend(
            ['Heads out of Clan territories to look for new herbs'])
    elif cat.trait == 'altruistic':
        thoughts.extend(['Declines to eat when prey is low'])
    elif cat.trait == 'ambitious':
        thoughts.extend([
            'Insists on taking on more tasks',
            'Spends all day gathering herbs'
        ])
    elif cat.trait == 'bloodthirsty':
        thoughts.extend([
            'Is gathering deathberries',
            'Has been disappearing a lot lately',
            'Insists only on treating cats who need it',
            'Is ripping some leaves to shreds',
            'Debates becoming a warrior',
            'Gives the wrong herbs to a warrior on purpose'
        ])
    elif cat.trait == 'bold':
        thoughts.extend(
            ['Decides to try a new herb as treatment for an injury'])
    elif cat.trait == 'calm':
        thoughts.extend(
            ['Stays composed when treating a severe injury'])
    elif cat.trait == 'careful':
        thoughts.extend(['Counts and recounts the poppy seeds'])
    elif cat.trait == 'charismatic':
        thoughts.extend(['Is doing their daily checkup on the elders'])
    elif cat.trait == 'childish':
        thoughts.extend(['Bounces excitedly at the half-moon meeting'])
    elif cat.trait == 'cold':
        thoughts.extend(['Refuses to treat an injured, abandoned kit'])
    elif cat.trait == 'compassionate':
        thoughts.extend(
            ['Works long into the night taking care of the Clan'])
    elif cat.trait == 'confident':
        thoughts.extend(
            ['Is proud of their ability to care for their Clanmates'])
    elif cat.trait == 'daring':
        thoughts.extend(['Steals catmint from a Twoleg garden'])
    elif cat.trait == 'empathetic':
        thoughts.extend([
            'Listens to the apprentices complain about their training'
        ])
    elif cat.trait == 'faithful':
        thoughts.extend(
            ['Has been hearing the voices of StarClan cats...'])
    elif cat.trait == 'fierce':
        thoughts.extend(
            ['Insists on joining battle training once a moon'])
    elif cat.trait == 'insecure':
        thoughts.extend(
            ['Is saying that they don\'t deserve their full name'])
    elif cat.trait == 'lonesome':
        thoughts.extend([
            'Is wishing they could have a mate and kits',
            'Wishes their Clanmates could understand their struggles'
        ])
    elif cat.trait == 'loving':
        thoughts.extend(['Watches over some newborn kits'])
    elif cat.trait == 'loyal':
        thoughts.extend([
            'Refuses to share gossip at the half-moon meeting',
            'Refuses to give another Clan\'s medicine cat some herbs'
        ])
    elif cat.trait == 'nervous':
        thoughts.extend(
            ['Recounts the amount of catmint in their stores'])
    elif cat.trait == 'patient':
        thoughts.extend(['Helps a warrior regain their strength'])
    elif cat.trait == 'playful':
        thoughts.extend(
            ['Excitedly teaches the kits about basic herbs'])
    elif cat.trait == 'responsible':
        thoughts.extend(
            ['Ensures that all of their duties are taken care of'])
    elif cat.trait == 'righteous':
        thoughts.extend(['Gives herbs to an injured loner'])
    elif cat.trait == 'shameless':
        thoughts.extend(['Refuses to groom themselves'])
    elif cat.trait == 'sneaky':
        thoughts.extend([
            'Seems to be hiding something in the medicine they give to the leader'
        ])
    elif cat.trait == 'strange':
        thoughts.extend([
            'Insists everyone eat chamomile leaves everyday at moonhigh',
            'Sleeps in the middle of the clearing', 'Looks dazed',
            'Hisses at the kits randomly'
        ])
    elif cat.trait == 'strict':
        thoughts.extend(
            ['Forbids anyone from disturbing them when working'])
    elif cat.trait == 'thoughtful':
        thoughts.extend(['Realizes what an omen might mean'])
    elif cat.trait == 'troublesome':
        thoughts.extend(['Mixes up herbs'])
    elif cat.trait == 'vengeful':
        thoughts.extend(
            ['Refuses to treat a cat that once bullied them'])
    elif cat.trait == 'wise':
        thoughts.extend(['Tells an ancient tale about StarClan'])

def get_deputy_thoughts(cat, other_cat):
    thoughts = []
    thoughts.extend([
        'Is assigning cats to a border patrol',
        'Is assigning cats to a hunting patrol',
        'Is wondering what it would be like to be a leader',
        'Is stressed about organizing patrols',
        'Wonders who will give them nine lives', 'Feels overworked',
        'Is hoping for a break', 'Is assessing the apprentices',
        'Wishes they had an extra set of paws',
        'Is assigning cats to the dawn patrol',
        'Is assigning cats to the hunting patrol',
        'Is assigning cats to patrol the borders',
        'Can\'t believe they overslept today',
        'Is unsure of what the rest of the clan thinks of them as deputy',
        'Is doing their best to honor their Clan and their leader',
        'Must speak with the leader soon about something they found while out on patrol'
    ])
    # trait specific deputy thoughts
    if cat.trait == 'bloodthirsty':
        thoughts.extend([
            'Thinks about killing the leader and staging it as an accident',
            'Encourages the leader to start a war'
        ])
    elif cat.trait == 'strange':
        thoughts.extend([
            'Accidentally assigns the same cat to three patrols',
            'Insists a hunting patrol only bring back mice',
            'Goes missing and comes back smelling like garlic',
            'Is making odd noises'
        ])
    return thoughts

def get_leader_thoughts(cat, other_cat):
    thoughts = []
    thoughts.extend([
        'Is hoping for a sign from StarClan',
        'Is hoping that they are leading their Clan well',
        'Thinks about who should mentor new apprentices',
        'Is worried about Clan relations',
        'Tries to set a good example for the deputy',
        'Is assessing some apprentices',
        'Is thinking about forming an alliance',
        'Is thinking about battle strategies',
        'Almost lost a life recently',
        'Is counting how many lives they have left',
        'Is thinking about what to say at the Gathering',
        'Is questioning their ability to lead',
        'Is dreading the Clan meeting they must call later today',
        'Is finding the responsibility of leadership to be quite the heavy burden',
        'Is feeling blessed by StarClan this moon',
        'Is making a solemn vow to protect their Clanmates',
        'Has been letting their deputy call the shots recently, and is proud of their initiative',
        'Called an important Clan meeting recently',
        'Is pondering the next mentors for the kits of the Clan',
        'Think they have been hearing the voices of StarClan cats...',
        'Is pondering recent dreams they have had... perhaps from StarClan?',
        'Recently called a Clan meeting, but forgot what to say'
    ])
    # checks for specific roles
    if other_cat.status == 'kitten':
        thoughts.extend([
            'Has recently picked up the scent of mischievous kits in their den...'
        ])
    # trait specific leader thoughts
    if cat.trait == 'bloodthirsty':
        thoughts.extend([
            'Encourages warriors to start fights on border patrols',
            'Is debating if they should declare a war with another Clan',
            'Is wondering if they could hold apprentice ceremonies at 4 moons old instead'
        ])
    elif cat.trait == 'strange':
        thoughts.extend([
            'No thoughts, head empty',
            'Insists they they received ten lives instead of nine',
            'Has a crazed look in their eyes',
            'Is wondering how many cats would agree to changing the Clan\'s name...'
        ])
    return thoughts

def get_elder_thoughts(cat, other_cat):
    thoughts = ELDER_GENERAL
    return thoughts

def get_trait_thoughts(cat, other_cat):
    # nonspecific age trait thoughts (unused traits: bold)
    thoughts = []
    thoughts.extend(TRAITS[cat.trait])
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


GENERAL_DEAD = None
with open(f"{resource_directory}cat_dead_general.json", 'r') as read_file:
    GENERAL_DEAD = ujson.loads(read_file.read())

GENERAL = None
with open(f"{resource_directory}cat_alive_general.json", 'r') as read_file:
    GENERAL = ujson.loads(read_file.read())

TRAITS = None
with open(f"{resource_directory}traits.json", 'r') as read_file:
    GENERAL = ujson.loads(read_file.read())

# ---------------------------------------------------------------------------- #
#                           specific status thoughts                           #
# ---------------------------------------------------------------------------- #

status_path = "alive_status/"

KITTEN_GENERAL = None
with open(f"{resource_directory}{status_path}kitten.json", 'r') as read_file:
    KITTEN_GENERAL = ujson.loads(read_file.read())

ALL_APPR_GENERAL = None
with open(f"{resource_directory}{status_path}all_apprentices.json", 'r') as read_file:
    ALL_APPR_GENERAL = ujson.loads(read_file.read())

ELDER_GENERAL = None
with open(f"{resource_directory}{status_path}elder.json", 'r') as read_file:
    ELDER_GENERAL = ujson.loads(read_file.read())

