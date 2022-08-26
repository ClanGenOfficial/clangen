from random import choice, randint
from math import ceil, floor
from .events import events_class
from .game_essentials import *
from .names import *
from .cats import *
from .pelts import *


class Patrol(object):

    def __init__(self):
        self.patrol_cats = []
        self.patrol_size = len(self.patrol_cats)
        self.patrol_skills = []
        self.patrol_statuses = []
        self.patrol_traits = []
        self.patrol_total_experience = 0
        self.patrol_max_experience = 0
        self.patrol_leader = None
        self.patrol_event = []
        self.before = 1
        self.success = 0
        self.patrol_random_cat = None
        self.patrol_stat_cat = None
        # [#,prompt,win,lose,decline,threshold,reward,size,status,season,trait,function,autowin skills]
        self.patrol_events = []
        self.eligible_events = []
        self.patrol_result_text = ''
        self.other_clan = {}

        self.experience_levels = ['very low', 'low', 'slightly low', 'average', 'somewhat high', 'high', 'very high', 'master',
                                  'max']

    # get patrol personalities, patrol total experience, patrol max experience
    def new_patrol(self):
        self.patrol_cats = game.switches['current_patrol']
        self.patrol_size = len(self.patrol_cats)
        self.patrol_skills = []
        self.patrol_statuses = []
        self.patrol_traits = []
        self.refresh_events()
        self.patrol_event = []
        self.patrol_total_experience = 0
        self.patrol_max_experience = 0
        self.before = 1
        self.success = 0
        self.patrol_leader = None
        self.patrol_random_cat = None
        self.patrol_stat_cat = None
        self.patrol_result_text = ''
        self.eligible_events = []
        self.other_clan = {}
        self.new_cat_patrols = [37, 43, 44, 45]
        self.failable_patrols = self.new_cat_patrols + [11]
        self.intentional_fail = ''
        self.patrol_random_cat = choice(self.patrol_cats)
        for i in range(self.patrol_size):
            self.patrol_skills.append(self.patrol_cats[i].skill)
            self.patrol_traits.append(self.patrol_cats[i].trait)
            self.patrol_statuses.append(self.patrol_cats[i].status)
            self.patrol_total_experience += float(self.patrol_cats[i].experience)
            if int(self.patrol_cats[i].experience) >= int(self.patrol_max_experience):
                self.patrol_leader = self.patrol_cats[i]
                self.patrol_max_experience = self.patrol_cats[i].experience
        for i in range(len(self.patrol_events)):
            test_event = self.patrol_events[i]
            if test_event[7] == 1 and self.patrol_size != 1:
                continue
            if test_event[7] == 2 and self.patrol_size == 1:
                continue
            if test_event[10] != 0 and test_event[10] not in self.patrol_traits and test_event[10] not in self.patrol_skills:
                continue
            if test_event[9] not in [0, game.clan.current_season]:
                continue
            if test_event[8] != 0 and test_event[8] not in self.patrol_statuses:
                continue
            self.eligible_events.append(test_event)
        self.patrol_event = choice(self.eligible_events)
        if len(game.clan.all_clans) > 0:
            if self.patrol_event[0] in self.new_cat_patrols and len(game.clan.clan_cats) > 20 and randint(0, 4):
                self.other_clan = self.meet_other_clan()
            if self.patrol_event[0] == 11:
                self.other_clan = self.meet_other_clan()
        else:
            while self.patrol_event[0] in [37, 43, 44, 45, 11]:
                self.patrol_event = choice(self.eligible_events)
        if len(game.clan.all_clans) > 0:
            for other_clan in game.clan.all_clans:
                if int(other_clan.relations) < 7 and randint(1, 3) == 1:
                    self.other_clan = self.meet_other_clan(other_clan)
        if self.patrol_event[0] == 36:
            self.patrol_event[5] = 30 * self.patrol_size
        if self.patrol_event[10] != 0 and self.patrol_event[10] in self.patrol_traits:
            self.patrol_stat_cat = self.patrol_cats[self.patrol_traits.index(self.patrol_event[10])]

        if self.patrol_event[10] != 0 and self.patrol_event[10] in self.patrol_skills:
            self.patrol_stat_cat = self.patrol_cats[self.patrol_skills.index(self.patrol_event[10])]

        self.patrol_event[1] = self.patrol_event[1].replace('(patrol_size)', str(self.patrol_size))

        self.patrol_event[1] = self.patrol_event[1].replace('p_l', str(self.patrol_leader.name))

        self.patrol_event[2] = self.patrol_event[2].replace('p_l', str(self.patrol_leader.name))

        self.patrol_event[3] = self.patrol_event[3].replace('p_l', str(self.patrol_leader.name))

        self.patrol_event[4] = self.patrol_event[4].replace('p_l', str(self.patrol_leader.name))

        self.patrol_event[1] = self.patrol_event[1].replace('r_c', str(self.patrol_random_cat.name))

        self.patrol_event[2] = self.patrol_event[2].replace('r_c', str(self.patrol_random_cat.name))

        self.patrol_event[3] = self.patrol_event[3].replace('r_c', str(self.patrol_random_cat.name))

        self.patrol_event[4] = self.patrol_event[4].replace('r_c', str(self.patrol_random_cat.name))

        self.patrol_event[1] = self.patrol_event[1].replace('clan_name', f'{str(game.clan.name)}Clan')

        self.patrol_event[1] = self.patrol_event[1].replace('other2_clan', f'{choice(names.normal_prefixes)}Clan')

        if game.clan.deputy:
            self.patrol_event[1] = self.patrol_event[1].replace('(deputy)', str(game.clan.deputy.name))

            self.patrol_event[2] = self.patrol_event[2].replace('(deputy)', str(game.clan.deputy.name))

            self.patrol_event[3] = self.patrol_event[3].replace('(deputy)', str(game.clan.deputy.name))

            self.patrol_event[4] = self.patrol_event[4].replace('(deputy)', str(game.clan.deputy.name))

        if game.clan.leader:
            self.patrol_event[1] = self.patrol_event[1].replace('(leader)', str(game.clan.leader.name))

            self.patrol_event[2] = self.patrol_event[2].replace('(leader)', str(game.clan.leader.name))

            self.patrol_event[3] = self.patrol_event[3].replace('(leader)', str(game.clan.leader.name))

            self.patrol_event[4] = self.patrol_event[4].replace('(leader)', str(game.clan.leader.name))

        if self.patrol_stat_cat is not None:
            self.patrol_event[1] = self.patrol_event[1].replace('s_c', str(self.patrol_stat_cat.name))

            self.patrol_event[2] = self.patrol_event[2].replace('s_c', str(self.patrol_stat_cat.name))

            self.patrol_event[3] = self.patrol_event[3].replace('s_c', str(self.patrol_stat_cat.name))

            self.patrol_event[4] = self.patrol_event[4].replace('s_c', str(self.patrol_stat_cat.name))

    def intentionally_fail(self):
        if self.patrol_event[0] in self.new_cat_patrols:
            self.intentional_fail = 'Drive away the loner'
            # success
            self.patrol_event[2] = 'Your patrol talks to the cat and asks them to not cross the border again.'
            # fail
            self.patrol_event[3] = 'The stranger says mean things to the patrol after being asked to leave.'

        if self.patrol_event[0] == 11:
            self.intentional_fail = 'Antagonize'  # for this event the success and fails are calculated in meet_other_clans() because they will be different depending on relations

    def meet_other_clan(self, other_clan=''):
        if not other_clan:
            other_clan = choice(game.clan.all_clans)
        other_clan_name = f"{other_clan.name}Clan"
        other_clan_relations = int(other_clan.relations)
        other_clan_temperament = int(other_clan.relations)
        if other_clan_relations > 17:
            self.patrol_event = [11, f'clan_name meets their allies, {other_clan_name}, at the border.', 'Your cats have a nice conversation with them',
                                 'Although they act nice, the alliance seems to be weakening.', 'You decide not to talk with the ally patrol', 60, 8, 0, 0, 0, 0, 1,
                                 ['good speaker', 'great speaker', 'excellent speaker']]
            if self.intentional_fail:
                self.patrol_event[2] = f'Your cats seem to ignore the alliance, threatening {other_clan_name} anyway'
                self.patrol_event[3] = 'Your cats try to offend to the other clan but only make things slightly awkward'


        elif other_clan_relations < 11 and other_clan_relations > 6:
            self.patrol_event = [11, f'clan_name is threatened by a {other_clan_name} patrol at the border', 'Your cats manage to smooth things out a bit',
                                 'The patrol ends with threats and malice. Clan relations have worsened.', 'You decide to back off from the opposing patrol', 60, 8, 0, 0, 0, 0, 1,
                                 ['great speaker', 'excellent speaker']]
            if self.intentional_fail:
                self.patrol_event[2] = f'Your cats shoot back threats as well, hurting clan relations'
                self.patrol_event[3] = 'Your cats mostly ignore the other clan\'s threats'

        elif other_clan_relations < 7 and 'fierce' not in self.patrol_traits and 'bloodthirsty' not in self.patrol_traits:
            self.patrol_event = [11, f'Your patrol is attacked by a {other_clan_name} patrol at the border', 'Your cats manage to escape without injury',
                                 f'r_c is killed by the {other_clan_name} patrol.', 'You run away from the other patrol', 60, 8, 0, 0, 0, 0, 1,
                                 ['great fighter', 'excellent fighter', 'excellent speaker']]
            if self.intentional_fail:
                self.patrol_event[2] = f'Your cats attack {other_clan_name} right back'
                self.patrol_event[3] = f'r_c is killed by the {other_clan_name} patrol.'


        elif other_clan_relations < 7 and 'fierce' in self.patrol_traits:
            self.patrol_event = [11, f'Your patrol is attacked by a {other_clan_name} patrol at the border',
                                 'Your cats manage to escape, but only after s_c kills an enemy ' + choice(['warrior', 'apprentice']),
                                 f'r_c is killed by the {other_clan_name} patrol.', 'You run away from the other patrol', 60, 8, 0, 0, 0, 'fierce', 1,
                                 ['great fighter', 'excellent fighter', 'excellent speaker']]
            if self.intentional_fail:
                self.patrol_event[2] = f'Your cats chase {other_clan_name} away as they flee'
                self.patrol_event[3] = f'r_c is killed by the {other_clan_name} patrol.'


        elif other_clan_relations < 7:
            self.patrol_event = [11, f'Your patrol is attacked by a {other_clan_name} patrol at the border',
                                 'Your cats manage to escape, but only after s_c kills an enemy ' + choice(['warrior', 'apprentice']),
                                 f'r_c is killed by the {other_clan_name} patrol.', 'You run away from the other patrol', 60, 8, 0, 0, 0, 'bloodthirsty', 1,
                                 ['great fighter', 'excellent fighter', 'excellent speaker']]
            if self.intentional_fail:
                self.patrol_event[2] = f'Your cats chase {other_clan_name} away as they flee'
                self.patrol_event[3] = f'r_c is killed by the {other_clan_name} patrol.'


        else:
            self.patrol_event = [11, f'clan_name meets a {other_clan_name} patrol at the border, but nobody is hostile.', 'Your cats have a nice conversation with them',
                                 'Despite the lack of outright hostilities, the situation turns awkward fast', 'You decide not to talk with the opposing patrol', 60, 8, 0, 0, 0, 0,
                                 1, ['great speaker', 'excellent speaker']]
            if self.intentional_fail:
                self.patrol_event[2] = f'Your cats intentionally antagonize the other clan anyway.'
                self.patrol_event[3] = f'Despite the vague threats, the situation only turns awkward'

        self.patrol_event[2] = self.patrol_event[2].replace('r_c', str(self.patrol_random_cat.name))
        self.patrol_event[3] = self.patrol_event[3].replace('r_c', str(self.patrol_random_cat.name))

        return other_clan

    def calculate(self):
        self.patrol_result_text = self.patrol_event[4]
        if game.switches['event'] == 3:
            self.intentionally_fail()
            if self.patrol_event[0] == 11:
                self.meet_other_clan(other_clan=self.other_clan)
            game.switches['event'] = 1
        if game.switches['event'] == 1:
            self._extracted_from_calculate_6()
        for i in range(self.patrol_size):
            self.patrol_cats[i].in_camp = 0
        game.switches['event'] = 4

    # TODO Rename this here and in `calculate`
    def _extracted_from_calculate_6(self):
        self.success = False
        if self.patrol_total_experience < self.patrol_event[5]:
            chance = 3
        elif self.patrol_total_experience >= self.patrol_event[5] * 2:
            chance = 10
        else:
            chance = 9
        if randint(1, 10) <= chance:
            self.success = True
        for skill in self.patrol_skills:
            if skill in self.patrol_event[12]:
                self.success = True
        if self.patrol_event[11]:
            self.event_special()
        if self.success:
            self.patrol_result_text = self.patrol_event[2]
            experience_each = ceil(int(self.patrol_event[6]) / int(self.patrol_size) / 2)
            experiencelevels = ['very low', 'low', 'slightly low', 'average', 'somewhat high', 'high', 'very high', 'master', 'max']

            for i in range(self.patrol_size):
                self.patrol_cats[i].experience = int(self.patrol_cats[i].experience) + int(experience_each)

                self.patrol_cats[i].experience = max(self.patrol_cats[i].experience, 0)
                self.patrol_cats[i].experience = min(self.patrol_cats[i].experience, 80)
                self.patrol_cats[i].experience_level = experiencelevels[floor(self.patrol_cats[i].experience / 10)]

        else:
            self.patrol_result_text = self.patrol_event[3]
        self.before = 0
        if self.patrol_event[11]:
            self.event_special()

    def refresh_events(self):
        # patrol = id, first text, success, fail, ignore,
        self.patrol_events = [[1, 'Your patrol comes upon the scent of a mouse', 'Your patrol catches the mouse', 'Your patrol narrowly misses catching the mouse',
                               'You decide not to pursue the mouse', 10, 8, 0, 0, 0, 0, 0, ['good hunter', 'great hunter', 'fantastic hunter']],
                              [2, 'Your patrol doesnt find anything useful', 'It was still a fun outing, and you learned a lot', 'How? How did you fail this?',
                               'You decide to cut the patrol short and head home.', -5, 6, 0, 0, 0, 0, 0, []],
                              [3, 'The hunting is good this greenleaf, and the patrol finds a nice spot to sun themselves',
                               'The sunlight feels great, and the cats have a successful patrol', 'Unfortunately, the patrol doesnt get much accomplished beyond that',
                               'p_l decides that the patrol should stay focused', 30, 8, 0, 0, 'Greenleaf', 0, 0, []],
                              [4, 'Your patrols comes upon the scent of a hare', 'Your patrol catches the hare!', 'Unfortunately, your patrol missed the hare',
                               'You decide not to pursue the hare', 20, 12, 0, 0, 0, 0, 0, ['great hunter', 'fantastic hunter']],
                              [5, 'Your patrol comes upon the scent of a large rat', 'Your patrol catches the rat! More fresh kill!',
                               'Your patrols confidence is shaken by missing the rat', 'You decide not to pursue the rat', 20, 12, 0, 0, 0, 0, 1, ['fantastic hunter']],
                              [6, 'Your patrol catches the scent of a fox', 'Your patrol finds the fox and drives it away.',
                               'Your patrol fails to drive away the fox, but nobody was injured', 'You decide not to pursue the fox', 50, 15, 0, 0, 0, 0, 0,
                               ['good fighter', 'great fighter', 'excellent fighter']],
                              [7, 'Your patrol catches the scent of a fox', 'Your patrol finds a fox and her cubs and drives them away',
                               'The mother fox fights to defend her cubs; r_c is left with a scar', 'You decide not to pursue the fox', 70, 25, 0, 0, 0, 0, 1,
                               ['great fighter', 'excellent fighter']], [8, 'Your patrol catches the scent of a large dog', 'Your patrol manages to valiantly drive away the dog',
                                                                         'The dog is driven away, but only after killing r_c', 'You decide not to pursue the dog', 150, 50, 0, 0, 0,
                                                                         0, 1, ['excellent fighter']],
                              [9, 'Your patrol comes across a thunderpath. Do you cross it?', 'Your patrol crosses the path, and can hunt on the other side',
                               'r_c is hit by a Monster and debates retiring to the elder den', 'You decide to not cross the thunderpath', 20, 10, 0, 0, 0, 0, 1,
                               ['very smart', 'extremely smart']],
                              [10, 'Your patrol has a disagreement. They look to p_l to settle the dispute', 'p_l manages to skillfully smooth over any disagreement',
                               'p_l stutters; they dont think they are fit to lead a patrol', 'Instead of moderating, you decide to turn the patrol back home', 100, 15, 2, 0, 0, 0,
                               1, []], [11, 'clan_name meets a other2_clan patrol at the border, but nobody is hostile.', 'Your cats have a nice conversation with them',
                                        'Despite the lack of outright hostilities, the situation turns awkward fast', 'You decide not to talk with the opposing patrol', 60, 8, 0,
                                        0, 0, 0, 0, ['great speaker', 'excellent speaker']],
                              [12, 'p_l suggests this patrol might be a good chance for an apprentice to practice', 'The apprentice has a good practice session',
                               'Unfortunately, nobody in the patrol is good at teaching', 'You decide to focus on the patrol instead of practice', 60, 15, 2, 'apprentice', 0, 0, 1,
                               ['good teacher', 'great teacher', 'fantastic teacher']],
                              [13, 'p_l suggests this might be a good chance for the cats to practice teamwork', 'Everybody has a nice practice session',
                               'Unfortunately, nobody steps up to teach', 'You decide to focus on the patrol instead of practice', 60, 15, 2, 0, 0, 0, 0,
                               ['good teacher', 'great teacher', 'fantastic teacher']],
                              [14, 'The patrol quickly devolves into ghost stories; everybody is on edge', 'Despite that, you have a successful patrol',
                               'A branch snaps, and the whole patrol runs back to camp', 'p_l quickly silences any talk of ghosts', 40, 10, 2, 0, 0, 0, 1, []],
                              [15, 'r_c admits that they had a vision from StarClan last night', 'The patrol talks them through the vision as they hunt',
                               'The patrol cant make any sense of the vision', 'The patrol does not talk about the vision at all.', 60, 10, 2, 0, 0, 0, 0,
                               ['strong connection to starclan']],
                              [16, 's_c is eager to prove their skill and tries to take charge of the patrol', 's_c is actually a good leader, and the patrol runs smoothly',
                               'The other cats are annoyed by s_c and dont listen', 'The patrol turns back before long', 60, 10, 2, 0, 0, 'ambitious', 1, []],
                              [17, 's_c starts questioning the loyalty of one of their clanmates', 's_c convinces the other cat to stay loyal to the clan',
                               's_c brings it up and the rest of the patrol just feels awkward', 's_c decides to keep such to themselves', 60, 10, 2, 0, 0, 'loyal', 1, []],
                              [18, 's_c sees somebody claiming another cats kill as their own', 's_c talks with the patrol about honesty',
                               's_c brings it up but the other cat denies it', 's_c decides to keep such to themselves', 60, 10, 2, 0, 0, 'righteous', 0, []],
                              [19, 'The patrol starts doubting (deputy)s ability as the clans deputy', '(deputy) performs well in the patrol and quells doubt',
                               'The patrol fails to catch anything, and they blame (deputy)', 'Nobody brings it up again', 60, 10, 2, 'deputy', 0, 0, 1, []],
                              [20, 'The patrol tries to get their leader to tell stories about their warrior days', '(leader)s stories engage the patrol; all have a good time',
                               '(leader)s stories are a bit disappointing', 'The leader declines to tell stories', 60, 10, 2, 'leader', 0, 0, 1, []],
                              [21, 'The patrol finds a young loner near the border, and s_c volunteers to scare them off', 's_cs ferocity frightens the young cat away',
                               's_cs ferocity frightens their clanmates a bit', 'The patrol decides to leave him alone', 60, 10, 2, 0, 0, 'fierce', 1, []],
                              [22, 's_c is nervous about going on patrol', 'The rest of the patrol comfort s_c', 's_cs nerves make them fail a hunt',
                               's_c ends up turning back instead of joining', 60, 10, 2, 0, 0, 'nervous', 1, []],
                              [23, 's_c is worried that their clanmates think theyre a bad hunter', 'The rest of the patrol comfort s_c', 's_cs nerves make them fail a hunt',
                               's_c ends up turning back instead of joining', 60, 10, 2, 0, 0, 'insecure', 1, []],
                              [24, 's_c notices that the patrol isn\'t following the exact rules', 's_c convinces the other cats to follow the rules',
                               's_cs concerns are dismissed by the other cats', 's_c decides to keep such to themselves', 60, 10, 2, 0, 0, 'strict', 0, []],
                              [25, 's_c is the life of the patrol; everybody loves having them there', 'The patrol succeeds and everybody had a good time',
                               's_cs chatting distracts the others from a hunt', 'The patrol decides to focus on hunting instead of on s_c', 60, 10, 2, 0, 0, 'charismatic', 0, []],
                              [26, 'One of the cats get their foot stuck; its up to s_c to stay calm and help', 's_c helps them get unstuck',
                               'Getting the cat out takes so long that the patrol has to turn back without hunting', 'The cat manages to free themselves after a moment', 60, 10, 2,
                               0, 0, 'calm', 0, []], [27, 's_c runs off ahead of the group, craving excitement', 's_c doesnt find anything, and returns to the patrol',
                                                      's_c gets chastised for straying too far', 's_c changes their mind and decides to stick around', 60, 10, 2, 0, 0, 'daring', 1,
                                                      []],
                              [28, 's_c keeps getting distracted, trying to play around', 's_cs playfulness lightens the mood', 'The other cats are annoyed by s_cs distractions',
                               'The patrol more or less ignores s_c', 60, 10, 2, 0, 0, 'playful', 1, []],
                              [29, 's_c finds an old rival rogue of theirs at the border', 's_c attacks the rogue, and drives them away',
                               'The rogue is unimpressed by the patrols attempt to drive him off', 'You decide to not confront that rogue', 60, 10, 2, 0, 0, 'vengeful', 1, []],
                              [30, 's_c spends all patrol talking about their love life', 'The rest of the cats are pleasantly amused by the antics',
                               's_cs talking annoys the other cats', 'The patrol leader tells them to shut up', 60, 10, 2, 0, 0, 'shameless', 1, []],
                              [31, 'One of the other cats on the patrol wants to talk to s_c about StarClan', 's_c has a nice conversation with them about their faith',
                               's_cs blind faith isn\'t quite what the other cat needed right then', 's_c decides to keep such to themselves', 60, 10, 2, 0, 0, 'faithful', 1, []],
                              [32, 's_c seems to be picking on the other cats', 'The rest of the cats manage to ignore s_c', 'The other cats report s_c when they return to camp',
                               's_c gets bored and stops after a bit', 60, 10, 2, 0, 0, 'troublesome', 1, []],
                              [33, 's_c realizes that one of the other cats is worried about something', 's_c comforts them with a nice conversation',
                               'The other cats unease rubs off on s_c', 's_c distances themselves from the other cat', 60, 10, 2, 0, 0, 'empathetic', 0, []],
                              [34, 'The patrol comes upon a strange object that smells strongly of two-legs', 'The patrol interprets the purpose of the object',
                               'After interacting with the object, r_c is nauseous for a couple days', 'The patrol decides to avoid such object', 80, 20, 0, 0, 0, 0, 1,
                               ['smart', 'very smart', 'extremely smart']],
                              [35, 'The patrol comes across a rogue', 'The patrol successfully drives off the rogue', 'The rogue finally leaves, but not before giving r_c a scar',
                               'You decide to not confront that rogue', 120, 25, 0, 0, 0, 0, 1, ['great fighter', 'excellent fighter']],
                              [36, 'The patrol comes across (patrol size) rogues', 'The patrol successfully drives off the rogues',
                               'The rogues finally leave, but not after giving r_c a scar', 'You decide to not confront the rogues', 30, 2, 0, 0, 0, 1, ['excellent fighter']],
                              [37, 'The patrol finds a loner who is interested in joining the clan', 'The patrol convinces the loner to join',
                               'The patrol doesnt quite convince the loner to join', 'You decide to not confront that loner', 80, 10, 0, 0, 0, 0, 1,
                               ['great speaker', 'excellent speaker']],
                              [38, 'p_l comes across a group of four bloodthirsty rogues', 'In a skillful display, p_l chases them away', 'The rogues outnumber p_l and kill them',
                               'p_l knows they are outnumbered and turns away', 70, 30, 1, 0, 0, 0, 1, ['excellent fighter']],
                              [39, 'p_l worries that an apprentice should not be out here alone', 'At least this is a good chance to learn the territory',
                               'The apprentice gets lost and doesnt learn anything', 'p_l turns back to camp, deciding this is a bad idea', 20, 6, 1, 'apprentice', 0, 0, 1,
                               ['very smart', 'extremely smart']],
                              [40, 'The patrol notices new leaves and flowers starting to grow', 'The hunting is plentiful as new prey is born',
                               'Unfortunately, with newleaf comes allergies', 'The patrol is uneventful', 30, 8, 0, 0, 'Newleaf', 0, 0, []],
                              [41, 'The leaves are starting to turn colors; the patrol knows that leaf-bare will be here soon', 'But for now, the hunting is still good.',
                               'A chilly wind makes it difficult to hunt', 'The patrol is uneventful', 30, 8, 0, 0, 'Leaf-fall', 0, 0, []],
                              [42, 'It starts snowing soon after the patrol sets out', 'Despite the cold, the patrol manages to hunt',
                               'The patrol is caught outside in the snow, and doesnt manage to hunt', 'The patrol turns back, waiting until the snow dies down', 30, 8, 0, 0,
                               'Leaf-bare', 0, 0, []],
                              [43, 's_c finds the scent of an old friend of theirs from when they were a loner', 's_c invites their friend to join the clan',
                               's_c and their friend reminisce about old times.', 'The patrol turns back without meeting the other loner.', 20, 10, 0, 0, 0, 'formerly a loner', 1,
                               []], [44, 'The patrol finds a kittypet who is interested in clan cats', 'The patrol convinces the kittypet to join',
                                     'The descriptions of clan cats frighten the kittypet', 'You decide to not confront that kittypet', 80, 10, 0, 0, 0, 0, 1,
                                     ['great speaker', 'excellent speaker']],
                              [45, 'The patrol finds a loner who is interested in joining the clan', 'The loner joins, bringing with them a litter of kits',
                               'The loner thinks for a while, and decides against joining', 'You decide to not confront that loner', 120, 10, 0, 0, 0, 0, 1, ['excellent speaker']],
                              [46, 'r_c admits that they have been training in the Dark Forest', 'The patrol convinces them to stop',
                               'Your patrol doesnt manage to convince them to stop and later r_c is found dead in their nest', 'Your patrol doesnt react to the news', 100, 10, 0,
                               0, 0, 0, 1, ['excellent speaker']],
                              [47, 'There is a large river dividing your territory. Should your patrol cross it?', 'Your patrol crosses the river and can hunt on the other side',
                               'r_c is swept away by the strong current and dies', 'Your patrol decides to avoid the river', 40, 10, 0, 0, 0, 0, 1, ['excellent speaker']],
                              [48, 'Your patrol sees a large rabbit, but it is just over the border', 'Your patrol manages to catch the rabbit without the enemy clan noticing',
                               'Your patrol is caught by enemy warriors', 'Your patrol doesnt attempt to catch the rabbit', 50, 10, 0, 0, 0, 0, 1, ['fantastic hunter']],
                              [49, 'The smell of food lures r_c close to a twoleg trap', 'The patrol leads r_c away before it goes off',
                               'r_c is caught in the trap and is taken by twolegs shortly after', 'r_c loses interest and walks back to the patrol', 60, 10, 0, 0, 0, 0, 1,
                               ['smart', 'very smart', 'extremely smart']], [50, 'The patrol is helping gather herbs and r_c stumbles upon a bush of red berries',
                                                                             'The patrol tells r_c to stay away from the death berries just in time',
                                                                             'r_c chews some of the berries and dies', 'r_c decides to not touch the berries', 40, 10, 0, 2, 0, 0,
                                                                             1, ['great teacher', 'fantastic teacher']],
                              [51, 'The patrol approaches a deep ravine. There is a lot of prey here, but the ground is very slippery.', 'The patrol has a very successful hunt',
                               'While hunting, r_c slips and falls into the ravine, never to be seen again', 'The patrol decides to hunt elsewhere', 50, 10, 0, 0, 0, 0, 1,
                               ['great hunter', 'fantastic hunter']],
                              [52, 'The patrol runs into a small dog.', 'They manage to scare it back to its twolegs.', 'The dog\'s barking scares away the prey',
                               'The patrol decides to avoid the dog', 120, 10, 0, 0, 0, 0, 1, ['great fighter', 'fantastic fighter']],
                              [53, 'r_c notices a suspicious trail of pawprints in the mud',
                               'The pawprints lead them to a trespassing rogue and the patrol chases them off the territory',
                               'Turns out they were following their own pawprints... How embarrassing.', 'r_c decides to ignore the pawprints', 30, 10, 0, 0, 0, 0, 1,
                               ['great fighter']], [54, 'r_c notices a clanmate trapped in some brambles', 'The patrol frees their clanmate',
                                                    'The patrol works all day to free their clanmate and gets nothing done', 'The patrol decides to leave their clanmate alone',
                                                    40, 10, 0, 0, 0, 0, 1, ['great speaker', 'fantastic speaker']],
                              [55, 'r_c is tempted to eat the prey they caught', 'They eat the prey without anyone noticing',
                               'The patrol notices r_c eating the freshkill and report them', 'They decide not to eat the prey', 30, 10, 0, 2, 0, 0, 1,
                               ['great hunter', 'fantastic hunter']],
                              [56, 'The patrol approaches some twoleg dens while hunting', 'The patrol has a successful hunt, avoiding any twolegs',
                               'Twoleg kits chase the patrol away', 'The patrol decides to hunt elsewhere', 30, 10, 0, 0, 0, 0, 1, ['great hunter', 'fantastic hunter']],
                              [57, 'The patrol comes across a badger den', 'The patrol drives the badger off of the territory', 'r_c is killed trying to attack the badger',
                               'The patrol decides to leave the den alone', 50, 10, 0, 0, 0, 0, 1, ['good fighter', 'great fighter', 'fantastic fighter']],
                              [58, 'The patrol comes across a deer', 'The patrol looks in wonder at the strange animal, and continue on their way',
                               'The deer kicks at the cats, giving r_c a scar', 'The patrol turns around, avoiding the deer', 70, 10, 0, 0, 0, 0, 1,
                               ['good speaker', 'great speaker', 'fantastic speaker']],
                              [59, 'The patrol sees a wounded cat near the thunderpath', 'Your patrol brings the wounded cat back to camp and later they join the clan.',
                               'As r_c inspects the cat, they notice they are already hunting with their ancestors', 'They leave the wounded cat alone', 100, 10, 0, 0, 0, 0, 1,
                               ['strong connection to starclan']],
                              [60, 'r_c notices the patrol is not staying on task', 'They manage to steer the patrol back on course', 'The patrol is annoyed by r_c\'s pestering',
                               'They keep their thoughts to themselves', 30, 10, 0, 2, 0, 0, 1, ['good speaker', 'great speaker', 'excellent speaker']],
                              [61, 'r_c spots a rabbit up ahead, but it seems to be acting strange', 'r_c catches the rabbit and it is eaten as normal',
                               'r_c catches the rabbit and later the cats who eat it are violently ill', 'They avoid catching the rabbit', 50, 10, 0, 0, 0, 0, 1,
                               ['good hunter', 'great hunter', 'fantastic hunter']], [62, 'The patrol finds a patch of herbs that they believe the medicine cat mentioned needing',
                                                                                      'They bring the herb back to camp and the herbs are put to good use',
                                                                                      'The herbs turn out to be useless weeds', 'They decide to continue patrolling instead', 30,
                                                                                      10, 0, 0, 0, 0, 1, ['strong connection to starclan', 'great teacher', 'fantastic teacher']],
                              [62, 'r_c goes missing during the patrol', 'r_c is found with an abandoned kit', 'r_c is found laying on the ground injured',
                               'r_c eventually catches up', 50, 10, 0, 2, 0, 0, 1, ['excellent speaker']]]

    # [ ,'','','','', 120, 10, 0, 0, 0, 0, 1, [, '']],

    def event_special(self):
        # special functions for each event defined here
        if self.patrol_event[0] == 5:
            if self.before:
                # stuff that happens during calculations
                return
            else:
                # stuff that happens after the results
                # losing experience
                if not self.success:
                    experience_each = ceil((-10) / int(self.patrol_size) / 2)
                    for i in range(self.patrol_size):
                        self.patrol_cats[i].experience = int(self.patrol_cats[i].experience) + int(experience_each)
                        if self.patrol_cats[i].experience < 0:
                            self.patrol_cats[i].experience = 0
                        if self.patrol_cats[i].experience > 80:
                            self.patrol_cats[i].experience = 80
                        experiencelevels = ['very low', 'low', 'slightly low', 'average', 'somewhat high', 'high', 'very high', 'master', 'max']
                        self.patrol_cats[i].experience_level = experiencelevels[floor(self.patrol_cats[i].experience / 10)]
                return

        if self.patrol_event[0] == 7:
            if self.before:
                # stuff that happens during calculations
                return
            else:
                # stuff that happens after the results
                # left with a scar
                if not self.success:
                    if self.patrol_random_cat.specialty is None:
                        self.patrol_random_cat.specialty = choice([choice(scars1), choice(scars2)])
                    elif self.patrol_random_cat.specialty2 is None:
                        self.patrol_random_cat.specialty2 = choice([choice(scars1), choice(scars2)])
                    return

        if self.patrol_event[0] == 8 or self.patrol_event[0] == 46 or self.patrol_event[0] == 47 or self.patrol_event[0] == 49 or self.patrol_event[0] == 51:
            if self.before:
                # stuff that happens during calculations
                return
            else:
                # stuff that happens after the results
                # cat straight up dies
                if not self.success:
                    events_class.dies(self.patrol_random_cat)
                    return

        if self.patrol_event[0] == 9:
            if self.before:
                # stuff that happens during calculations
                return
            else:
                # disables random cat
                if not self.success:
                    if self.patrol_random_cat.status == 'deputy':
                        game.clan.deputy = None
                    if self.patrol_random_cat.status == 'leader':
                        self.patrol_random_cat.experience = 0
                        self.patrol_result_text = str(self.patrol_random_cat.name) + ' is injured by a Monster and has to relearn everything.'
                    elif game.settings.get('retirement'):
                        self.patrol_random_cat.status_change('elder')
                    self.patrol_random_cat.skill = choice(['paralyzed', 'blind', 'missing a leg'])
                    if self.patrol_random_cat.skill == 'paralyzed':
                        self.patrol_random_cat.paralyzed = True
                    return

        if self.patrol_event[0] == 10:
            if self.before:
                # stuff that happens during calculations
                if int(self.patrol_max_experience) > 49:
                    self.success = True
                return
            else:
                # stuff that happens after the results
                if not self.success:
                    self.patrol_leader.experience = int(self.patrol_leader.experience) - 10
                    if int(self.patrol_leader.experience) < 0:
                        self.patrol_leader.experience = 0
                return

        if self.patrol_event[0] == 11:
            if self.before:
                # stuff that happens during calculations
                return
            else:
                # stuff that happens after the results
                if self.success and not self.intentional_fail:
                    self.other_clan.relations = int(self.other_clan.relations) + 1
                    if int(self.other_clan.relations) == 7:
                        self.patrol_result_text = game.clan.name + 'Clan and ' + self.other_clan.name + 'Clan declare a truce.'
                elif (self.intentional_fail and self.success) or (not self.intentional_fail and not self.success):
                    self.other_clan.relations = int(self.other_clan.relations) - 1
                    if int(self.other_clan.relations) < 1:
                        self.other_clan.relations = 1
                    if int(self.other_clan.relations) == 6:
                        self.patrol_result_text = self.other_clan.name + 'Clan declares war on ' + game.clan.name + 'Clan.'

                if int(self.other_clan.relations) < 7 and not self.success:
                    events_class.dies(self.patrol_random_cat)

                return

        if self.patrol_event[0] == 12:
            if self.before:
                # stuff that happens during calculations
                return
            else:
                # stuff that happens after the results
                if self.success:
                    for i in range(self.patrol_size):
                        if self.patrol_cats[i].status == 'apprentice':
                            self.patrol_cats[i].experience = int(self.patrol_cats[i].experience) + 10
                            if self.patrol_cats[i].experience < 0:
                                self.patrol_cats[i].experience = 0
                            if self.patrol_cats[i].experience > 80:
                                self.patrol_cats[i].experience = 80
                            experiencelevels = ['very low', 'low', 'slightly low', 'average', 'somewhat high', 'high', 'very high', 'master', 'max']
                            self.patrol_cats[i].experience_level = experiencelevels[floor(self.patrol_cats[i].experience / 10)]
                    return

        if self.patrol_event[0] == 14:
            if self.before:
                # stuff that happens during calculations
                return
            else:
                # stuff that happens after the results
                # losing experience
                if not self.success:
                    experience_each = ceil((-6) / int(self.patrol_size) / 2)
                    for i in range(self.patrol_size):
                        self.patrol_cats[i].experience = int(self.patrol_cats[i].experience) + int(experience_each)
                        if self.patrol_cats[i].experience < 0:
                            self.patrol_cats[i].experience = 0
                        if self.patrol_cats[i].experience > 80:
                            self.patrol_cats[i].experience = 80
                        experiencelevels = ['very low', 'low', 'slightly low', 'average', 'somewhat high', 'high', 'very high', 'master', 'max']
                        self.patrol_cats[i].experience_level = experiencelevels[floor(self.patrol_cats[i].experience / 10)]
                return

        if self.patrol_event[0] == 16:
            if self.before:

                # stuff that happens during calculations
                if int(self.patrol_stat_cat.experience) > 39:
                    self.success = True

                return
            else:
                # stuff that happens after the results
                return

        if self.patrol_event[0] == 17:
            if self.before:
                # stuff that happens during calculations
                if self.patrol_stat_cat.skill in ['good speaker', 'great speaker', 'excellent speaker']:
                    self.success = True
                return
            else:
                # stuff that happens after the results
                return

        if self.patrol_event[0] == 19:
            if self.before:

                # stuff that happens during calculations
                if int(game.clan.deputy.experience) > 39:
                    self.success = True

                return
            else:
                # stuff that happens after the results
                return

        if self.patrol_event[0] == 20:
            if self.before:
                # stuff that happens during calculations
                if game.clan.leader.skill in ['good speaker', 'great speaker', 'excellent speaker']:
                    self.success = True
                return
            else:
                # stuff that happens after the results
                return

        if self.patrol_event[0] == 21:
            if self.before:
                # stuff that happens during calculations
                return
            else:
                # stuff that happens after the results
                # losing experience
                if not self.success:
                    experience_each = ceil((-6) / int(self.patrol_size) / 2)
                    for i in range(self.patrol_size):
                        self.patrol_cats[i].experience = int(self.patrol_cats[i].experience) + int(experience_each)
                        if self.patrol_cats[i].experience < 0:
                            self.patrol_cats[i].experience = 0
                        if self.patrol_cats[i].experience > 80:
                            self.patrol_cats[i].experience = 80
                        experiencelevels = ['very low', 'low', 'slightly low', 'average', 'somewhat high', 'high', 'very high', 'master', 'max']
                        self.patrol_cats[i].experience_level = experiencelevels[floor(self.patrol_cats[i].experience / 10)]
                return

        if self.patrol_event[0] == 22 or self.patrol_event[0] == 23:
            if self.before:
                # stuff that happens during calculations
                if self.patrol_stat_cat.skill in ['good hunter', 'great hunter', 'fantastic hunter']:
                    self.success = True
                return
            else:
                # stuff that happens after the results
                # losing experience
                if not self.success:
                    experience_each = ceil((-6) / int(self.patrol_size) / 2)
                    for i in range(self.patrol_size):
                        self.patrol_cats[i].experience = int(self.patrol_cats[i].experience) + int(experience_each)
                        if self.patrol_cats[i].experience < 0:
                            self.patrol_cats[i].experience = 0
                        if self.patrol_cats[i].experience > 80:
                            self.patrol_cats[i].experience = 80
                        experiencelevels = ['very low', 'low', 'slightly low', 'average', 'somewhat high', 'high', 'very high', 'master', 'max']
                        self.patrol_cats[i].experience_level = experiencelevels[floor(self.patrol_cats[i].experience / 10)]
                return

        if self.patrol_event[0] == 27:
            if self.before:
                # stuff that happens during calculations
                return
            else:
                # stuff that happens after the results
                # losing experience
                if not self.success:
                    experience_each = ceil((-6) / int(self.patrol_size) / 2)
                    for i in range(self.patrol_size):
                        self.patrol_cats[i].experience = int(self.patrol_cats[i].experience) + int(experience_each)
                        if self.patrol_cats[i].experience < 0:
                            self.patrol_cats[i].experience = 0
                        if self.patrol_cats[i].experience > 80:
                            self.patrol_cats[i].experience = 80
                        experiencelevels = ['very low', 'low', 'slightly low', 'average', 'somewhat high', 'high', 'very high', 'master', 'max']
                        self.patrol_cats[i].experience_level = experiencelevels[floor(self.patrol_cats[i].experience / 10)]
                return

        if self.patrol_event[0] == 28:
            if self.before:
                # stuff that happens during calculations
                if self.patrol_stat_cat.skill in ['good speaker', 'great speaker', 'excellent speaker']:
                    self.success = True
                return
            else:
                # stuff that happens after the results
                # losing experience
                if not self.success:
                    experience_each = ceil((-6) / int(self.patrol_size) / 2)
                    for i in range(self.patrol_size):
                        self.patrol_cats[i].experience = int(self.patrol_cats[i].experience) + int(experience_each)
                        if self.patrol_cats[i].experience < 0:
                            self.patrol_cats[i].experience = 0
                        if self.patrol_cats[i].experience > 80:
                            self.patrol_cats[i].experience = 80
                        experiencelevels = ['very low', 'low', 'slightly low', 'average', 'somewhat high', 'high', 'very high', 'master', 'max']
                        self.patrol_cats[i].experience_level = experiencelevels[floor(self.patrol_cats[i].experience / 10)]
                return

        if self.patrol_event[0] == 29:
            if self.before:
                # stuff that happens during calculations
                if self.patrol_stat_cat.skill in ['good fighter', 'great fighter', 'excellent fighter']:
                    self.success = True
                return
            else:
                # stuff that happens after the results
                # losing experience
                if not self.success:
                    experience_each = ceil((-6) / int(self.patrol_size) / 2)
                    for i in range(self.patrol_size):
                        self.patrol_cats[i].experience = int(self.patrol_cats[i].experience) + int(experience_each)
                        if self.patrol_cats[i].experience < 0:
                            self.patrol_cats[i].experience = 0
                        if self.patrol_cats[i].experience > 80:
                            self.patrol_cats[i].experience = 80
                        experiencelevels = ['very low', 'low', 'slightly low', 'average', 'somewhat high', 'high', 'very high', 'master', 'max']
                        self.patrol_cats[i].experience_level = experiencelevels[floor(self.patrol_cats[i].experience / 10)]
                return

        if self.patrol_event[0] == 30:
            if self.before:
                # stuff that happens during calculations
                return
            else:
                # stuff that happens after the results
                # losing experience
                if not self.success:
                    experience_each = ceil((-6) / int(self.patrol_size) / 2)
                    for i in range(self.patrol_size):
                        self.patrol_cats[i].experience = int(self.patrol_cats[i].experience) + int(experience_each)
                        if self.patrol_cats[i].experience < 0:
                            self.patrol_cats[i].experience = 0
                        if self.patrol_cats[i].experience > 80:
                            self.patrol_cats[i].experience = 80
                        experiencelevels = ['very low', 'low', 'slightly low', 'average', 'somewhat high', 'high', 'very high', 'master', 'max']
                        self.patrol_cats[i].experience_level = experiencelevels[floor(self.patrol_cats[i].experience / 10)]
                return

        if self.patrol_event[0] == 31:
            if self.before:
                # stuff that happens during calculations
                if self.patrol_stat_cat.skill in ['strong connection to starclan']:
                    self.success = True
                return
            else:
                # stuff that happens after the results
                return

        if self.patrol_event[0] == 32:
            if self.before:
                # stuff that happens during calculations
                return
            else:
                # stuff that happens after the results
                # losing experience
                if not self.success:
                    experience_each = ceil((-10) / int(self.patrol_size) / 2)
                    for i in range(self.patrol_size):
                        self.patrol_cats[i].experience = int(self.patrol_cats[i].experience) + int(experience_each)
                        if self.patrol_cats[i].experience < 0:
                            self.patrol_cats[i].experience = 0
                        if self.patrol_cats[i].experience > 80:
                            self.patrol_cats[i].experience = 80
                        experiencelevels = ['very low', 'low', 'slightly low', 'average', 'somewhat high', 'high', 'very high', 'master', 'max']
                        self.patrol_cats[i].experience_level = experiencelevels[floor(self.patrol_cats[i].experience / 10)]
                return

        if self.patrol_event[0] == 34:
            if self.before:
                # stuff that happens during calculations
                return
            else:
                # stuff that happens after the results
                # losing experience
                if not self.success:
                    experience_each = ceil((-6) / int(self.patrol_size) / 2)
                    for i in range(self.patrol_size):
                        self.patrol_cats[i].experience = int(self.patrol_cats[i].experience) + int(experience_each)
                        if self.patrol_cats[i].experience < 0:
                            self.patrol_cats[i].experience = 0
                        if self.patrol_cats[i].experience > 80:
                            self.patrol_cats[i].experience = 80
                        experiencelevels = ['very low', 'low', 'slightly low', 'average', 'somewhat high', 'high', 'very high', 'master', 'max']
                        self.patrol_cats[i].experience_level = experiencelevels[floor(self.patrol_cats[i].experience / 10)]
                return

        if self.patrol_event[0] == 35 or self.patrol_event[0] == 36 or self.patrol_event[0] == 58 or self.patrol_event[0] == 62:
            if self.before:
                # stuff that happens during calculations
                return
            else:
                # stuff that happens after the results
                # left with a scar
                if not self.success:
                    if self.patrol_random_cat.specialty is None:
                        self.patrol_random_cat.specialty = choice([choice(scars1), choice(scars2)])
                    elif self.patrol_random_cat.specialty2 is None:
                        self.patrol_random_cat.specialty2 = choice([choice(scars1), choice(scars2)])
                    return

        if self.patrol_event[0] == 37 or self.patrol_event[0] == 59 or self.patrol_event[0] == 62:
            if self.before:
                # stuff that happens during calculations
                return
            else:
                # stuff that happens after the results
                if self.success and not self.intentional_fail:
                    new_cat_status = choice(['warrior', 'warrior', 'warrior', 'warrior', 'warrior', 'warrior', 'apprentice', 'apprentice', 'apprentice', 'elder'])
                    if self.patrol_event[0] == 62:
                        new_cat_status = 'kitten'
                    kit = Cat(status=new_cat_status)
                    if randint(0, 2) == 0 and self.patrol_event[0] != 62:
                        kit.name.suffix = ""
                    game.clan.add_cat(kit)
                    kit.skill = 'formerly a loner'
                    kit.thought = 'Is looking around the camp with wonder'
                    self.patrol_cats.append(kit)
                return

        if self.patrol_event[0] == 38 or self.patrol_event[0] == 57 or self.patrol_event[0] == 50:
            if self.before:
                # stuff that happens during calculations
                return
            else:
                # stuff that happens after the results
                # cat straight up dies
                if not self.success:
                    events_class.dies(self.patrol_random_cat)
                    return

        if self.patrol_event[0] == 39:
            if self.before:
                # stuff that happens during calculations
                return
            else:
                # stuff that happens after the results
                # losing experience
                if not self.success:
                    experience_each = ceil((-6) / int(self.patrol_size) / 2)
                    for i in range(self.patrol_size):
                        self.patrol_cats[i].experience = int(self.patrol_cats[i].experience) + int(experience_each)
                        if self.patrol_cats[i].experience < 0:
                            self.patrol_cats[i].experience = 0
                        if self.patrol_cats[i].experience > 80:
                            self.patrol_cats[i].experience = 80
                        experiencelevels = ['very low', 'low', 'slightly low', 'average', 'somewhat high', 'high', 'very high', 'master', 'max']
                        self.patrol_cats[i].experience_level = experiencelevels[floor(self.patrol_cats[i].experience / 10)]
                return

        if self.patrol_event[0] == 43:
            if self.before:
                # stuff that happens during calculations
                return
            else:
                # stuff that happens after the results
                if self.success and not self.intentional_fail:
                    kit = Cat(status='warrior')
                    game.clan.add_cat(kit)
                    kit.skill = 'formerly a loner'
                    if randint(0, 1):
                        kit.name.suffix = ""
                    kit.thought = 'Is looking around the camp with wonder'
                    self.patrol_cats.append(kit)

        if self.patrol_event[0] == 44:
            if self.before:
                # stuff that happens during calculations
                return
            else:
                # stuff that happens after the results
                if self.success and not self.intentional_fail:
                    new_cat_status = choice(['warrior', 'warrior', 'warrior', 'warrior', 'warrior', 'warrior', 'apprentice', 'apprentice', 'apprentice'])
                    kit = Cat(status=new_cat_status)
                    game.clan.add_cat(kit)
                    kit.skill = 'formerly a kittypet'
                    kit.thought = 'Is looking around the camp with wonder'
                    self.patrol_cats.append(kit)
                    if randint(0, 1):
                        kit.specialty2 = choice(scars3)
                    if randint(0, 1):
                        kit.name.prefix = choice(kit.name.loner_names)
                        if randint(0, 2) > 0:
                            kit.name.suffix = ""
                return

        if self.patrol_event[0] == 45:
            if self.before:
                # stuff that happens during calculations
                return
            else:
                # stuff that happens after the results
                if self.success and not self.intentional_fail:
                    new_cat_status = choice(['warrior', 'warrior', 'warrior', 'warrior', 'warrior', 'warrior', 'warrior', 'warrior', 'warrior', 'warrior', 'medicine cat'])
                    kit = Cat(status=new_cat_status)
                    game.clan.add_cat(kit)
                    kit.skill = 'formerly a loner'
                    kit.thought = 'Is looking around the camp with wonder'
                    self.patrol_cats.append(kit)
                    kits = choice([2, 2, 2, 3])
                    for new_kit in range(kits):
                        new_kit = Cat(parent1=kit.ID, moons=0)
                        new_kit.thought == 'Wonders where they are'
                        game.clan.add_cat(new_kit)

                return


patrol = Patrol()
