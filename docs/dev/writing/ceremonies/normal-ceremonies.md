# Normal Ceremonies

Ceremonies utilize the `TextPoolEvent` format.

## Usable Cat References

| abbreviation  | use                                                                                                                                                                                                                                                                                                                                                                                                                      |
|---------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `m_c`         | The main cat. This is the cat undergoing the ceremony. You can always assume that this cat is appropriate for a given ceremony (i.e. that the `m_c` for an apprentice ceremony is of an appropriate age and rank for that ceremony). This means that you do not need to specify constraints to ensure that they are appropriate (i.e. the `m_c` of our apprentice ceremony needs no `"age": ["adolescent"]` constraint). |                                                                                                 |
| `r_c#`        | A random cat: this cat is chosen at complete random and will not be m_c. You can specify constraints on this cat to require it to have certain attributes rather than being entirely random. The `#` is replaced with a number: 0-5. It's recommended to begin at 0 and increment as needed.                                                                                                                             | |      
| `past_deputy` | This is a ceremony-unique abbreviation and can only be used within *deputy* ceremonies. The cat who held the deputy position immediately prior to `m_c` will be this cat, even if dead or outside of the Clan (however, you can apply constraints as typical to ensure a certain sort of `past_deputy`.) If there is no past deputy to be used, then any ceremony requiring one will not be chosen.                      |                                                                                                                                                                                                                                                                                 |
| `n_c#`        | A newly generated or existing outsider/other clan cat: The `#` is replaced with a number: 0-6. It's recommended to begin at 0 and increment as needed. Generating new cats is not necessarily typical for ceremony events, however it is possible.                                                                                                                                                                       |

## Directory Structure
The relationship event directory is found in `resources/lang/en/events/ceremonies`.

Within this folder are multiple files:

| name                           | use                                                                                                                                                                         |
|--------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `apprentice.json`              | Ceremonies for cats becoming warrior apprentices.                                                                                                                           |
| `deputy.json`                  | Ceremonies for cats becoming deputies.                                                                                                                                      |
| `elder.json`                   | Ceremonies for cats retiring to become elders.                                                                                                                              |
| `leader.json`                  | Ceremonies for cats becoming leader (this does not include the life-receiving ceremony)                                                                                     |
| `mediator.json`                | Ceremonies for cats becoming mediators.                                                                                                                                     |
| `mediator_apprentice.json`     | Ceremonies for cats becoming mediator apprentices.                                                                                                                          |
| `medicine_cat.json`            | Ceremonies for cats becoming medicine cats.                                                                                                                                 |
| `medicine_cat_apprentice.json` | Ceremonies for cats becoming medicine cat apprentices.                                                                                                                      |
| `warrior.json`                 | Ceremonies for cats becoming warriors.                                                                                                                                      |
| `ceremony_traits.json`         | This does not include any ceremonies! Rather this holds the "honors" that replace the `r_h` text within a ceremony string. Each cat trait has a list of potential "honors". |

## Ceremony Event Format

### Minimum Required
> The smallest amount of information you're required to include in this format.

```json
{
    "event_id": "",
    "strings": [
        "m_c was promoted to deputy."
    ],
}
```

### Full Format

```json
{
    "event_id": "",
    "location": [],
    "season": [],
    "tags": [],
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
        }
    },
    "strings": [
        "m_c was promoted to deputy."
    ],
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
    "other_clan_temperament": [],
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

### event_id: str
A unique string used to identify the event block. Generally, the ID tries to specify specific circumstances or themes of the ceremony. The rank of the ceremony is typically used as a prefix for this id.

* `app_no_mentor0`
* `warrior_unsure0`
* `deputy_clan_chosen1`

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

### strings: list[str]
This is a list of events applicable to the constraints on this events block. You may include as many or as few events here as you wish, but remember that the constraints will apply to *all* of them. 

For example:
```json
"strings": [
    "m_c has reached the age of six moons and has been made an apprentice, with r_c0 as {PRONOUN/m_c/poss} mentor.",
    "Newly-made apprentice m_c touches noses with {PRONOUN/m_c/poss} new mentor, r_c0."
],
```

### involved_cats: dict[str: dict]
This dictionary holds all constraints for the cats whom we wish to reference in the ceremony.

[Full Involved Cat Dictionary Information](../reference/involved-cat-dict.md)

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

### other_clan_temperament: list[str]
List of allowed temperaments for the other Clan involved in the event. [Possible Tempers](../reference/tag-lists.md/#clan-temperaments). You can utilize [exclusionary tags](../reference/tag-lists.md#exclusionary-tags).

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
> The amount to increase the specified supply type. Allowed increase tags are: `increase_tiny`, `increase_small`, `increase_medium`, `increase_large`, `increase_huge`. 

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
        }
```
**cats**
> List of cats who will die.

**body**
> True if the body can be retrieved, False if the body has been lost.

**history**
> String to add to the cat's death history.  Use `m_c` in place of the dead cat's name and pronoun.

***

### condition: list[dict]
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
> List of cats who will receive these conditions. 

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
> List of cats who will be lost. 

***

### join: list[dict]
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
 
