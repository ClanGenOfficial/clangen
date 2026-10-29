# TextPoolEvent Format

### Full Format
If looking for a "minimum required" version of this format, check the doc page for the event type you are writing for. Different event types have different requirements.

!!! important
    Remember that some parameters are only used for specific types of events. The doc page for that event type will specify any parameters that cannot be used.

```json
{
    "event_id": "",
    "location": [],
    "season": [],
    "tags": [],
    "frequency": 4,
    "outcome_art": "",
    "outcome_art_clean": "",
    "required_cat_types": {},
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
            "backstory": [],
            "accessory": []
        }
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
    "patrol_temperament": [],
    "other_clan_temperament": [],
    "strings": [
        "m_c was promoted to deputy."
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
    "meet": [
        {
            "cats": []
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

#### event_id: str
A unique string used to identify the event block. 

- [Ceremony Specific Notes](normal-ceremonies.md#event_id-str)
- [Thought Specific Notes](thoughts.md#event_id-str)
- [Relationship Event Specific Notes](relationship-events.md#event_id-str)

***

#### location:list[str]
This controls the biome and camp the event appears in. [Tagging Instructions](../reference/tag-lists.md#locations)

***

#### season: list[str]
List of seasons in which the event may occur. You can utilize [exclusionary tags](../reference/tag-lists.md#exclusionary-tags).
You can tag with a mix of "newleaf", "greenleaf", "leaf-fall", "leaf-bare", or remove the parameter altogether to allow for any season.

***

#### tags: list[str]
Used to dictate some odds-and-ends about event constraints: [General Tags](../reference/tag-lists.md#general-tags).

***

#### frequency: int
>Controls how common an event is. This works on a 1-4 scale. 

| int | commonality |
|-----|-------------|
| 1   | Very Rare   |
| 2   | Rare        |
| 3   | Uncommon    |
| 4   | Common      |

!!! tip
    It's good to consider frequency as relative to that event's set up. While players likely aren't sending out a patrol of 2 apprentices every moon, that doesn't mean a 2-app patrol event should be marked as Rare frequency. Rather, consider it in terms of "in 10 *instances* of this patrol set up, how often should this specific patrol appear?". Seeing this sort of patrol in 4/10 instances would mean it's a common event! Seeing it just once within those 10 instances would mean it's a very rare event.

!!! warning
    Don't try to boost an event's frequency to make up for it being heavily constrained! While we used to do that with our old system, the new code automatically decides how to weight an event according to its constraints in a way that is completely divorced from the frequency. We decide event rarities and the code decides if events should be prioritized in specific instances.

***

#### poi: Dict
> Used to specify which POI (Point Of Interest) a Clan must have access to in order for this event to trigger. [POI Constraint Tagging](../points-of-interest.md/#using-points-of-interest)

[Patrol Outcome Specific Notes](../patrols/patrol_outcome.md#poi-dict)

***

#### required_cat_types: Dict[str, List[int]]
Utilizes the same functionality as the greater patrol parameter: [required_cat_types](../patrols/patrols.md/#required_cat_types-dictstr-listint)

[Patrol Outcome Specific Notes](../patrols/patrol_outcome.md#required_cat_types-dictstr-listint)

***

#### involved_cats: dict[str: dict]
This dictionary holds all constraints for the cats whom we wish to reference in the ceremony.

[Full Involved Cat Dictionary Information](../reference/involved-cat-dict.md)

[Patrol Outcome Specific Notes](../patrols/patrol_outcome.md#involved_cats-dictstr-dict)

***

#### required_reputation: dict:
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

#### relationship_constraint: list[dict]
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

#### patrol_temperament: list[str]
List of allowed patrol temperaments. The patrol's temperament is calculated from the personalities of the cats on it, weighted by rank. [Possible Tempers](../reference/tag-lists.md/#clan-temperaments). You can utilize [exclusionary tags](../reference/tag-lists.md#exclusionary-tags).

[Patrol Outcome Specific Notes](../patrols/patrol_outcome.md#patrol_temperament-liststr)


***

#### other_clan_temperament: list[str]
List of allowed temperaments for the other Clan involved in the event. [Possible Tempers](../reference/tag-lists.md/#clan-temperaments). You can utilize [exclusionary tags](../reference/tag-lists.md#exclusionary-tags).

[Patrol Outcome Specific Notes](../patrols/patrol_outcome.md#other_clan_temperament-liststr)

***

#### outcome_art: str
Optional. Name of outcome-specific art, without file extension (no .png). If no art is specified, the intro art will be used. If you would like this to be art of the POI, you can just enter `"POI"` as the art file.

 Example: "outcome_art": "bord_general_intro",


#### outcome_art_clean: str
Optional. Name of non-gore outcome-specific art, without file extension (no .png). Adding a clean version of the art marks the normal version as containing gore. The game will then use the clean version if the "Allow mild gore and blood in patrol artwork" setting is off, and the explicit version if this setting is on.

 Example: "outcome_art_clean": "bord_general_intro",

***

#### strings: list[str]
This is a list of events applicable to the constraints on this events block. You may include as many or as few events here as you wish, but remember that the constraints will apply to *all* of them. 

For example:
```json
"strings": [
    "m_c has reached the age of six moons and has been made an apprentice, with r_c0 as {PRONOUN/m_c/poss} mentor.",
    "Newly-made apprentice m_c touches noses with {PRONOUN/m_c/poss} new mentor, r_c0."
],
```

!!! caution
    Be careful about referencing actions only specific types of cats take! For example, if an event refers to patrolling, consider if you've adequately constrained the event to only allow cats who *can* go on a patrol (of course, that isn't necessary for patrol outcome events! Those cats will always be patrol-worthy.) We don't want kittens talking about their trip to the Gathering!

***

#### exp_gained: int
The amount of exp cats receive (sorta). The exact amount also depends on the number of cats and current EXP levels, but in general, a higher number here means more exp. If exp is 0, no exp will be given. 

***

#### reputation_changes: dict
How the player Clan's reputation will change with outsiders or the other_clan. Specify a positive or negative integer.

```json
    "reputation_changes": {
        "other_clan": 0,
        "outsider": 0
    }
```

[Patrol Outcome Specific Notes](../patrols/patrol_outcome.md#reputation_changes-dict)

***

#### relationship_changes:list[dict[str, various]]
Indicates effects on cat relationships. Check [Writing Relationship Changes](../reference/common-formats.md#writing-relationship-changes) for full parameters.

***

#### supply:list[dict]
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

#### death: list[dict]
Indicate which cats should die as a result of this event. You can specify different "types" of death as separate blocks.

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
> List of cats who will die.

**body**
> True if the body can be retrieved, False if the body has been lost.

**history**
> String to add to the cat's death history.  Use `m_c` in place of the dead cat's name and pronoun.

**no_results**
> Not required. Set to True to prevent the result text for this death from appearing on the patrol screen. Defaults to False.

***

#### condition: list[dict]
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

#### lost: list[dict]
Indicate which cats should be lost from their Clan. You can add multiple lost blocks.

Lost block:
```json
        {
            "cats": []
        }
```
**cats**
> List of cats who will be lost. 

[Patrol Outcome Specific Notes](../patrols/patrol_outcome.md#reputation_changes-dict)

***

#### join: list[dict]
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

#### meet: list[dict]
> Indicate which cats will meet the player Clan. You can add multiple meet blocks.

meet block:
```json
        {
            "cats": []
        }
```
**cats**
> List of cats who will meet the Clan.

***

#### future_event:list[dict{str, various}]

 [Using Future Events](../future.md)
 
