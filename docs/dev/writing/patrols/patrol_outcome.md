Outcomes utilize the `TextPoolEvent` format.

## Outcome Event Format

### Minimum Required
>The smallest amount of information you're required to include in this format. 

```json
{
    "frequency": 4,
    "strings": [
        "m_c spent time chatting with r_c."
    ],
    "exp_gained": 0
}
```

### Full Format
```json
{
    "location": [],
    "season": [],
    "tags": [],
    "frequency": 4,
    "outcome_art": "",
    "outcome_art_clean": "",
    "strings": [
        "m_c spent time chatting with r_c."
    ],
    "required_cat_types": {},
    "involved_cats": {
        "p_l": {
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
    },
    "required_reputation": {
        "outsider": [],
        "other_clan": []
    },
    "relationship_constraint": [
        {
            "cats_from": [],
            "cats_to": [],
            "mutual": false,
            "constraints": []
        }
    ],
    "exp_gained": 0,
    "reputation_changes": {
        "other_clan": 0,
        "outsider": 0
    },
    "relationship_changes": [
        {
            "cats_from": [],
            "cats_to": [],
            "mutual": false,
            "values": [],
            "amount": 0,
            "log": {
                "cats_from": "",
                "cats_to": ""
            }
        }
    ],
    "supply": [
        {
            "type": "",
            "trigger": [],
            "adjust": ""
        }
    ],
    "death": [
        {
            "cats": [],
            "body": true,
            "history": "",
            "no_results": false
        }
    ],
    "condition": [
        {
            "cats": [],
            "no_results": false,
            "conditon": [],
            "non_lethal": false,
            "scar_pool_override": [],
            "scar_history": "",
            "death_history": ""
        }
    ],
    "lost": [
        {
            "cats": []
        }
    ], 
    "join": [
        {
            "cats": [],
            "change_name": false,
            "new_status": []
        }
    ],
    "future_event": [
        {
            "event_type": "",
            "pool": {},
            "moon_delay": [],
            "involved_cats": {}
        }
    ]
}
```

***

### location:list[str]
This controls the biome and camp the event appears in. [Tagging Instructions](../reference/tag-lists.md#locations)

***

### season: list[str]
List of seasons in which the event may occur. You can utilize [exclusionary tags](../reference/tag-lists.md#exclusionary-tags).
You can tag with a mix of "newleaf", "greenleaf", "leaf-fall", "leaf-bare", or remove the parameter altogether to allow for any season.

***

### tags: list[str]
Used to dictate some odds-and-ends about event constraints: [General Tags](../reference/tag-lists.md#general-tags).

***

#### frequency: int
>Controls how common a patrol is. This works on a 1-4 scale. 

| int | commonality |
|-----|-------------|
| 1   | Very Rare   |
| 2   | Rare        |
| 3   | Uncommon    |
| 4   | Common      |

!!! tip
    It's good to consider frequency as relative to that patrol's set up.  While players likely aren't sending out a patrol of 2 apprentices every moon, that doesn't mean a 2-app patrol event should be marked as Rare frequency. Rather, consider it in terms of "in 10 *instances* of this patrol set up, how often should this specific patrol appear?". Seeing this sort of patrol in 4/10 instances would mean it's a common event! Seeing it just once within those 10 instances would mean it's a very rare event.

!!! warning
    Don't try to boost a patrol's frequency to make up for it being heavily constrained! While we used to do that with our old system, the new code automatically decides how to weight a patrol according to its constraints in a way that is completely divorced from the frequency. We decide event rarities and the code decides if events should be prioritized in specific instances.


***

### art: str
Optional. Name of outcome-specific art, without file extension (no .png). If no art is specified, the intro art will be used. 

 Example: "art": "bord_general_intro",


### art_clean: str
Optional. Name of non-gore outcome-specific art, without file extension (no .png). Adding a clean version of the art marks the normal version as containing gore. The game will then use the clean version if the "Allow mild gore and blood in patrol artwork" setting is off, and the explicit version if this setting is on.

 Example: "art_clean": "bord_general_intro",

### strings: list[str]
This is a list of events applicable to the constraints on this events block. You may include as many or as few events here as you wish, but remember that the constraints will apply to *all* of them. 

For example:
```json
"strings": [
        "p_l fought a fox and was hurt.",
        "p_l killed a fox and was hurt.",
]
```

#### required_cat_types: Dict[str, List[int]]
Utilizes the same functionality as the greater patrol parameter: [required_cat_types](patrols.md/#required_cat_types-dictstr-listint)

!!! caution
    Remember that the greater patrol parameter will have already been applied, so adding an outcome-specific `required_cat_types` will require even *more* specific patrol compositions.

***

### involved_cats: dict[str: dict]
Utilizes the same functionality as the greater patrol parameter: [required_cat_types](patrols.md/#involved_cats-dictstr-var)

You can either specify further constraints for cats already specified in the greater patrol `involved_cats`, or you can specify new involved cats for this outcome.

It's possible to "reuse" a cat under a new designation, but with tighter constraints. You can utilize the `s_c` designations for this use. You will need to add the `prior_abbreviation` parameter to the dictionary for the `s_c` cat:

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

***

### required_reputation: dict:
Constrains the event to only occur if the player clan has the required reputation.
```json
    "required_reputation": {
        "outsider": [],
        "other_clan": []
    },
```
**outsider**
`welcoming`, `neutral`, or `hostile`

**other_clan**
`ally`, `neutral`, or `hostile`

***

### relationship_constraint: list[dict]
Constrains the event to only occur if the specified relationships exist. Multiple dictionary blocks can be added to specify multiple required configurations of relationships.
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
>The cats from whom the relationship originates. Use the designations (`p_l`, `r_c`, etc.) of cats listed in `involved_cats`.

**cats_to:list**
>The cats who are the target of the relationship. Use the designations (`p_l`, `r_c`, etc.) of cats listed in `involved_cats`.

!!! caution "For example"
    If we want to ensure that `p_l` trusts `r_c`, we would put `p_l` in the `cats_from` list and `r_c` in the `cats_to` list. The feeling of trust is going *from* `p_l` *to* `r_c`.

**mutual:bool**
>Defaults to `false`. Set this to `true` if the constraints should be mutual between the `cats_from` and `cats_to` groups.

!!! caution "For example"
    To work off of our earlier example: if we want `r_c` to *also* trust `p_l`, then we would set `mutual` to `true`.

!!! tip
    Specify `"can_romance"` as a constraint to allow the cats to have romantic interactions 

**constraints:list**
>The list of required relationships. You can include any tags in [Relationship Tiers](../reference/tag-lists.md#relationship-tiers) and [Interpersonal Relationships](../reference/tag-lists.md#interpersonal-relationships). For the purposes of tag use explanations in those references: `cats_from` is considered "cat1" and `cats_to` is considered "cat2".

!!! caution "For example"
    To work off of our earlier example: we would list `trusts` in our `constraints`

***

### exp_gained: int
The amount of exp cats receive (sorta). The exact amount also depends on the number of cats and current EXP levels, but in general, a higher number here means more exp. If exp is 0, no exp will be given. 

***

### reputation_changes: dict
How the player Clan's reputation will change with outsiders or the other_clan. Specify a positive or negative integer.

```json
    "reputation_changes": {
        "other_clan": 0,
        "outsider": 0
    }
```

> Defaults:
>
> | Outcome type          | Change                  |
> |-----------------------|-------------------------|
> | Success               | 2                       |
> | Failure               | 0 or -1                 |
> | Antagonize success    | -2                      |
> | Antagonize failure    | -1 or 0                 |

***

### relationship_changes:list[dict[str, various]]
Indicates effects on cat relationships. Check [Writing Relationship Changes](../reference/common-formats.md#writing-relationship-changes) for full parameters.

***

### supply:list[dict]
Indicates changes to the supply of the Clan. Each supply change block is a new change.

Change block:
```json
        {
            "type": "",
            "trigger": [],
            "adjust": ""
        }
```
**type** 
> The type of supply changing. Can be: `freshkill`, `random_herb`, or any single specific herb name.

**trigger**
> If the Clan's current level of the specified supply type should be at a certain threshold for this outcome to occur, specify it here.  Allowed specification are: `always` 'low', 'adequate', 'full', 'excess'.  You **do not have** to specify a trigger.

**adjust**
> The amount to increase the specified supply type. Allowed increase tags are: `increase_tiny`, `increase_small`, `increase_medium`, `increase_large`, `increase_huge`. Keep in mind that this increase is "per" cat on the patrol. A 3 cat patrol being given an `increase_medium` will take home 3 times as much as a similar 1 cat patrol.

!!! tip
    `increase_medium` should be the "default" increase used.

    When awarding multiple herb types, consider downgrading the increases from `medium` to `small` or even `tiny`. Consider what a cat could reasonably carry back and how you might acknowledge an unusual amount in the text.

***

### death: list[dict]
Indicate which cats should die as a result of this outcome. You can specify different "types" of death as separate blocks.

Death block:
```json
        {
            "cats": [],
            "body": true,
            "history": "",
            "no_results": false
        }
```
**cats**
> List of cats who will die. `patrol_cats` can be used to kill the entire patrol.

**body**
> True if the body can be retrieved, False if the body has been lost.

**history**
> String to add to the cat's death history.  Use `m_c` in place of the dead cat's name and pronoun.

**no_results**
> Not required. Set to True to prevent the result text for this death from appearing on the patrol screen. Defaults to False.

***

## condition: list[dict]
Indicate which cats should receive conditions and what conditions they receive. You can add multiple condition blocks.

Condition block:
```json
        {
            "cats": [],
            "no_results": false,
            "conditon": [],
            "non_lethal": false,
            "scar_pool_override": [],
            "scar_history": "",
            "death_history": ""
        }
```
**cats**
> List of cats who will receive these conditions. `patrol_cats` can be used to give the condition to the entire patrol.

**no_results**
> Set to True if there should be no result text about this condition application. 

**condition**
> List of possible conditions. One condition will be chosen from this list. You can also utilize [Injury Pools](../reference/tag-lists.md#__tabbed_1_1)

**non_lethal**
> Set to True to prevent this condition from killing the cat. It's not necessary if the condition is already non-lethal (eg. scrapes)

**scar_pool_override**
> Override the default scars given for the assigned condition. Instead, a scar will be chosen from this list.

**scar_history**
> String to be added to the cat's history if the condition creates a scar. Use `m_c` in place of the dead cat's name and pronoun.

**death_history**
> String to be added to the cat's history if the condition kills them. Use `m_c` in place of the dead cat's name and pronoun.

***

### lost: list[dict]
Indicate which cats should be lost from their Clan. You can add multiple lost blocks.

Lost block:
```json
        {
            "cats": []
        }
```
**cats**
> List of cats who will be lost. `patrol_cats` can be used to give the condition to the entire patrol.

***

## join: list[dict]
> Indicate which cats will join the player Clan. You can add multiple join blocks.

Join block:
```json
        {
            "cats": [],
            "change_name": false,
            "new_status": []
        }
```
**cats**
> List of cats who will join.

**change_name**
> True if the cat should take on a more Clan-like name.

**new_status**
> A list of possible ranks for the cat to take within the Clan. If left blank, the cat will take on a rank appropriate for their age.

***

### future_event:list[dict{str, various}]

 [Using Future Events](../future.md)
 
