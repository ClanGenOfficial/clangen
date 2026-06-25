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

| Directory              | Usage                                                                                                                                                                            | `json` Structure                                                                                                                                                                                                                                                                                                     |
|------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `is_guide`             | Thoughts that appear for the "guide cat"                                                                                                                                         | Guides can either be in the Dark Forest or StarClan, the guide's current location dictates which of these files their thought is pulled from                                                                                                                                                                         |
| `on_afterlife_change`  | Thoughts that appear when a dead cat is moved to a different afterlife                                                                                                           | The cat will pull a thought from the file matching their new afterlife                                                                                                                                                                                                                                               |
| `on_birth`             | Thoughts that appear after a cat is born                                                                                                                                         | Currently only houses `parent.json`. New parents will pull a thought from this file. If you'd like to add thoughts for the newborn, head to `while_alive/newborn.json`.                                                                                                                                              |
| `on_death`             | Thoughts that appear after a cat dies                                                                                                                                            | The cat will pull a thought from the folder matching the afterlife they join. If they're a leader and are only losing a life, they take a thought from `leader_life.json`. If they're *fully* dying, they take a thought from `leader_death.json`. All other cats pull from `general.json`                           |
| `on_exile`             | Thoughts that appear after a cat is exiled                                                                                                                                       | All cats pull from `general.json`                                                                                                                                                                                                                                                                                    |
| `on_grief_no_body`     | Thoughts that appear for grieving cats after a cat dies and has no retrievable body                                                                                              | All cats pull from `general.json`                                                                                                                                                                                                                                                                                    |
| `on_grief_toward_body` | Thoughts that appear for grieving cats after a cat dies and *has* a retrievable body                                                                                             | All cats pull from `general.json`                                                                                                                                                                                                                                                                                    |
| `on_join`              | Thoughts that appear for a cat who has just joined the Clan                                                                                                                      | All cats pull from `general.json`                                                                                                                                                                                                                                                                                    |
| `on_lost`              | Thoughts that appear for a cat who has just been lost from the Clan                                                                                                              | All cats pull from `general.json`                                                                                                                                                                                                                                                                                    |
| `on_meeting`           | Thoughts that appear for a cat who has just met, but not joined, the Clan                                                                                                        | If the cat is part of another Clan, they pull from `clancat.json`, otherwise they pull from `outsider.json`                                                                                                                                                                                                          |
| `on_rank_change`       | Thoughts that appear for a cat whose rank has just changed. Note that rank changes can happen OUTSIDE of ceremonies, so these thoughts should not reference a ceremony outright. | Cats will pull from the file matching their *current* status. Remember you can use `status_history` constraints to constrain the pool to cats who used to be certain ranks.  All cats will pull from `general.json`                                                                                                  |
| `while_alive`          | Thoughts that living cats will choose from upon timeskip                                                                                                                         | Cats will pull from the file matching their current status, if a cat is currently lost, they'll pull from the file in `while_lost` which matches with the status they had upon becoming lost. All cats (except newborns and lost cats) will pull from `general.json`. Clancats additionally draw from `clancat.json` |
| `while_dead`           | Thoughts that dead cats will choose from upon timeskip                                                                                                                           | Cats will pull from the folder matching their current afterlife, and the file matching the status they had upon death. All cats (except newborns and outsiders) will pull from `general.json`                                                                                                                        |

!!! tip
    Within `while_alive` and `while_dead`, thoughts should be placed in `general.json` if they apply to multiple statuses.

## Thought Format

### Full Format
```json
    {
        "id": "test",
        "location": [],
        "season": [],
        "tags": [],
        "strings": [
            "Is thinking"
        ],
        "involved_cats": {
            "m_c": {
                "status": [],
                "past_status": [],
                "age": [],
                "group": [],
                "standing": {
                    "group": [],
                    "currently": [],
                    "past": []
                  },
                "stat": {
                    "skill": [],
                    "trait": [],
                    "must_have_both": false
                },
                "health": {
                    "working": true,
                    "condition": [],
                    "must_be_congenital": false,
                    "must_be_acquired": false
                },
                "backstory": []
            }
        },
        "relationship_constraint": [
            {
                "cats_from": [],
                "cats_to": [],
                "mutual": false,
                "constraints": []
            }
        ]
    }
```
!!! note "Important"
    If you do not use a constraint, you can remove it from the thought to make the JSONS less hefty and more readable. Check out the below "Minimum Required" to see what parameters are always required.

### Minimum Required
>The smallest amount of information you're required to include in this format. 

```json
{
    "id": "test",
    "strings": [
        "Is thinking"
    ]
}
```

***

### id: str
A unique string used to identify the thought block. Generally, the ID includes the condition, personality, age, and status of the main_cat, as well as the condition, personality, age, and status of any other cat mentioned.

* `paralyzed_gen_to_alive_gen`
* `insecure_apprentice`
* `general_formerclancat_dead_thoughts`

***

### location:list[str]
This controls the biome and camp the event appears in. [Tagging Instructions](reference/tag-lists.md#locations)

***

### season: list[str]
List of seasons in which the event may occur. You can utilize [exclusionary tags](reference/tag-lists.md#exclusionary-tags).
You can tag with a mix of "newleaf", "greenleaf", "leaf-fall", "leaf-bare", or remove the parameter altogether to allow for any season.

***

### tags: list[str]
Used to dictate some odds-and-ends about thought constraints: [General Tags](reference/tag-lists.md#general-tags).

***

### strings: list[str]
This is a list of thoughts applicable to the constraints on this thought block. You may include as many or as few thoughts here as you wish, but remember that the constraints will apply to *all* of them. 

For example:
```json
"strings": [
        "Is wondering what r_c would think of current conflicts in the Clan",
        "Wishes r_c was alive to solve {PRONOUN/m_c/poss} problems",
        "Wonders if r_c is ending arguments in StarClan"
]
```

!!! caution
    Be careful about referencing actions only specific types of cats take! For example, if a thought refers to patrolling, consider if you've adequately constrained the thought to only allow cats who *can* go on a patrol. We don't want kittens talking about their trip to the Gathering!

***

### involved_cats: dict[str: dict]
This dictionary holds all constraints for the cats whom we wish to reference in the thought, including the thinking cat!

Each entry is an individual cat, with the key being their event designation (`r_c`, `m_c`, etc.) and the value being their personal constraints. In thoughts, you are allowed to reference `m_c`, who is the "owner" of the thoughts, and `r_c`, who is a cat being referenced by the thought. Allowed constraints are as follows:

***

**status: list[str]**
>Constrains the thought to only happen if the cat holds a certain role. You can utilize [exclusionary tags](reference/tag-lists.md#exclusionary-tags).

> [Status Tag List](reference/tag-lists.md#__tabbed_2_2)
> 
> You can also remove the parameter to allow the thought to occur for all roles except "newborns", who are only allowed if specifically tagged as such.

***

**past_status: list[str]**
>Constrains the thought to only happen if the cat held a certain role in the past. You can utilize [exclusionary tags](reference/tag-lists.md#exclusionary-tags).

> [Status Tag List](reference/tag-lists.md#__tabbed_2_2)

***
**age: list[str]**
>Constrains the thought to only occur if the cat is within a certain age group. You can utilize [exclusionary tags](reference/tag-lists.md/#exclusionary-tags).

> [Age Tag List](reference/tag-lists.md#__tabbed_2_1)
> 
> You can also remove the parameter to allow the thought to occur for all ages except "newborns", who are only allowed if specifically tagged as such.

***

**group:list[str]**
>Constraints the thought to only happen if the cat is a member of a listed group or a member of no group. you can use tags in: [possible group tags](reference/tag-lists.md#groups) and you can utilize [exclusionary tags](reference/tag-lists.md/#exclusionary-tags).

**standing: dict[str: var]**
>Constrains the thought to only happen if the cat matches with the dictated group standings. A group standing is the relationship between a cat and a group, for example: if they are an exile or lost.

```json
    "standing": {
        "group": [],
        "currently": [],
        "past": []
      },
```
>**`"group"`** - the group we are checking the cat's standing with. you can utilize [exclusionary tags](reference/tag-lists.md/#exclusionary-tags). tags can be mixed and matched as necessary. if multiple tags are used, the cat will only need to qualify against *one* of the groups. [possible group tags.](reference/tag-lists.md#groups). You should not try to tag `no_group`.

>**`"currently"`** - the standing the cat should currently possess with this group. tags can be mixed and matched as necessary. if multiple tags are used, the cat will only need to have *one* of the standings. [possible standing tags.](reference/tag-lists.md#standings)

>**`"past"`** - standings the cat used to have with this group. tags can be mixed and matched as necessary. if multiple tags are used, the cat will only need to have had *one* of the standings. [possible standing tags.](reference/tag-lists.md#standings)


***


**stat: dict[str: list]**
> Constrains the thought to only occur if the cat holds specific skills or traits. You can utilize [exclusionary tags](reference/tag-lists.md/#exclusionary-tags).

```json
    "stat": {
        "skill": [],
        "trait": [],
        "must_have_both": false
    },
```
>**`"skill"`** - list of allowed skills from [Skill Tag List](reference/tag-lists.md#__tabbed_3_1)
> 
> **`"trait"`** - list of allowed traits from [Trait Tag List](reference/tag-lists.md#__tabbed_3_2)
> 
> **`"must_have_both"`** - defaults to `false`. if set to `true`, the cat's trait *and* skills must qualify. if `false`, the cat must have *either* a listed trait or a listed skill.

***

**health: dict[str: var]**
> Constrains the thought to only occur if the cat's health matches the constraints.
 
```json
    "health": {
        "working": true,
        "condition": [],
        "must_be_congenital": false,
        "must_be_acquired": false
    }
```
> **`"working"`** - by default, this is always set to `true`. if set to `false`, the cat can't be a working cat (aka, they are currently disabled by a condition of some kind)

> **`"condition`** - a list of conditions that the cat must have *at least* one of. if any condition is allowed, use `"any"`. supports [exclusionary tags](reference/tag-lists.md#exclusionary-tags). check [illness](reference/tag-lists.md/#__tabbed_1_3), [injury](reference/tag-lists.md#__tabbed_1_2), and [permanent condition](reference/tag-lists.md#__tabbed_1_4) references for lists of current condition possibilities.

> **`"must_be_congenital"`** - by default, this is always set to `false`. if set to `true`, the cat must have been born with a permanent condition listed in the `condition`.

> **`"must_be_acquired"`** - by default, this is always set to `false`. if set to `true`, the cat must have acquired a permanent condition listed in `condition` later in life.

!!! warning
    `must_be_congenital` and `must_be_acquired` naturally conflict with each other. Be careful not to set both of them to `true`, else they won't behave correctly.

!!! note
    Be careful when specifying `must_be_congenital`. If you force a condition to be congenital when it can never generate as such or vice versa, the thought will never trigger!

***

**backstory:list**
>Constrains the thought to only occur if the cat has a listed backstory. To find what each backstory describes, you can find more by going to `resources/lang/en/cat/backstories.en.json`.  You can utilize [exclusionary tags](reference/tag-lists.md#exclusionary-tags).

> [Backstory Tag List](reference/tag-lists.md#backstories)


### relationship_constraint: list[dict]
Constrains the thought to only occur is the specified relationships exist. Multiple dictionary blocks can be added to specify multiple required configurations of relationships.
```json
        "relationship_constraint": [
            {
                "cats_from": [],
                "cats_to": [],
                "mutual": false,
                "constraints": []
            }
        ]
```
**cats_from:list**
>The cats from whom the relationship originates. Use the designations (`m_c`, `r_c`, etc.) of cats listed in `involved_cats`.

**cats_to:list**
>The cats who are the target of the relationship. Use the designations (`m_c`, `r_c`, etc.) of cats listed in `involved_cats`.

!!! caution "For example"
    If we want to ensure that `m_c` trusts `r_c`, we would put `m_c` in the `cats_from` list and `r_c` in the `cats_to` list. The feeling of trust is going *from* `m_c` *to* `r_c`.

**mutual:bool**
>Defaults to `false`. Set this to `true` if the constraints should be mutual between the `cats_from` and `cats_to` groups.

!!! caution "For example"
    To work off of our earlier example: if we want `r_c` to *also* trust `m_c`, then we would set `mutual` to `true`.

**constraints:list**
>The list of required relationships. You can include any tags in [Relationship Tiers](reference/tag-lists.md#relationship-tiers) and [Interpersonal Relationships](reference/tag-lists.md#interpersonal-relationships). For the purposes of tag use explanations in those references: `cats_from` is considered "cat1" and `cats_to` is considered "cat2".

!!! caution "For example"
    To work off of our earlier example: we would list `trusts` in our `constraints`

