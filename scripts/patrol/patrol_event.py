#!/usr/bin/env python3
# -*- coding: ascii -*-
from typing import List, Union
from scripts.patrol.patrol_outcome import PatrolOutcome


class PatrolEvent:

    def __init__(self,
                patrol_id,
                biome: List[str] = None,
                season: List[str] = None,
                types: List[str] = None,
                tags: List[str] = None,
                weight: int = 20,
                patrol_art: Union[str, None] = None,
                patrol_art_clean: Union[str, None] = None,
                intro_text: str = "",
                decline_text: str = "",
                chance_of_success=0,
                success_outcomes: List[PatrolOutcome] = None,
                fail_outcomes: List[PatrolOutcome] = None,
                antag_success_outcomes: List[PatrolOutcome] = None,
                antag_fail_outcomes: List[PatrolOutcome] = None,
                min_cats=1,
                max_cats=6,
                min_max_status: dict = None,
                relationship_constraints: List[str] = None,
                pl_skill_constraints: List[str] = None,
                pl_trait_constraints: List[str] = None):
        
        self.patrol_id = patrol_id
        self.weight = weight
        self.types = types if types is not None else []
        
        self.patrol_art = patrol_art
        self.patrol_art_clean = patrol_art_clean
        self.biome = biome if biome is not None else ["Any"]
        self.season = season if season is not None else ["Any"]
        self.tags = tags if tags is not None else []
        self.intro_text = intro_text
        
        self.success_outcomes = success_outcomes if success_outcomes is not None \
                                else []
        self.fail_outcomes = fail_outcomes if fail_outcomes is not None else []
        self.decline_text = decline_text
        self.chance_of_success = chance_of_success  # out of 100
        self.min_cats = min_cats
        self.max_cats = max_cats
        self.antag_success_outcomes = antag_success_outcomes if antag_success_outcomes \
                                      is not None else []
        self.antag_fail_outcomes = antag_fail_outcomes if antag_fail_outcomes \
                                   is not None else []
        self.relationship_constraints = relationship_constraints if relationship_constraints \
                                              is not None else []
        self.pl_skill_constraints = pl_skill_constraints if pl_skill_constraints is not None else []
        self.pl_trait_constraints = pl_trait_constraints if pl_trait_constraints is not None else []
        self.min_max_status = min_max_status if min_max_status is not None else {}

    @property
    def new_cat(self) -> bool:
        """Returns boolian if there are any outcomes that results in 
            a new cat joining (not just meeting)"""
        
        for out in self.success_outcomes + self.fail_outcomes + \
             self.antag_fail_outcomes + self.antag_success_outcomes:
            for sublist in out.new_cat:
                if "join" in sublist:
                    return True
                
        return False
    
    @property
    def other_clan(self) -> bool:
        """Return boolian indicating if any outcome has any reputation effect"""
        for out in self.success_outcomes + self.fail_outcomes + \
             self.antag_fail_outcomes + self.antag_success_outcomes:
            if out.other_clan_rep is not None:
                return True
            
        return False
        
# ---------------------------------------------------------------------------- #
#                              GENERAL INFORMATION                             #
# ---------------------------------------------------------------------------- #

"""
New experimental patrol format:

The idea for this new format is to make this more like a proper "tree", with 
more vesible outcomes. 

What's in a patrol?

"patrol_id": str - the unique string ID of a patrol
"biome": list - which biome can this patrol occur in
"season": list - which seasons the patrol occurs in
"type": list - which type(s) of patrol is this? Also option for "general", and "all"
"tags": list - list of strings ONLY FOR THINGS THAT ARE NEEDED IN THE PATROL FILTERING PROCESS. Right now, only "new_cat"
"min_cats": int
"max_cats": int
"weight": int - NEW!! This will weight the patrol when it's being chosen, allowing some patrols to be
                less common than others. Common is ~20. 
"into_text": str - into text
"decline_text": str - decline text
"chance_of_success: int

# Big change - how things status is determined, to move these out of tags. 
# These are optional. If not included, no constaints are placed. 
"min_max_status" {
    "warrior", [1, 4],
    "leader", [1, 1],
    "apprentice": [2, 3],
}

:: Also option. Restricts the patrols
"pl_rc_relationship_containts": ["list of relationship containts" ]
"pl_skill_containts": [list of skill constaints]
"pl_trait_constaints: [list of trait constaints]

# Buggest change in success outcomes and fail outcomes. More tree-like
# more outcome veritlity, less relience on tags to determine outcome behavior. 

"success_outcomes : [
    {
        
        ::following are nessesary!::
        
        "text": str - the displayed text. 
        "weight": int - The weight of this outcome during outcome determination. 
        "exp": int - the amount of EXP gained in this outcome. 
        
        ::optional, allow more outcome control::
        
        :: Including anything in either of these makes this a stat outcome ::
        "stat_trait": [list, of, traits] 
        "stat_skill": [list, of, skill, strings]
        "can_have_stat": ["p_l", "r_c", "app1" ]
        
        :: Including any of these makes this a death or injury outcome
        :: A outcome can be both. If either death or injury is given, 
        :: make sure history text is also included. 
        "dead_cats": [various, strs, telling, which, cats, should die]
        "injury: {
            "cats": [list of cats]
            "injury": [list of injury],
            "scars" [list of scars]
        }
        "lost_cats": [list, of cats]
        "history_text": {
            "reg_death": "",
            "lead_death: "",
            "scar": "",
        }
        
        
        :: New Cat Block. Including this makes this
        :: outcome a new_cat outcome.
        "new_cat": [
            [ details for new_cat block, includeing "meet" or "join" ],
            [  ],
            [  ]
        ]
        
        ::Resources Block
        "herbs": []
        "prey": []
        
        :: Relationships block
        "outsider_rep": int (-2, -1, 0, 1, 2) IE, gain, neutral or lose. 
        "other_clan_rep": int (-2, 1, 0, 1, 2) IE, gain, neutral or lose
        "relationship" [
            {
                :: at least two ::
                cat_from: str
                cat_to: [list]
                type: str: "normal", "two-way", "all-way"
                value: "jeliousy"
                amount: "amount"
                log: "optional relationship log entry"
            }
        ]
        
        :: relationship_containts - works the same as the containts for the whole patrol. 
        relationship_containts: list[str]
        
        
        
        
    }
]





"""


"""

OLD
    hunting patrols - "hunting", "small_prey", "medium_prey", "large_prey", "huge_prey"

    training patrols - "training",

    border patrols - "border", "other_clan", "reputation",

    med patrols - "med_cat", "herb", "random_herbs", "many_herbs#"

    un-used for now - "npc", "gone_cat"
            
    death and gone tags -
    "death", "disaster", "multi_deaths", "no_body", "cruel_season", "gone", "multi_gone", "disaster_gone",

    relationship tags - 
    "romantic", "platonic", "comfort", "respect", "trust", "dislike", "pos_dislike", "jealous", "pos_jealous", "distrust", "disrespect",
    "apprentice", "two_apprentices", "three_apprentices", "warrior", "no_app", "med_only", "no_leader",
    "no_deputy", "leader", "deputy",

    "clan_to_p_l", "clan_to_r_c", "patrol_to_p_l", "patrol_to_r_c",
    "rel_two_apps", "p_l_to_r_c", "s_c_to_r_c", "clan_to_patrol", "rel_patrol",
    "sacrificial", "pos_fail", "no_change_fail", "no_change_success", "big_change",
    "all_lives", "some_lives"

    relationship constraint - 
    "siblings", "mates", "parent/child", "child/parent",
    "romantic_NUMBER", "platonic_NUMBER", "dislike_NUMBER", "comfortable_NUMBER", "jealousy_NUMBER", "trust_NUMBER"

"""

# ! Patrol Notes
"""
-- success outcomes -- 
    "unscathed_common": 
    "unscathed_rare":
    "stat_skill": 
    "stat_trait":

-- fail outcomes -- 
    "unscathed_common": 
    "unscathed_stat": 
    "death": 
    "injury": 
    "stat_death": 
    "stat_injury": 
    "leader_death":

-- history text -- 
    History text[0] is scar text
    History text[1] is death text for normal cats
    History text[2] is death text for leaders
        
-- PATROL ABBREVIATIONS --
    Clan name - c_n
    Other Clan name - o_c_n
    Random cat - r_c
    Patrol leader - p_l
    Stat Cat - s_c (this is the cat with relevant skills/traits for the situation)
    Apprentice 1 - app1
    Apprentice 2 - app2
    Apprentice 3 - app3 
    Apprentice 4 - app4 
    Apprentice 5 - app5 
    Apprentice 6 - app6 
    Random cat 2 - r_c2
    Random cat 3 - r_c3
    Random cat 4 - r_c4
    Random cat 5 - r_c5

-- PATROL ID GUIDELINES --
    ID format: biome_type_descriptor 
        
    biomes:
    Forest - fst
    Plains - pln
    Mountainous - mtn
    Beach - bch
    Wetlands - wtlnd
    Desert - dst
    If no specific biome - gen
    If it needs multiple biomes, but not all biomes, then create dupe patrols in relevant biomes with appropriate 
    patrol IDs
        
    types:
    Hunting - hunt
    Border - bord
    Training - train
    Med Cat - med
    If no specific type, pick one bc they gotta be categorized somewhere.  Make dupes in each type if you feel like 
    they all apply or some apply.

    descriptors:
    Descriptors should be one word and a number, starting at 1 and incrementing up (i.e. mtn_hunt_mouse1 then 
    mtn_hunt_mouse2 for another patrol involving a mouse. If you then make a new patrol that is not mouse 
    related, choose a different descriptor word and start over again at 1) try to keep descriptor words unique from 
    other descriptors being used to make identification and sorting easier. 

-- RELATIONSHIP CONSTRAINT:
    This is an optional constraint, if you use this, all cats in the patrol has to have these relation.
    If there are multiple 'tags', all 'tags' will be be used for the filtering.

    general:
    "sibling", "mates"
    "parent/child" -> patrol leader is parent, random cat is child
    "child/parent" -> patrol leader is child, random cat is parent

    'thresholds':
    for a 'threshold' tag, you only have to add the value type and then a number.
    !ALL! relationship values of each cat to each other has to have these values or higher
    "romantic_NUMBER",
    "platonic_NUMBER",
    "dislike_NUMBER",
    "comfortable_NUMBER",
    "jealousy_NUMBER",
    "trust_NUMBER"

    NUMBER has to be replaced with a number -> e.g. "romantic_10"


-- TAG INFO: --
    You can ONLY have one of these:
    "death" (r_c dies), "disaster" (all die), "multi_deaths" (2-4 cats die)
    If you have more than one, it takes the first one in this order.
    same for: "gone" (r_c leaves the clan), "disaster_gone" (all leave the clan), "multi_gone" (2-4 cats leave the clan)

    #!FOR INJURIES, SEE CONDITIONS LIST FOR TAGGING
    Tag all injury patrols that should give a scar with "scar" to ensure that classic mode will still scar the cat.
    If you'd like a patrol to have an injury from one of the injury pools, tag with the pool name
    -- Possible Pools --
        "battle_injury": ["claw-wound", "bite-wound", "mangled leg", "mangled tail", "torn pelt"],
        "minor_injury": ["sprain", "sore", "bruises", "scrapes"],
        "blunt_force_injury": ["broken bone", "paralyzed", "head damage", "broken jaw"],
        "hot_injury": ["heat exhaustion", "heat stroke", "dehydrated"],
        "cold_injury": ["shivering", "frostbite"],
        "big_bite_injury": ["bite-wound", "broken bone", "torn pelt", "mangled leg", "mangled tail"],
        "small_bite_injury": ["bite-wound", "torn ear", "torn pelt", "scrapes"]
        "beak_bite": ["beak bite", "torn ear", "scrapes"]
    If you want to specify a certain condition, tag both with "injury" and the condition
    If you want to injure all the cats in the patrol, tag with "injure_all"
    This will work with any condition whether they are an illness, injury, or perm condition
    If you want to ensure that a cat cannot die from the condition, tag with "non_lethal"
    Keep in mind that minor injuries are already non lethal by default and permanent conditions will not be affected by this tag.
    These tags will stack! So you could tag a patrol as "blunt_force_injury", "injury", "water in their lungs" to give all the 
    conditions from blunt_force_injury AND water in their lungs as possible conditions for that patrol. 
    Keep in mind that the "non_lethal" tag will apply to ALL the conditions for that patrol.
    Right now, nonlethal shock is auto applied to all cats present when another cat dies. This may change in the future.

    ! To tag injuries/illnesses on cats joining, you MUST use "new_cat_injury"
    You can choose from these:
        "nc_blunt_force_injury": ["broken bone", "broken back", "head damage", "broken jaw"],
        "nc_sickness": ["greencough", "redcough", "whitecough", "yellowcough"],
        "nc_battle_injury": ["claw-wound", "mangled leg", "mangled tail", "torn pelt", "bite-wound"],
        "nc_hot_injury": ["heat exhaustion", "heat stroke", "dehydrated"],
        "nc_cold_injury": ["shivering", "frostbite"]

    or you can tag a specific injury like this: "nc_broken back"

    - HERB TAGGING: -
        herbs are given on successes only
        "random_herbs" <give a random assortment of herbs
        
        "herbs" < use to mark that this patrol gives a specific herb, use in conjunction with a herb tag. 
        
        Herb tags:
        reference herbs.json, you can use any herb name listed there
        
        "many_herbs#" < to cause the patrol to give a large number of herbs automatically. Numbering starts at 0. 
        Replace the # with the outcome number (i.e. if you want success[2] - which is the skill success - to give lots of herbs, then 
        use "many_herbs2")
        
        "no_herbs#" < to cause the patrol to give no herbs on a certain outcome, while still giving herbs on other 
        outcomes. Numbering starts at 0. Replace the # with the outcome number (i.e. if you want success[2] - which is the skill 
        success - to give no herbs, then use "no_herbs2")

    - TO SPECIFY -
        "one_apprentice" is for patrols with one apprentice in them. It works with the "apprentice" tag. 
        "two_apprentices" is for patrols with two apprentices in them. It works with the "apprentice" tag. 
        "three_apprentices" is for patrols with two apprentices in them. It works with the "apprentice" tag. 
        "four_apprentices" is for patrols with two apprentices in them. It works with the "apprentice" tag. 
        "five_apprentices" is for patrols with two apprentices in them. It works with the "apprentice" tag. 
        "six_apprentices" is for patrols with two apprentices in them. It works with the "apprentice" tag. 

        "rel_two_apps" is for patrols with relationship changes between app1 and app2 that don't affect the rest of the 
        patrol, and also works with "two_apprentices" (or any of the higher numbered apprentice specifiers) and "apprentice".

        "warrior" is used to specify that the patrol should only trigger with at least 1 warrior in it. 
        "no_app" is for when no apps should be on the patrol

    - RELATIONSHIP TAGS -
        I think all of these can be used together. the tag for which relationships are increased should ALSO be used
        # whole Clan gains relationship towards p_l - "clan_to_p_l"
        # whole Clan gains relationship towards s_c - "clan_to_r_c" (triggers to be s_c if s_c is present)
        # whole Clan gains relationship towards r_c - "clan_to_r_c"
        # patrol gains relationship towards p_l - "patrol_to_p_l"
        # patrol gains relationship towards s_c - "patrol_to_r_c" (triggers to be s_c if s_c is present)
        # patrol gains relationship towards r_c - "patrol_to_r_c"
        # "p_l_to_r_c" is for specifically pl and rc gaining relationship with EACH OTHER
        # two apps gain relationship towards each other - "rel_two_apps"
        # whole Clan gains relationship towards patrol - "clan_to_patrol"
        # whole patrol gains relationship with each other - "rel_patrol" 
        (also default, so if you don't add any other tags, it goes to this. If you want this outcome, 
        you don't need to add any tags, this is just if you need to add one of the other tags)
        
        "romantic" < change romantic value
        "platonic" < change platonic value
        "comfort" < change comfort value
        "respect" < change admiration/respect value
        "trust" < change trust value
        "dislike" < change dislike value (decrease on success, increase on fail)
        "pos_dislike" < change dislike value (increase on success, decrease on fail)
        "jealous" < change jealousy value (decrease on success, increase on fail)
        "pos_jealous" < change jealous value (increase on success, decrease on fail)
        "distrust" < always decrease trust
        "disrespect" < always decrease respect
        
        ^^^ On a success, the above tagged values will increase (or if values are dislike and jealousy, 
        they will decrease).  On a fail, the tagged values will decrease (or if values are dislike and jealousy, they will increase)
        
        "sacrificial" is for fail outcomes where a cat valiantly sacrifices themselves for the Clan 
        (such as the single cat big dog patrol) this will give the tagged for group ("clan_to_r_c", "patrol_to_r_c", etc) 
        a big boost to respect and trust in that cat even though they failed (if the cat survives lol) Other tagged for values 
        will be disregarded for these fail outcomes.
        "pos_fail" is for if you want the tagged relationship values to still be positive on a failure, rather than negative.
        
        "big_change" is for if you want the values to increment by a larger number.  This will make all tagged relationship values change by 10 instead of 5
        
        "no_change_fail" to set all relationship value changes to 0 on fail outcomes
        "no_change_success" to set all relationship value changes to 0 on success outcomes

        "no_change_fail_rep" is for when rep should not change when a new_cat patrol fails

    - PREY TAGS -
        If there is no tag, there will be no prey if the hunt is successful
        There are 4 tag types "small_prey", "medium_prey", "large_prey" and "huge_prey". 
        If you want to differentiate between the success texts how much prey each success will get, you have to use the tag and then add the index of the sentence you want the prey to
        E.g. 3 successful outcome texts -> "small_prey0", "medium_prey1", "medium_prey2"

        There will be auto prey for failed hunts to stop the auto, following tags do not allow auto prey:
        > "no_fail_prey"
        + all disaster tags ("death", "disaster", "multi_deaths", "no_body", "cruel_season", "gone", "multi_gone", "disaster_gone")
        + "poison_clan"

        We want a mix of medium_prey and large_prey under normal conditions.


-- WHEN WRIING --   
        Event text should be kept to 350 characters at the maximum to keep it easily readable and concise.
        History text needs to be written in past tense.
        o_c_n and c_n should use "a" not "an" in front of them

"""
