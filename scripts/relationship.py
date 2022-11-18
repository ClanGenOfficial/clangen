from random import choice, randint
from .game_essentials import *
import copy

# if another cat is involved
THIRD_RELATIONSHIP_INCLUDED = {
    "charismatic": ['Is convincing (cat 1) that (cat 2) isn\'t so bad once you get to know them'],
    "troublesome": ['Made (cat) and (cat) start an argument'],
    "sneaky": ['Is gossiping about (cat) and (cat)'],
    "like": '(cat) confesses to (cat) that they think they like (cat)',
    "trick": 'Has successfully tricked (cat) into believing a crazy tale about the clan leader'
}

EXILED_CATS = {
    "cat_to": ['Bumped into (cat) at the clan border', 'Caught a glimpse of (cat) from the distance'],
    "cat_from": ['Was wandering near the clan territory and met (cat)'],
    "both":['Ran into (cat) by chance']
}

# IN increase or decrease
NOT_AGE_SPECIFIC = {
    "unfriendly": ['Doesn\'t think that (cat) has been completely honest lately',
                   'Is mocking (cat)', 'Ignores (cat)', 'Is telling jokes about (cat)',
                   'Is spreading a rumour about (cat)'],
    "neutral": ['Complains about (cat)', 'Is telling a story to (cat)', 'Is talking with (cat)',
                'Is sharing prey with (cat)', 'Had a huge argument with (cat)', 'Had a fight with (cat)'],
    "friendly": ['Is sharing tongues with (cat)', 'Has been spending time with (cat) lately'],
    "close": ['Tells (cat) a secret']
}


KITTEN_TO_OTHER = {
    "kitten": {
        "unfriendly": ['Tries to scare (cat)', 'Constantly pulling pranks on (cat)'],
        "neutral": ['Has a mock battle with (cat)', 
                    'Is jealous that (cat) is getting more attention than them',
                    'Plays mossball with (cat)', 'Sticks their tongue out at (cat)',
                    'Is pretending to be (cat)'],
        "friendly": ['Chomps on (cat)\'s ear',
                     'Pretends to be a warrior with (cat)',
                     'Is pretending to ward off foxes with (cat)',
                     'Is pretending to fight off badgers with (cat)',
                     'Is racing (cat) back and forth across the camp clearing'],
        "close": [  'Comes up with a plan to sneak out of camp with (cat)',
                    'Wants to snuggle with (cat)']
    },
    "apprentice": {
        "unfriendly": ['Constantly pulling pranks on (cat)'],
        "neutral": ['Sticks their tongue out at (cat)',
                    'Is hiding under a bush from (cat), but they can\'t stop giggling',
                    'Is pretending to be (cat)', 'Is asking (cat) how babies are made'],
        "friendly": ['Ask (cat) what it\'s like to be a apprentice'],
        "close": ['Wants to snuggle with (cat)']
    },
    "warrior": {
        "unfriendly": ['Constantly pulling pranks on (cat)'],
        "neutral": ['Is biting (cat)\'s tail',
                    'Sticks their tongue out at (cat)', 'Is asking (cat) how babies are made',
                    'Is demanding (cat)\'s attention', 'Is pretending to be (cat)',
                    'Is hiding under a bush from (cat), but they can\'t stop giggling',
                    ],
        "friendly": ['Tells (cat) that they would like to be like them when they grows up'],
        "close": ['Wants to snuggle with (cat)']
    },
    "elder": {
        "unfriendly": ['Constantly pulling pranks on (cat)'],
        "neutral": ['Sticks their tongue out at (cat)', 
                    'Is hiding under a bush from (cat), but they can\'t stop giggling',
                    'Is asking (cat) how babies are made'],
        "friendly": [],
        "close": []
    }
}

APPRENTICE_TO_OTHER = {
    "kitten": {
        "unfriendly": [],
        "neutral": ['Trips over (cat)','Is watching over (cat)'],
        "friendly": ['Train playfully with (cat)','Gave (cat) a trinket they found while out on patrol today'],
        "close": []
    },
    "apprentice": {
        "unfriendly": [],
        "neutral": ['Is frustrated that (cat) won\'t take their duties more seriously',
                    'Has a mock battle with (cat)'],
        "friendly": [],
        "close": []
    },
    "warrior": {
        "unfriendly": [],
        "neutral": ['Is frustrated that (cat) won\'t take their duties more seriously'],
        "friendly": [],
        "close": []
    },
    "elder": {
        "unfriendly": [],
        "neutral": [],
        "friendly": [],
        "close": []
    }
}

WARRIOR_TO_OTHER = {
    "kitten": {
        "unfriendly":['Is scolding (cat)'],
        "neutral": ['Trips over (cat)', 'Had to nip (cat) on the rump because they were being naughty',
                    'Is watching (cat) perform an almost-decent hunting crouch', 
                    'Is watching over (cat)'],
        "friendly": ['Is giving (cat) a badger ride on their back!', 'Hopes that their own kits are as cute as (cat) someday',
                     'Is promising to take (cat) outside of camp if they behave', 'Gave (cat) a trinket they found while out on patrol today',
                     'Is feeling proud of (cat)'],
        "close":['Train playfully with (cat)'],
    },
    "apprentice": {
        "unfriendly": ['Is scolding (cat)'],
        "neutral": ['Is giving advice to (cat)', 'Is watching (cat) perform an almost-decent hunting crouch',
                    'Is telling (cat) about a hunting technique', 'Is giving (cat) a task',
                    'Wishes (cat) would take things more seriously'],
        "friendly": ['Is telling (cat) about their own days as an apprentice', 'Is feeling proud of (cat)'],
        "close": []
    },
    "warrior": {
        "unfriendly": [],
        "neutral": ['Is telling (cat) about a hunting technique',
                    'Is giving (cat) a task','Is frustrated that (cat) won\'t take their duties more seriously',
                    'Sparring with (cat)'],
        "friendly": [],
        "close": ['Just told (cat) a hilarious joke']
    },
    "elder": {
        "unfriendly": [],
        "neutral": [],
        "friendly": [],
        "close": []
    }
}

ELDER_TO_OTHER = {
    "kitten": {
        "unfriendly": ['Is scolding (cat)'],
        "neutral": [],
        "friendly": [],
        "close": []
    },
    "apprentice": {
        "unfriendly": ['Is scolding (cat)', 'Is bossing (cat) around'],
        "neutral": ['Is frustrated that (cat) won\'t take their duties more seriously',
                    'Bestowing wisdom onto (cat)', 'Is asking (cat) to check them for ticks'],
        "friendly": [],
        "close": []
    },
    "warrior": {
        "unfriendly": ['Is scolding (cat)', 'Is bossing (cat) around'],
        "neutral": ['Is frustrated that (cat) won\'t take their duties more seriously',
                    'Bestowing wisdom onto (cat)'],
        "friendly": [],
        "close": []
    },
    "elder": {
        "unfriendly": [],
        "neutral": [],
        "friendly": [],
        "close": []
    }
}

LOVE = {
    "love_interest_only": ['Is developing a crush on (cat)', 'Is admiring (cat) from afar...', 'Is spending a lot of time with (cat)',
                            'Gave a pretty flower they found to (cat)', 'Laughs at bad jokes from (cat)', 
                            'Enjoys the time with (cat) and feels secure', 'Made (cat) laugh again and again',
                            'Ensnares (cat) with a charming smile', 'Go for a nice long walk with (cat)',
                            'Wants to spend the entire day with (cat)'],
    "love_interest": [  'Can\'t seem to stop talking about (cat)', 'Would spend the entire day with (cat) if they could', 
                        'Keeps shyly glancing over at (cat) as the clan talks about kits', 
                        'Is thinking of the best ways to impress (cat)', 'Doesn\'t want (cat) to overwork themselves', 
                        'Is rolling around a little too playfully with (cat)...', 
                        'Is wondering what it would be like to grow old with (cat)', 'Thinks that (cat) is really funny',
                        'Thinks that (cat) is really charming', 'Wants to confess their love to (cat)'],
    "mates": ['Was caught enjoying a moonlit stroll with (cat) last night...']
}

LEADER = {
    "from":{
        "unfriendly": ['Punishes (cat) with extra work'],
        "neutral": [],
        "friendly": [],
        "close": ['Talks with (cat) about difficult decisions', 'Tells (cat) about their last encounter with StarClan']
    },
    "to":{
        "unfriendly": ['Accuses (cat) of being a bad leader'],
        "neutral": [],
        "friendly": [],
        "close": []
    }
}

DEPUTY = {
    "from":{
        "unfriendly": ['Punishes (cat) with extra work', 'Divides (cat) into extra patrols'],
        "neutral": [],
        "friendly": [],
        "close": []
    },
    "to":{
        "unfriendly": ['Thinks they should be deputy instead of (cat)', 'Accuses (cat) of being a bad deputy'],
        "neutral": ['Is tired from (cat) putting them on so many patrols'],
        "friendly": [],
        "close": []
    }
}

MEDICINE = {
    "from":{
        "unfriendly": ['Treats (cat)\'s splinter wound more roughly', 'Gives (cat) bitter herbs on purpose'],
        "neutral": [],
        "friendly": [],
        "close": ['Tells (cat) about their last encounter with StarClan']
    },
    "to":{
        "unfriendly": [],
        "neutral": ['Thought of (cat) on the last patrol and took a rare herb with them'],
        "friendly": ['Escorted (cat) so they could gather herbs'],
        "close": []
    }
}

SPECIAL_CHARACTER = {
    "strange": ['Is following (cat) around', 'Tells (cat) that their pelt looks like a different colour today'],
    "bloodthirsty": ['Talks to (cat) how best to kill prey, very enthusiastic', 'Started a fight with (cat)'],
    "righteous": ['Makes sure (cat) is following the warrior code', 'Has a fight with (cat) about what\'s right'],
    "fierce": [ 'Is not backing down in an argument with (cat)', 
                'Is telling (cat) in great detail how they would protect them from any danger'],
    "nervous": ['Is stuttering while speaking to (cat)'],
    "strict":['Scorns (apprentice) for not catching enough prey'],
    "charismatic": ['Charms (cat)', 'Smiles at (cat) whenever they meet', 'Knows what to say to make (cat) feel better', 
                    'Compliments (cat) for their good disposition'],
    "calm": ['Relaxing with (cat)','Is soothing (cat)\'s irrational thoughts', 'Is helping (cat) calm down'],
    "daring": ['Challenges (cat) to a race'],
    "loving": [ 'Is making sure (cat) knows that they are loved','Is telling (cat) how much they cherish them', 
                'Is purring loudly to comfort (cat)'],
    "playful": ['Is playing tag with (cat)'],
    "cold": ['Hissed at (cat)', 'Tells (cat) to leave them alone', 'Glaring at (cat) from across the camp'],
    "vengeful": ['Thinking about how (cat) wronged them', 'Is watching (cat) scornfully', 'Is glaring daggers at (cat)'],
    "shameless": ['Is asking (cat) to tell them about how good they look'],
    "troublesome": ['Pulled a prank on (cat)', 'Blamed (cat) for their own mistake', 'Won\'t stop bothering (cat)',
                    'Feels bad that they caused a problem for (cat)'],
    "empathetic": [ 'Listening to (elder)\'s woes', 'Is listening to (cat)\'s troubles',
                    'Noticed (apprentice) was struggling, and offered to help them'],
    "adventurous": ['Wants to explore Twoleg place with (cat)', 'Wants to sneak along the border with (cat)', 
                    'Tells (cat) that there\'s so much to see in the world!'],
    "thoughful": [  'Gave (cat) their favorite piece of prey', 'Is being quite considerate with (cat)', 
                    'Took the time to help (apprentice) work through a technique they are struggling with'],
    "compassionate": [  'Curled around (cat) to share warmth', 'Lets (cat) have the last piece of fresh kill', 
                        'Listening to (cat)\'s problems', 'Gives (cat) an item they may like', 
                        'Helps (elder) get around camp'],
    "childish": ['Is hiding behind a bush ready to pounce on (cat)'],
    "confident": ['Is building up (cat)\'s confidence', 'Stands tall when (cat) walks by'],
    "careful": ['Tells (cat) to get their ailment treated as soon as possible', 'Chiding (cat) for being so reckless',
                'Apologized to (cat) for possibly hurting their feelings'],
    "altruistic": ['Let (cat) lean on their shoulder after a recent injury', 'Is poised to help train (apprentice)'],
    "bold": ['Challenged (cat) to spar with them'],
    "patient": ['Watching the shooting stars with (cat)', 
                'Calmly explains hunting techniques to (cat) again for the fourth time today'],
    "sneaky": [ 'Is gossiping about (cat)', 'Is teaching (cat) how to walk without making a sound', 
                'Is showing (cat) how to sneak up on their enemies'],
    "wise": ['Is giving (cat) advice'],
    "cowardly": ['Is hiding from (cat)'],
    "impulsive": [  'Crashes into (cat) while eager for patrol', 'Rejects (cat)\'s advice without letting them finish', 
                    'Interrupts (cat) during a conversation'],
    "tidy": [   'Is annoyed by the mess (cat) made', 'Grooms the grime off (cat)\'s pelt', 
                'Is cross with (cat) for getting dirt all over the fresh-kill pile'],
    "dreamy": ['Talks about dreams with (cat)', 'Gets distracted from conversation with (cat)']
}

# How increasing one state influences another directly: (an increase of one state doesn't trigger a chain reaction)
# increase romantic_love -> decreases: dislike | increases: like, comfortable
# increase like -> decreases: dislike | increases: comfortable
# increase dislike -> decreases: romantic_love, like | increases: -
# increase admiration -> decreases: - | increases: -
# increase comfortable -> decreases: jealousy, dislike | increases: trust, like
# increase jealousy -> decreases: - | increases: dislike
# increase trust -> decreases: dislike | increases: -

# !! DECREASING ONE STATE DOES'T INFLUENCE OTHERS !!

# This defines effect the action has, not every action has to have a effect
INCREASE_HIGH = {
    "from": {
        "romantic_love": ['Is developing a crush on (cat)', 'Is admiring (cat) from afar...', 
                          'Is spending a lot of time with (cat)', 'Gave a pretty flower they found to (cat)',
                          'Can\'t seem to stop talking about (cat)', 'Would spend the entire day with (cat) if they could',
                          'Laughs at bad jokes from (cat)', 'Wants to confess their love to (cat)',
                          'Is rolling around a little too playfully with (cat)...', 'Enjoys the time with (cat) and feels secure',
                          'Was caught enjoying a moonlit stroll with (cat) last night...', 'Wants to spend the entire day with (cat)',
                          'Is wondering what it would be like to grow old with (cat)','Go for a nice long walk with (cat)'
                          ],
        "like": ['Is telling a story to (cat)','Is talking with (cat)','Pretends to be a warrior with (cat)',
                'Is sharing tongues with (cat)', 'Is playing tag with (cat)',
                'Has been spending time with (cat) lately','Just told (cat) a hilarious joke', 'Relaxing with (cat)',
                'Tells (cat) a secret', 'Wants to snuggle with (cat)', 'Curled around (cat) to share warmth',
                'Is making sure (cat) knows that they are loved', 'Is telling (cat) how much they cherish them',
                'Noticed (apprentice) was struggling, and offered to help them','Gave (cat) their favorite piece of prey',
                'Took the time to help (apprentice) work through a technique they are struggling with',
                'Watching the shooting stars with (cat)'],
        "dislike": ['Is mocking (cat)', 'Ignores (cat)', 'Sticks their tongue out at (cat)','Had a huge argument with (cat)',
                    'Had a fight with (cat)', 'Is jealous that (cat) is getting more attention than them',
                    'Constantly pulling pranks on (cat)', 'Started a fight with (cat)', 'Hissed at (cat)',
                    'Tells (cat) to leave them alone', 'Accuses (cat) of being a bad leader', 'Accuses (cat) of being a bad deputy'],
        "admiration": ['Tells (cat) that they would like to be like them when they grows up', 'Train playfully with (cat)',
                        'Sparring with (cat)', 'Is feeling proud of (cat)', 'Compliments (cat) for their good disposition'],
        "comfortable": ['Is telling a story to (cat)','Is sharing prey with (cat)','Tells (cat) a secret',
                        'Is sharing tongues with (cat)', 'Talks with (cat) about difficult decisions',
                        'Just told (cat) a hilarious joke', 'Thinks that (cat) is really funny',
                        'Escorted (cat) so they could gather herbs', 'Is helping (cat) calm down',
                        'Curled around (cat) to share warmth', 'Watching the shooting stars with (cat)',
                        'Talks about dreams with (cat)'],
        "jealousy": ['Is jealous that (cat) is getting more attention than them', 'Thinking about how (cat) wronged them'],
        "trust":['Is talking with (cat)','Tells (cat) a secret','Comes up with a plan to sneak out of camp with (cat)',
                 'Escorted (cat) so they could gather herbs','Let (cat) lean on their shoulder after a recent injury',
                 'Ask (cat) to collect herbs on the next patrol', 'Tells (cat) about their last encounter with StarClan']
    },
    "to": {
        "romantic_love": ['Is spending a lot of time with (cat)', 'Gave a pretty flower they found to (cat)',
                          'Is rolling around a little too playfully with (cat)...', 'Ensnares (cat) with a charming smile',
                          'Was caught enjoying a moonlit stroll with (cat) last night...', 'Makes (cat) laugh again and again',
                          'Go for a nice long walk with (cat)', 'Wants to spend the entire day with (cat)', 'Charms (cat)'],
        "like": ['Is telling a story to (cat)','Is talking with (cat)','Is sharing tongues with (cat)',
                'Is giving (cat) a badger ride on their back!', 'Is promising to take (cat) outside of camp if they behave',
                'Is telling (cat) about a hunting technique',
                'Is sharing tongues with (cat)','Has been spending time with (cat) lately', 'Relaxing with (cat)', 
                'Just told (cat) a hilarious joke', 'Plays mossball with (cat)','Pretends to be a warrior with (cat)',
                'Comes up with a plan to sneak out of camp with (cat)', 'Tells (cat) a secret', 'Laughs at bad jokes from (cat)',
                'Knows what to say to make (cat) feel better', 'Is making sure (cat) knows that they are loved',
                'Is telling (cat) how much they cherish them', 'Is playing tag with (cat)', 'Curled around (cat) to share warmth',
                'Noticed (apprentice) was struggling, and offered to help them', 'Gave (cat) their favorite piece of prey',
                'Took the time to help (apprentice) work through a technique they are struggling with',
                'Lets (cat) have the last piece of fresh kill', 'Gives (cat) an item they may like',
                'Apologized to (cat) for possibly hurting their feelings', 'Watching the shooting stars with (cat)',
                'Calmly explains hunting techniques to (cat) again for the fourth time today'],
        "dislike": ['Is mocking (cat)','Is telling jokes about (cat)','Sticks their tongue out at (cat)',
                    'Is spreading a rumour about (cat)','Tries to scare (cat)','Had a huge argument with (cat)',
                    'Had a fight with (cat)', 'Constantly pulling pranks on (cat)', 'Started a fight with (cat)',
                    'Hissed at (cat)', 'Tells (cat) to leave them alone', 'Accuses (cat) of being a bad leader',
                    'Accuses (cat) of being a bad deputy', 'Punishes (cat) with extra work',
                    'Treats (cat)\'s splinter wound more roughly','Gives (cat) bitter herbs on purpose'],
        "admiration": ['Is promising to take (cat) outside of camp if they behave', 'Is telling (cat) about a hunting technique',
                        'Is giving advice to (cat)','Sparring with (cat)', 'Is showing (cat) how to sneak up on their enemies',
                        'Noticed (apprentice) was struggling, and offered to help them', 'Is giving (cat) advice',
                        'Took the time to help (apprentice) work through a technique they are struggling with',
                        'Calmly explains hunting techniques to (cat) again for the fourth time today',
                        'Is teaching (cat) how to walk without making a sound', 'Thought of (cat) on the last patrol and took a rare herb with them',
                        'Is poised to help train (apprentice)'],
        "comfortable": ['Is telling a story to (cat)','Is sharing prey with (cat)','Tells (cat) a secret', 
                        'Is sharing tongues with (cat)','Is telling (cat) about their own days as an apprentice',
                        'Comes up with a plan to sneak out of camp with (cat)', 'Escorted (cat) so they could gather herbs',
                        'Compliments (cat) for their good disposition', 'Is helping (cat) calm down',
                        'Is listening to (cat)\'s troubles',
                        'Curled around (cat) to share warmth', 'Listening to (cat)\'s problems',
                        'Is building up (cat)\'s confidence', 'Apologized to (cat) for possibly hurting their feelings',
                        'Watching the shooting stars with (cat)','Is giving (cat) advice', 'Grooms the grime off (cat)\'s pelt',
                        'Is soothing (cat)\'s irrational thoughts'],
        "jealousy": [],
        "trust":['Is talking with (cat)','Tells (cat) a secret', 'Escorted (cat) so they could gather herbs',
                'Comes up with a plan to sneak out of camp with (cat)', 'Let (cat) lean on their shoulder after a recent injury',
                'Talks with (cat) about difficult decisions', 'Thought of (cat) on the last patrol and took a rare herb with them',
                'Tells (cat) about their last encounter with StarClan']
    }
}

INCREASE_LOW = {
    "from": {
        "romantic_love": ['Keeps shyly glancing over at (cat) as the clan talks about kits', 'Thinks that (cat) is really charming',
                          'Is thinking of the best ways to impress (cat)'],
        "like": ['Is pretending to ward off foxes with (cat)', 'Is pretending to fight off badgers with (cat)',
                 'Is racing (cat) back and forth across the camp clearing', 'Has a mock battle with (cat)',
                 'Hopes that their own kits are as cute as (cat) someday', 'Is asking (cat) to check them for ticks',
                 'Is hiding behind a bush ready to pounce on (cat)', 'Tells (cat) to get their ailment treated as soon as possible',
                 'Plays mossball with (cat)', 'Is giving (cat) a badger ride on their back!',
                 'Calmly explains hunting techniques to (cat) again for the fourth time today'],
        "dislike": ['Divides (cat) into extra patrols', 'Chiding (cat) for being so reckless'],
        "admiration": ['Is watching (cat) perform an almost-decent hunting crouch', 'Ask (cat) what it\'s like to be a apprentice',
                        'Is admiring (cat) from afar...'],
        "comfortable": ['Is hiding under a bush from (cat), but they can\'t stop giggling', 'Is watching over (cat)',
                        'Bestowing wisdom onto (cat)', 'Is telling (cat) in great detail how they would protect them from any danger',
                        'Is purring loudly to comfort (cat)'],
        "jealousy": [],
        "trust": ['Is asking (cat) how babies are made', 'Wants to explore Twoleg place with (cat)', 'Wants to sneak along the border with (cat)']
    },
    "to": {
        "romantic_love": ['Doesn\'t want (cat) to overwork themselves'],
        "like": ['Is pretending to ward off foxes with (cat)', 'Is pretending to fight off badgers with (cat)',
                 'Is racing (cat) back and forth across the camp clearing', 'Has a mock battle with (cat)', 
                 'Is hiding under a bush from (cat), but they can\'t stop giggling', 'Helps (elder) get around camp',
                 'Gave (cat) a trinket they found while out on patrol today', 'Listening to (elder)\'s woes'],
        "dislike": ['Divides (cat) into extra patrols', 'Chiding (cat) for being so reckless'],
        "admiration": ['Bestowing wisdom onto (cat)'],
        "comfortable": ['Hopes that their own kits are as cute as (cat) someday', 'Smiles at (cat) whenever they meet',
                        'Is purring loudly to comfort (cat)', 'Listening to (elder)\'s woes', 'Is being quite considerate with (cat)'],
        "jealousy": [],
        "trust": ['Wants to explore Twoleg place with (cat)', 'Wants to sneak along the border with (cat)',
                  'Tells (cat) to get their ailment treated as soon as possible']
    }
}


DECREASE_HIGH  = {
    "from": {
        "romantic_love": [],
        "like": ['Is telling jokes about (cat)', 'Whines about (cat)', 'Is tired from (cat) putting them on so many patrols',
                 'Is bossing (cat) around', 'Started a fight with (cat)', 'Has a fight with (cat) about what\'s right',
                 'Hissed at (cat)', 'Tells (cat) to leave them alone', 'Blamed (cat) for their own mistake',
                 'Is cross with (cat) for getting dirt all over the fresh-kill pile'],
        "dislike": [],
        "admiration": ['Is frustrated that (cat) won\'t take their duties more seriously', 'Is annoyed by the mess (cat) made',
                        'Wishes (cat) would take things more seriously', 'Thinks they should be deputy instead of (cat)'],
        "comfortable": ['Is stuttering while speaking to (cat)','Glaring at (cat) from across the camp'],
        "jealousy": [],
        "trust": ['Doesn\'t think that (cat) has been completely honest lately', 'Accuses (cat) of being a bad leader',
                  'Accuses (cat) of being a bad deputy']
    },
    "to": {
        "romantic_love": ['Started a fight with (cat)'],
        "like": ['Is telling jokes about (cat)', 'Started a fight with (cat)', 'Has a fight with (cat) about what\'s right',
                 'Is not backing down in an argument with (cat)', 'Scorns (apprentice) for not catching enough prey',
                 'Hissed at (cat)', 'Tells (cat) to leave them alone', 'Blamed (cat) for their own mistake',
                 'Rejects (cat)\'s advice without letting them finish', 'Is cross with (cat) for getting dirt all over the fresh-kill pile',
                 'Punishes (cat) with extra work'],
        "dislike": [],
        "admiration": ['Is scolding (cat)', 'Rejects (cat)\'s advice without letting them finish'],
        "comfortable": ['Tells (cat) that they\'re pelt looks like a different colour today', 'Is following (cat) around',
                        'Glaring at (cat) from across the camp',
                        'Pulled a prank on (cat)', 'Won\'t stop bothering (cat)','Interrupts (cat) during a conversation',
                        'Gets distracted from conversation with (cat)', 'Is glaring daggers at (cat)',
                        'Gives (cat) bitter herbs on purpose'],
        "jealousy": [],
        "trust": ['Is spreading a rumour about (cat)','Tries to scare (cat)', 'Pulled a prank on (cat)',
                'Has successfully tricked (cat) into believing a crazy tale about the clan leader',
                'Blamed (cat) for their own mistake', 'Is gossiping about (cat)', 'Treats (cat)\'s splinter wound more roughly']
    }
}

DECREASE_LOW = {
    "from": {
        "romantic_love": [],
        "like": ['Is hiding from (cat)', 'Complains about (cat)'],
        "dislike": [],
        "admiration": [],
        "comfortable": ['Chomps on (cat)\'s ear'],
        "jealousy": [],
        "trust": ['Chiding (cat) for being so reckless']
    },
    "to": {
        "romantic_love": [],
        "like": ['Trips over (cat)', 'Divides (cat) into extra patrols', 'Is watching (cat) scornfully'],
        "dislike": ['Feels bad that they caused a problem for (cat)'],
        "admiration": ['Is asking (cat) to tell them about how good they look'],
        "comfortable": ['Is biting (cat)\'s tail', 'Tells (cat) that their pelt looks like a different colour today',
                        'Talks to (cat) how best to kill prey, very enthusiastic',
                        'Makes sure (cat) is following the warrior code',
                        'Crashes into (cat) while eager for patrol'],
        "jealousy": [],
        "trust": ['Trips over (cat)']
    }
}

# weigths of the stat change
DIRECT_INCREASE_HIGH = 12
DIRECT_DECREASE_HIGH = 9
DIRECT_INCREASE_LOW = 7
DIRECT_DECREASE_LOW = 4
INDIRECT_INCREASE = 6
INDIRECT_DECREASE = 3

class Relationship(object):
    def __init__(self, cat_from, cat_to, mates=False, family=False, romantic_love=0, platonic_like=0, dislike=0, admiration=0, comfortable=0, jealousy=0, trust=0, log = []) -> None:        
        self.cat_from = cat_from
        self.cat_to = cat_to
        self.mates = mates
        self.family = family
        self.opposit_relationship = None #link to oppositting relationship will be created later
        self.current_action_str = ''
        self.triggerd_event = False
        self.log = log

        if self.cat_from.is_parent(self.cat_to) or self.cat_to.is_parent(self.cat_from):
            self.family = True
            if platonic_like == 0:
                platonic_like = 30
                comfortable = 15

        if self.cat_from.is_sibling(self.cat_to):
            self.family = True
            if platonic_like == 0:
                platonic_like = 20
                comfortable = 10

        if self.cat_from.mate != None and self.cat_from.mate == self.cat_to.ID:
            self.mates = True
            if romantic_love == 0:
                romantic_love = 20
                comfortable = 20
                trust = 10

        # each stat can go from 0 to 100
        self.romantic_love = romantic_love
        self.platonic_like = platonic_like
        self.dislike = dislike
        self.admiration = admiration
        self.comfortable = comfortable
        self.jealousy = jealousy
        self.trust = trust

    def link_relationship(self):
        """Add the other relationship object to this easly access and change the other side."""
        opposite_relationship = list(filter(lambda r: r.cat_to.ID == self.cat_from.ID , self.cat_to.relationships))
        if opposite_relationship is not None and len(opposite_relationship) > 0:
            self.opposit_relationship = opposite_relationship[0]
        else:
            # create relationship
            relation = Relationship(self.cat_to,self.cat_from)
            self.cat_to.relationships.append(relation)
            self.opposit_relationship =relation
            
    def start_action(self):
        """This function checks current state of relationship and decides which actions can happen."""
        # update relationship
        if self.cat_from.mate == self.cat_to.ID:
            self.mates = True

        if self.opposit_relationship is None:
            self.link_relationship()

        # quick fix for exiled cat relationships
        if self.cat_to.exiled and not self.cat_from.exiled:
            action = choice(EXILED_CATS['cat_to'])
            string_to_replace = '(' + action[action.find("(")+1:action.find(")")] + ')'
            self.current_action_str = action.replace(string_to_replace, str(self.cat_to.name)) 
            game.relation_events_list.append(f"{str(self.cat_from.name)} - {self.current_action_str} (neutral effect)")
            return
        elif self.cat_from.exiled and not self.cat_to.exiled:
            action = choice(EXILED_CATS['cat_from'])
            string_to_replace = '(' + action[action.find("(")+1:action.find(")")] + ')'
            self.current_action_str = action.replace(string_to_replace, str(self.cat_to.name)) 
            game.relation_events_list.append(f"{str(self.cat_from.name)} - {self.current_action_str} (neutral effect)")
            return
        elif self.cat_from.exiled and self.cat_to.exiled:
            action = choice(EXILED_CATS['both'])
            string_to_replace = '(' + action[action.find("(")+1:action.find(")")] + ')'
            self.current_action_str = action.replace(string_to_replace, str(self.cat_to.name)) 
            game.relation_events_list.append(f"{str(self.cat_from.name)} - {self.current_action_str} (neutral effect)")
            return

        # get action possibilities
        action_possibilies = self.get_action_possibilities()

        # check if the action is relevant (action of characters include age in the replacement string)
        action_relevant = False
        action = None
        while not action_relevant:
            action = choice(action_possibilies)
            relevant_ages = action[action.find("(")+1:action.find(")")]
            relevant_ages = relevant_ages.split(',')
            relevant_ages = [age.strip() for age in relevant_ages]

            if len(relevant_ages) == 1 and relevant_ages[0] == 'cat':
                action_relevant = True
            if self.cat_to.age in relevant_ages:
                action_relevant = True
                    
        # change the stats of the relationships
        self_relation_effect = self.affect_relationship(action)
        other_relation_effect = self.opposit_relationship.affect_relationship(action, other=True)

        # broadcast action
        string_to_replace = '(' + action[action.find("(")+1:action.find(")")] + ')'
        self.current_action_str = action.replace(string_to_replace, str(self.cat_to.name))

        actionstring_all = f"{str(self.cat_from.name)} - {self.current_action_str} "
        if self_relation_effect == 'neutral effect':
            self_relation_effect = other_relation_effect
        effect_string =  f"({self_relation_effect})"
        both = actionstring_all+effect_string
        self.log.append(both)
        if len(both) < 100:
            game.relation_events_list.append(both)
        else:
            game.relation_events_list.append(actionstring_all)
            game.relation_events_list.append(effect_string)

    def get_action_possibilities(self):
        """Creates a list of possibles actions of this relationship"""
        # check if opposit_relationship is here, otherwise creates it       
        action_possibilies = copy.deepcopy(NOT_AGE_SPECIFIC['neutral'])

        key = self.cat_to.status
        if key == "senior warrior" or key == "deputy" or\
                key == "leader" or key == "medicine cat":
            key = "warrior"
        
        if key == "medicine cat apprentice":
            key = "apprentice"

        # NORMAL INTERACTIONS
        # check how the relationship is
        relation_keys = ['neutral']
        if self.dislike > 20 or self.jealousy > 20:
            action_possibilies += NOT_AGE_SPECIFIC['unfriendly']
            relation_keys.append('unfriendly')
            # increase the chance for unfriendly behaviour
            if self.dislike > 30:
                relation_keys.append('unfriendly')
        if self.platonic_like > 40 or self.comfortable > 30:
            action_possibilies += NOT_AGE_SPECIFIC['friendly']
            relation_keys.append('friendly')
        if self.platonic_like > 50 and self.comfortable > 40 and self.trust > 30:
            action_possibilies += NOT_AGE_SPECIFIC['close']
            relation_keys.append('close')

        # add the interactions to the posssible ones
        if self.cat_from.status == "kitten":
            for relation_key in relation_keys:
                action_possibilies += KITTEN_TO_OTHER[key][relation_key]
        if self.cat_from.status == "apprentice":
            for relation_key in relation_keys:
                action_possibilies += APPRENTICE_TO_OTHER[key][relation_key]
        if (self.cat_from.status == "warrior" or self.cat_from.status == "senior warrior"):
            for relation_key in relation_keys:
                action_possibilies += WARRIOR_TO_OTHER[key][relation_key]
        if self.cat_from.status == "elder":
            for relation_key in relation_keys:
                action_possibilies += ELDER_TO_OTHER[key][relation_key]

        # STATUS INTERACTIONS
        if self.cat_from.age != 'kitten' and self.cat_to.age != 'kitten':
            if self.cat_from.status == 'leader':
                for relation_key in relation_keys:
                    action_possibilies += LEADER['from'][relation_key]
            if self.cat_to.status == 'leader':
                for relation_key in relation_keys:
                    action_possibilies += LEADER['to'][relation_key]

            if self.cat_from.status == 'deputy':
                for relation_key in relation_keys:
                    action_possibilies += DEPUTY['from'][relation_key]
            if self.cat_to.status == 'deputy':
                for relation_key in relation_keys:
                    action_possibilies += DEPUTY['to'][relation_key]

            if self.cat_from.status == 'medicine cat':
                for relation_key in relation_keys:
                    action_possibilies += MEDICINE['from'][relation_key]
            if self.cat_to.status == 'medicine cat':
                for relation_key in relation_keys:
                    action_possibilies += MEDICINE['to'][relation_key]

        # CHARACTERISTIC INTERACTION
        character_keys = SPECIAL_CHARACTER.keys()
        if self.cat_from.trait in character_keys:
            action_possibilies += SPECIAL_CHARACTER[self.cat_from.trait]

        # LOVE
        if (not self.cat_from.is_potential_mate(self.cat_to, for_love_interest = True) or
            not self.cat_to.is_potential_mate(self.cat_from, for_love_interest = True)):
            return action_possibilies

        # chance to fall in love with some the character is not close to:
        love_p = randint(0,30)
        if self.platonic_like > 30 or love_p == 1 or self.romantic_love > 5:
            # increase the chance of an love event for two unmated cats
            action_possibilies = action_possibilies + LOVE['love_interest_only']
            if self.cat_from.mate == None and self.cat_to.mate == None:
                action_possibilies = action_possibilies + LOVE['love_interest_only']

        if self.opposit_relationship.romantic_love > 20:
            action_possibilies = action_possibilies + LOVE['love_interest_only']

        if self.romantic_love > 25 and self.opposit_relationship.romantic_love > 15:
            action_possibilies = action_possibilies + LOVE['love_interest']

        if self.mates and self.romantic_love > 30 and self.opposit_relationship.romantic_love > 25 :
            action_possibilies = action_possibilies + LOVE['mates']

        return action_possibilies

    def affect_relationship(self, action, other = False):
        """Affect the relationship according to the action."""
        key = 'from'
        if other:
            key = 'to'

        # for easier value change
        number_increase = DIRECT_INCREASE_HIGH
        number_decrease = DIRECT_DECREASE_HIGH
        effect = 'neutral effect'

        # increases
        if action in INCREASE_HIGH[key]['romantic_love']:
            self.romantic_love += number_increase
            effect = 'positive effect'
            # indirekt influences
            self.dislike -= INDIRECT_DECREASE
            self.platonic_like += INDIRECT_INCREASE
            self.comfortable += INDIRECT_INCREASE
        if action in INCREASE_HIGH[key]['like']:
            self.platonic_like += number_increase
            effect = 'positive effect'
            # indirekt influences
            self.dislike -= INDIRECT_DECREASE
            self.comfortable += INDIRECT_INCREASE
        if action in INCREASE_HIGH[key]['dislike']:
            self.dislike += number_increase
            effect = 'negative effect'
            # indirekt influences
            self.platonic_like -= INDIRECT_DECREASE
            self.romantic_love -= INDIRECT_DECREASE
            # if dislike reaced a certain point, and is increased, like will get decrease more
            if self.dislike > 24:
                self.platonic_like -= INDIRECT_DECREASE
                self.romantic_love -= INDIRECT_DECREASE
                self.comfortable -= INDIRECT_DECREASE
                self.trust -= INDIRECT_DECREASE
        if action in INCREASE_HIGH[key]['admiration']:
            self.admiration += number_increase
            effect = 'positive effect'
        if action in INCREASE_HIGH[key]['comfortable']:
            self.comfortable += number_increase
            effect = 'positive effect'
            # indirekt influences
            self.dislike -= INDIRECT_DECREASE
            self.jealousy -= INDIRECT_DECREASE
            self.platonic_like += INDIRECT_INCREASE
            self.trust += INDIRECT_INCREASE
        if action in INCREASE_HIGH[key]['jealousy']:
            self.jealousy += number_increase
            effect = 'negative effect'
        if action in INCREASE_HIGH[key]['trust']:
            self.trust += number_increase
            effect = 'positive effect'
            # indirekt influences
            self.dislike -= INDIRECT_DECREASE

        number_increase = DIRECT_INCREASE_LOW
        if action in INCREASE_LOW[key]['romantic_love']:
            self.romantic_love += number_increase
            if effect == 'neutral effect':
                effect = 'small positive effect'
        if action in INCREASE_LOW[key]['like']:
            self.platonic_like += number_increase
            if effect == 'neutral effect':
                effect = 'small positive effect'
        if action in INCREASE_LOW[key]['dislike']:
            self.dislike += number_increase
            if effect == 'neutral effect':
                effect = 'small negative effect'
            # if dislike reaced a certain point, and is increased, like will get decrease more
            if self.dislike > 24:
                self.platonic_like -= INDIRECT_DECREASE
                self.romantic_love -= INDIRECT_DECREASE
                self.comfortable -= INDIRECT_DECREASE
                self.trust -= INDIRECT_DECREASE
        if action in INCREASE_LOW[key]['admiration']:
            self.admiration += number_increase
            if effect == 'neutral effect':
                effect = 'small positive effect'
        if action in INCREASE_LOW[key]['comfortable']:
            self.comfortable += number_increase
            if effect == 'neutral effect':
                effect = 'small positive effect'
        if action in INCREASE_LOW[key]['jealousy']:
            self.jealousy += number_increase
            if effect == 'neutral effect':
                effect = 'small negative effect'
        if action in INCREASE_LOW[key]['trust']:
            self.trust += number_increase
            if effect == 'neutral effect':
                effect = 'small positive effect'

        # decreases
        if action in DECREASE_HIGH[key]['romantic_love']:
            self.romantic_love -= number_decrease
            effect = 'negative effect'
        if action in DECREASE_HIGH[key]['like']:
            self.platonic_like -= number_decrease
            effect = 'negative effect'
        if action in DECREASE_HIGH[key]['dislike']:
            self.dislike -= number_decrease
            effect = 'positive effect'
        if action in DECREASE_HIGH[key]['admiration']:
            self.admiration -= number_decrease
            effect = 'negative effect'
        if action in DECREASE_HIGH[key]['comfortable']:
            self.comfortable -= number_decrease
            effect = 'negative effect'
        if action in DECREASE_HIGH[key]['trust']:
            self.trust -= number_decrease
            effect = 'negative effect'
        if action in DECREASE_HIGH[key]['jealousy']:
            self.jealousy -= number_decrease
            effect = 'positive effect'

        number_decrease = DIRECT_DECREASE_LOW
        if action in DECREASE_LOW[key]['romantic_love']:
            self.romantic_love -= number_decrease
            if effect == 'neutral effect':
                effect = 'small negative effect'
        if action in DECREASE_LOW[key]['like']:
            self.platonic_like -= number_decrease
            if effect == 'neutral effect':
                effect = 'small negative effect'
        if action in DECREASE_LOW[key]['dislike']:
            self.dislike -= number_decrease
            if effect == 'neutral effect':
                effect = 'small positive effect'
        if action in DECREASE_LOW[key]['admiration']:
            self.admiration -= number_decrease
            if effect == 'neutral effect':
                effect = 'small negative effect'
        if action in DECREASE_LOW[key]['comfortable']:
            self.comfortable -= number_decrease
            if effect == 'neutral effect':
                effect = 'small negative effect'
        if action in DECREASE_LOW[key]['jealousy']:
            self.jealousy -= number_decrease
            if effect == 'neutral effect':
                effect = 'small positive effect'
        if action in DECREASE_LOW[key]['trust']:
            self.trust -= number_decrease
            if effect == 'neutral effect':
                effect = 'small negative effect'

        self.cut_boundries()
        return effect

    def cut_boundries(self):
        """Cut the stats of involved relationships."""
        upper_bound = 100
        lower_bound = 0

        # current_relationship
        self.romantic_love = upper_bound if self.romantic_love > upper_bound else self.romantic_love
        self.romantic_love = lower_bound if self.romantic_love < lower_bound else self.romantic_love
        self.platonic_like = upper_bound if self.platonic_like > upper_bound else self.platonic_like
        self.platonic_like = lower_bound if self.platonic_like < lower_bound else self.platonic_like
        self.dislike = upper_bound if self.dislike > upper_bound else self.dislike
        self.dislike = lower_bound if self.dislike < lower_bound else self.dislike
        self.admiration = upper_bound if self.admiration > upper_bound else self.admiration
        self.admiration = lower_bound if self.admiration < lower_bound else self.admiration
        self.comfortable = upper_bound if self.comfortable > upper_bound else self.comfortable
        self.comfortable = lower_bound if self.comfortable < lower_bound else self.comfortable
        self.trust = upper_bound if self.trust > upper_bound else self.trust
        self.trust = lower_bound if self.trust < lower_bound else self.trust
        self.jealousy = upper_bound if self.jealousy > upper_bound else self.jealousy
        self.jealousy = lower_bound if self.jealousy < lower_bound else self.jealousy

    def special_interactions(self):
        actions_possibilities = []

        # more in dept relationship actions

        return actions_possibilities