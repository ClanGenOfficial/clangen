# Patrols

## Guidelines
When considering patrols, keep in mind challenge vs reward. That isn't to say certain patrol events should necessarily be locked behind certain patrol sizes, but try to imagine what a group of cats that size would do in a given situation, and how likely it would be for them to succeed in whatever it is they're trying to do. If making large size and small sized variants of the same patrol, it's encouraged to give different outcomes even if the success chance is the same for both variants. For example, 6 cats have very different options for dealing with an owl than 2 cats do.


## Usable Cat References

| abbreviation  | use                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
|---------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `p_l`         | The patrol leader: the cat in the patrol with the highest relevant rank and, within involved cats of that rank, is either the oldest or the most experienced.  For medicine cat patrols, this will either be a medicine cat or medicine cat apprentice. For normal patrols, this will go from the highest to lowest rank (leader > deputy > warrior > apprentice).                                                                                                                                   |                                                                                                 |
| `r_c#`        | A random cat: this cat is chosen at complete random and will not be the patrol leader. You can specify constraints on this cat to require it to have certain attributes rather than being entirely random. The `#` is replaced with a number: 0-5. It's recommended to begin at 0 and increment as needed.                                                                                                                                                                                           | |      
| `s_c#`        | An additional special cat, mainly used in outcomes: this cat has some constraints being required of it and could be a cat who was previously assigned an abbreviation. For example, if the patrol as a whole requires `r_c0` to be a warrior and you wish to add an outcome in which any cat with the `calm` trait, including `r_c0`, could also play a role, then you would use `s_c` for that cat. The `#` is replaced with a number: 0-5. It's recommended to begin at 0 and increment as needed. |                                                                                                                                                                                                                                                                                 |
| `n_c#`        | A newly generated or existing outsider/other clan cat: The `#` is replaced with a number: 0-6. It's recommended to begin at 0 and increment as needed.                                                                                                                                                                                                                                                                                                                                               |
| `patrol_cats` | Only for use within `required_cat_types` and cat lists for consequences. Refers to all the cats on the patrol.                                                                                                                                                                                                                                                                                                                                                                                       |
| `some_patrol` | Only for use within cat lists for consequences. Refers to a subsection of the patrol. This will always be at least 2 cats, but never the entire patrol. **Should not be used in cases where a patrol could be 2 or less cats in total**                                                                                                                                                                                                                                                              |

!!! tip
    While not usable within the text of the events, you *can* use keys listed in [required_cat_types](#required_cat_types-dictstr-listint) to gather cats for other parts of the event, such as the `cats_from`/`cats_to` lists. For example, if apprentices are able to come on the patrol, then you can use `"apprentice"` in the `cats_from` list of `relationship_constraint` to specify constraints that the apprentices as a whole must abide by.


## Formatting

!!! tip
    Before beginning, be sure to at least read the first section of [Coding Terms for Writers to Know](../reference/terminology.md#coding-terms-for-writers-to-know). This explains much of the terminology used here.

### Minimum Required
>The smallest amount of information you're required to include in this format. 


```json
{
    "event_id": "test",
    "types": [],
    "frequency": 4,
    "required_cat_types": {
        "patrol_cats": [1, 6]
    },
    "chance_of_success": 100,
    "patrol_art": "art.png",
    "intro_strings": ["Patrol heads out to do some-such."],
    "decline_strings": ["Patrol turns around"],
    "success_outcomes": [
        TextPoolEvent
    ],
    "fail_outcomes": [
        TextPoolEvent
    ],
}
```

### Full Format

```json
{
    "event_id": "test",
    "types": [],
    "frequency": 4,
    "location": [],
    "season": [],
    "tags": [],
    "poi": {},
    "required_cat_types": {
        "patrol_cats": [1, 6]
    },
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
    "chance_of_success": 100,
    "patrol_art": "art.png",
    "patrol_art_clean": "pleasant_art.png",
    "intro_strings": ["Patrol heads out to do some-such."],
    "decline_strings": ["Patrol turns around"],
    "success_outcomes": [
        TextPoolEvent
    ],
    "fail_outcomes": [
        TextPoolEvent
    ],
    "antag_success_outcomes": [
        TextPoolEvent
    ],
    "antag_fail_outcomes": [
        TextPoolEvent
    ],
}
```

***

#### event_id:str
> The id is a unique string used to identify the patrol. It does not affect patrol behavior, but it allows us to easily find patrols.

> An id is formatted as following: `biome_type_enemy_seasondescription#`, enemy and season are optional (some patrols do not have a specific enemy or season), # is a number at the end of the descriptive section starting at 1 and incrementing up as you create new versions of that patrol. 

>- If you are making new_cat or other_clan patrols, please include if the patrol is hostile/neutral/welcoming or hostile/neutral/allies in the ID
>- If the patrol is under some kind of constraint, like being skill locked or relationship locked, please indicate that in the ID 

| Abbreviations |      Meaning                     |
|---------------|----------------------------------|
| mtn           | appears in the mountainous biome |
| pln           | appears in the plains biome      |
| fst           | appears in the forest biome      |
| bch           | appears in the beach biome       |
| wtlnd         | appears in the wetlands biome    |
| dst           | appears in the desert biome      |
| gen           | appears in any biome             |
| hunt          | hunting type patrol              |
| bord          | border type patrol               |
| train         | training type patrol             |
| med           | herb gathering type patrol       |

Example:
>`fst_hunt_foxgray_leafbarescavenge_huntinglocked3` is a hunting patrol in the forest biome, involves a gray fox, and takes place in leafbare. The word scavenge tells us it's about a gray fox scavenging something, huntinglocked indicates it's locked behind p_l having the hunting skill, and 3 tells us it is the third variant of this patrol that exists in the game. 

How to make sure your patrol_id is unique:
> ctrl (or command) + f through the .json file you're writing the patrol into. As each patrol_id contains the biome & type within it and we have different jsons for different biomes/patrol types/seasons, if your potential patrol_id isn't in the json already, your patrol_id will be unique.

!!! caution
    No NSFW patrol_ids. No exceptions.


***

#### types: list[str]
> This controls the type of patrol

| string           |                                          |
|------------------|------------------------------------------|
| "hunting"        | hunting patrol                           |
| "herb_gathering" | herb_gathering (ie, medicine cat) patrol |
| "border"         | border patrol                            |
| "training"       | training patrol                          |

**Differences between the types** 
> Training patrols are an easy difficulty for [success chance](#chance-of-success-int), but the lowest with regards to [exp reward](patrol_outcome.md/#exp_gained-int). They are a relatively safe patrol type of low danger, and the [injuries](patrol_outcome.md/#condition-listdict) cats can obtain on them should either be rare (low weighed outcome), or minor. Training patrols have high [relationship rewards](patrol_outcome.md/#relationship_changeslistdictstr-various).

> Hunting patrols are of moderate difficulty for [success chance](#chance-of-success-int).  Hunting patrols are subject to [extra filtering](../advanced-documentation.md) that effects what patrols are available based on their [prey reward](patrol_outcome.md/#supplylistdict). This filtering ensures that we cannot starve out the player's cats simply by adding too many patrols that give out a certain prey reward. Hunting patrols are of medium danger, and the [injuries](patrol_outcome.md/#condition-listdict) cats can obtain on them should either be minor and common (high frequency outcome), moderate and of a mid frequency, or severe and of a low frequency. The same guidelines apply to [killing cats](patrol_outcome.md/#death-listdict) on this patrol type. Hunting patrols should have only minor [relationship rewards](patrol_outcome.md/#relationship_changeslistdictstr-various) (less than 5) unless the hunting patrol text focuses on the relationship, e.g a warrior and a apprentice hunting together with the warrior teaching the apprentice.

> Border patrols needs to be the hardest and most dangerous, with a high difficulty for [success chance](#chance-of-success-int).  This is where experienced cats should shine! The [injuries](patrol_outcome.md/#condition-listdict) cats can obtain on them should be a wide range. Failure outcomes on border patrols that don't cause injury should be rare. You are encouraged to apply minor injuries even on success outcome. The same guidelines apply to [killing cats](patrol_outcome.md/#death-listdict) on this patrol type, with the exception that you cannot kill cats on any success outcomes. This is by far the mostly likely patrol type to have cats become [lost](patrol_outcome.md/#lost-listdict) on.

> Herb gathering patrols are of moderate difficulty for [success chance](#chance-of-success-int) (like hunting patrols). Herb gathering patrols are focused on gathering herbs, so successful outcomes must have a [herb reward](patrol_outcome.md/#supplylistdict) under most circumstances. Herb gathering patrols are of medium danger, and the [injuries](patrol_outcome.md/#condition-listdict) cats can obtain on them should either be minor and common (high frequency outcome), moderate and of a mid frequency, or severe and of a low frequency. The same guidelines apply to [killing cats](patrol_outcome.md/#death-listdict) on this patrol type. Herb gathering patrols should be highly seasonal, as not all herbs are available in all seasons, or in the same seasons in different [biomes](../reference/biomes.md). 

> The subtypes of [new_cat](patrol_outcome.md/#required_reputation-dict) and [other_clan](patrol_outcome.md/#required_reputation-dict) patrols should primarily use the type specific success, danger, injuries, death, and rewards of whatever the primary patrol type is. For example, use the success chance for herb gathering patrols if your medicine cat finds an injured kitten. However, a subtype is more likely to move away from the 'normal' setting for that type of patrol as they are by definition unusual examples of that patrol type. Brainstorm with other developers!

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

#### location:list[str]
This controls the biome and camp the event appears in. [Tagging Instructions](../reference/tag-lists.md#locations)

***

#### season: list[str]
List of seasons in which the event may occur. You can utilize [exclusionary tags](../reference/tag-lists.md#exclusionary-tags).
You can tag with a mix of "newleaf", "greenleaf", "leaf-fall", "leaf-bare", or remove the parameter altogether to allow for any season.

***

#### tags: list[str]
>Tags are used for some filtering purposes, and some odd-and-ends. Tags never affect outcome. [General Tags](../reference/tag-lists.md#general-tags).

***

#### poi: Dict
> Used to specify which POI (Point Of Interest) a Clan must have access to in order for this event to trigger. [POI Constraint Tagging](../points-of-interest.md/#using-points-of-interest)

***

#### required_cat_types: Dict[str, List[int]]
>Optional. Allows specification of the minimum and maximum number of specific types of cats that are allowed on the patrol, as well as the general number of cats allowed in the patrol. The format for each dictionary entry is 
>
>`"status_type": [min_value, max_value]`
>
>To specify that a type of cat can't be on the patrol, use [-1, -1]

| status types                |                                                               |
|-----------------------------|---------------------------------------------------------------|
| `"patrol_cats"`             | Amount of cats allowed in the patrol.                         |
| `"medicine cat"`            | Amount of medicine cats (not including apprentices)           |
| `"warrior"`                 | Amount of warriors (not including leader or deputy)           |
| `"leader"`                  | Amount of leaders                                             |
| `"deputy"`                  | Amount of deputies                                            |
| `"apprentice"`              | Amount of warrior apprentices                                 |
| `"medicine cat apprentice"` | Amount of medicine cat apprentices                            |
| `"healer cats"`             | Amount of medicine cats and medicine cat apprentices combined |
| `"normal adult"`            | Amount of warriors, leaders and deputies                      |
| `"all apprentices"`         | Amount of warrior apprentices and medicine cat apprentices.   |

!!! warning
    You *must* at least specify `patrol_cats`.

***

#### involved_cats: Dict[str, var]
This dictionary holds all constraints for the cats whom we wish to reference in the patrol.

**When To Use**

`p_l` is the only cat designation you can *assume* has a cat attached at all times. With this in mind, you do not need to add a `p_l` entry to `involved_cats` unless you would like to add constraints regarding the sort of cat `p_l` is. **Important**: This will not override the game's selection process for patrol leaders. (e.g. You cannot use these constraints to make `p_l` a warrior leading their deputy on patrol, because the deputy will automatically be `p_l`.)

[Full Involved Cat Dictionary Information](../reference/involved-cat-dict.md)

#### relationship_constraint: list[dict]
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
  
***

#### patrol_temperament: list[str]
>List of allowed patrol temperaments. A patrol's temperament isn't set by you, it's calculated from the personalities of the cats on it, weighted so that a leader counts for more than a deputy, who counts for more than everyone else. The patrol leader gets a little extra weight on top of their rank. [Possible Tempers](../reference/tag-lists.md/#clan-temperaments). You can utilize [exclusionary tags](../reference/tag-lists.md#exclusionary-tags).

!!! tip
    Because temperament comes out of the cats you've already constrained, it's easy to write a patrol that can never appear. If you've required a bloodthirsty patrol, you've implicitly required a patrol full of low social, high aggression cats. Reach for this when the patrol's *mood* is the point, and prefer excluding a temperament that would read as wildly out of character over requiring a specific one.

***

#### other_clan_temperament: list[str]
>List of allowed temperaments for the other Clan involved in the patrol. [Possible Tempers](../reference/tag-lists.md/#clan-temperaments). You can utilize [exclusionary tags](../reference/tag-lists.md#exclusionary-tags).

!!! caution
    This only filters the temperament, it doesn't cause an other Clan to be involved. The patrol still needs to be an other Clan patrol for this to mean anything.

***

#### chance of success: int
>Control the chance for a patrol to succeed. Not an exact chance, since there are a lot of other factors (exp, skills, number of cats on the patrol) that affect the chance. Still, a higher number here indicates a higher chance to succeed. For a full explanation of how the game calculated success chance, check the [advanced documentation for success chance](../advanced-documentation.md/#success-chance-calculation).

> You do not need to adjust the success chance for different patrol sizes.  The success rate for a solo cat patrol should match its full patrol size variation.  Remember that each cat added to a patrol buffs its success chance, we don't need to give them any extra help.

> The rarer the patrol, the more you should feel comfortable differing from these guidelines. Factors that make patrols rarer are [frequency](#frequency-int), and the amount of constraints that cats must qualify for.

> For medicine cat patrols that involve 'magic', such as ghosts, StarClan, the Dark Forest, or anything else unnatural, you should not automatically use the default medicine success values. Instead, consult an experienced writer for adjusting your chance of success.

> Border patrols gain most of their danger not necessarily from an increased chance of failing, but from worse consequences being associated with their failure (death, massive injury). However, border patrols also tend to be more varied in their chance of success than most patrol types, with both extremely safe and extremely risky patrols present in the patrol pool. You are both welcome and encouraged to adjust the chance of success away from the default values.

> Tiri has made default success chances to work from for the general [non biome specific patrols](#default-success-any-biome), for [beach](#default-success-beach), for [desert](#default-success-desert), for [forest](#default-success-forest), for [mountains](#default-success-mountainous), for [plains](#default-success-plains), and for [wetlands](#default-success-wetlands).



##### Default Success Any Biome:

> This section covers the chance of success for the patrols that are general to any biome and season, in the resources/dicts/patrols/general folder, for border, hunting, medcat, and training. Therefore all these patrols do not have a chance of success that varies with the seasons.

| Patrol type             | Success chance         |
|-------------------------|------------------------|
| border                  | 40                     |
| hunting                 | 50                     |
| herb_gathering          | 50                     |
| training                | 60                     |



##### Default Success Beach:

| Season                        | Patrol type              | Success chance           |
|-------------------------------|--------------------------|--------------------------|
| Non-seasonal default          | training                 | 60                       |
| greenleaf                     | training                 | 65                       |
| leaf-bare                     | training                 | 55                       |
| leaf-fall                     | training                 | 60                       |
| newleaf                       | training                 | 60                       |
| ----------------------------- | ------------------------ | ------------------------ |
| Non-seasonal default          | hunting                  | 50                       |
| greenleaf                     | hunting                  | 50                       |
| leaf-bare                     | hunting                  | 40                       |
| leaf-fall                     | hunting                  | 50                       |
| newleaf                       | hunting                  | 50                       |
| ----------------------------- | ------------------------ | ------------------------ |
| Non-seasonal default          | border                   | 40                       |
| greenleaf                     | border                   | 50                       |
| leaf-bare                     | border                   | 40                       |
| leaf-fall                     | border                   | 40                       |
| newleaf                       | border                   | 40                       |
| ----------------------------- | ------------------------ | ------------------------ |
| Non-seasonal default          | herb_gathering           | 50                       |
| greenleaf                     | herb_gathering           | 60                       |
| leaf-bare                     | herb_gathering           | 40                       |
| leaf-fall                     | herb_gathering           | 50                       |
| newleaf                       | herb_gathering           | 50                       |
| ----------------------------- | ------------------------ | ------------------------ |



##### Default Success Desert:

| Season                        | Patrol type              | Success chance           |
|-------------------------------|--------------------------|--------------------------|
| Non-seasonal default          | training                 | 60                       |
| greenleaf                     | training                 | 40                       |
| leaf-bare                     | training                 | 70                       |
| leaf-fall                     | training                 | 60                       |
| newleaf                       | training                 | 60                       |
| ----------------------------- | ------------------------ | ------------------------ |
| Non-seasonal default          | hunting                  | 50                       |
| greenleaf                     | hunting                  | 30                       |
| leaf-bare                     | hunting                  | 65                       |
| leaf-fall                     | hunting                  | 50                       |
| newleaf                       | hunting                  | 50                       |
| ----------------------------- | ------------------------ | ------------------------ |
| Non-seasonal default          | border                   | 40                       |
| greenleaf                     | border                   | 20                       |
| leaf-bare                     | border                   | 60                       |
| leaf-fall                     | border                   | 40                       |
| newleaf                       | border                   | 40                       |
| ----------------------------- | ------------------------ | ------------------------ |
| Non-seasonal default          | herb_gathering           | 40                       |
| greenleaf                     | herb_gathering           | 30                       |
| leaf-bare                     | herb_gathering           | 50                       |
| leaf-fall                     | herb_gathering           | 40                       |
| newleaf                       | herb_gathering           | 40                       |
| ----------------------------- | ------------------------ | ------------------------ |



##### Default Success Forest:

| Season                        | Patrol type              | Success chance           |
|-------------------------------|--------------------------|--------------------------|
| Non-seasonal default          | training                 | 60                       |
| greenleaf                     | training                 | 70                       |
| leaf-bare                     | training                 | 50                       |
| leaf-fall                     | training                 | 60                       |
| newleaf                       | training                 | 60                       |
| ----------------------------- | ------------------------ | ------------------------ |
| Non-seasonal default          | hunting                  | 50                       |
| greenleaf                     | hunting                  | 60                       |
| leaf-bare                     | hunting                  | 35                       |
| leaf-fall                     | hunting                  | 50                       |
| newleaf                       | hunting                  | 50                       |
| ----------------------------- | ------------------------ | ------------------------ |
| Non-seasonal default          | border                   | 40                       |
| greenleaf                     | border                   | 50                       |
| leaf-bare                     | border                   | 30                       |
| leaf-fall                     | border                   | 40                       |
| newleaf                       | border                   | 40                       |
| ----------------------------- | ------------------------ | ------------------------ |
| Non-seasonal default          | herb_gathering           | 50                       |
| greenleaf                     | herb_gathering           | 60                       |
| leaf-bare                     | herb_gathering           | 40                       |
| leaf-fall                     | herb_gathering           | 50                       |
| newleaf                       | herb_gathering           | 50                       |
| ----------------------------- | ------------------------ | ------------------------ |



##### Default Success Mountainous:

| Season                        | Patrol type              | Success chance           |
|-------------------------------|--------------------------|--------------------------|
| Non-seasonal default          | training                 | 60                       |
| greenleaf                     | training                 | 70                       |
| leaf-bare                     | training                 | 40                       |
| leaf-fall                     | training                 | 60                       |
| newleaf                       | training                 | 60                       |
| ----------------------------- | ------------------------ | ------------------------ |
| Non-seasonal default          | hunting                  | 50                       |
| greenleaf                     | hunting                  | 65                       |
| leaf-bare                     | hunting                  | 35                       |
| leaf-fall                     | hunting                  | 50                       |
| newleaf                       | hunting                  | 50                       |
| ----------------------------- | ------------------------ | ------------------------ |
| Non-seasonal default          | border                   | 40                       |
| greenleaf                     | border                   | 60                       |
| leaf-bare                     | border                   | 20                       |
| leaf-fall                     | border                   | 40                       |
| newleaf                       | border                   | 40                       |
| ----------------------------- | ------------------------ | ------------------------ |
| Non-seasonal default          | herb_gathering           | 60                       |
| greenleaf                     | herb_gathering           | 70                       |
| leaf-bare                     | herb_gathering           | 40                       |
| leaf-fall                     | herb_gathering           | 60                       |
| newleaf                       | herb_gathering           | 60                       |
| ----------------------------- | ------------------------ | ------------------------ |



##### Default Success Plains:

| Season                        | Patrol type              | Success chance           |
|-------------------------------|--------------------------|--------------------------|
| Non-seasonal default          | training                 | 60                       |
| greenleaf                     | training                 | 70                       |
| leaf-bare                     | training                 | 50                       |
| leaf-fall                     | training                 | 60                       |
| newleaf                       | training                 | 60                       |
| ----------------------------- | ------------------------ | ------------------------ |
| Non-seasonal default          | hunting                  | 50                       |
| greenleaf                     | hunting                  | 60                       |
| leaf-bare                     | hunting                  | 35                       |
| leaf-fall                     | hunting                  | 50                       |
| newleaf                       | hunting                  | 50                       |
| ----------------------------- | ------------------------ | ------------------------ |
| Non-seasonal default          | border                   | 40                       |
| greenleaf                     | border                   | 50                       |
| leaf-bare                     | border                   | 30                       |
| leaf-fall                     | border                   | 40                       |
| newleaf                       | border                   | 40                       |
| ----------------------------- | ------------------------ | ------------------------ |
| Non-seasonal default          | herb_gathering           | 50                       |
| greenleaf                     | herb_gathering           | 60                       |
| leaf-bare                     | herb_gathering           | 40                       |
| leaf-fall                     | herb_gathering           | 50                       |
| newleaf                       | herb_gathering           | 50                       |
| ----------------------------- | ------------------------ | ------------------------ |



##### Default Success Wetlands:

| Season                        | Patrol type              | Success chance           |
|-------------------------------|--------------------------|--------------------------|
| Non-seasonal default          | training                 | 60                       |
| greenleaf                     | training                 | 65                       |
| leaf-bare                     | training                 | 55                       |
| leaf-fall                     | training                 | 60                       |
| newleaf                       | training                 | 60                       |
| ----------------------------- | ------------------------ | ------------------------ |
| Non-seasonal default          | hunting                  | 50                       |
| greenleaf                     | hunting                  | 50                       |
| leaf-bare                     | hunting                  | 40                       |
| leaf-fall                     | hunting                  | 50                       |
| newleaf                       | hunting                  | 50                       |
| ----------------------------- | ------------------------ | ------------------------ |
| Non-seasonal default          | border                   | 40                       |
| greenleaf                     | border                   | 50                       |
| leaf-bare                     | border                   | 40                       |
| leaf-fall                     | border                   | 40                       |
| newleaf                       | border                   | 40                       |
| ----------------------------- | ------------------------ | ------------------------ |
| Non-seasonal default          | herb_gathering           | 60                       |
| greenleaf                     | herb_gathering           | 70                       |
| leaf-bare                     | herb_gathering           | 50                       |
| leaf-fall                     | herb_gathering           | 60                       |
| newleaf                       | herb_gathering           | 60                       |
| ----------------------------- | ------------------------ | ------------------------ |



***


#### patrol_art: str
>The name of displayed patrol art file, without any file extension (no .png).
>
> Example: "patrol_art": "bord_general_intro",


***

#### patrol_art_clean: str
>If patrol_art contains gore, this line can hold a clean version. The existence of a non-empty string in this parameter marks the patrol art in "patrol_art" as explicit. The game will then use the clean version if the "Allow mild gore and blood in patrol artwork" setting is off, and the explicit version if this setting is on. Specify art by using the name of the image without the file extension (no .png).
>
> Example: "patrol_art_clean": "bord_general_intro",


***


#### intro_strings: list[str]
>The text that displays when the patrol first starts. You can add multiple options to this list and a random one will be chosen to be displayed.


***

#### decline_strings: list[str]
>The text that displays if the patrol is declined (do not proceed.) You can add multiple options to this list and a random one will be chosen to be displayed.


***

#### success_outcomes: list[TextPoolEvent]
> The possible success outcomes. Utilize the [patrol outcome format](patrol_outcome.md). Patrols must have at least one success.

***

#### fail_outcomes: list[TextPoolEvent]
> The possible fail outcomes. Utilize the [patrol outcome format](patrol_outcome.md). Patrols must have at least one fail.

***

#### antag_success_outcomes: list[TextPoolEvent]
> The possible antagonize success outcomes. Utilize the [patrol outcome format](patrol_outcome.md). Antagonize outcomes can be added for patrols involving outsiders, other clan cats, or afterlife visitors.

***

#### antag_fail_outcomes: list[TextPoolEvent]
> The possible antagonize fail outcomes. Utilize the [patrol outcome format](patrol_outcome.md). Antagonize outcomes can be added for patrols involving outsiders, other clan cats, or afterlife visitors.

***

## What To Consider When Assessing Older Patrols

When assessing an older patrol for ways to make its information clearer or more condensed, there's a few common problems you can look for.

### Required Cats

Check the `required_cat_types` for extraneous or confusing information. For example:

```json
    "required_cat_types":{
        "patrol_cats": [2, 2],
        "warrior": [2, 6],
        "apprentice": [-1, -1]
    }
```

* The `warrior` entry should be `[2, 2]` as `patrol_cats` has established that there can never be more than 2 cats on this patrol.
* The `apprentice` entry could be removed. It's trying to ensure that no apprentices are allowed, but we've already specified that 2 warriors are necessary on the patrol and only 2 cats can be on the patrol. Thus we know those 2 cats must already be warriors.

A "cleaned" version of that example would be:
```json
    "required_cat_types":{
        "patrol_cats": [2, 2],
        "warrior": [2, 2]
    }
```

### Use of s_c

#### Explanation of Use

`s_c`'s current use is to allow already-designated cats as well as un-designated cats to take on a new `s_c` designation. 

For example, let's say our patrol intro is `"p_l leads the patrol towards a gully where they encounter a fox."`.  We decide we want an outcome to allow *any* cat in the patrol with the `FIGHTER` skill to defeat the fox. We *could* add a new `involved_cat` role for a `r_c`, but the cat who is `p_l` won't be able to take this role as they are already `p_l`.  If we did this, it would look like:

```json
    "involved_cats": {
        "r_c0": {
            "stat": {
                "skill": ["FIGHTER,1"]
            }      
        }   
    }
```

If we want `p_l` to have a chance to take that role, then we can make our `FIGHTER` involved cat `s_c0` and specify their `prior_abbreviation` as `["any"]`. Now any cat, including `p_l` can be `s_c0`.  This would change our `involved_cats` to look like this:

```json
    "involved_cats": {
        "s_c0": {
            "prior_abbreviation": ["any"],
            "stat": {
                "skill": ["FIGHTER,1"]
            }      
        }   
    }
```

However, let's say that we actually *do* have a specific cat we would like to be the fighter!  Perhaps we *only* want `p_l` to be the `FIGHTER` cat.  In this case, we don't even need to use `s_c` or `prior_abbreviation`.  Instead, we could just specify it as a further constraint on `p_l` like so:

```json
    "involved_cats": {
        "p_l": {
            "stat": {
                "skill": ["FIGHTER,1"]
            }      
        }   
    }
```

#### Applying This Knowledge

With all of this in mind, let's look at common mishaps that may be present in patrols.

* Utilizing s_c needlessly
```json
    "involved_cats": {
        "s_c0": {
            "prior_abbreviation": ["p_l"],
            "stat": {
                "skill": ["FIGHTER,1"]
            }      
        }   
    }
```
In this example, the only `prior_abbreviation` allowed is `p_l`!  In this case, we shouldn't be using `s_c` at all and should just apply this constraint to `p_l` like:
```json
    "involved_cats": {
        "p_l": {
            "stat": {
                "skill": ["FIGHTER,1"]
            }      
        }   
    }
```

* No `prior_abbreviation`
```json
    "involved_cats": {
        "s_c0": {
            "stat": {
                "skill": ["FIGHTER,1"]
            }      
        }   
    }
```
If no `prior_abbreviation` is given, then `s_c` is treated like any other cat designation. That is, it will find a cat who has not been given a designation yet. Since this is the *normal* behavior for cat designations, there's no need for this to be an `s_c` abbreviation.
The patrol should be assessed to check if:

    * A prior abbreviation should be added, such as `"any"`
```json
    "involved_cats": {
        "s_c0": {
            "prior_abbreviation": ["any"]
            "stat": {
                "skill": ["FIGHTER,1"]
            }      
        }   
    }
```

    * Or `s_c0` replaced with a normal designation
```json
    "involved_cats": {
        "r_c0": {
            "stat": {
                "skill": ["FIGHTER,1"]
            }      
        }   
    }
```

### Near-Duplicate Patrols

Check if this patrol is a near-duplicate to other patrols. If it is, consider if you could utilize outcome-level `location`, `season`, `tags`, or other constraints to combine the patrols.

### Romance Constraints

Patrols used to be determined as "romance" purely based off the `romance` tag. Now they can also dictate *who* on the patrol is engaging in romance via the `relationship_constraint` constraint: `can_romance`.

Previously, the `romance` tag assumed that all cats on the patrol were intended as romantic interests with each other. Thus, the automatic script conversion created the new `can_romance` `relationship_constraint` dicts as being from `patrol_cats` *to* `patrol_cats`.

This isn't necessarily accurate to the intention of all these patrols, and thus the `cats_from` and `cats_to` of these `relationship_constraint` dicts should be assessed. Don't worry! Patrols that have been mistagged in this fashion won't appear in the game, they'll be filtered out as impossible. So we won't have patrols trying to pair two cats together inappropriately, we'll just have patrols that don't appear at all.

You can also check if the `romance` tag and `relationship_constraint` could be moved into an outcome rather than being patrol-wide. 

### Don't Re-iterate

There's no need to "repeat" a constraint in a different manner. For example:

```json
    "required_cat_types":{
        "patrol_cats": [1, 1],
        "warrior": [1, 1]
    },
    "involved_cats": {
        "p_l": {
            "status": ["warrior"]    
        }   
    }
```

* We know this patrol only allows 1 warrior. Thus, we don't need to constraint `p_l` to be a warrior as only warriors are allowed.


### Keep It Consistent

Each cat can only have one designation, with the exception of `s_c` designations. This differs from the prior version of patrols, where a cat could have many designations (i.e. `app1` could also be `r_c` and `p_l` depending on what other cats were on the patrol). This inconsistency means that some old patrols will have "mismatched" designations.  

For example, you might see:
```json
    "strings": ["p_l dies."],
    "death": {
        "cats": ["r_c0"]
    },
```

* `p_l` is dying in the string, but `r_c0` is dying in the `death` dict. It's likely that this patrol used to be written with the assumption that `p_l` was also `r_c`. This no longer works and so this should be adjusted to:
```json
    "strings": ["p_l dies."],
    "death": {
        "cats": ["p_l"]
    },
```
