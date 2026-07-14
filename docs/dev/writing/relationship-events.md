# Relationship Events

!!! warning "Under Development"
    Relationship events are in the midst of being reformatted to work with the below documentation. Group events and Normal interactions are currently the only categories that match this documentation.


Relationship events are events that occur each timeskip that are focused entirely on influencing the relationships between certain cats. 

These should be fairly short, like all timeskip events. Less than 300 characters, with shorter being better, is preferred.

## Usable Cat References

| abbreviation | use                                                                                                                                                                                                                                                                                                                           |
|--------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `m_c`        | The main cat of the event. Their relationship towards other cats will be affected the most by the event.                                                                                                                                                                                                                      |
| `r_c`        | The second cat within a two-cat event.  `m_c`'s relationship towards `r_c` will be changing in the event.                                                                                                                                                                                                                     |
| `r_c{#}`     | If multiple cats other than `m_c` will be present, use this tag instead of `r_c` to denote them. For example `"m_c avoids joining r_c1 and r_c2's conversation."`. The numbering of these abbreviations should begin at `1` and increment upwards.                                                                            |
| `multi_cat`  | If multiple cats other than `m_c` are present and they're all being affected in the exact same way, then you can use this tag to insert a list of their names into the event. For example `"m_c spends time with multi_cat."` will appear to the player as `"Examplecat spends time with Blankpelt, Someclaw, and Otherfur."` |


## Directory Structure
The relationship event directory is found in `resources/lang/en/events/relationship_events`.

Within this folder are 3 folders:

| name                   | use                                                                   |
|------------------------|-----------------------------------------------------------------------|
| `group_interactions`   | holds events that include 3 or more cats                              |
| `normal_interactions`  | the general 2-cat interactions that are most common in the game       |
| `welcome_interactions` | these are special events only triggered when a new cat joins the Clan |

Within `normal_interactions` and `welcome_interactions` are folders for each relationship value: `comfort`, `like`, `respect`, `romance`, `trust`. This value will be the "main" value affected by the events inside that folder.

There's one more layer of folders after this one. These dictate the strength of the effect on the "main" value: `low`, `medium`, or `high`.

From there, each folder contains a `negative.json` and `positive.json`. Events the decrease the "main" value will go in `negative.json` and events that increase the "main" value will go into `positive.json`.

Altogether this might look like `normal_interations/comfort/medium/negative.json`.

`group_interactions` is unique. It skips the first layer of folders dictating relationship value as its nature in affecting many relationships at once means determining a "main" value is difficult. Instead, consider how large of a relationship change is being made and whether it's largely positive or negative.

!!! important
    While there are other files within `relationship_events` beyond just the 3 interaction folders listed, these do NOT contain events using the format that will be explained in this documentation.

## Relationship Event Format

!!! note "Important"
    If you do not use a constraint, you can remove it from the event to make the JSONS less hefty and more readable. Check out the below "Minimum Required" to see what parameters are always required.

### Minimum Required
>The smallest amount of information you're required to include in this format. 

```json
{
    "id": "test",
    "strings": [
        "m_c spent time chatting with r_c."
    ]
}
```

### Full Format
```json
    {
        "id": "test",
        "location": [],
        "season": [],
        "tags": [],
        "strings": [
            "m_c spent time chatting with r_c."
        ],
        "involved_cats": {
            "m_c": {
                "status": [],
                "past_status": [],
                "age": [],
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
            },
            "r_c": {
                "status": [],
                "past_status": [],
                "age": [],
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
        ],
        "relationship_changes": [
            {
                "cats_from": [],
                "cats_to": [],
                "mutual": false,
                "values": [],
                "amount": 0
            }
        ]
    }
```

### id: str
A unique string used to identify the event block. Generally, the ID tries to specify the main relationship value being affected, the intensity of the affect, and the type of effect; along with any other identifiers that might indicate a unique aspect of the events contained within.

* `like_inc_med1`
* `like_to_app_inc_med1`
* `trust_for_leader_de_high1`

***

### location:list[str]
This controls the biome and camp the event appears in. [Tagging Instructions](reference/tag-lists.md#locations)

***

### season: list[str]
List of seasons in which the event may occur. You can utilize [exclusionary tags](reference/tag-lists.md#exclusionary-tags).
You can tag with a mix of "newleaf", "greenleaf", "leaf-fall", "leaf-bare", or remove the parameter altogether to allow for any season.

***

### tags: list[str]
Used to dictate some odds-and-ends about event constraints: [General Tags](reference/tag-lists.md#general-tags).

!!! note
    You do not need to use the `romance` tag for events intended to be romantic. These are already filtered as necessary.

***

### strings: list[str]
This is a list of events applicable to the constraints on this events block. You may include as many or as few events here as you wish, but remember that the constraints will apply to *all* of them. 

For example:
```json
"strings": [
        "m_c and r_c agree to be best friends forever.",
        "m_c is surprised to hear r_c express an ideal {PRONOUN/m_c/subject} can agree with.",
        "m_c and r_c heckled another Clan at the Gathering together."
]
```

!!! caution
    Be careful about referencing actions only specific types of cats take! For example, if an event refers to patrolling, consider if you've adequately constrained the event to only allow cats who *can* go on a patrol. We don't want kittens talking about their trip to the Gathering!

***

### involved_cats: dict[str: dict]
This dictionary holds all constraints for the cats whom we wish to reference in the event, including the main cat!

Each entry is an individual cat, with the key being their event designation (`r_c`, `m_c`, etc.) and the value being their personal constraints. Allowed constraints are as follows:

***

**status: list[str]**
>Constrains the event to only happen if the cat holds a certain role. You can utilize [exclusionary tags](reference/tag-lists.md#exclusionary-tags).

> [Status Tag List](reference/tag-lists.md#__tabbed_2_2)
> 
> You can also remove the parameter to allow the event to occur for all roles except "newborns", who are only allowed if specifically tagged as such.

***

**past_status: list[str]**
>Constrains the event to only happen if the cat held a certain role in the past. You can utilize [exclusionary tags](reference/tag-lists.md#exclusionary-tags).

> [Status Tag List](reference/tag-lists.md#__tabbed_2_2)

***
**age: list[str]**
>Constrains the event to only occur if the cat is within a certain age group. You can utilize [exclusionary tags](reference/tag-lists.md/#exclusionary-tags).

> [Age Tag List](reference/tag-lists.md#__tabbed_2_1)
> 
> You can also remove the parameter to allow the event to occur for all ages except "newborns", who are only allowed if specifically tagged as such.

***

**standing: dict[str: var]**
>Constrains the event to only happen if the cat matches with the dictated group standings. A group standing is the relationship between a cat and a group, for example: if they are an exile or lost.

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

!!! warning
    Keep in mind that currently the only cats who receive and are included in relationship events are player Clan cats. Cats currently outside the Clan cannot be part of an event. `standing` can still be constrained for in the context of a cat who *used* to be lost, exiled, etc.

***


**stat: dict[str: list]**
> Constrains the event to only occur if the cat holds specific skills or traits. You can utilize [exclusionary tags](reference/tag-lists.md/#exclusionary-tags).

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
> Constrains the event to only occur if the cat's health matches the constraints.
 
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
    Be careful when specifying `must_be_congenital`. If you force a condition to be congenital when it can never generate as such, the event will never trigger! The same also applies for forcing a condition to be non-congenital when it is always generated as such.

***

**backstory:list**
>Constrains the event to only occur if the cat has a listed backstory. To find what each backstory describes, you can find more by going to `resources/lang/en/cat/backstories.en.json`.  You can utilize [exclusionary tags](reference/tag-lists.md#exclusionary-tags).

> [Backstory Tag List](reference/tag-lists.md#backstories)


### relationship_constraint: list[dict]
Constrains the event to only occur is the specified relationships exist. Multiple dictionary blocks can be added to specify multiple required configurations of relationships.
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

### relationship_changes:list[dict[str, various]]
>Optional. Indicates *additional* effects on cat relationships. Check [Writing Relationship Changes](reference/common-formats.md#writing-relationship-changes) for full parameters.

!!! caution
    The ONLY `cats_from` and `cats_to` parameters allowed here are the ones you have defined in `involved_cats`. Exclusionary tags and facet tags shouldn't be used. Logs are unnecessary as we always use the chosen event string for the logs. 

!!! caution
    As noted in [Directory Structure](#directory-structure), `normal_interactions` and `welcoming_interactions` events are already categorized according the values they will affect, as well as the size of the effect. You *do not* need to include those effects in this dict. They are applied *automatically* from `m_c` to `r_c`. 
    
    So, if an event is in `comfort/mid/decrease` then you do not need to change the comfort amount from `m_c` to `r_c`. **However**, if you wish to change the comfort from `r_c` to `m_c`, then you *do* need to use this parameter to do so.

    Events in `group_interactions` are exempt from this. For those you will have to dictate every single intended change to the relationships.
***
