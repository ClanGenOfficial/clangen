# Thoughts
_by summoner (clownthoughts)_

This is a very simple guide to adding or editing thoughts within the developmental version of ClanGen.

## Accessing Thoughts
![image](https://github.com/CL0WNTH0UGHTS/Summoners-Clownthoughts-Death-Events/assets/124001594/da21f222-952d-45e8-af74-a2349c16001c)

Thoughts are accessed by going to the resources, dict, and the thought folder. The thought folder contains two separate folders based on whether the cat thinks the thought is alive or dead.

The alive folder contains all thoughts regarding being alive (whether the thinker is inside or outside the clan, like lost cats, kittypets, or rogues). Additionally, the dead folder contains all thoughts regarding being dead in the Dark Forest, StarClan, and the Unknown Residence.

![Screenshot 2024-04-20 060949](https://github.com/CL0WNTH0UGHTS/Summoners-Clownthoughts-Death-Events/assets/124001594/1d57924a-b64f-4b05-821a-06694798c1e2)
![Screenshot 2024-04-20 061018](https://github.com/CL0WNTH0UGHTS/Summoners-Clownthoughts-Death-Events/assets/124001594/7fbe2365-4c8c-4a6c-8aa9-7c94ed86eba9)

## Thought Format

It's essential to know how thoughts are formatted when adding or altering them so that you don't cause errors. The thought format is:

```json
{
    "id": " ",
    "biome": [],
    "season": [],
    "camp": [],
    "thoughts": [],
    "has_injuries": {
        "m_c": [],
        "r_c": []
    },
    "perm_conditions": {
        "m_c": [],
        "r_c": [],
        "born_with": {
            "m_c": bool,
            "r_c": bool
        }
    },
    "relationship_constraint": [],
    "backstory_constraint": {
        "m_c": [],
        "r_c": []
    },
    "main_status_constraint": [],
    "random_status_constraint": [],
    "main_age_constraint": [],
    "random_age_constraint": [],
    "main_trait_constraint": [],
    "random_trait_constraint": [],
    "main_skill_constraint": [],
    "random_skill_constraint": [],
    "random_living_status": [],
    "random_outside_status": []
}
```
!!! note "Important"
    If you do not use a constraint, you can remove it from the thought to make the JSONS less hefty and more readable.

### Tags
Each constraint within a thought has specific tags that limit the thought to occurring only when that constraint is fulfilled (IE, if the tag used is "leaf-bare," then the thought will only have a chance of occurring once the player Clan is in leaf-bare).
***

**ID:**
Separates the thoughts into their blocks. Generally, the ID includes the condition, personality, age, and status of the main_cat, as well as the condition, personality, age, and status of any other cat mentioned.

* paralyzed_gen_to_alive_gen
* insecure_apprentice
* general_formerclancat_dead_thoughts


**BIOME:**
Constrains the thought to only occur if a player chooses a specific biome.
> "plains", "beach", "mountainous", "forest",


**SEASON:**
Constrains the thought to only occur once the Clan is in a specific season.
> "Newleaf", "Greenleaf", "Leaf-fall", "Leaf-bare",


**CAMP:**
Constrains the thought to only occur if a specific camp type is chosen (IE “camp4”, which is the lake camp in the forest). Furthermore, you can check the image file names of the camps to find the which number they are.
> "camp1", "camp2", "camp3","camp4",


**THOUGHTS:**
This is where the text that will be displayed in-game is placed, current abbreviations that work are r_c (for random_cat) and c_n (for player clan name).

* "Mewls pitifully for milk" (gen_dead_newborn)
* "Wonders if {PRONOUN/m_c/subject} would have gotten the chance to do r_c's first check-up" (general_med_cat_app_to_dead_starclan_newborn1)
* "Is wondering if r_c would have been {PRONOUN/m_c/poss} friend" (kit_dead_kit)


**HAS_INJURIES:**            
Constraints the thought to only occur if m_c (the cat that is thinking the thought) or r_c (the cat that is being thought about) has a certain condition (either illness or injury).

> [Illness Tag List](reference/index.md#__tabbed_1_3)
>
> [Injury Tag List](reference/index.md#__tabbed_1_2)

You can additionally use the tag "any" to allow the thought to occur if the cat is experiencing any illness or injury.


**PERM_CONDITIONS:**
Constrains the thought to only occur if m_c (the cat that is thinking the thought) or r_c (the cat that is being thought about) has a certain perm condition. 

> [Permanent Conditions Tag List](reference/index.md#__tabbed_1_4)
>
> You can additionally use the tag "any" to allow the thought to occur if the cat is experiencing any permanent condition.

The additional constraint `born_with` allows you to constrain whether this thought appears for cats born with a condition (congenital) or not. Not providing the constraint is the same as saying either is acceptable.

!!! note Important
    Be careful when specifying `born_with`. If you force a condition to be congenital when it can never generate as such, the thought will never trigger! The same also applies for forcing a condition to be non-congenital when it is always generated as such.

**RELATIONSHIP_CONSTRAINT:**
Constrains the thought to only occur if m_c and r_c fulfill the tags requirements: for the "parent/child" tag, the thinker is the parent, and whoever it's directed towards the child (vise versa with "child/parent"), and the same goes for the "app/mentor" and "mentor/app."
> "siblings", "littermates", "mates", "not_mates", "parent/child", "child/parent",  "app/mentor", "mentor/app", "stranger",


BACKSTORY_CONSTRAINT:
Constrains the thought to only occur if m_c or r_c has the specific listed backstory. To find what each backstory describes, you can find more by going to resources, dicts, then the backstories.json (thank you Tiri and Ryos!)

> [Backstory Tag List](reference/index.md#backstories)

STATUS_CONSTRAINT:
Constrains the thought to only happen if m_c or r_c are in a certain role. 

> [Status Tag List](reference/index.md#__tabbed_2_2)
> 
> You can also use the tag "any" to allow the thought to occur for all roles except "newborns", who shouldn't get any general thoughts, just the ones placed in their specific JSON.

AGE_CONSTRAINT:
Constrains the thought to only occur if m_c or r_c are within a certain age group.

> [Age Tag List](reference/index.md#__tabbed_2_1)

TRAIT_CONSTRAINT:
Constrains the thought to only occur if m_c or r_c has a specific trait.

> [Trait Tag List](reference/index.md#__tabbed_3_2)

**SKILL_CONSTRAINT:**
Constrains the thought to occur only if m_c or r_c has a specific skill.

> [Skill Tag List](reference/index.md#__tabbed_3_1)

**RANDOM_LIVING/OUTSIDE_STATUS:**
Constrains the thought if r_c has a specific place of death (first set of tags) or outside role (second set of tags).

> [Other Status Tag List](reference/index.md#__tabbed_2_3)

## Examples and Notes
Some general notes for thoughts:

* Make sure everything is pronoun tagged before they go into a PR (if PR-ing to the official branch)
* Try to keep the thoughts short, roughly around a 20-25 max word count
* Do not include the name of the "thinker" (or the cat who is experiencing the thought)
* Do not include the "main_status_constraint" unless the thought can apply to multiple roles. If this does occur, the thought will need to be placed in the applicable general.json
* If the thought is unique to one status, put it into its respective .json without the "main_status_constraint" (we only use it, as stated above, if it can apply to multiple roles)
* Try and avoid adding punctuation to the end of a thought (however, this is one of those rules that is "know it before you break it")

Some examples of thoughts include:

    {
        "id": "gen_dead_exiled",
        "thoughts": [
            "Wishes {PRONOUN/m_c/subject} had the chance to fix {PRONOUN/m_c/poss} mistakes while alive",
            "Curses c_n for making {PRONOUN/m_c/object} die alone",
            "Wonders what is happening in StarClan",
            "Regrets not trying to join a different Clan before {PRONOUN/m_c/subject} died",
            "Is wondering if {PRONOUN/m_c/subject} {VERB/m_c/have/has} a purpose anymore",
            "Is thinking bitterly about {PRONOUN/m_c/poss} former Clanmates"
        ],
        "main_status_constraint": [
            "exiled"
        ]
    }

_Found in the dead folder > Unknown Residence folder > exiled.json_

    {
        "id": "fierce_deputy",
        "thoughts": [
            "Is sternly instructing a patrol about the importance of strength in defending the Clan",
            "Feels a rush of adrenaline at the thought of an upcoming battle",
            "Impressed {PRONOUN/m_c/poss} Clanmates by scaring off an intruder"
        ],
        "main_trait_constraint": [
            "fierce"
        ]
    }

_Found in the alive folder > deputy.json_

## Common Errors
### In-Game Text

If, while editing or adding new thoughts to any of the jsons, you boot up the game and notice all of the cats share the same bug message ("Prrp! You shouldn't see this! Report as a bug."), then you've either left an extra comma somewhere within the additions or alterations (also referred to as a trailing comma), removed a comma that was needed, or used a non-ASCII character.

![Screenshot 2024-04-17 082047](https://github.com/CL0WNTH0UGHTS/Summoners-Clownthoughts-Death-Events/assets/124001594/053f58e4-7b2b-4fb7-b2dd-94a2a19cda28)

### Thought not occurring at all
If, while editing or adding thoughts, you notice the thought hasn't appeared once while testing it in game, it could either be really terrible luck or you mis-spelled a constraint tag. If a thought is more 'complex' (IE has more constraints it must meet to appear), then there is less of a chance it will appear. However, if you have a 'simple' thought and it hasn't appeared once, then it could indicate there is a tag misspelling.

![image](https://github.com/CL0WNTH0UGHTS/Summoners-Clownthoughts-Death-Events/assets/124001594/fe6cafee-5204-4c6a-8091-0167a78239b0)
In a quick 10 moon study with a "simple" thought (this one had one constraints), the thought appeared for most moons. However, when I did the same clan within the same amount of cats and with the same thought just having a single misspelled tag, it didn't occur once.

If you think there is an error with the thought not occuring, you best bet is to thoroughly check all the tags over, as even just a simple misspelling (IE any to ny) can cause the thought to glitch out.
