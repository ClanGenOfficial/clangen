# Patrols

## Guidelines
When considering patrols, keep in mind challenge vs reward. That isn't to say certain patrol events should necessarily be locked behind certain patrol sizes, but try to imagine what a group of cats that size would do in a given situation, and how likely it would be for them to succeed in whatever it is they're trying to do. If making large size and small sized variants of the same patrol, it's encouraged to give different outcomes even if the success chance is the same for both variants. For example, 6 cats have very different options for dealing with an owl than 2 cats do.

!!! todo "TODO"
    add some guidelines here for success chance and weights, just an idea of number baselines compared to the current patrol spread

!!! todo "TODO"
    add guidelines regarding tracking and requests sheets for art

!!! todo "TODO"
    add guide to hunting filtering code


### Replacement Text
When writing the text for patrol events, we use a variety of abbreviations that will later be replaced automatically before displaying to the player.  These are things like names and pronouns.  Pronoun Tagging is discussed in the basic guidelines.

| string      |                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| p_l         | Random cat, a (mostly) randomly selected cat in the patrol.  When used on it's own this will generate the cat's name, when used in a pronoun tag this will generate that cat's pronouns.                                                                                                                                                                                                                                                                   |
| s_c         | Stat cat, a cat with one of the indicated outcome stats.    When used on it's own this will generate the cat's name, when used in a pronoun tag this will generate that cat's pronouns.                                                                                                                                                                                                                                                                    |
| app1        | The first apprentice on the patrol.  When used on it's own this will generate the cat's name, when used in a pronoun tag this will generate that cat's pronouns.                                                                                                                                                                                                                                                                                           |
| app2        | The second apprentice on the patrol.  When used on it's own this will generate the cat's name, when used in a pronoun tag this will generate that cat's pronouns.                                                                                                                                                                                                                                                                                          |
| n_c:{index} | The newly generated cat specified in list index {index}. The list is 0-indexed, so the first entry is 0. If more than one cat is generated in a single list entry (for example, a litter), this will use the first generated cat. Currently, there is no way to retrieve the name's or pronouns of other members of a litter.  When used on it's own this will generate the cat's name, when used in a pronoun tag this will generate that cat's pronouns. |

!!! todo "TODO"
    look over patrol code and find the other abbreviations, i know this ain't all of it

## Formatting

!!! tip
    If you are new to patrol writing, I recommend going through the [Full Featured Patrol Example](#full-featured-patrol-example) line by line and reading the following parameter explanations as you do.

    Likewise, before beginning, be sure to at least read the first section of [Coding Terms for Writers to Know](index.md#coding-terms-for-writers-to-know). This explains much of the terminology used here.

### Patrol Template
This is a good starting point for writing your own patrols. 

```json
{
    "patrol_id": "some_unique_id",
    "biome": [],
    "season": [],
    "types": [],
    "tags": [],
    "patrol_art": null,
    "patrol_art_clean": null,
    "min_cats": 1,
    "max_cats": 6,
    "min_max_status": {
        "apprentice": [
            0,
            6
        ],
        "medicine cat apprentice": [
            0,
            6
        ],
        "medicine cat": [
            0,
            6
        ],
        "deputy": [
            0,
            6
        ],
        "warrior": [
            0,
            6
        ],
        "leader": [
            0,
            6
        ],
        "healer cats": [
            0,
            6
        ],
        "normal adult": [
            0,
            6
        ],
        "all apprentices": [
            0,
            6
        ]
    },
    "weight": 20,
    "chance_of_success": 50,
    "relationship_constraint": [],
    "pl_skill_constraint": [],
    "intro_text": "The patrol heads out.",
    "decline_text": "And they head right back!",
    "success_outcomes": [
        {
            SEE OUTCOME BLOCK TEMPLATE
        },
        {
            SEE OUTCOME BLOCK TEMPLATE
        }
    ],
    "fail_outcomes": [
        {
            SEE OUTCOME BLOCK TEMPLATE
        },
        {
            SEE OUTCOME BLOCK TEMPLATE
        }
    ],
    "antag_success_outcomes": [
        {
            SEE OUTCOME BLOCK TEMPLATE
        },
        {
            SEE OUTCOME BLOCK TEMPLATE
        }
    ],
    "antag_fail_outcomes": [
        {
            SEE OUTCOME BLOCK TEMPLATE
        },
        {
            SEE OUTCOME BLOCK TEMPLATE
        }
    ]
}
```

### By Parameter - Patrol
What each parameter does, and what the options are for patrol.

***

#### patrol_id:str
>patrol_id is a unique string used to identify the patrol. It does not affect patrol behavior, but it allows us to easily find patrols.

> A patrol_id is formatted as following: `biome_type_enemy_seasondescription#`, enemy and season are optional (some patrols do not have a specific enemy or season), # is a number at the end of the descriptive section starting at 1 and incrementing up as you create new versions of that patrol. 
>
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

#### biome: list[str]
>This controls the biome the patrol appears in. 

| string        | use                              |
|---------------|----------------------------------|
| "mountainous" | appears in the mountainous biome |
| "plains"      | appears in the plains biome      |
| "forest"      | appears in the forest biome      |
| "beach"       | appears in the beach biome       |
| "wetlands"    | appears in the wetlands biome    |
| "desert"      | appears in the desert biome      |
| "any"         | appears in any biome             |

Please have a look at the [full biome differences list](index.md#clangen-biomes) when thinking about writing patrols. 


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
> Training patrols are an easy difficulty for [success chance](#chance-of-success-int), but the lowest with regards to [exp reward](#exp-int). They are a relatively safe patrol type of low danger, and the [injuries](#injury-listdictstr-various) cats can obtain on them should either be rare (low weighed outcome), or minor. Training patrols have high [relationship rewards](#relationships-listdictstr-various).

> Hunting patrols are of moderate difficulty for [success chance](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#chance-of-success-int).  Hunting patrols are subject to [extra filtering](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Advanced-documentation#todo-hunting-filtering-in-depth) that effects what patrols are available based on their [prey reward](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#prey-liststr). This filtering ensures that we cannot starve out the player's cats simply by adding too many patrols that give out a certain prey reward. Hunting patrols are of medium danger, and the [injuries](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#injury-listdictstr-various) cats can obtain on them should either be minor and common (high weighed outcome), moderate and of a normal weight, or severe and of a low weight. The same guidelines apply to [killing cats](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#dead_cats-liststr) on this patrol type. Hunting patrols should have only minor [relationship rewards](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#relationships-listdictstr-various) (less than 5) unless the hunting patrol text focuses on the relationship, e.g a warrior and a apprentice hunting together with the warrior teaching the apprentice.

> Border patrols needs to be the hardest and most dangerous, with a high difficulty for [success chance](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#chance-of-success-int).  This is where experienced cats should shine! The [injuries](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#injury-listdictstr-various) cats can obtain on them should be a wide range. Failure outcomes on border patrols that don't cause injury should be rare. You are encouraged to apply minor injuries even on success outcome. The same guidelines apply to [killing cats](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#dead_cats-liststr) on this patrol type, with the exception that you cannot kill cats on any success outcomes. This is by far the mostly likely patrol type to have cats become [lost](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#lost_cats-liststr) on.

> Herb gathering patrols are of moderate difficulty for [success chance](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#chance-of-success-int) (like hunting patrols). Herb gathering patrols are focused on gathering herbs and thus need to have a [herb reward](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#herbs-liststr) under most circumstances. Herb gathering patrols are of medium danger, and the [injuries](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#injury-listdictstr-various) cats can obtain on them should either be minor and common (high weighed outcome), moderate and of a normal weight, or severe and of a low weight. The same guidelines apply to [killing cats](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#dead_cats-liststr) on this patrol type. Herb gathering patrols should be highly seasonal, as not all herbs are available in all seasons, or in the same seasons in different [biomes](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Basic#clangen-biomes). 

> The subtypes of [new_cat](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#outsider_rep) and [other_clan](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#other_clan_rep) patrols should primarily use the type specific success, danger, injuries, death, and rewards of whatever the primary patrol type is. For example, use the success chance for herd gathering patrols if your medicine cat finds an injured kitten. However, a subtype is more likely to move away from the 'normal' setting for that type of patrol as they are by definition unusual examples of that patrol type. Brainstorm with other developers!


!!! tip
    There are two further subtypes of patrols which occur as isolated events within the four main types. These are other_clan and new_cat patrols. Other clan patrols deal with the Clans neighboring the player Clan and are discussed [here](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#other_clan_rep). New cat patrols deal with patrols where a new cat joins the player Clan. The chance of finding a new_cat patrol is discussed [here](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#outsider_rep), the new_cat tag is discussed [here](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#tags-liststr), and the code to generate a new_cat is discussed [here](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#new_cat-listliststr). A patrol is firstly one of the four types, e.g herb gathering, and then can also be a other_clan or new_cat (or both!) patrol in addition to the four basic types. 


***

#### tags: list[str]
>Tags are used for some filtering purposes, and some odd-and-ends. Tags never affect outcome. 

| tag            | use                                                                                                                                                                                                                                                                                                                   |
|----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| "romantic"      | Marks the patrol as a romance patrol. Romance patrols are special, and are filtered to require patrol leader (p_l) and random cat (r_c) to to be potential mates or current mates. If any outcomes have effects on romantic-like, make sure this tag has been added, and the romantic-like is applied to p_l and r_c. |
| "rom_two_apps" | Does nothing on its own. When "romance" present, check for potential mate or current mate between app1 and app2, rather than p_l and r_c                                                                                                                                                                              |
| "disaster"     | These patrols are only possible when mass extinction is turned ON. Used to mark patrols where the entire patrol can die or become lost.                                                                                                                                                                               |
| "new_cat"      | Used to mark when a new cat can join during this patrol. Marking these patrols allows for better balancing.                                                                                                                                                                                                           |
| "halloween"    | Used to mark patrols that should only occur around halloween                                                                                                                                                                                                                                                          |
| "april_fools"  | Used to mark patrols that should only occur on april fools                                                                                                                                                                                                                                                            |
| "new_years"    | Used to mark patrols that should only occur on new years.                                                                                                                                                                                                                                                             |


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

#### min_cats: int
>Minimum total number of cats for this patrol. An _integer_ (number) is needed here.


***

#### max_cats: int
>Maximum total number of cats for this patrol. An _integer_ (number) is needed here.


***

#### min_max_status: Dict[str, List[int]]
>Optional. Allows specification of the minimum and maximum number of specific types of cats that are allowed on the patrol. The format for each dictionary entry is 
>
>`"status_type": [min_value, max_value]`
>
>To specify that a type of cat can't be on the patrol, use [-1, -1]

| status types              |                                                                     |
|---------------------------|---------------------------------------------------------------------|
| "medicine cat"            | Total medicine cats (not including apprentices)                     |
| "warrior"                 | Total number of warriors (not including leader or deputy)           |
| "leader"                  | Total number of leaders                                             |
| "deputy"                  | Total number of deputies                                            |
| "apprentice"              | Total number of warrior apprentices                                 |
| "medicine cat apprentice" | Total number of medicine cat apprentices                            |
| "healer cats"             | Total number of medicine cats and medicine cat apprentices combined |
| "normal adult"            | Total number of warriors, leaders and deputies                      |
| "all apprentices"         | Total number of warrior apprentices and medicine cat apprentices.   |


***

#### weight: int
>Controls how common a patrol is. A "normal" patrol would be ~20. A lower number makes the patrol less common, and a higher number make the patrol more common

> Most constrained patrols ([relationship](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#relationship_constraint-liststr) or [p_l skill](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#pl_skill_constraint-liststr) constraints) have a weight of 40, making them twice as likely to trigger if the conditions to unlock them are met.

> The default weight for patrols in the general training json (that is, training patrols that can be triggered no matter what the biome) that don't have any constraints on the patrol ([relationship](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#relationship_constraint-liststr) or [p_l skill](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#pl_skill_constraint-liststr) constraints) is 5. This is so that these patrols are four times less likely to be chosen than biome specific content. 

> The general hunting and border jsons have balancing patrols in them. These have very low weights (between 1-5) and aren't very interesting patrols, but they are made so that no matter what biome and season it is, the game has a pool of valid hunting and border patrols to choose from. 

!!! tip
    Hunting patrols have an additional level of filtering active above the patrol weights. First the game decides what prey reward the patrol should give (based on chances that change depending on the biome and season), and then, from the patrols that give that prey reward _as a non-stat success_, the acceptable patrols are weighed against each other. This naturally makes patrols that give huge prey rewards rare, no matter how many of those patrols you write. Don't worry about weighing hunting patrols according to their prey reward. Instead make each hunting patrol give roughly the same prey reward for all non-stat successes. The hunting filtering code will make sure the appropriate amount of prey is given. 


***

#### chance of success: int
>Control the chance for a patrol to succeed. Not an exact chance, since there are a lot of other factors (exp, skills, number of cats on the patrol) that affect the chance. Still, a higher number here indicates a higher chance to succeed. For a full explanation of how the game calculated success chance, check the [advanced documentation for success chance](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Advanced-documentation#success-chance-calculation).

> You do not need to adjust the success chance for different patrol sizes.  The success rate for a solo cat patrol should match its full patrol size variation.  Remember that each cat added to a patrol buffs its success chance, we don't need to give them any extra help.

> The rarer the patrol, the more you should feel comfortable differing from these guidelines. Factors that make patrols rarer are [weight](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#weight-int), constraints ([relationship](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#relationship_constraint-liststr) or [p_l skill](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#pl_skill_constraint-liststr)), [min_max_status](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#min_max_status-dictstr-listint) for example requiring the patrol to have both the leader and deputy on it to unlock, [patrol size](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#min_cats-int), and the subtypes of [new_cat](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#outsider_rep) and [other_clan](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#other_clan_rep) 

> For medicine cat patrols that involve 'magic', such as ghosts, StarClan, the Dark Forest, or anything else unnatural, you should not automatically use the default medicine success values. Instead, consult an experienced writer for adjusting your chance of success.

> Border patrols gain most of their danger not necessarily from an increased chance of failing, but from worse consequences being associated with their failure (death, massive injury). However, border patrols also tend to be more varied in their chance of success than most patrol types, with both extremely safe and extremely risky patrols present in the patrol pool. You are both welcome and encouraged to adjust the chance of success away from the default values.

> Tiri has made default success chances to work from for the general [non biome specific patrols](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#default-success-any-biome), for [beach](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#default-success-beach), for [desert](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#default-success-desert), for [forest](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#default-success-forest), for [mountains](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#default-success-mountainous), for [plains](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#default-success-plains), and for [wetlands](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Patrols#default-success-wetlands).



##### Default Success Any Biome:

> This section covers the chance of success for the patrols that are general to any biome and season, in the resources/dicts/patrols/general folder, for border, hunting, medcat, and training. Therefore all these patrols do not have a chance of success that varies with the seasons.

| Patrol type             | Success chance         |
|-------------------------|------------------------|
| border                  | 40                     |
| hunting                 | 50                     |
| herb_gathering          | 50                     |
| training                | 60                     |



##### Default Success Beach: 

| Season                      | Patrol type            | Success chance         |
|-----------------------------|------------------------|------------------------|
| Non-seasonal default        | training               | 60                     |
| greenleaf                   | training               | 65                     |
| leaf-bare                   | training               | 55                     |
| leaf-fall                   | training               | 60                     |
| newleaf                     | training               | 60                     |
|-----------------------------|------------------------|------------------------|
| Non-seasonal default        | hunting                | 50                     |
| greenleaf                   | hunting                | 50                     |
| leaf-bare                   | hunting                | 40                     |
| leaf-fall                   | hunting                | 50                     |
| newleaf                     | hunting                | 50                     |
|-----------------------------|------------------------|------------------------|
| Non-seasonal default        | border                 | 40                     |
| greenleaf                   | border                 | 50                     |
| leaf-bare                   | border                 | 40                     |
| leaf-fall                   | border                 | 40                     |
| newleaf                     | border                 | 40                     |
|-----------------------------|------------------------|------------------------|
| Non-seasonal default        | herb_gathering         | 50                     |
| greenleaf                   | herb_gathering         | 60                     |
| leaf-bare                   | herb_gathering         | 40                     |
| leaf-fall                   | herb_gathering         | 50                     |
| newleaf                     | herb_gathering         | 50                     |
|-----------------------------|------------------------|------------------------|



##### Default Success Desert: 

| Season                      | Patrol type            | Success chance         |
|-----------------------------|------------------------|------------------------|
| Non-seasonal default        | training               | 60                     |
| greenleaf                   | training               | 40                     |
| leaf-bare                   | training               | 70                     |
| leaf-fall                   | training               | 60                     |
| newleaf                     | training               | 60                     |
|-----------------------------|------------------------|------------------------|
| Non-seasonal default        | hunting                | 50                     |
| greenleaf                   | hunting                | 30                     |
| leaf-bare                   | hunting                | 65                     |
| leaf-fall                   | hunting                | 50                     |
| newleaf                     | hunting                | 50                     |
|-----------------------------|------------------------|------------------------|
| Non-seasonal default        | border                 | 40                     |
| greenleaf                   | border                 | 20                     |
| leaf-bare                   | border                 | 60                     |
| leaf-fall                   | border                 | 40                     |
| newleaf                     | border                 | 40                     |
|-----------------------------|------------------------|------------------------|
| Non-seasonal default        | herb_gathering         | 40                     |
| greenleaf                   | herb_gathering         | 30                     |
| leaf-bare                   | herb_gathering         | 50                     |
| leaf-fall                   | herb_gathering         | 40                     |
| newleaf                     | herb_gathering         | 40                     |
|-----------------------------|------------------------|------------------------|



##### Default Success Forest: 

| Season                      | Patrol type            | Success chance         |
|-----------------------------|------------------------|------------------------|
| Non-seasonal default        | training               | 60                     |
| greenleaf                   | training               | 70                     |
| leaf-bare                   | training               | 50                     |
| leaf-fall                   | training               | 60                     |
| newleaf                     | training               | 60                     |
|-----------------------------|------------------------|------------------------|
| Non-seasonal default        | hunting                | 50                     |
| greenleaf                   | hunting                | 60                     |
| leaf-bare                   | hunting                | 35                     |
| leaf-fall                   | hunting                | 50                     |
| newleaf                     | hunting                | 50                     |
|-----------------------------|------------------------|------------------------|
| Non-seasonal default        | border                 | 40                     |
| greenleaf                   | border                 | 50                     |
| leaf-bare                   | border                 | 30                     |
| leaf-fall                   | border                 | 40                     |
| newleaf                     | border                 | 40                     |
|-----------------------------|------------------------|------------------------|
| Non-seasonal default        | herb_gathering         | 50                     |
| greenleaf                   | herb_gathering         | 60                     |
| leaf-bare                   | herb_gathering         | 40                     |
| leaf-fall                   | herb_gathering         | 50                     |
| newleaf                     | herb_gathering         | 50                     |
|-----------------------------|------------------------|------------------------|



##### Default Success Mountainous: 

| Season                      | Patrol type            | Success chance         |
|-----------------------------|------------------------|------------------------|
| Non-seasonal default        | training               | 60                     |
| greenleaf                   | training               | 70                     |
| leaf-bare                   | training               | 40                     |
| leaf-fall                   | training               | 60                     |
| newleaf                     | training               | 60                     |
|-----------------------------|------------------------|------------------------|
| Non-seasonal default        | hunting                | 50                     |
| greenleaf                   | hunting                | 65                     |
| leaf-bare                   | hunting                | 35                     |
| leaf-fall                   | hunting                | 50                     |
| newleaf                     | hunting                | 50                     |
|-----------------------------|------------------------|------------------------|
| Non-seasonal default        | border                 | 40                     |
| greenleaf                   | border                 | 60                     |
| leaf-bare                   | border                 | 20                     |
| leaf-fall                   | border                 | 40                     |
| newleaf                     | border                 | 40                     |
|-----------------------------|------------------------|------------------------|
| Non-seasonal default        | herb_gathering         | 60                     |
| greenleaf                   | herb_gathering         | 70                     |
| leaf-bare                   | herb_gathering         | 40                     |
| leaf-fall                   | herb_gathering         | 60                     |
| newleaf                     | herb_gathering         | 60                     |
|-----------------------------|------------------------|------------------------|



##### Default Success Plains: 

| Season                      | Patrol type            | Success chance         |
|-----------------------------|------------------------|------------------------|
| Non-seasonal default        | training               | 60                     |
| greenleaf                   | training               | 70                     |
| leaf-bare                   | training               | 50                     |
| leaf-fall                   | training               | 60                     |
| newleaf                     | training               | 60                     |
|-----------------------------|------------------------|------------------------|
| Non-seasonal default        | hunting                | 50                     |
| greenleaf                   | hunting                | 60                     |
| leaf-bare                   | hunting                | 35                     |
| leaf-fall                   | hunting                | 50                     |
| newleaf                     | hunting                | 50                     |
|-----------------------------|------------------------|------------------------|
| Non-seasonal default        | border                 | 40                     |
| greenleaf                   | border                 | 50                     |
| leaf-bare                   | border                 | 30                     |
| leaf-fall                   | border                 | 40                     |
| newleaf                     | border                 | 40                     |
|-----------------------------|------------------------|------------------------|
| Non-seasonal default        | herb_gathering         | 50                     |
| greenleaf                   | herb_gathering         | 60                     |
| leaf-bare                   | herb_gathering         | 40                     |
| leaf-fall                   | herb_gathering         | 50                     |
| newleaf                     | herb_gathering         | 50                     |
|-----------------------------|------------------------|------------------------|



##### Default Success Wetlands: 

| Season                      | Patrol type            | Success chance         |
|-----------------------------|------------------------|------------------------|
| Non-seasonal default        | training               | 60                     |
| greenleaf                   | training               | 65                     |
| leaf-bare                   | training               | 55                     |
| leaf-fall                   | training               | 60                     |
| newleaf                     | training               | 60                     |
|-----------------------------|------------------------|------------------------|
| Non-seasonal default        | hunting                | 50                     |
| greenleaf                   | hunting                | 50                     |
| leaf-bare                   | hunting                | 40                     |
| leaf-fall                   | hunting                | 50                     |
| newleaf                     | hunting                | 50                     |
|-----------------------------|------------------------|------------------------|
| Non-seasonal default        | border                 | 40                     |
| greenleaf                   | border                 | 50                     |
| leaf-bare                   | border                 | 40                     |
| leaf-fall                   | border                 | 40                     |
| newleaf                     | border                 | 40                     |
|-----------------------------|------------------------|------------------------|
| Non-seasonal default        | herb_gathering         | 60                     |
| greenleaf                   | herb_gathering         | 70                     |
| leaf-bare                   | herb_gathering         | 50                     |
| leaf-fall                   | herb_gathering         | 60                     |
| newleaf                     | herb_gathering         | 60                     |
|-----------------------------|------------------------|------------------------|



***

#### relationship_constraint: List[str]
>Optional. Only allows the patrol if the cats meet relationship constraints. You can include any tags in [Relationship Levels](reference/tag-lists.md#relationship-levels) and [Relationship Types](reference/tag-lists.md#relationship-types).

***

#### pl_skill_constraint: List[str]
>Optional. Only allow this patrol if the patrol leader (p_l) meets at least one of these skill requirements. Skills are formatted "_skillname_, _level_". See skills here: [Skill list](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-Basic#skills)

>Example: `"pl_skill_constraint": ["TEACHER,1", "INSIGHTFUL,1", "KIT,1", "CAMP,1"],`


***

#### intro_text: str
>The text that displays when the patrol first starts.


***

#### decline_text: str
>The text that displays if the patrol is declined (do not proceed)


***

### Outcome Block Template
This is a good starting point for writing your own outcomes.

```json
{
    "text": "The raw displayed outcome text.",
    "exp": 0,
    "weight": 20,
    "stat_skill": [],
    "stat_trait": [],
    "can_have_stat": [],
    "prey": [],
    "herbs": [],
    "lost_cats": [],
    "dead_cats": [],
    "outsider_rep": null,
    "other_clan_rep": null,
    "injury": [
        {
            "cats": [],
            "injuries": [],
            "scars": [],
            "no_results": false
        }
    ],
    "history_text": {
        "reg_death": "m_c died while on a patrol.",
        "lead_death": "died on patrol",
        "scars": "m_c was scarred on patrol"
    },
    "relationships": [
        {
            "cats_to": [],
            "cats_from": [],
            "mutual": false,
            "values": [],
            "amount": 5
        }
    ],
    "new_cat": [],
    "art": "patrol_outcome_art",
    "art_clean": "non_gore_outcome_art",
    "future_event": []
}
```

### By-Parameter - Outcome
What each parameter does, and what the options are for outcomes.

***

#### text: str
>The displayed text. Unlike intro text, can include stat cat (s_c) and new cat (n_c:{index}) names.
>

***

#### exp: int
>The amount of exp cats receive (sorta). The exact amount also depends on the number of cats and current EXP levels, but in general, a higher number here means more exp. If exp is 0, no exp will be given. 
>

***

#### stat_skill: List[str]
>Optional. Including this "stat_skill" or "stat_trait" makes this a stat outcome, which can only occur if a stat cat can be found. Requires stat cats to have at least one of these skills. For s_c to be used anywhere in the outcome, "stat_skill" or "stat_trait" must be included. See elsewhere for skill formatting. 
>

***

#### stat_trait: List[str]
>Optional. Including this "stat_skill" or "stat_trait" makes this a stat outcome, which can only occur if a stat cat can be found. Requires stat cats to have one of these traits. For s_c to be used anywhere in the outcome, "stat_skill" or "stat_trait" must be included.
>

***

#### can_have_stat: List[str]
>Optional, although strongly encouraged for all outcomes (it helps with readability and catching errors). Overrides default behavior or adds additional requirements for stat_cat picking. 
>
>Default behavior: 
>In 1 and 2 cat patrols, only p_l can be stat_cat.
>
>In 3+ cat patrols, p_l and r_c can't be stat_cat, but anyone else is eligible. 

>To override default behavior:

| string      | new behavior                                                                                                                                                                                                                                                 |
|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| "p_l"       | Patrol leader (p_l) can be stat cat                                                                                                                                                                                                                          |
| "r_c"       | Random cat can be stat cat                                                                                                                                                                                                                                   |
| "app1"      | app1 (the first apprentice) can be stat cat                                                                                                                                                                                                                  |
| "app2"      | app2 (the second apprentice) can be stat cat                                                                                                                                                                                                                 |
| "not_pl_rc" | Any cat but p_l or r_c can be stat_cat. This is the default behavior for 3 + cat patrols. This allows that requirement to be applied to 2 and 1 cat patrols. Note that, with this constraint, no cats will be allowed to be stat_cat on 1 and 2 cat patrols. |
| "not_pl"    | Any cat but p_l can be stat cat                                                                                                                                                                                                                              |
| "not_rc"    | Any cat but r_c can be stat cat                                                                                                                                                                                                                              |
| "any"       | Any cat can be stat_cat. Still subject to the additional requirement tags below, if present. Be careful with using s_c's name when this is used - it might lead to self-interaction                                                                          |

>To add additional requirements to stat_cat:

| string      | additional requirement                                                                                                                             |
|----------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| "adult"  | Stat cat can't be an apprentice. Note that this doesn't override default behavior, only adds an additional requirement.                            |
| "app"    | Stat cat must be an apprentice. Note that this doesn't override default behavior, only adds an additional requirement.                             |
| "healer" | Stat cat must be a medicine cat or medicine cat apprentice. Note that this doesn't override default behavior, only adds an additional requirement. |

>

***

#### prey: List[str]


***

#### herbs: List[str]


***

#### lost_cats: List[str]
>Optional. Indicates which cats will become lost. 

| string   |                                                   |
|----------|---------------------------------------------------|
| "p_l"    | Patrol leader (p_l) becomes lost                  |
| "r_c"    | Random cat becomes lost                           |
| "s_c"    | stat cat (s_c) becomes lost                       |
| "app1"   | app1 (the first apprentice) becomes lost          |
| "app2"   | app2 (the second apprentice) becomes lost         |
| "patrol" | The entire patrol becomes lost                    |
| "multi"  | Multiple, but not all, of the patrol becomes lost |

>

***

#### dead_cats: List[str]
>Optional. Indicates which cats will die.

| string   |                                                   |
|----------|---------------------------------------------------|
| "p_l"    | Patrol leader (p_l) will die                  |
| "r_c"    | Random cat will die                           |
| "s_c"    | stat cat (s_c) will die                       |
| "app1"   | app1 (the first apprentice) will die          |
| "app2"   | app2 (the second apprentice) will die         |
| "patrol" | The entire patrol will die                    |
| "multi"  | Multiple, but not all, of the patrol will die |

>

***

#### injury: List[Dict[str, various]]
>Optional. Indicates which cats get injured, and how. In classic mode, there are no conditions, so you can include a "scars" line to scar the cat instead. You can include as many of the following blocks (in a list) as you want. 
>
>```json
>{
>     "cats": [],
>     "injuries": [],
>     "scars": [],
>     "no_results": false
>}
>```
>
>Parameter for each:
>
>**cats: List[str]:** Which cats are injured

| string   |                                                      |
|----------|------------------------------------------------------|
| "p_l"    | Patrol leader (p_l) become injured                   |
| "r_c"    | Random cat become injured                            |
| "s_c"    | stat cat (s_c) become injured                        |
| "app1"   | app1 (the first apprentice) become injured           |
| "app2"   | app2 (the second apprentice) become injured          |
| "patrol" | The entire patrol becomes injured                    |
| "multi"  | Multiple, but not all, of the patrol becomes injured |

>**injuries: List[str]:** Pool of injures to draw from
>
>[Injury List](reference/tag-lists.md#__tabbed_1_1)
>
>The above list includes both singular injuries and injury pools.  Adding an injury pool will allow for any of the injuries within that pool to be possible.  One will be chosen at random.  You don't have to pick just one injury or injury pool, you can include as many as you like!

>**scars: List[str]:** 
>Optional. If in classic mode, a scar is chosen from this pool to be given instead of an injury.  If in expanded mode, a scar is chosen from this pool to possibly be given upon healing their injury.
>
>[Scar List](reference/tag-lists.md#__tabbed_1_5)

>**no_results: bool:** 
>Optional. Controls if the injury "got" message shows up in patrol results, as well as potential history text.

| bool  |                                                                                                                                                                                                                                                 |
|-------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| true  | Cat will be given the condition, but it will not show up in results, and any given history_text will not be used (default history text will be used instead). Designed for giving conditions to new cats, but you might find other uses for it. |
| false | Default. A "got" message will appear in patrols results, and any given history text will be used.                                                                                                                                               |

>

***

#### history_text: Dict[str, str]
>Optional, but it should be included if any death or injury is indicated. Controls the history-text for scars and death. 
>
>Format:
>
>```
>{text_type}: "custom history message"
>```

| text_type    | "custom history message"                            |
|--------------|-----------------------------------------------------|
| "reg_death"  | Death history text for non-leaders. Whole sentence. |
| "lead_death" | Death history text for leaders. Sentence fragment.  |
| "scar"       | Scar history. Whole sentence.                       |

>

***

#### relationships: List[Dict[str, various]]
>Optional. Indicates effect on cat relationships. You can include as many of the following blocks as you want, in a list
>
>```
>{
>     "cats_from": [],
>   "cats_to": [],
>     "mutual": false
>     "values" [],
>     "amount": 5
>}
>```
>
>Parameter for each:

>**cats_from: List[str] :** The cat's whose relationship values are being edited. You are changing how the "cats_from" feels. 

| string        |                                                                     |
|---------------|---------------------------------------------------------------------|
| "p_l"         | Patrol leader (p_l)'s feeling are effected                          |
| "r_c"         | Random cat's feeling are effected                                   |
| "s_c"         | stat cat (s_c)'s feeling are effected                               |
| "app1"        | app1 (the first apprentice)'s feeling are effected                  |
| "app2"        | app2 (the second apprentice)'s feeling are effected                 |
| "patrol"      | The entire patrol's feeling are effected                            |
| "clan"        | The entire clan's feeling are effected                              |
| "n_c:{index}" | The new cat(s) with the index number {index}'s feeling are effected |

>**cats_to: List[str] :** The target of the relationship. You can changing how "cats_from" feel about "cats_to"

| string        |                                                                           |
|---------------|---------------------------------------------------------------------------|
| "p_l"         | Feelings toward patrol leader (p_l) are effected                          |
| "r_c"         | Feelings toward random cat's feeling are effected                         |
| "s_c"         | Feelings toward stat cat (s_c) are effected                               |
| "app1"        | Feelings toward app1 (the first apprentice) are effected                  |
| "app2"        | Feelings toward app2 (the second apprentice) are effected                 |
| "patrol"      | Feelings toward the entire patrol are effected                            |
| "clan"        | Feelings toward the entire clan are effected                              |
| "n_c:{index}" | Feelings toward the new cat(s) with the index number {index} are effected |

> Group modifiers: These will modify the cats already being gathered according to the other strings. For example, a block with `"cats_from": ["clan", "low_lawful"]` will gather all the cats in the Clan with a 0-8 lawfulness facet.  These can be combined to get cats with specific ranges of multiple facets.

| modifier     |                                                |
|--------------|------------------------------------------------|
| low_lawful   | cats with a 0-8 lawfulness facet are affected  |
| high_lawful  | cats with a 9-16 lawfulness facet are affected |
| low_social   | cats with a 0-8 sociable facet are affected    |
| high_social  | cats with a 9-16 sociable facet are affected   |
| low_stable   | cats with a 0-8 stability facet are affected   |
| high_stable  | cats with a 9-16 stability facet are affected  |
| low_aggress  | cats with a 0-8 aggression facet are affected  |
| high_aggress | cats with a 9-16 aggression facet are affected |


>**mutual: bool :** Optional. Controls if the relation effect will be applied in both directions. 

| bool  |                                                                                                                                              |
|-------|----------------------------------------------------------------------------------------------------------------------------------------------|
| true  | Relationship effects will be applied in both directions. Equivalent to repeating the relation block with "cats_from" and "cats_to" swapped.  |
| false | Default. Relationship effects will be applied in a single direction.                                                                         |

>**values: bool :** Controls which relationship values are affected.

| string     |                                                                                                                                                                                                                            |
|------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| "romantic" | Romantic-like is affected. Be careful with this one! There is no automatic check to ensure the cats are potential mates. See "tags" and ensure that the correct tags are added, and "cats_to" and "cats_from" are correct. |
| "platonic" | Platonic like is effected                                                                                                                                                                                                  |
| "dislike"  | Dislike (hate) is effected                                                                                                                                                                                                 |
| "comfort"  | Comfort (comfortable) is effected                                                                                                                                                                                          |
| "jealous"  | Jealousy is effected                                                                                                                                                                                                       |
| "trust"    | Trust (reliance) is effected                                                                                                                                                                                               |
| "respect"  | Respect (admiration) is affected.                                                                                                                                                                                          |

>**amount: int :** Exact amount the relationship value will be affected. Can be positive or negative. 

| int           |                                                                                                                                |
|---------------|--------------------------------------------------------------------------------------------------------------------------------|
| {any integer} | The amount the relationship will be affected. 5 is a normal amount, and 15 is a large amount. Try to stay within those bounds. |

>

***

#### new_cat: List[List[str]]
>Optional. Adds a new cat, either joining the clan or as an outside cat. 
>
>Format:
>
>```
>[
>    [cat details],
>    [cat 2 details]
>]
>```
>
>You are able to refer to new-cats in several places, including patrol results text (but not patrol intro text!), injuries, relationships, ect. The {index} value  corresponds to their index value on this list. Remember, computers start counting from 0. So the first entry in the list is 0, the second is 1, and so on. 
>
>You can include the following details:

| string                                      | effect                                                                                                                                                                                                                                                                                                                                                              |
|---------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| "male"                                      | Makes the cat male                                                                                                                                                                                                                                                                                                                                                  |
| "female"                                    | Makes the cat female                                                                                                                                                                                                                                                                                                                                                |
| "can_birth"                                 | If same-sex breeding is OFF, make the cat female. Otherwise, 50 - 50 gender-roll.                                                                                                                                                                                                                                                                                   |
| "new_name"                                  | Ensure the cat takes on a clan-like name                                                                                                                                                                                                                                                                                                                            |
| "old_name"                                  | Ensure the cat keeps their old (maybe loner or kittypet) name. Doesn't work for kittens or litters.                                                                                                                                                                                                                                                                 |
| "kittypet"                                  | Gives the cat a kitty-pet type backstory. If "meeting" is also included, this tag will make the cat an kittypet outsider                                                                                                                                                                                                                                            |
| "loner"                                     | Gives the cat a loner type backstory. If "meeting" is also included, this tag will make the cat an loner outsider                                                                                                                                                                                                                                                   |
| "clancat"                                   | Gives the cat a former-clancat type backstory. If "meeting" is also included, this tag will make the cat a former Clancat outsider.                                                                                                                                                                                                                                 |
| "meeting"                                   | Make the cat an outsider (the patrol just met them, but they didn't join). That cat will never take a new clan-like name.                                                                                                                                                                                                                                           |
| "litter"                                    | Turns a single cat generation into a litter of kittens or newborns. Make sure to have a parent for them!                                                                                                                                                                                                                                                            |
| "status:{some_status}"                      | Cats will join with this status. Include "medicine cat", "apprentice", "mediator", "kitten", "newborn", "medicine cat apprentice", etc, but not leader or deputy. Default for not-litters is warrior. Be very careful specifying both age and status-  there is no extra check to ensure they make sense together.                                                  |
| "age:{some_age}"                            | Cats are "newborn", "kitten", "adolescent", "young adult", "adult", "senior adult", "senior". You can also specify "mate" to put them in the same age-category as the first specified mate, or "has_kits" to generate an age between 14 and 120 moons. Be very careful specifying both age and status-  there is no extra check to ensure they make sense together. |
| "backstory:{some}, {backstories},{another}" | Comma-separated exact backstories to pick from. Overrides "kittypet", "loner", "clancat"                                                                                                                                                                                                                                                                            |
| "parent:{index},{index}"                    | You can include one or two biological parents. Parents must be created BEFORE children, so the parent details must be listed before the children. If you mark parents, and the child(ren) are young enough, one will be given the "recovering from birth" condition.                                                                                                |
| "adoptive:{index},{index}"                  | You can include multiple adoptive parents. Parents must be created BEFORE children, so the parent details must be listed before the children. You can denote any cat included in the event as being an adoptive parent by using their abbreviation (`m_c`, `p_l`, ect).  The mates of the adoptive parent will automatically be included as adoptive parents.       |                                                                                              |
| "mate:{index},{index}"                      | Indexes of mates. Mates must be created BEFORE the cat with this tag. You can also specify patrol-cats (p_l, r_c, or s_c)                                                                                                                                                                                                                                           |

>

***

#### art: str
>Optional. Name of outcome-specific art, without file extension (no .png). If no art is specified, the intro art will be used. 
>
> Example: "art": "bord_general_intro",
>

#### art_clean: str
>Optional. Name of non-gore outcome-specific art, without file extension (no .png). Adding a clean version of the art marks the normal version as containing gore. The game will then use the clean version if the "Allow mild gore and blood in patrol artwork" setting is off, and the explicit version if this setting is on.
>
> Example: "art_clean": "bord_general_intro",
>

***

#### outsider_rep
> This parameter is used for **all** patrols that involve new_cats, loners, and rogues (regardless of if the new cat joins, or if the loner or rogue is even open to joining the clan). It changes the reputation the player Clan has among outsiders, those who don't belong to any Clan. 
>
> If the player Clan has a welcoming reputation (above 71), new_cat patrols tagged with the "new_cat" tag have an increased chance to appear, and will be generated from the resources/dicts/patrols/new_cat_welcoming.json. 
>
> If the player Clan has a neutral reputation (between 31 to 70), new_cat patrols have no increased or deceased chance to appear, and will be generated from the resources/dicts/patrols/new_cat.json.
>
> If the player Clan has a hostile reputation (from 1 to 30), new_cat patrols have a decreased chance to appear, and will be generated from the resources/dicts/patrols/new_cat_hostile.json.
>
> The exception to this is if the player Clan has less than 20 cats. If the player Clan is small, the chance to get a new_cat patrol is overridden and becomes equal to the chance of the welcoming reputation. However, the new_cat patrols that are generated with the small_clan chance will still be generated from the json that is appropriate to the Clan's reputation.
>
> Patrols that encounter outsiders without using the new_cat code or tag can effect outsider_rep without being a new-cat patrol. Patrols that generate a new_cat do not have to add the new_cat tag unless the cat is an outsider, for example, when stealing an apprentice from an other_clan, the new_cat code block is used to make the apprentice, but outsider_rep and the new_cat tag are not used, due to the apprentice being from an interaction with an other_clan. Always default to using the new_cat tag if unsure.

Outsider reputation changes
> Defaults:
>
> | Outcome type          | Change                  |
> |-----------------------|-------------------------|
> | Success               | 1                       |
> | Failure               | 1 or 0                  |
> | Antagonize success    | -2                      |
> | Antagonize failure    | -1 or 0                 |
>
> Please check with the other developers before changing from these defaults. However, there are lots of reasons why outsider_rep might be effected more or less than these defaults. For example, rescuing a mother cats and her newborn kittens may have a greater positive effect on a Clan's reputation than allowing random loner number 27 to join the Clan.

***

#### other_clan_rep
> This parameter is used for **all** patrols that involve the other Clans that border the player Clan. It changes the reputation the player Clan has among it neighbors. 
>
> If the player Clan is allied with the other_clan the reputation will be greater than 17. The other_clan patrols will be generated from the resources/dicts/patrols/other_clan_allies.json. 
>
> If the player Clan is neutral with the other_clan the reputation will be equal or greater than 7 and less than or equal to 17. The other_clan patrols will be generated from the resources/dicts/patrols/other_clan.json. 
>
> If the player Clan is hostile with the other_clan the reputation will be less than 7. The other_clan patrols will be generated from the resources/dicts/patrols/other_clan_hostile.json. 
>
> By default 3 to 5 other Clans are generated on Clan creations to neighbor the player Clan. Relationships with the other Clans are individual, the player Clan can get along with one Clan and hate another. Relationships can also be influenced by the temperament of the other Clan and of the player Clan (link to appropriate documentation WIP)
>

Other clan reputation changes
> Defaults:
>
> | Outcome type          | Change                  |
> |-----------------------|-------------------------|
> | Success               | 2                       |
> | Failure               | 0 or -1                 |
> | Antagonize success    | -2                      |
> | Antagonize failure    | -1 or 0                 |

> Please check with the other developers before changing from these defaults. However, there are lots of reasons why other_clan_rep might be effected more or less than these defaults. For example, failing to antagonize an enemy clan and getting your warriors killed in a border skirmish might make the player Clan absolutely _hate_ the other_clan. Create an argument for why your patrol deserves a greater effect and talk to the other developers.
>

***

### future_event:list[dict{str, various}]

 [Using Future Events](future.md)

***

## Minimal Patrol Example
This is a perfectly good patrol, with the bare minimum features needed!

```json
{
    "patrol_id": "some_unique_id",
    "biome": [
        "Any"
    ],
    "season": [
        "Any"
    ],
    "types": [
        "hunting"
    ],
    "tags": [],
    "patrol_art": "hunt_general_intro",
    "min_cats": 1,
    "max_cats": 6,
    "weight": 20,
    "chance_of_success": 50,
    "intro_text": "The patrol heads out.",
    "decline_text": "And they head right back!",
    "success_outcomes": [
        {
            "text": "Wow! The patrol did great!",
            "exp": 10,
            "weight": 20
        }
    ],
    "fail_outcomes": [
        {
            "text": "Oof. The patrol didn't do so hot.",
            "exp": 0,
            "weight": 20
        }
    ]
}
```

## Full Featured Patrol Example
This uses almost all features somewhere. Yes, it is long. Most patrols are not this long. 

!!! tip
    If you are new to patrol writing, I recommend going through this example line by line and reading the parameter explanation from above alongside it.

```json
{
    "patrol_id": "some_unique_id",
    "biome": [
        "Any"
    ],
    "season": [
        "Any"
    ],
    "types": [
        "hunting"
    ],
    "tags": [
        "disaster",
        "new_cat"
    ],
    "patrol_art": "explict_art_name",
    "patrol_art_clean": "hunt_general_intro",
    "min_cats": 3,
    "max_cats": 6,
    "min_max_status": {
        "warrior": [
            1,
            6
        ],
        "leader": [
            1,
            6
        ],
        "normal adult": [
            1,
            6
        ],
        "apprentice": [
            -1,
            -1
        ]
    },
    "weight": 20,
    "chance_of_success": 50,
    "relationship_constraint": [
        "siblings",
        "platonic_20"
    ],
    "pl_skill_constraint": [
        "FIGHTER,1"
    ],
    "intro_text": "The patrol heads out.",
    "decline_text": "And they head right back!",
    "success_outcomes": [
        {
            "text": "Wow! The patrol did great!",
            "exp": 10,
            "weight": 20,
            "relationships": [
                {
                    "cat_to": [
                        "p_l"
                    ],
                    "cat_from": [
                        "r_c"
                    ],
                    "values": [
                        "platonic",
                        "comfort"
                    ],
                    "amount": 5
                },
                {
                    "cat_to": [
                        "p_l"
                    ],
                    "cat_from": [
                        "r_c"
                    ],
                    "values": [
                        "dislike"
                    ],
                    "amount": -5
                }
            ],
            "prey": [
                "medium"
            ],
            "art": "patrol_outcome_art",
            "art_clean": "patrol_outcome_art_clean"
        },
        {
            "text": "Wow! This is an uncommon outcome, and someone new joined!",
            "exp": 2,
            "weight": 10,
            "new_cat": [
                [
                    "can_birth",
                    "age:has_kits"
                ],
                [
                    "litter",
                    "parent:0"
                ]
            ],
            "art": "patrol_outcome_art"
        },
        {
            "text": "Wow! s_c did extra great!",
            "exp": 10,
            "weight": 20,
            "stat_trait": [
                "loving",
                "cold"
            ],
            "stat_skill": [
                "TEACHER,1"
            ],
            "can_have_stat": [
                "p_l",
                "adult"
            ]
        }
    ],
    "fail_outcomes": [
        {
            "text": "Oof. The patrol didn't do so hot. They also all died.",
            "exp": 0,
            "weight": 20,
            "dead_cats": [
                "patrol"
            ],
            "history_text": {
                "reg_death": "m_c died while on a patrol.",
                "lead_death": "died on patrol"
            },
            "art": "patrol_outcome_art",
            "art_clean": "patrol_outcome_art_clean"
        },
        {
            "text": "Wow, a fail-stat outcome. Cool.",
            "exp": 0,
            "weight": 20,
            "stat_trait": [
                "grumpy",
                "nervous"
            ],
            "stat_skill": [
                "SPEAKER,1"
            ],
            "art": "patrol_outcome_art"
        },
        {
            "text": "They didn't die.. , but they got hurt and lost!",
            "exp": 0,
            "weight": 20,
            "lost_cats": [
                "r_c"
            ],
            "injury": [
                {
                    "cats": [
                        "p_l"
                    ],
                    "injuries": [
                        "battle_injury"
                    ],
                    "scars": [
                        "ONE"
                    ]
                }
            ],
            "history_text": {
                "reg_death": "m_c died from an patrol.",
                "lead_death": "died from a patrol",
                "scar": "m_c was scarred on patrol"
            }
        }
    ],
    "antag_success_outcomes": [
        {
            "text": "Wow, you did the antagonize!",
            "exp": 0,
            "weight": 20,
            "outsider_rep": -1,
            "other_clan_rep": -2,
            "art": "patrol_outcome_art"
        }
    ],
    "antag_fail_outcomes": [
        {
            "text": "Wow, you did the antagonize, and failed!",
            "exp": 0,
            "weight": 20,
            "outsider_rep": 0,
            "other_clan_rep": -2
        }
    ]
}
```
