# Involved Cat Dictionaries
General information on the formatting and constraints within an involved cat dictionary. Event format documentation will link to this page if these dictionaries can be used within them.

This dictionary holds all constraints for the cats whom we wish to reference in the event.

Each entry is an individual cat, with the key being their event designation (`r_c0`, `p_l`, etc.) and the value being their personal constraints. Event documentation will include a list of valid designations for that event type.

```json
    "designation": {
        "prior_abbreviation": [],
        "can_create_new_cat": {},
        "status": [],
        "past_status": [],
        "age": [],
        "name": {
            "has_suffix": true
        }      
        "gender": [],
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
        "current_exp": [],
        "health": {
            "working": true,
            "condition": [],
            "must_be_congenital": false,
            "must_be_acquired": false
        },
        "backstory": [],
        "has_mentor": {
            "current": false,
            "former": false
        },
        "has_apprentice": {
            "current": false,
            "former": false
        },
}
```

## When To Use

If you want to be able to reference the cat designation within the text or within other constraint/consequence lists (cats who die, cats who must abide by relationship constraints, etc.), then you *must* declare them within an `involved_cats` dict for that event (there are some exceptions to this which may be specified by the format documentation for specific event types.) This can be an empty dict if no constraints are needed:
```json
"r_c0": {}
```

!!! tip
    You do not need to "repeat" constraints! If a patrol can only have apprentices on it via the `required_cat_types` then you don't need to specify that `r_c0` is an apprentice.

## Specifying an outsider or other Clan cat

If you would like to include an outsider or other Clan cat, you can specify them using the `n_c#` designation and some additional parameters.

If the outsider/other_clan cat can be newly generated rather than having to utilize an existing cat, you can add the `can_create_new_cat` parameter.
```json
    "can_create_new_cat": {
        "become_litter": false,
        "assign_blood_parent": [],
        "assign_adoptive_parent": [],
        "assign_mate": []
    }
```
This can even be added as an empty dict: `can_create_new_cat: {}` to simply mark it as a new cat creation without any additional specifications.

> **`become_litter`** - True will generate a 2-5 litter of kittens rather than a single cat. This means the abbreviation for this litter should not be used within the text of the event, since they have no singular name or pronoun.
> 
> **`assign_blood_parent`** - List of designations for cats who will become this cat's blood parents. These cats must have already been specified prior in `involved_cats`.
> 
> **`assign_adoptive_parent`** - List of designations for cats who will become this cat's adoptive parents. These cats must have already been specified prior in `involved_cats`.
> 
> **`assign_mate`** - List of designations for cats who will become this cat's mates. These cats must have already been specified prior in `involved_cats`.

## Prior Abbreviation
For **patrols**, it's possible to "reuse" a cat under a new designation for an outcome, but with tighter constraints. You can utilize the `s_c` designations for this use. You will need to add the `prior_abbreviation` parameter to the dictionary for the `s_c` cat:

For example:
```json
"s_c0":{
    "prior_abbreviation": ["p_l", "r_c1"],
    "status": ["warrior"]
}
```
In this example, `s_c` can be either `p_l` or `r_c1`, but only if those cats are also `warrior` rank.

You can utilize any prior declared cat designation *or* to allow any cat in the patrol to be s_c, you can use `any`.

These can also be exclusionary tags such as: `-p_l` to allow any cat *except* `p_l` to take this role.

!!! tip
    `s_c` used to be used only for trait and skill constrained cats. Now it's for *any* sort of constraint. This could be a health constraint, group constraint, literally any constraint.

## General Constraints

### **status: list[str]**
>Constrains the event to only happen if the cat holds a certain role. You can utilize [exclusionary tags](../reference/tag-lists.md#exclusionary-tags).

> [Status Tag List](../reference/tag-lists.md#__tabbed_2_2)
> 
> You can also remove the parameter to allow the event to occur for all roles except "newborns", who are only allowed if specifically tagged as such.

***

### **past_status: list[str]**
>Constrains the event to only happen if the cat held a certain role in the past. You can utilize [exclusionary tags](../reference/tag-lists.md#exclusionary-tags).

> [Status Tag List](../reference/tag-lists.md#__tabbed_2_2)

***

### **age: list[str]**
>Constrains the event to only occur if the cat is within a certain age group. You can utilize [exclusionary tags](../reference/tag-lists.md/#exclusionary-tags).

> [Age Tag List](../reference/tag-lists.md#__tabbed_2_1)
> 
> You can also remove the parameter to allow the event to occur for all ages except "newborns", who are only allowed if specifically tagged as such.

***

### **name: dict[str, bool]**
>Constrains the event to only occur if the cat matches the name constraints.
```json
"name": {
    "has_suffix": false
}
```
>**`"has_suffix"`** - if `true`, cat must have a suffix as part of their name. if `false`, cat must have no suffix as part of their name. this only applies to the base suffix of the cat, special suffixes (i.e. "paw", "kit") are not counted for this constraint.

***

### **gender: str**
>Constrains the event to only occur if the cat has a certain birth gender. Valid entries are: `male`, `female`, `can_birth`. `can_birth` will allow either female or male cats dependant upon the player's settings. 

***

### **group:list[str]**
>Constraints the thought to only happen if the cat is a member of a listed group or a member of no group. This should only be used to dictate what group a new cat is originally part of. you can use tags in: [possible group tags](../reference/tag-lists.md#groups) and you can utilize [exclusionary tags](../reference/tag-lists.md/#exclusionary-tags).
> 
***

### **standing: dict[str: var]**
>Constrains the event to only happen if the cat matches with the dictated group standings. A group standing is the relationship between a cat and a group, for example: if they are an exile or lost.

```json
    "standing": {
        "group": [],
        "currently": [],
        "past": []
      },
```
>**`"group"`** - the group we are checking the cat's standing with. you can utilize [exclusionary tags](../reference/tag-lists.md/#exclusionary-tags). tags can be mixed and matched as necessary. if multiple tags are used, the cat will only need to qualify against *one* of the groups. [possible group tags.](../reference/tag-lists.md#groups). You should not try to tag `no_group`.

>**`"currently"`** - the standing the cat should currently possess with this group. tags can be mixed and matched as necessary. if multiple tags are used, the cat will only need to have *one* of the standings. [possible standing tags.](../reference/tag-lists.md#standings)

>**`"past"`** - standings the cat used to have with this group. tags can be mixed and matched as necessary. if multiple tags are used, the cat will only need to have had *one* of the standings. [possible standing tags.](../reference/tag-lists.md#standings)

!!! warning
    Keep in mind that currently the only cats who receive and are included in relationship events are player Clan cats. Cats currently outside the Clan cannot be part of an event. `standing` can still be constrained for in the context of a cat who *used* to be lost, exiled, etc.

***


### **stat: dict[str: list]**
> Constrains the event to only occur if the cat holds specific skills or traits. You can utilize [exclusionary tags](../reference/tag-lists.md/#exclusionary-tags).

```json
    "stat": {
        "skill": [],
        "trait": [],
        "must_have_both": false
    },
```
>**`"skill"`** - list of allowed skills from [Skill Tag List](../reference/tag-lists.md#__tabbed_3_1)
> 
> **`"trait"`** - list of allowed traits from [Trait Tag List](../reference/tag-lists.md#__tabbed_3_2)
> 
> **`"must_have_both"`** - defaults to `false`. if set to `true`, the cat's trait *and* skills must qualify. if `false`, the cat must have *either* a listed trait or a listed skill.

***

### **current_exp: list[str]**
> Constrains the event to only occur if the cat's exp level is part of the constraints

Possible levels:

- `untrained`
- `learning`
- `prepared`
- `capable`
- `proficient`
- `adept`
- `masterful`

!!! tip
    Cats are generally `untrained` until they become adolescents. Cats will graduate when they are `prepared` or when they reach a "maximum" age (typically a few moons into adulthood.)

### **health: dict[str: var]**
> Constrains the event to only occur if the cat's health matches the constraints.
 
```json
    "health": {
        "working": true,
        "condition": [],
        "must_be_congenital": false,
        "must_be_acquired": false
    }
```
> **`"working"`** - by default, this is always set to `true`. if set to `false`, the cat can't be a working cat (aka, they are currently disabled by a condition of some kind). In the case of patrols, it is impossible for a non-working cat to be patrolling, so this will not be used.

> **`"condition`** - a list of conditions that the cat must have *at least* one of. if any condition is allowed, use `"any"`. supports [exclusionary tags](../reference/tag-lists.md#exclusionary-tags). check [illness](../reference/tag-lists.md/#__tabbed_1_3), [injury](../reference/tag-lists.md#__tabbed_1_2), and [permanent condition](../reference/tag-lists.md#__tabbed_1_4) references for lists of current condition possibilities.

> **`"must_be_congenital"`** - by default, this is always set to `false`. if set to `true`, the cat must have been born with a permanent condition listed in the `condition`.

> **`"must_be_acquired"`** - by default, this is always set to `false`. if set to `true`, the cat must have acquired a permanent condition listed in `condition` later in life.

!!! warning
    `must_be_congenital` and `must_be_acquired` naturally conflict with each other. Be careful not to set both of them to `true`, else they won't behave correctly.

!!! note
    Be careful when specifying `must_be_congenital`. If you force a condition to be congenital when it can never generate as such, the event will never trigger! The same also applies for forcing a condition to be non-congenital when it is always generated as such.

***

### **backstory:list**
>Constrains the event to only occur if the cat has a listed backstory. To find what each backstory describes, you can find more by going to `resources/lang/en/cat/backstories.en.json`.  You can utilize [exclusionary tags](../reference/tag-lists.md#exclusionary-tags).

> [Backstory Tag List](../reference/tag-lists.md#backstories)

***

### **has_mentor:dict[str, bool]**
> Set specific mentorship circumstances.
```json
"has_mentor": {
    "current": false,
    "former": false
}
```
> **`"current"`** - if `true`, cat must currently have a mentor. if `false`, cat must have no current mentor.

> **`"former"`** - if `true`, cat must have a former mentor. if `false`, cat must have no former mentor.

***

### **has_apprentice:dict[str, bool]**
> Set specific apprentice circumstances.
```json
"has_apprentice": {
    "current": false,
    "former": false
}
```
> **`"current"`** - if `true`, cat must currently have an apprentice. if `false`, cat must have no current apprentice.

> **`"former"`** - if `true`, cat must have a former apprentice. if `false`, cat must have no former apprentice.