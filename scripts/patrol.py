from os import name
from pydoc import text
from random import choice, randint
from math import ceil, floor
from .events import events_class
from .game_essentials import *
from .names import *
from .cats import *
from .pelts import *


class Patrol(object):

    def __init__(self):
        self.patrol_event = None
        self.patrol_leader = None
        self.patrol_cats = []
        self.patrol_names = []
        self.possible_patrol_leaders = []
        self.patrol_skills = []
        self.patrol_statuses = []
        self.patrol_traits = []
        self.patrol_total_experience = 0
        self.success = False
        self.patrol_random_cat = None
        self.patrol_stat_cat = None
        self.experience_levels = [
            'very low', 'low', 'slightly low', 'average', 'somewhat high',
            'high', 'very high', 'master', 'max'
        ]

    def add_patrol_cats(self):
        self.patrol_cats.clear()
        self.patrol_names.clear()
        self.possible_patrol_leaders.clear()
        self.patrol_skills.clear()
        self.patrol_statuses.clear()
        self.patrol_traits.clear()
        self.patrol_total_experience = 0
        for cat in game.switches['current_patrol']:
            name = str(cat.name)
            self.patrol_cats.append(cat)
            self.patrol_names.append(name)
            if cat.status != 'apprentice':
                self.possible_patrol_leaders.append(cat)
            self.patrol_skills.append(cat.skill)
            self.patrol_statuses.append(cat.status)
            self.patrol_traits.append(cat.trait)
            self.patrol_total_experience += cat.experience
            game.patrolled.append(cat)
        if self.possible_patrol_leaders:
            self.patrol_leader = choice(self.possible_patrol_leaders)
        elif not self.possible_patrol_leaders:
            self.patrol_leader = choice(self.patrol_cats)
        self.patrol_random_cat = choice(self.patrol_cats)

    def add_possible_patrols(self):
        possible_patrols = []
        # general hunting patrols
        possible_patrols.extend([
            PatrolEvent(
                1,
                'Your patrol comes across a mouse',
                'Your patrol catches the mouse!',
                'Your patrol narrowly misses the mouse',
                'Your patrol ignores the mouse',
                60,
                10,
                win_skills=['good hunter', 'great hunter',
                            'fantastic hunter']),
            PatrolEvent(
                2,
                'Your patrol comes across a large rat',
                'Your patrol catches the rat! More freshkill!',
                'Your patrol misses the rat, and the patrol\'s confidence is shaken',
                'Your patrol ignores the rat',
                50,
                10,
                win_skills=['great hunter', 'fantastic hunter']),
            PatrolEvent(3,
                        'Your patrol comes across a large hare',
                        'Your patrol catches the hare!',
                        'Your patrol narrowly misses the hare',
                        'Your patrol ignores the hare',
                        40,
                        20,
                        win_skills=['fantastic hunter']),
            PatrolEvent(4,
                        'Your patrol comes across a bird',
                        'Your patrol catches the bird before it flies away!',
                        'Your patrol narrowly misses the bird',
                        'Your patrol ignores the bird',
                        50,
                        10,
                        win_skills=['great hunter', 'fantastic hunter']),
            PatrolEvent(
                5,
                'Your patrol comes across a squirrel',
                'Your patrol catches the squirrel!',
                'Your patrol narrowly misses the squirrel',
                'Your patrol ignores the squirrel',
                50,
                10,
                win_skills=['good hunter', 'great hunter',
                            'fantastic hunter']),
            PatrolEvent(6,
                        'Your patrol sees the shadow of a fish in a river',
                        'r_c hooks the fish out of the water! More freshkill!',
                        'Your patrol accidentally scares the fish away',
                        'Your patrol ignores the fish',
                        50,
                        10,
                        win_skills=['great hunter', 'fantastic hunter']),
            PatrolEvent(
                7,
                'r_c spots a rabbit up ahead but it seems to be acting strange',
                'r_c catches the rabbit and it is eaten as normal',
                'r_c catches the rabbit and later the cats who eat it become violently ill',
                'r_c avoids catching the rabbit and looks for other prey',
                40,
                10,
                win_skills=['smart', 'very smart', 'extremely smart']),
            PatrolEvent(
                8,
                'The patrol approaches a Twoleg nest while hunting',
                'The patrol has a successful hunt, avoiding any Twolegs',
                'Twoleg kits scare the cats away',
                'The patrol decides to hunt elsewhere',
                40,
                10,
                win_skills=['great hunter', 'fantastic hunter'])
        ])

        # general/misc patrols
        possible_patrols.extend([
            PatrolEvent(100, 'Your patrol doesn\'t find anything useful',
                        'It was still a fun outing!',
                        'How did you fail this??',
                        'Your patrol decides to head home early', 100, 10),
            PatrolEvent(
                101, 'The patrol finds a nice spot to sun themselves',
                'The sunlight feels great and the cats have a pleasant patrol',
                'The patrol doesn\'t get much done because of that',
                'They decide to stay focused instead', 80, 10),
            PatrolEvent(
                102,
                'The patrol comes across a thunderpath',
                'Your patrol crosses the thunderpath and can hunt on the other side',
                'r_c is hit by a monster and debates retiring to the elder den',
                'They decide it is better not to cross',
                50,
                10,
                win_skills=['very smart', 'extremely smart']),
            PatrolEvent(
                106,
                'p_l finds a patch of herbs that they believe the medicine cat mentioned they needed',
                'The patrol brings the herbs back to camp and they are put to good use',
                'The herbs turn out to be useless weeds',
                'They decide to focus on the patrol instead and leave the herb collecting to the medicine cat',
                40,
                10,
                win_skills=['very smart', 'extremely smart']),
            PatrolEvent(
                107,
                'r_c goes missing during the patrol',
                'r_c is later found carrying loads of prey after a successful hunt',
                'r_c is found lying injured on the ground',
                'r_c eventually catches up',
                40,
                10,
            ),
            PatrolEvent(
                108,
                'The smell of food lures r_c close to a Twoleg trap',
                'r_c grabs the food before the trap goes off',
                'r_c is caught in the trap and is taken by Twolegs shortly after',
                'r_c loses interest and walks back to the patrol',
                40,
                10,
                win_skills=['very smart', 'extremely smart']),
            PatrolEvent(
                108,
                'While helping gathering herbs, r_c stumbles upon a bush of red berries',
                'The patrol tells r_c to stay away from the deathberries just in time',
                'r_c chews some of the deathberries and dies',
                'r_c decides not to touch the berries',
                50,
                10,
                win_skills=['very smart', 'extremely smart']),
            PatrolEvent(
                109,
                'r_c notices a Clanmate trapped in some brambles',
                'r_c frees their Clanmate',
                'The patrol works all day to free their Clanmate and gets nothing else done',
                'r_c runs back to camp to fetch help and rejoins the patrol later',
                50,
                10,
                win_skills=['very smart', 'extremely smart']),
            PatrolEvent(
                110,
                'r_c spots a large rabbit, but it is just over the border',
                'r_c catches the rabbit without the enemy Clan noticing',
                'r_c is caught by an enemy Clan patrol and is sent on their way',
                'r_c decides against chasing the rabbit',
                50,
                10,
                win_skills=['fantastic hunter'])
        ])

        # season patrols
        if game.clan.current_season == 'Newleaf':
            possible_patrols.extend([
                PatrolEvent(
                    111,
                    'Your patrol notices new leaves and flowers starting to grow',
                    'The hunting is plentiful as new prey is born',
                    'With newleaf comes allergies...',
                    'Your patrol decides to head home early', 95, 10),
                PatrolEvent(
                    112,
                    'r_c notes that it is a beautiful day outside, birds are singing and flowers are blooming',
                    'On days like these, patrolling is very pleasant',
                    'On days like these, cats are too lazy to patrol',
                    'Your patrol decides to head home early', 95, 10),
                PatrolEvent(
                    113,
                    'The patrol approaches a deep ravine. There is a lot of prey here, but the ground is very slippery from newleaf rain',
                    'The patrol has a very successful hunt',
                    'While hunting, r_c slips and falls into the ravine, never to be seen again',
                    'The patrol decides to hunt elsewhere',
                    50,
                    10,
                    win_skills=['fantastic hunter']),
                PatrolEvent(
                    114,
                    'A large river divides the Clan\'s territory and the water is high from newleaf rain. Should your patrol cross it?',
                    'The patrol crosses the river and the rest of the patrol goes smoothly',
                    'r_c is swept away from the strong current and drowns',
                    'The patrol decides it is too dangerous to cross right now',
                    50, 10)
            ])

        elif game.clan.current_season == 'Greenleaf':
            possible_patrols.extend([
                PatrolEvent(
                    120,
                    'It is extremely hot out today; r_c debates turning back home',
                    'They decide to power through the weather and the patrol is successful',
                    'r_c collapses from heat exhaustion',
                    'Your patrol decides to head home early to beat the heat',
                    50, 10),
                PatrolEvent(
                    121,
                    'r_c spots a pond and debates if they should stop for a quick swim to cool off',
                    'They stop to swim for a few moments and feel rejuvenated',
                    'They get distracted while splashing in the water',
                    'r_c decides to continue with the patrol instead', 50, 10),
                PatrolEvent(
                    122,
                    'The patrol comes across a strange Twoleg object smelling slightly of smoke and prey',
                    'The patrol interprets the purpose of the object. It seems like Twolegs light their freshkill on fire before eating it! How strange.',
                    'The patrol can\'t seem to interpret the purpose of the object',
                    'The patrol decides to avoid the Twoleg object',
                    50,
                    10,
                    win_skills=['smart', 'very smart', 'extremely smart']),
            ])
        elif game.clan.current_season == 'Leaf-fall':
            possible_patrols.extend([
                PatrolEvent(
                    130,
                    'The leaves are starting to turn colors; the patrol know leaf-bare will be here soon',
                    'For now, hunting is still good',
                    'A chilly wind makes it difficult to hunt',
                    'The patrol is uneventful',
                    50,
                    10,
                    win_skills=['great hunter', 'fantastic hunter']),
                PatrolEvent(
                    131,
                    'r_c stalks a squirrel under a tree',
                    'They use the leaf-fall foliage to their advantage and catch the squirrel easily',
                    'Leaves crunch under their paws and the squirrel gets away',
                    'r_c decides to go after other prey instead',
                    50,
                    10,
                    win_skills=['fantastic hunter'])
            ])
        elif game.clan.current_season == 'Leaf-bare':
            possible_patrols.extend([
                PatrolEvent(
                    140,
                    'It starts snowing soon after the patrol sets out',
                    'Despite the snow, the patrol manages to hunt successfully',
                    'The prey must be hiding; the patrol catches nothing and is caught in a snowstorm',
                    'They decide to turn back and wait until the snow dies down',
                    50,
                    10,
                    win_skills=['great hunter', 'fantastic hunter']),
                PatrolEvent(
                    141,
                    'r_c thinks that it is too cold to patrol and that they should turn back',
                    'r_c warms up as they patrol the territory and says it isn\'t so bad anymore',
                    'The cold is too much for r_c, they go missing and are later found frozen to death',
                    'They decide to turn back and wait for warmer weather',
                    50,
                    10,
                    win_skills=[
                        'good teacher', 'great teacher', 'fantastic teacher'
                    ])
            ])

        if self.patrol_random_cat.status == 'apprentice' and len(
                self.patrol_cats) > 1:
            possible_patrols.extend([
                PatrolEvent(
                    150, 'The patrol wants to hold a training session for r_c',
                    'r_c becomes more confident in their abilities after the training session',
                    'r_c is nervous and doesn\'t perform well',
                    'They decide to focus on the patrol instead', 50, 10)
            ])

        # conversation patrols
        if len(self.patrol_cats) > 1:
            possible_patrols.extend([
                PatrolEvent(200, 'Your patrol doesn\'t find anything useful',
                            'It was still a fun outing!',
                            'How did you fail this??',
                            'Your patrol decides to head home', 100, 10),
                PatrolEvent(
                    201, 'The patrol finds a nice spot to sun themselves',
                    'The sunlight feels great and the cats have a successful patrol',
                    'The patrol doesn\'t get much done because of that',
                    'They decide to stay focused instead', 80, 10),
                PatrolEvent(
                    204,
                    'Your patrol has a disagreement and look to p_l to settle the dispute',
                    'p_l manages to skillfully smooth over any disagreement',
                    'p_l stutters; they don\'t think they are fit to lead the patrol',
                    'Your patrol decides to head home',
                    50,
                    10,
                    win_skills=['great speaker', 'excellent speaker']),
                PatrolEvent(
                    205,
                    'r_c admits that they had a vision from StarClan last night',
                    'The patrol talks them through the vision as they hunt',
                    'No one can make sense of the vision',
                    'The patrol doesn\'t talk about the vision',
                    50,
                    10,
                    win_skills=['strong connection to starclan']),
                PatrolEvent(
                    202,
                    'The patrol quickly devolves into ghost stories and everyone is on edge',
                    'Despite the tense mood, the patrol is successful',
                    'A branch snaps and the whole patrol runs back to camp',
                    'p_l quickly silences any talk about ghosts', 50, 10),
                PatrolEvent(
                    203, 'r_c is tempted to eat the prey they just caught',
                    'They eat the prey without anyone noticing',
                    'The patrol notices r_c eating the prey and reports them back at camp',
                    'r_c decides against breaking the warrior code', 50, 10),
                PatrolEvent(
                    103,
                    'p_l suggests this might be a good chance for the cats to practice teamwork',
                    'Everyone has a nice practice session and their connection to their Clanmates grows stronger',
                    'Unfortunately, no one steps up to teach',
                    'They decide to focus on the patrol instead',
                    50,
                    10,
                    win_skills=[
                        'good teacher', 'great teacher', 'fantastic teacher'
                    ]),
                PatrolEvent(
                    104,
                    'p_l suggests this might be a good chance for the cats to practice new hunting techniques',
                    'Everyone has a nice practice session and their hunting skills grow stronger',
                    'Unfortunately, no one steps up to teach',
                    'They decide to focus on the patrol instead',
                    50,
                    10,
                    win_skills=[
                        'good teacher', 'great teacher', 'fantastic teacher'
                    ]),
                PatrolEvent(
                    105,
                    'p_l suggests this might be a good chance for the cats to practice new fighting techniques',
                    'Everyone has a nice practice session and their fighting skills grow stronger',
                    'Unfortunately, no one steps up to teach',
                    'They decide to focus on the patrol instead',
                    50,
                    10,
                    win_skills=[
                        'good teacher', 'great teacher', 'fantastic teacher'
                    ])
            ])

            # if self.patrol_random_cat.status == 'warrior' or self.patrol_random_cat.status == 'apprentice':
            #     possible_patrols.extend([
            #         PatrolEvent(
            #             250,
            #             'r_c admits that they have been training in the dark forest',
            #             'The patrol manages to convince r_c to stop',
            #             'The patrol isn\'t able to convince r_c to stop and a few nights later they are found dead in their nest',
            #             'The patrol decides not to advise r_c what they should do',
            #             50,
            #             10,
            #             win_skills=[
            #                 'great speaker', 'excellent speaker',
            #                 'strong connection to starclan'
            #             ]),
            #         PatrolEvent(
            #             251,
            #             'r_c admits that they have been training in the dark forest',
            #             'The patrol manages to convince r_c to stop',
            #             'The patrol isn\'t able to convince r_c to stop and a few nights later they wake up injured in their nest',
            #             'The patrol decides not to advise r_c what they should do',
            #             50,
            #             10,
            #             win_skills=[
            #                 'great speaker', 'excellent speaker',
            #                 'strong connection to starclan'
            #             ])
            #     ])
            if self.patrol_random_cat.status == 'deputy':
                possible_patrols.extend([
                    PatrolEvent(
                        260,
                        'r_c admits that they don\'t think that they are a good deputy',
                        'The patrol tells r_c that the Clan wouldn\'t be the same without them, and r_c feels a sense of relief',
                        'The patrol secretly agrees with r_c',
                        'The patrol doesn\'t say anything about r_c\'s statement',
                        50,
                        10,
                        win_skills=['great speaker', 'excellent speaker']),
                    PatrolEvent(
                        251,
                        'The patrol starts to doubt r_c\'s ability as the Clan\'s deputy',
                        'r_c performs well on the patrol and all doubt is quelled',
                        'The patrol performs poorly and they blame r_c',
                        'The patrol decides to keep their thoughts to themselves',
                        50,
                        10,
                    ),
                ])

        # fighting patrols
        possible_patrols.extend([
            PatrolEvent(
                300,
                'Your patrol catches the scent of a fox',
                'Your patrol finds the fox and drives it away',
                'Your patrol fails to drive away to fox, but luckily no cat was injured',
                'Your patrol decides not to pursue the fox',
                40,
                20,
                win_skills=[
                    'good fighter', 'great fighter', 'excellent fighter'
                ]),
            PatrolEvent(
                301,
                'Your patrol comes catches the scent of a fox',
                'Your patrol drives away the fox and her cubs',
                'The mother fox fights to defend her cubs, and r_c is injured in the attack',
                'Your patrol decides not to pursue the fox',
                30,
                30,
                win_skills=['excellent fighter']),
            PatrolEvent(302,
                        'Your patrol comes across a large dog',
                        'Your patrol valiantly drives away the dog',
                        'The dog is driven away, but not before injuring r_c',
                        'Your patrol decides not to pursue the dog',
                        40,
                        20,
                        win_skills=['excellent fighter']),
            PatrolEvent(303,
                        'Your patrol comes across a small dog',
                        'Your patrol drives away the dog',
                        'The dog\'s barking scares away prey',
                        'The patrol decides not to pursue the dog',
                        20,
                        60,
                        win_skills=[
                            'good fighter', 'great fighter',
                            'excellent fighter'
                        ]),
            PatrolEvent(
                304,
                'r_c alerts the rest of the patrol that there is a rogue near the Clan border',
                'Your patrol chases the rogue off of the territory',
                'The rogue leaves, but not before giving r_c a scar',
                'Your patrol decides not to confront the rogue',
                50,
                20,
                win_skills=['great fighter', 'excellent fighter']),
            PatrolEvent(
                305,
                'A gang of rogues confronts your patrol',
                'Your patrol drives away the rogues',
                'The rogues are bloodthirsty and kill r_c before they leave',
                'The patrol sprints back to camp',
                40,
                20,
                win_skills=['excellent fighter']),
            PatrolEvent(
                306,
                'There is a badger den up ahead',
                'Your patrol chases the badger off of the territory',
                'The badger is angered when the patrol nears its den and badly injures r_c',
                'The patrol avoids the badger den',
                40,
                20,
                win_skills=['excellent fighter']),
            PatrolEvent(
                307,
                'There is a badger den up ahead',
                'Your patrol chases the badger off of the territory',
                'The badger is furious when the patrol nears its den and kills r_c',
                'The patrol avoids the badger den',
                50,
                20,
                win_skills=['excellent fighter']),
            PatrolEvent(
                308,
                'While on patrol, r_c notices some suspicious pawprints in the ground',
                'The pawprints lead to a trespassing rogue and the patrol drives them off of the '
                'territory',
                'It turns out they were r_c\'s own pawprints... How embarrassing',
                'They decide not to investigate',
                60,
                20,
                win_skills=[
                    'good fighter', 'great fighter', 'excellent fighter'
                ]),
            PatrolEvent(
                309,
                'While on patrol, r_c notices some suspicious pawprints in the ground',
                'The pawprints lead to a trespassing rogue and the patrol drives them off of the '
                'territory',
                'It turns out they were r_c\'s own pawprints... How embarrassing',
                'They decide not to investigate',
                60,
                20,
                win_skills=[
                    'good fighter', 'great fighter', 'excellent fighter'
                ])
        ])

        # single cat patrol
        if len(self.patrol_cats) == 1:
            possible_patrols.extend([
                PatrolEvent(
                    400,
                    'r_c is nervous doing a patrol by themselves',
                    'They don\'t let their nerves get to them and continue the patrol successfully',
                    'They run back to camp, unable to continue',
                    'They continue the patrol but progress is slow',
                    40,
                    10,
                    win_skills=['very smart', 'extremely smart']),
                PatrolEvent(
                    401,
                    'Since r_c is alone, they debate taking a bite out of the freshkill they have just caught',
                    'They decide not to and end up catching extra prey for the kits and elders',
                    'They eat the freshkill; however, they do not catch more prey to make up for it and the kits and elders go hungry',
                    'They shake the thought from their mind',
                    30,
                    10,
                    win_skills=['smart', 'very smart', 'extremely smart']),
                PatrolEvent(
                    402,
                    'While alone on patrol, r_c thinks about life',
                    'They find peace within themselves and enjoy the rest of the patrol',
                    'Their thoughts are plagued with bad memories',
                    'r_c decides to focus on the patrol',
                    40,
                    10,
                )
            ])
            if self.patrol_cats[0].status == 'apprentice':
                possible_patrols.extend([
                    PatrolEvent(
                        450,
                        'r_c worries that an apprentice should not be out here alone',
                        'At least this is a good chance to learn the territory',
                        'r_c gets lost in the territory and doesn\'t learn anything',
                        'r_c turns back to camp, deciding that this is a bad idea',
                        40,
                        10,
                        win_skills=['very smart', 'extremely smart']),
                    PatrolEvent(
                        451,
                        'r_c\'s mentor assesses them by sending them on a solo hunt',
                        'r_c catches a lot of prey and passes their assessment',
                        'Hunting is poor and r_c\'s mentor is disappointed',
                        'r_c asks their mentor to do the assessment some other time',
                        40,
                        10,
                        win_skills=[
                            'good hunter', 'great hunter', 'fantastic hunter'
                        ]),
                    PatrolEvent(
                        452,
                        'r_c\'s mentor assesses them by sending them on a solo border patrol',
                        'r_c successfully marks the Clan territory',
                        'r_c messes up the territory markings and almost starts a border skirmish',
                        'r_c asks their mentor to do the assessment some other time',
                        40,
                        10,
                    )
                ])

        # new cat patrols (not kit)
        possible_patrols.extend([
            PatrolEvent(
                500,
                'Your patrol finds a loner who is interested in joining the Clan',
                'The patrol convinces the loner to join the Clan',
                'The loner decides against joining',
                'Your patrol decides not to confront the loner',
                40,
                10,
                antagonize_text=
                'Your patrol drives the loner off of the territory',
                antagonize_fail_text=
                'The loner is taken aback by their hostility and decides that Clan life is not for them',
                win_skills=['great speaker', 'excellent speaker']),
            PatrolEvent(
                501,
                'Your patrol finds a loner who is interested in joining the Clan',
                'The patrol convinces the loner to join the Clan and they bring with '
                'them a litter of kits',
                'The loner decides against joining',
                'Your patrol decides not to confront the loner',
                40,
                10,
                antagonize_text=
                'Your patrol drives the loner off of the territory',
                antagonize_fail_text=
                'The loner is taken aback by their hostility '
                'and decides that Clan life is not for them',
                win_skills=['great speaker', 'excellent speaker']),
            PatrolEvent(
                502,
                'Your patrol finds a kittypet who is interested in joining the Clan',
                'The patrol convinces the kittypet to join the Clan',
                'The description of Clan life frightens the kittypet',
                'Your patrol decides not to confront the kittypet',
                40,
                10,
                antagonize_text=
                'Your patrol drives the kittypet off of the territory',
                antagonize_fail_text=
                'The kittypet is taken aback by their hostility '
                'and decides that Clan life is not for them',
                win_skills=['great speaker', 'excellent speaker']),
            PatrolEvent(
                503,
                'r_c finds a wounded cat near the thunderpath',
                'The patrol brings the cat back to camp. Once nursed back to health, '
                'the cat decides to join the Clan',
                'As r_c inspects the cat, they find that they are already hunting '
                'with their ancestors',
                'They leave the wounded cat alone',
                40,
                10,
                antagonize_text=
                'Your patrol drives the cat off of the territory',
                antagonize_fail_text=
                'The wounded cat is killed in an attempt to drive them off of the territory',
                win_skills=['smart', 'very smart', 'extremely smart']),
            PatrolEvent(
                504,
                'r_c finds an abandoned kit whose mother is nowhere to be found',
                'The kit is taken back to camp and nursed back to health',
                'The kit is taken back to camp, but grows weak and dies a few days later',
                'They leave the kit alone', 40, 10)
        ])

        if self.patrol_random_cat.status == 'formerly a loner':
            possible_patrols.extend([
                PatrolEvent(
                    510,
                    'r_c finds an old friend of their\'s from when they were a loner',
                    'r_c invites their friend to join the Clan',
                    'r_c and their friend reminisce about old times',
                    'r_c says farewell to their friend and rejoins the patrol')
            ])

        if self.patrol_random_cat.status == 'formerly a kittypet':
            possible_patrols.extend([
                PatrolEvent(
                    520,
                    'r_c finds an old friend of their\'s from when they were a kittypet',
                    'r_c invites their friend to join the Clan',
                    'r_c and their friend reminisce about old times',
                    'r_c says farewell to their friend and rejoins the patrol')
            ])

        # status specific patrols

        # season specific patrols

        # trait specific patrols

        if len(self.patrol_cats) > 1:
            if self.patrol_random_cat.trait == 'strange':
                possible_patrols.extend([
                    PatrolEvent(
                        600,
                        'r_c tells the patrol to roll in a patch of garlic to diguise their scent while hunting',
                        'The plan works and their hunt goes well',
                        'The patrol finds no prey and blame r_c; it seems like all the prey was scared off because of their stench!',
                        'The patrol ignores r_c\'s odd instructions', 50, 10)
                ])
            elif self.patrol_random_cat.trait == 'bloodthirsty':
                possible_patrols.extend([
                    PatrolEvent(
                        605,
                        'r_c deliberately provokes a border patrol skirmish',
                        'The other cats in the patrol keep r_c from fighting and no one is hurt',
                        'r_c is injured by the enemy patrol',
                        'r_c decides to back down by themselves',
                        50,
                        10,
                        win_skills=['great speaker', 'fantastic speaker'])
                ])

        # biome specific patrols

        if game.clan.biome == 'forest':
            possible_patrols.extend([
                PatrolEvent(700, 
                            'Your patrol comes across a vole',
                            'Your patrol catches the vole!',
                            'Your patrol narrowly misses the vole',
                            'Your patrol decides to look for other prey',
                            50,
                            10,
                            win_skills=['great hunter', 'fantastic hunter']),
                PatrolEvent(701, 
                            'While hunting, r_c comes across a rabbit burrow',
                            'r_c catches the rabbit hiding in its burrow',
                            'The burrow is abandoned, with no prey to be found in there',
                            'r_c decides to ignore the burrow',
                            50,
                            10,
                            win_skills=['great hunter', 'fantastic hunter']),
                PatrolEvent(702, 
                            'Your patrol comes across a small fallen tree blocking their path',
                            'Your patrol successfully moves the tree out of the way and continues the patrol',
                            'Your patrol can\'t seem to move the tree out of the way and is discouraged',
                            'Your patrol decides to find another route to continue to patrol',
                            40,
                            10)
            ])
        elif game.clan.biome == 'plains':
            possible_patrols.extend([
                PatrolEvent(710, 
                            'Your patrol comes across a praire dog',
                            'Your patrol catches the praire dog!',
                            'Your patrol narrowly misses the praire dog',
                            'Your patrol decides to look for other prey',
                            50,
                            10,
                            win_skills=['great hunter', 'fantastic hunter'])
            ])
        elif game.clan.biome == 'mountains':
            possible_patrols.extend([
                PatrolEvent(710, 
                            'Your patrol comes across a shrew',
                            'Your patrol catches the shrew!',
                            'Your patrol narrowly misses the shrew',
                            'Your patrol decides to look for other prey',
                            50,
                            10,
                            win_skills=['great hunter', 'fantastic hunter'])
            ])
        elif game.clan.biome == 'swamp':
            possible_patrols.extend([
                PatrolEvent(710, 
                            'Your patrol comes across a lizard',
                            'Your patrol catches the lizard!',
                            'Your patrol narrowly misses the lizard',
                            'Your patrol decides to look for other prey',
                            50,
                            10,
                            win_skills=['great hunter', 'fantastic hunter'])
            ])
        elif game.clan.biome == 'beach':
            possible_patrols.extend([
                PatrolEvent(710, 
                            'Your patrol comes across a turtle',
                            'Your patrol catches the turtle!',
                            'Your patrol narrowly misses the turtle',
                            'Your patrol decides to look for other prey',
                            50,
                            10,
                            win_skills=['great hunter', 'fantastic hunter'])
            ])


        # other_clan patrols
        if len(game.clan.all_clans) > 0:
            1 == 1  # will add here

        # deadly patrols
        if game.settings.get('disasters') == True:
            possible_patrols.extend([
                PatrolEvent(
                    900,
                    'Your patrol hears some odd noises coming from an abandoned Twoleg nest',
                    'It\'s just an old loner singing to themselves',
                    'Your patrol walks into an ambush by a group of rogues and everyone is slaughtered',
                    'Your patrol decides not to investigate',
                    70,
                    20,
                    win_skills=['fantastic fighter']),
                PatrolEvent(
                    901,
                    'There are dark clouds in the horizon and p_l wonders if they should continue',
                    'The cats become wet from the rain but otherwise the patrol is successful',
                    'There is a downpour and a sudden flood from the overflowing river sweeps all of the cats in the patrol away',
                    'Your patrol decides to head back early',
                    70,
                    20,
                    win_skills=['fantastic fighter']),
                PatrolEvent(
                    902,
                    'Your patrol encounters a clearing where a lot of Twolegs linger',
                    'They continue hunting undetected',
                    'The Twolegs notice the cats and trap them in their monsters. The cats on your patrol are never seen again',
                    'Your patrol decides to hunt elsewhere',
                    60,
                    20,
                    win_skills=['extremely smart'])
            ])

        self.patrol_event = choice(possible_patrols)

    def calculate_success(self):
        if self.patrol_event is None:
            return
        # if patrol contains cats with autowin skill, chance of success is high
        # otherwise it will calculate the chance by adding the patrolevent's chance of success plus the patrol's total exp
        chance = self.patrol_event.chance_of_success + int(
            self.patrol_total_experience / 10)
        if self.patrol_event.patrol_id != 100:
            chance = min(chance, 80)
        if self.patrol_event.win_skills is not None:
            if set(self.patrol_skills).isdisjoint(
                    self.patrol_event.win_skills):
                chance = 90
        c = randint(0, 100)
        if c < chance:
            self.success = True
            self.handle_exp_gain()
            self.add_new_cats()
        else:
            self.success = False
            self.handle_deaths()
            self.handle_scars()

    def handle_exp_gain(self):
        if self.success:
            for cat in self.patrol_cats:
                cat.experience = cat.experience + (
                    self.patrol_event.exp + 6 // len(self.patrol_cats)) // 5
                cat.experience = min(cat.experience, 80)
                cat.experience_level = self.experience_levels[floor(
                    cat.experience / 10)]

    def handle_deaths(self):
        if self.patrol_event.patrol_id in [
                108, 113, 114, 120, 141, 250, 305, 307
        ]:
            if self.patrol_random_cat.status == 'leader':
                if self.patrol_event.patrol_id in [108, 113]:
                    game.clan.leader_lives -= 9 # taken by twolegs, fall into ravine
                else:
                    game.clan.leader_lives -= 1
            events_class.dies(self.patrol_random_cat)
        elif self.patrol_event.patrol_id in [900, 901, 902]:
            for cat in self.patrol_cats:
                cat.experience += self.patrol_event.exp
                cat.experience = min(cat.experience, 80)
                if cat.status == 'leader':
                    game.clan.leader_lives -= 10
                events_class.dies(cat)

    def handle_scars(self):
        if self.patrol_event.patrol_id in [107, 251, 301, 302, 304, 306]:
            if self.patrol_random_cat.specialty is None:
                self.patrol_random_cat.specialty = choice(
                    [choice(scars1),
                     choice(scars2),
                     choice(scars4)])
            elif self.patrol_random_cat.specialty2 is None:
                self.patrol_random_cat.specialty2 = choice(
                    [choice(scars1),
                     choice(scars2),
                     choice(scars4)])
        elif self.patrol_event.patrol_id == 102:
            self.patrol_random_cat.skill = choice(
                ['paralyzed', 'blind', 'missing a leg'])
            if game.settings['retirement']:
                self.patrol_random_cat.status_change('elder')
        elif self.patrol_event.patrol_id == 904:
            if self.patrol_random_cat.specialty is None:
                self.patrol_random_cat.specialty = choice([choice(scars5)])
            elif self.patrol_random_cat.specialty2 is None:
                self.patrol_random_cat.specialty2 = choice([choice(scars5)])

    def handle_retirements(self):
        if self.patrol_event.patrol_id == 102 and game.settings.get(
                'retirement'):
            self.patrol_random_cat.status_change('elder')

    def handle_relationships(self):
        romantic_love = 0
        platonic_like = 0
        dislike = 0
        admiration = 0
        comfortable = 0
        jealousy = 0
        trust = 0

        # change the values
        if self.patrol_event.patrol_id in []:
            romantic_love = 5
        if self.patrol_event.patrol_id in [
                2, 3, 6, 100, 103, 140, 141, 200, 204, 605
        ]:
            platonic_like = 5
        if self.patrol_event.patrol_id in [103, 110]:
            dislike = 5
        if self.patrol_event.patrol_id in [
                2, 3, 6, 104, 105, 108, 130, 131, 261, 300, 301, 302, 303, 305,
                307, 600
        ]:
            admiration = 5
        if self.patrol_event.patrol_id in [
                102, 120, 150, 202, 203, 250, 251, 260, 261
        ]:
            comfortable = 5
        if self.patrol_event.patrol_id in []:
            jealousy = 5
        if self.patrol_event.patrol_id in [
                7, 8, 102, 107, 110, 114, 115, 141, 250, 251, 605
        ]:
            trust = 5

        # affect the relationship
        cat_ids = [cat.ID for cat in self.patrol_cats]
        for cat in self.patrol_cats:
            relationships = list(
                filter(lambda rel: rel.cat_to.ID in cat_ids,
                       cat.relationships))
            for rel in relationships:
                if self.success:
                    rel.romantic_love += romantic_love
                    rel.platonic_like += platonic_like
                    rel.dislike += dislike
                    rel.admiration += admiration
                    rel.comfortable += comfortable
                    rel.jealousy += jealousy
                    rel.trust += trust
                    rel.cut_boundries()
                elif not self.success:
                    rel.romantic_love -= romantic_love
                    rel.platonic_like -= platonic_like
                    rel.dislike -= dislike
                    rel.admiration -= admiration
                    rel.comfortable -= comfortable
                    rel.jealousy -= jealousy
                    rel.trust -= trust
                    rel.cut_boundries()

    def add_new_cats(self):
        if self.patrol_event.patrol_id in [504]:  # new kit
            kit = Cat(status='kitten', moons=0)
            #create and update relationships
            relationships = []
            for cat_id in game.clan.clan_cats:
                the_cat = cat_class.all_cats.get(cat_id)
                if the_cat.dead or the_cat.exiled:
                    continue
                the_cat.relationships.append(Relationship(the_cat, kit))
                relationships.append(Relationship(kit, the_cat))
            kit.relationships = relationships
            game.clan.add_cat(kit)
            kit.skill = 'formerly a loner'
            kit.thought = 'Is looking around the camp with wonder'

        if self.patrol_event.patrol_id in [500, 501, 510]:  # new loner
            new_status = choice([
                'apprentice', 'warrior', 'warrior', 'warrior', 'warrior',
                'elder'
            ])
            if self.patrol_event.patrol_id == 501:
                new_status = 'warrior'
            kit = Cat(status=new_status)
            if (kit.status == 'elder'):
                kit.moons = randint(120, 150)
            #create and update relationships
            relationships = []
            for cat_id in game.clan.clan_cats:
                the_cat = cat_class.all_cats.get(cat_id)
                if the_cat.dead or the_cat.exiled:
                    continue
                the_cat.relationships.append(Relationship(the_cat, kit))
                relationships.append(Relationship(kit, the_cat))
            kit.relationships = relationships
            game.clan.add_cat(kit)
            kit.skill = 'formerly a loner'
            kit.thought = 'Is looking around the camp with wonder'
            if (kit.status == 'elder'):
                kit.moons = randint(120, 150)
            if randint(0, 5) == 0:  # chance to keep name
                kit.name.prefix = choice(names.loner_names)
                kit.name.suffix = ''
            if self.patrol_event.patrol_id == 501:
                num_kits = choice([2, 2, 2, 2, 3, 4])
                for _ in range(num_kits):
                    kit2 = Cat(status='kitten', moons=0)
                    kit2.skill = 'formerly a loner'
                    kit2.parent1 = kit.ID
                    kit2.thought = 'Is looking around the camp with wonder'
                    #create and update relationships
                    relationships = []
                    for cat_id in game.clan.clan_cats:
                        the_cat = cat_class.all_cats.get(cat_id)
                        if the_cat.dead or the_cat.exiled:
                            continue
                        if the_cat.ID in [kit2.parent1, kit2.parent2]:
                            the_cat.relationships.append(
                                Relationship(the_cat, kit2, False, True))
                            relationships.append(
                                Relationship(kit2, the_cat, False, True))
                        else:
                            the_cat.relationships.append(
                                Relationship(the_cat, kit2))
                            relationships.append(Relationship(kit2, the_cat))
                    kit2.relationships = relationships
                    game.clan.add_cat(kit2)

        elif self.patrol_event.patrol_id in [502, 503, 520]:  # new kittypet
            new_status = choice([
                'apprentice', 'warrior', 'warrior', 'warrior', 'warrior',
                'elder'
            ])
            kit = Cat(status=new_status)
            #create and update relationships
            relationships = []
            for cat_id in game.clan.clan_cats:
                the_cat = cat_class.all_cats.get(cat_id)
                if the_cat.dead or the_cat.exiled:
                    continue
                the_cat.relationships.append(Relationship(the_cat, kit))
                relationships.append(Relationship(kit, the_cat))
            kit.relationships = relationships
            game.clan.add_cat(kit)
            if (kit.status == 'elder'):
                kit.moons = randint(120, 150)
            kit.skill = 'formerly a kittypet'
            kit.thought = 'Is looking around the camp with wonder'
            if (kit.status == 'elder'):
                kit.moons = randint(120, 150)
            if randint(0, 2) == 0:  # chance to add collar
                kit.specialty2 = choice(scars3)
            if randint(0, 5) == 0:  # chance to keep name
                kit.name.prefix = choice(names.loner_names)
                kit.name.suffix = ''

    def check_territories(self):
        hunting_claim = str(game.clan.name) + 'Clan Hunting Grounds'
        self.hunting_grounds = []
        for y in range(44):
            for x in range(40):
                claim_type = game.map_info[(x, y)][3]
                if claim_type == hunting_claim:
                    self.hunting_claim_info[(x, y)] = game.map_info[(x, y)]
                    self.hunting_grounds.append((x, y))


class PatrolEvent(object):

    def __init__(self,
                 patrol_id,
                 intro_text,
                 success_text,
                 fail_text,
                 decline_text,
                 chance_of_success,
                 exp,
                 other_clan=None,
                 win_skills=None,
                 antagonize_text='',
                 antagonize_fail_text=''):
        self.patrol_id = patrol_id
        self.intro_text = intro_text
        self.success_text = success_text
        self.fail_text = fail_text
        self.decline_text = decline_text
        self.chance_of_success = chance_of_success  # out of 100
        self.exp = exp
        self.other_clan = other_clan
        self.win_skills = win_skills
        self.antagonize_text = antagonize_text
        self.antagonize_fail_text = antagonize_fail_text


patrol = Patrol()
