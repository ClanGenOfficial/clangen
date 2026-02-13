# Thoughts

"Thoughts" are the line of text below a cat's name on their profile. They're meant to signify a current action or line of thinking that the cat is "currently" taking, essentially a snapshot into a cat's day-to-day life.

As such, these can be very personal, silly, or specific! It's a chance to add a lot of additional character to each cat.

However, we also don't give thoughts a ton of room on the profile. 

* Thoughts should be short and sweet, **less than 150 characters**.
* They are sentence fragments, with the cat's name on its profile assumed as the beginning of the sentence.
* They must begin with a capital letter and should have no punctuation at the end.

A valid thought:
`Is giving badger-rides to a kit`

An invalid thought:
`ExampleCat is giving badger-rides to a kit!`

!!! tip
    Within this doc you'll see references to a "main_cat" (`m_c`) and a "random_cat" (`r_c`). The thought will be appearing on the `m_c`'s profile, while the `r_c` will be a randomly chosen cat whom you can optionally include in the thought.

## Directory Structure
The thoughts directory is found in `resources/lang/en/thoughts`. Within this folder, you'll see multiple folders, each one containing a different category of thought.

Within the game, all cats take a new thought each timeskip. However, there are also special events within the game that may "replace" the cat's thought, such as death or exile. Typical timeskip thoughts are found in `while_alive` and `while_dead` (`is_guide` is also timeskip thoughts, but for a specific cat.) The rest of the folders are for those special event thoughts. Each folder contains `json` files of their associated thoughts.

| Directory              | Usage                                                                                                                                                                            | `json` Structure                                                                                                                                                                                                                                                                           |
|------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `is_guide`             | Thoughts that appear for the "guide cat"                                                                                                                                         | Guides can either be in the Dark Forest or StarClan, the guide's current location dictates which of these files their thought is pulled from                                                                                                                                               |
| `on_afterlife_change`  | Thoughts that appear when a dead cat is moved to a different afterlife                                                                                                           | The cat will pull a thought from the file matching their new afterlife                                                                                                                                                                                                                     |
| `on_birth`             | Thoughts that appear after a cat is born                                                                                                                                         | Currently only houses `parent.json`. New parents will pull a thought from this file. If you'd like to add thoughts for the newborn, head to `while_alive/newborn.json`.                                                                                                                    |
| `on_death`             | Thoughts that appear after a cat dies                                                                                                                                            | The cat will pull a thought from the folder matching the afterlife they join. If they're a leader and are only losing a life, they take a thought from `leader_life.json`. If they're *fully* dying, they take a thought from `leader_death.json`. All other cats pull from `general.json` |
| `on_exile`             | Thoughts that appear after a cat is exiled                                                                                                                                       | All cats pull from `general.json`                                                                                                                                                                                                                                                          |
| `on_grief_no_body`     | Thoughts that appear for grieving cats after a cat dies and has no retrievable body                                                                                              | All cats pull from `general.json`                                                                                                                                                                                                                                                          |
| `on_grief_toward_body` | Thoughts that appear for grieving cats after a cat dies and *has* a retreivable body                                                                                             | All cats pull from `general.json`                                                                                                                                                                                                                                                          |
| `on_join`              | Thoughts that appear for a cat who has just joined the Clan                                                                                                                      | All cats pull from `general.json`                                                                                                                                                                                                                                                          |
| `on_lost`              | Thoughts that appear for a cat who has just been lost from the Clan                                                                                                              | All cats pull from `general.json`                                                                                                                                                                                                                                                          |
| `on_meeting`           | Thoughts that appear for a cat who has just met, but not joined, the Clan                                                                                                        | If the cat is part of another Clan, they pull from `clancat.json`, otherwise they pull from `outsider.json`                                                                                                                                                                                |
| `on_rank_change`       | Thoughts that appear for a cat whose rank has just changed. Note that rank changes can happen OUTSIDE of ceremonies, so these thoughts should not reference a ceremony outright. | Cats will pull from the file matching their *current* status. Remember you can use `status_history` constraints to constrain the pool to cats who used to be certain ranks.  All cats will pull from `general.json`                                                                        |
| `while_alive`          | Thoughts that living cats will choose from upon timeskip                                                                                                                         | Cats will pull from the file matching their current status, if a cat is currently lost, they'll pull from the file in `while_lost` which matches with the status they had upon becoming lost. All cats (except newborns) will pull from `general.json`                                     |
| `while_dead`           | Thoughts that dead cats will choose from upon timeskip                                                                                                                           | Cats will pull from the folder matching their current afterlife, and the file matching the status they had upon death. All cats (except newborns) will pull from `general.json`                                                                                                            |

!!! tip
    Within `while_alive` and `while_dead`, thoughts should be placed in `general.json` if they apply to multiple statuses.

## Thought Format

```json
{
    "id": "",
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
            "m_c": false,
            "r_c": false
        }
    },
    "relationship_constraint": [],
    "backstory_constraint": {
        "m_c": [],
        "r_c": []
    },
    "main_status_constraint": [],
    "random_status_constraint": [],
    "main_status_history": [],
    "random_status_history": [],
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

***

### id: str
A unique string used to identify the thought block. Generally, the ID includes the condition, personality, age, and status of the main_cat, as well as the condition, personality, age, and status of any other cat mentioned.

* `paralyzed_gen_to_alive_gen`
* `insecure_apprentice`
* `general_formerclancat_dead_thoughts`

***

### biome: list[str]
Constrains the thought to only occur if a player chooses a specific biome.
> "plains", "beach", "mountainous", "forest",

***

### season: list[str]
Constrains the thought to only occur once the Clan is in a specific season.
> "Newleaf", "Greenleaf", "Leaf-fall", "Leaf-bare",

***

### camp: list[str]
Constrains the thought to only occur if a specific camp type is chosen (IE “camp4”, which is the lake camp in the forest). Furthermore, you can check the image file names of the camps to find the which number they are.
> "camp1", "camp2", "camp3","camp4",

***

### thoughts: list[str]
This is a list of thoughts applicable to the constraints on this thought block. You may include as many or as few thoughts here as you wish, but remember that the constraints will apply to *all* of them. 

Examples:

* "Mewls pitifully for milk" (`gen_dead_newborn`)
* "Wonders if {PRONOUN/m_c/subject} would have gotten the chance to do r_c's first check-up" (`general_med_cat_app_to_dead_starclan_newborn1`)
* "Is wondering if r_c would have been {PRONOUN/m_c/poss} friend" (`kit_dead_kit`)

!!! caution
    Be careful about referencing actions only specific types of cats take! For example, if a thought refers to patrolling, consider if you've adequately constrained the thought to only allow cats who *can* go on a patrol. We don't want kittens talking about their trip to the Gathering!

 ***

### has_injuries: dict[str: list]
Constraints the thought to only occur if m_c (the cat that is thinking the thought) or r_c (the cat that is being thought about) has a certain condition (either illness or injury).

> [Illness Tag List](reference/tag-lists.md#__tabbed_1_3)
>
> [Injury Tag List](reference/tag-lists.md#__tabbed_1_2)

You can additionally use the tag "any" to allow the thought to occur if the cat is experiencing any illness or injury.

***

### perm_conditions: dict[str: var]
Constrains the thought to only occur if m_c (the cat that is thinking the thought) or r_c (the cat that is being thought about) has a certain perm condition. 

> [Permanent Conditions Tag List](reference/tag-lists.md#__tabbed_1_4)
>
> You can additionally use the tag "any" to allow the thought to occur if the cat is experiencing any permanent condition.

The additional constraint `born_with` allows you to constrain whether this thought appears for cats born with a condition (congenital) or not. Not providing the constraint is the same as saying either is acceptable.

!!! note Important
    Be careful when specifying `born_with`. If you force a condition to be congenital when it can never generate as such, the thought will never trigger! The same also applies for forcing a condition to be non-congenital when it is always generated as such.

***

### relationship_constraint: list
Constrains the thought to only occur if m_c and r_c fulfill the tags requirements. You can include any tags in [Relationship Tiers](reference/tag-lists.md#relationship-tiers) and [Interpersonal Relationships](reference/tag-lists.md#interpersonal-relationships).

***

### backstory_constraint: dict[str: list]
Constrains the thought to only occur if m_c or r_c has the specific listed backstory. To find what each backstory describes, you can find more by going to `resources/lang/en/cat/backstories.en.json`.  You can utilize [exclusionary values](reference/index.md#exclusionary-values).

> [Backstory Tag List](reference/tag-lists.md#backstories)

***

### main_status_constraint: list[str] & random_status_constraint: list[str]
Constrains the thought to only happen if m_c or r_c are in a certain role. You can utilize [exclusionary values](reference/index.md#exclusionary-values).

> [Status Tag List](reference/tag-lists.md#__tabbed_2_2)
> 
> You can also use the tag "any" to allow the thought to occur for all roles except "newborns", who shouldn't get any general thoughts, just the ones placed in their specific JSON.

***

### main_status_history: list[str] & random_status_history: list[str]::
Constrains the thought to only happen if m_c or r_c used to have a certain role, but are no longer that role. You can utilize [exclusionary values](reference/index.md#exclusionary-values).

> [Status Tag List](reference/tag-lists.md#__tabbed_2_2)

***

### main_age_constraint: list[str] & random_age_constraint: list[str]:
Constrains the thought to only occur if m_c or r_c are within a certain age group. You can utilize [exclusionary values](reference/index.md#exclusionary-values).

> [Age Tag List](reference/tag-lists.md#__tabbed_2_1)

***

### main_trait_constraint: list[str] & random_trait_constraint: list[str]:
Constrains the thought to only occur if m_c or r_c has a specific trait. You can utilize [exclusionary values](reference/index.md#exclusionary-values).

> [Trait Tag List](reference/tag-lists.md#__tabbed_3_2)

***

### main_skill_constraint: list[str] & random_skill_constraint: list[str]:
Constrains the thought to occur only if m_c or r_c has a specific skill. You can utilize [exclusionary values](reference/index.md#exclusionary-values).

> [Skill Tag List](reference/tag-lists.md#__tabbed_3_1)

***

### random_living_status: list[str] & random_outside_status: list[str]:
Constrains the thought if r_c has a specific place of death (first set of tags) or outside role (second set of tags).

> [Other Status Tag List](reference/tag-lists.md#__tabbed_2_3)

## Examples
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

_Found in `while_dead/unknown_residence/exiled.json`_

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

_Found in `while_alive/deputy.json`_


