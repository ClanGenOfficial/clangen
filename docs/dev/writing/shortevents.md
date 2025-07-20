# ShortEvents

When a timeskip occurs, the event code runs through each cat individually.  Each cat has a chance to trigger various moon events: condition event, death event, new cat event, and misc event.  Once an event is triggered, a second, random cat is also chosen for the event.  There are a few modifiers to determine which cat this is, such as one that increases the chance for mentor/app pairs to have events together.  It's important to remember that you *do not* have to include either cat in the event.

The cat who triggered the event in the first place is called the main cat, or `m_c`.  This is the cat that the event is happening *to*.  This is the cat that always dies in a death event, this is the cat that always gets injured/ill during a condition event, this is the cat that would gain an accessory in a misc event.

The second, random cat is called the random cat, or `r_c`.  This is the cat that is tagging along for the event.  It is possible to also kill them in a death event, but it is not mandatory.  It is possible to injure/sicken them in a condition event, but not mandatory.  There currently is not functionality for them to also gain accessories.

New cats can also join the clan through moon events.  They are referred to with `n_c:{index}`.  If you would like to ensure they are referred to by their pre-clan name, rather than any newly attained name, use `n_c_pre:{index}`.  The specific use of `n_c:{index}` is explained within the parameter documentation below.

Some death events are considered "mass death" events (aka "mass extinction").  These events kill 3-11 cats at a time.  Use the abbreviation `multi_cat` in place of a name and for the history block.  The names will replace this abbreviation in a "name1, name2, and name3" format, write your event accordingly.  The `m_c` age and status parameters will also be used to define which cats are allowed to be killed in this event.

## Event Format:
```json
{
    "event_id": "",
    "location": [],
    "season": [],
    "sub_type": [],
    "tags": [],
    "frequency": 0,
    "event_text": "event text here",
    "new_accessory": [],
    "m_c": {
        "age": [],
        "status": [],
        "relationship_status": [],
        "skill": [],
        "not_skill": [],
        "trait": [],
        "not_trait": [],
        "backstory": [],
        "dies": false
    },
    "r_c": {
        "age": [],
        "status": [],
        "relationship_status": [],
        "skill": [],
        "not_skill": [],
        "trait": [],
        "not_trait": [],
        "backstory": [],
        "dies": false
    },
    "new_cat": [
        []
    ],
    "injury": [
        {
            "cats": [],
            "injuries": [],
            "scars": []
        }
    ],
    "exclude_involved": [],
    "history:": [
        {
            "cats": [],
            "scar": "",
            "reg_death": "",
            "lead_death": ""
        }
    ],
    "relationships": [
        {
            "cats_from": [],
            "cats_to": [],
            "mutual": false,
            "values": [],
            "amount": 0
        }
    ],
    "outsider": {
        "current_rep": [],
        "changed": 0
    },
    "other_clan": {
        "current_rep": [],
        "changed": 0
    },
    "supplies": [
        {
            "type": "",
            "trigger": [],
            "adjust": ""
        }
    ],
    "future_event": []
}
```

***

### event_id:str
>
the event_id is a unique string used to identify the event. It does not affect event behavior, but it allows us to easily find events.

> An event_id is formatted as following: `biome_type_cause_seasondescription#`, 
>
>- 'cause' is something of a secondary type indicator.  Perhaps a death event is for death by heat stroke, you could use `heat` for the 'cause' section of the id. Or if a cat is hurt by a certain animal, you can indicate the animal here. If you cannot think of an appropriate 'cause' then you do not have to include one.
>- if an event happens in more than one season, but not all seasons, then you can use `multi` for the 'season' section of the id
>- If you are making new_cat or other_clan events, please include if the event is hostile/neutral/welcoming or hostile/neutral/allies in the ID
>- If the event is under some kind of constraint, like being skill locked or relationship locked, please indicate that in the ID 

| Abbreviations |      Meaning                     |
|---------------|----------------------------------|
| mtn           | appears in the mountainous biome |
| pln           | appears in the plains biome      |
| fst           | appears in the forest biome      |
| bch           | appears in the beach biome       |
| wtlnd         | appears in the wetlands biome    |
| dst           | appears in the desert biome      |
| gen           | appears in any biome             |
| death         | death type event                 |
| injury        | injury type event                |
| new_cat       | new_cat type event               |
| misc          | any event type that does not fit into the preceding three       |

Example:
!!! todo "TODO"
    write example

How to make sure your event_id is unique:
> ctrl (or command) + f through the .json file you're writing the event into. As each event_id contains the biome & type within it and we have different jsons for different biomes and event types, if your potential event_id isn't in the json already, your event_id will be unique.

!!! caution
    No NSFW event_ids. No exceptions.

***
### location:list[str]
>This controls the biome and camp the event appears in. If the event can appear in any location, use "any".  If you would like the event to occur in specific biomes, but do not want to restrict it to certain camps, then add the plain biome names.  If you would like the event to occur in specific camps, you can specify the camps by extending the biome name accordingly: `"biome:{camp1_camp2_camp3}"`.  In practice, this may look like the following examples: `"mountainous:camp1"`, `"beach:camp2_camp4"`, `"plains:camp1_camp2_camp3"`.  

| string        | use                              |
|---------------|----------------------------------|
| "mountainous" | appears in the mountainous biome |
| "plains"      | appears in the plains biome      |
| "forest"      | appears in the forest biome      |
| "beach"       | appears in the beach biome       |
| "wetlands"    | appears in the wetlands biome    |
| "desert"      | appears in the desert biome      |
| "any"         | appears in any biome             |

!!! todo "TODO"
    add a table listing various camps

Please have a look at the [full biome differences list](index.md#clangen-biomes) when thinking about writing patrols. 

### season:list[str]
>List of seasons in which the event may occur.

lowercase season names + "any"

*** 
### sub_type:list[str]
>List of subtypes for this event. If the event has no subtype, remove parameter.  Possible subtypes:

| death event subtypes | use                                                                                                               |
|----------------------|-------------------------------------------------------------------------------------------------------------------|
| war                  | marks event as only occurring during war                                                                          |
| murder               | marks event as being a murder (m_c is the victim, r_c is the murderer)                                            |
| old_age              | marks event as only occurring if the m_c is old enough to die of old age                                          |
| mass_death           | marks event as a mass death event, 3-11 cats will be selected for death                                       |

| injury event subtypes | use                                      |
|-----------------------|------------------------------------------|
| war                   | marks event as only occurring during war |

| new_cat event subtypes | use                                      |
|------------------------|------------------------------------------|
| war                    | marks event as only occurring during war |

| misc event subtypes | use                                                               |
|---------------------|-------------------------------------------------------------------|
| war                 | marks event as only occurring during war                          |
| murder_reveal       | marks event as being the reveal of a murder                       |
| accessory           | marks event as giving an accessory to m_c                         |
| ceremony            | marks event as being the gifting of an accessory after a ceremony |
| transition          | marks event as being a cat transitioning their gender             |

***

### tags:list[str]
>Tags are used for some filtering purposes.

| string               | use                                                                                                                                     |
|----------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| classic              | event only occurs in classic mode                                                                                                       |
| cruel_season         | event only occurs in cruel_season mode                                                                                                  |
| no_body              | use for death events only, this indicates that the dead body is not retrievable and cannot be referenced in grief events                |
| skill_trait_required | normally there is a small chance to bypass skill and trait requirements, this tag will make that chance nonexistent.                    |
| clan_wide            | if the event text does not mention the main or random cat, but is instead an event occurring towards the Clan as a whole, use this tag. |
| romance              | marks event as being between two cats who are allowed romantic relations                                                                |
| adoption             | marks event as being an adoption                                                                                                        |

> **Tags To Indicate Present Statuses** - Sometimes you may want to indicate in event text that other cats of a certain status as present in addition to m_c and r_c (perhaps m_c and r_c are watching kits play, or discussing the progress of apprentices, or complaining about tending to elders.) These tags can be used to ensure that there are cats of the mentioned status currently living within the Clan, this helps prevent situation where cats are watching nonexistent kits or other such impossibilities. Keep in mind that all of these tags check for the presence of *at least* 2 cats of the indicated status.

| string        | use                                                                                                                                                            |
|---------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| clan:{status} | event only occurs if the clan has at least 2 cats with the given status (do not include curly brackets in tag, tag should look something like: "clan:newborn") |
| clan:apps     | event only occurs if the clan has living apps, this includes ALL types of apps (medicine, mediator, and warrior)                                               |


> **Leader Specific Tags** - since leaders can have 9 lives, it's helpful to have tags that indicate how an event is influenced by those lives.

| leader event tag | use                                                                                                                                        |
|------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| all_lives        | indicates the death event will take all the remaining lives                                                                                |
| some_lives       | indicates the death event will take multiple lives, but that it will not take *all* lives. The leader will still be alive after the event. |
| lives_remain     | indicates that the death event can only occur if the leader has multiple lives left. This leader will still be alive after the event.      |
| high_lives       | this event will only occur if the leader has 7-9 lives left                                                                                |
| mid_lives        | this event will only occur if the leader has 4-6 lives left                                                                                |
| low_lives        | this event will only occur if the leader has 1-3 lives left                                                                                |

!!! tip
    Leader death events that are not tagged with `all_lives` or `some_lives` will take 1 life by default.

***

### frequency:int
>Controls how common an event is.  This works on a 1-4 scale. 

| int | commonality |
|-----|-------------|
| 1   | Very Rare   |
| 2   | Rare        |
| 3   | Uncommon    |
| 4   | Common      |

!!! tip
    Unsure what frequency your event should have? Think of it this way: if an event of this type were to happen every moon for 10 moons, how often should I see an event like this one? Seeing this sort of event for 4/10 moons would mean it's a common event! Seeing it just once within those 10 moons would mean it's a very rare event.

!!! warning
    When handling death and injury events, be careful not to think of the frequency as "how often should a death/injury occur". The event's frequency has no effect on regardless of whether a death/injury occurs! It only affects *how* a cat dies/is injured.  For injuries, it can be helpful to think about it in comparison to the cat's age or status. A kit shouldn't be getting mauled over and over, rather they should mostly get some bumps and bruises!
***

### event_text:str
>The text that appears within the event list when the event occurs.

### new_accessory:list[str]
>If the event gives a new accessory, list possible new accessories here (one will be chosen from the list).

!!! todo "TODO"
    need to make an accessory tag list

### m_c:dict[str, various]
>Specifies the requirements for the main cat (m_c) of the event. 
>
>**age:[list]** : a list of ages m_c can be. if they can be anything, use "any".  [Possible Ages](reference/index.md#__tabbed_2_1)
>
>**status:[list]** : a list of statuses m_c can b. if they can be anything, use "any".  [Possible Statuses](reference/index.md#__tabbed_2_2)

!!! tip
    Keep in mind that the status and ages you input can limit each other! For example, if you add "kitten" to `age`, remember that kitten age cats can only ever have the kitten status.  This means that you *could* leave `status` as "any" and be secure in the knowledge that kitten status cats will be the only ones chosen.  

    Another example could be adding "leader" to `status`.  If you do so, then you don't need to include all the age states possible for a leader in `age`.  Rather, you can leave `age` as "any".

    However, remember the wide range of ages and statuses we have and how they can overlap with each other.  It's possible to have warriors who graduate early and are still adolescent age.  It's also possible for apps to train longer than usual and become young adults without becoming warriors.  Elders, likewise, can be both young and old cats as it's possible for cats to retire to the elder den at any age.

>**relationship_status:[list]** : dictates what relationships m_c must have towards r_c.  Do not use this section if there is no r_c in the event.

| string                |                                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------|
| siblings              | m_c and r_c are siblings                                                                     |
| not_siblings          | m_c and r_c are not siblings                                                                 |
| littermates           | m_c and r_c are littermates                                                                  |
| not_littermates       | m_c and r_c are not littermates                                                              |
| mates                 | m_c and r_c are mates                                                                        |
| not_mates             | m_c and r_c are NOT mates                                                                    |
| parent/child          | m_c is the parent of r_c                                                                     |
| not_parent            | m_c is not r_c's parent                                                                      |
| child/parent          | m_c is the child of r_c                                                                      |
| not_child             | m_c is not the child of r_c                                                                  |
| app/mentor            | m_c is the apprentice of r_c                                                                 |
| not_app               | m_c is not the apprentice of r_c                                                             |
| mentor/app            | r_c is the mentor of m_c                                                                     |
| not_mentor            | r_c is not the mentor of m_c                                                                 |
| "romantic_{value}"    | Value is an integer between 0 and 100. m_c must have more than {value} romantic-like to r_c. |
| "platonic_{value}"    | Value is an integer between 0 and 100. m_c must have more than {value} platonic-like to r_c. |
| "dislike_{value}"     | Value is an integer between 0 and 100. m_c must have more than {value} dislike to r_c.       |
| "comfortable_{value}" | Value is an integer between 0 and 100. m_c must have more than {value} comfortable to r_c.   |
| "jealousy_{value}"    | Value is an integer between 0 and 100. m_c must have more than {value} jealousy to r_c.      |
| "admiration_{value}"  | Value is an integer between 0 and 100. m_c must have more than {value} admiration to r_c.    |
| "trust_{value}"       | Value is an integer between 0 and 100. m_c must have more than {value} trust to r_c.         |

>**skill[list]** : m_c must possess at least one skill from this list. if they can be anything, use "any"
>
>**not_skill[list]** : m_c cannot possess any of the skills on this list. 
>This is mostly useful in cases where a cat can have any skill except one or two, in which case you would need to list those few skills here, but would not have to list all the other skills in the skill parameter.  Cats are also capable of having multiple skills, so it can be valuable to specify if a cat with an allowed skill should still be prevented from this event due to possessing a second, un-allowed skill.  Also useful for stopping a cat with a certain skill (like FIGHTER,3) from getting an event incongruent with their skill (dying in a fight to an apprentice)
>
>**trait[list]** : m_c must possess at least one trait from this list. if they can be anything, use "any"
>
>**not_trait[list]** : m_c cannot possess any of the traits on this list. 
>This is mostly useful in cases where a cat can have any trait except one or two, in which case you would need to list those few traits here, but would not have to list all the other traits in the skill parameter.  
>
>**backstory[list]** : m_c must possess a backstory from this list. if they can be anything, use "any"
>
>**dies[bool]** : the m_c will die due to this event. default is False

***

### r_c:dict[str, various]
>Specifies the requirements for r_c of the event.  If there is no r_c in the event, then do not include this parameter. 
>
>**age:[list]** : a list of ages r_c can be. if they can be anything, use "any"
>
>**status:[list]** : a list of statuses r_c can be. if they can be anything, use "any"
>
>**relationship_status:[list]** : dictates what relationships the r_c must have towards m_c.  Note that this is not identical to the tag list from the cat block.  If you wish to dictate relationships like "siblings", "mates", ect. then you must do so within the m_c block, not the r_c block.

| string                |                                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------|
| "romantic_{value}"    | Value is an integer between 0 and 100. r_c must have more than {value} romantic-like to m_c. |
| "platonic_{value}"    | Value is an integer between 0 and 100. r_c must have more than {value} platonic-like to m_c. |
| "dislike_{value}"     | Value is an integer between 0 and 100. r_c must have more than {value} dislike to m_c.       |
| "comfortable_{value}" | Value is an integer between 0 and 100. r_c must have more than {value} comfortable to m_c.   |
| "jealousy_{value}"    | Value is an integer between 0 and 100. r_c must have more than {value} jealousy to m_c.      |
| "admiration_{value}"  | Value is an integer between 0 and 100. m_c must have more than {value} admiration to r_c.    |
| "trust_{value}"       | Value is an integer between 0 and 100. r_c must have more than {value} trust to m_c.         |

>**skill[list]** : r_c must possess at least one skill from this list. if they can be anything, remove parameter or leave list empty.
>
>**not_skill[list]** : r_c cannot possess any of the skills on this list
>This is mostly useful in cases where a cat can have any skill except one or two, in which case you would need to list those few skills here, but would not have to list all the other skills in the skill parameter.  Cats are also capable of having multiple skills, so it can be valuable to specify if a cat with an allowed skill should still be prevented from this event due to possessing a second, un-allowed skill.
>
>**trait[list]** : r_c must possess at least one trait from this list. if they can be anything, use "any"
>
>**not_trait[list]** : r_c cannot possess any of the traits on this list
>This is mostly useful in cases where a cat can have any trait except one or two, in which case you would need to list those few traits here, but would not have to list all the other traits in the skill parameter.  
>
>**backstory[list]** : r_c must possess a backstory from this list. if they can be anything, use "any"
>
>**dies[bool]** : r_c will die due to this event, default is False

***

### new_cat:list[list[str]]
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
>You are able to refer to new-cats in several places, including injuries, relationships, ect. The {index} value  corresponds to their index value on this list. Remember, computers start counting from 0. So the first entry in the list is 0, the second is 1, and so on. 
>
>You can include the following details:

| string                                      | effect                                                                                                                                                                                                                                                                                                                                                              |
|---------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| "dead"                                      | This cat will be generated as a dead cat.                                                                                                                                                                                                                                                                                                                           |
| "male"                                      | Makes the cat male.                                                                                                                                                                                                                                                                                                                                                 |
| "female"                                    | Makes the cat female.                                                                                                                                                                                                                                                                                                                                               |
| "can_birth"                                 | If same-sex breeding is OFF, make the cat female. Otherwise, either male or female will be chosen at random.                                                                                                                                                                                                                                                        |
| "new_name"                                  | Ensure the cat takes on a clan-like name.                                                                                                                                                                                                                                                                                                                           |
| "old_name"                                  | Ensure the cat keeps their old (maybe loner or kittypet) name. Doesn't work for kittens or litters.                                                                                                                                                                                                                                                                 |
| "kittypet"                                  | Gives the cat a kitty-pet type backstory. If "meeting" is also included, this tag will make the cat a kittypet outsider.                                                                                                                                                                                                                                            |
| "loner"                                     | Gives the cat a loner type backstory. If "meeting" is also included, this tag will make the cat a loner outsider.                                                                                                                                                                                                                                                   |
| "rogue"                                     | Gives the cat a rogue type backstory. If "meeting" is also included, this tag will make the cat a rogue outsider.                                                                                                                                                                                                                                                   |
| "clancat"                                   | Gives the cat a former-clancat type backstory. If "meeting" is also included, this tag will make the cat a former Clancat outsider.                                                                                                                                                                                                                                 |
| "meeting"                                   | Make the cat an outsider (the patrol just met them, but they didn't join). That cat will never take a new Clan-like name.                                                                                                                                                                                                                                           |
| "exists"                                    | Will attempt to find an existing outsider to utilize instead of creating a new one. Keep in mind that this ONLY checks if the existing outsider matches indicated status, age, and backstory.  DO NOT use this tag in conjunction with creating litters or assigning parentage.                                                                                     |
| "unknown"                                   | Prevents the inclusion of "notifying" text such as "The Clan has met `name`". Best used for situations in which a cat needs to be created, but the Clan didn't actually interact with them (i.e. creating abandoned litters).                                                                                                                                       |
| "litter"                                    | Turns a single cat generation into a litter of kittens or newborns. Make sure to have a parent for them!                                                                                                                                                                                                                                                            |
| "status:{some_status}"                      | Cats will join with this status. Include "medicine cat", "apprentice", "mediator", "kitten", "newborn", "medicine cat apprentice", etc, but not leader or deputy. Default for not-litters is warrior. Be very careful specifying both age and status-  there is no extra check to ensure they make sense together.                                                  |
| "age:{some_age}"                            | Cats are "newborn", "kitten", "adolescent", "young adult", "adult", "senior adult", "senior". You can also specify "mate" to put them in the same age-category as the first specified mate, or "has_kits" to generate an age between 14 and 120 moons. Be very careful specifying both age and status-  there is no extra check to ensure they make sense together. |
| "backstory:{some}, {backstories},{another}" | Comma-separated exact backstories to pick from. Overrides "kittypet", "loner", "clancat"                                                                                                                                                                                                                                                                            |
| "parent:{index},{index}"                    | You can include one or two biological parents. Parents must be created BEFORE children, so the parent details must be listed before the children. If you mark parents, and the child(ren) are young enough, one will be given the "recovering from birth" condition.                                                                                                |
| "adoptive:{index},{index}"                  | You can include multiple adoptive parents. Parents must be created BEFORE children, so the parent details must be listed before the children. You can denote any cat included in the event as being an adoptive parent by using their abbreviation (`m_c`, `p_l`, ect).  The mates of the adoptive parent will automatically be included as adoptive parents.       |
| "mate:{index},{index}"                      | Indexes of mates. Mates must be created BEFORE the cat with this tag. You can also specify patrol-cats (p_l, r_c, or s_c)                                                                                                                                                                                                                                           |

***

### injury:list[dict[str, various]]
>Optional. Indicates which cats get injured, and how. In classic mode, there are no conditions, so you can include a "scars" line to scar the cat instead. You can include as many of the blocks as you like within the list. 
>
>```json
>    {
>      "cats": [],
>      "injuries": [],
>      "scars": [],
>      "history:": {
>        "scar": "",
>        "reg_death": "",
>        "lead_death": ""
>      }
>    }
>```
>
>Parameter for each:
>
>**cats: List[str]:** Which cats are injured

| string      |                                   |
|-------------|-----------------------------------|
| m_c         | main cat is injured               |
| r_c         | other cat in the event is injured |
| n_c:{index} | new cat of given index is injured |

>**injuries: List[str]:** Pool of injures to draw from
>
>[Injury List](reference/index.md#__tabbed_1_1)
>
>The above list includes both singular injuries and injury pools.  Adding an injury pool will allow for any of the injuries within that pool to be possible.  One will be chosen at random.  You don't have to pick just one injury or injury pool, you can include as many as you like!

>**scars: List[str]:** 
>Optional. A scar is chosen from this pool to possibly be given upon healing their injury.
>
>[Scar List](reference/index.md#__tabbed_1_5)

### exclude_involved: List[str]:
>Optional. Excludes certain cats from showing up in the "involved cats" list of the event, meaning their button will not be present on the events screen. Cats listed here will still be a part of the event and can be affected by other parameters like injuries, accessories, relationships, and death, if they're written to.

| string      |                                    |
|-------------|------------------------------------|
| m_c         | main cat is excluded               |
| r_c         | other cat in the event is excluded |
| n_c:{index} | new cat of given index is excluded |

### history_text: Dict[str, str]:
>Controls the history-text for scars and death. You must include a list of cats for whom the history will be assigned (i.e. "m_c", "r_c").
>[History Writing Guidelines](reference/index.md#writing-histories)
>
>Block:
>
>```json
>    {
>        "cats": [],
>        "scar": "",
>        "reg_death": "",
>        "lead_death": ""
>    }
>```

| text_type    | "custom history message"                                                                                    |
|--------------|-------------------------------------------------------------------------------------------------------------|
| "reg_death"  | Death history text for non-leaders. Whole sentence.  must include if cat is dead or injured                 |
| "lead_death" | Death history text for leaders. Sentence fragment. must include if dead or injured cat could be the leader. |
| "scar"       | Scar history. Whole sentence.  must include if cat gets injured                                             |

***

### relationships:list[dict[str, various]]
>Optional. Indicates effect on cat relationships. You can include as many of the following blocks as you want, in a list
>
>```
>{
>    "cats_from": [],
>    "cats_to": [],
>    "mutual": false,
>    "values" [],
>    "amount": 5
>}
>```
>
>Parameter for each:

>**cats_from: List[str] :** The cat's whose relationship values are being edited. You are changing how the "cats_from" feels. 

| string      |                                                                                                            |
|-------------|------------------------------------------------------------------------------------------------------------|
| m_c         | main cat's feelings are affected                                                                           |
| r_c         | other cat's feelings are affected                                                                          |
| n_c:{index} | new cat's feelings are affected                                                                            |
| clan        | the clan's feelings are affected (experimental, unsupported in old format and not sure if i can make work) |


>**cats_to: List[str] :** The target of the relationship. You can changing how "cats_from" feel about "cats_to"

| string      |                                                                                                                 |
|-------------|-----------------------------------------------------------------------------------------------------------------|
| m_c         | feelings toward the main cat are affected                                                                       |
| r_c         | feelings toward the other_cat are affected                                                                      |
| n_c:{index} | feelings toward the new cat are affected                                                                        |
| clan        | feelings toward the clan are affected (experimental, unsupported in old format and not sure if i can make work) |

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

***

### outsider:dict[str, various]
>Dictates what reputation the clan is required to have with outsiders as well as how that reputation changes due to the event.
>
>**current_rep:[list[str]]:**  The reputation the Clan must have in order for this event to be possible. "hostile", "neutral", "welcoming". use "any" if any rep is allowed.
>
>**changed:int:**  How the reputation of the Clan changes as a result of this event.

***

### other_clan:dict[str, various]
>Dictates what reputation the clan is required to have with the other clan as well as how that reputation changes due to the event.
>
>**current_rep:[list[str]]:**  The reputation the Clan must have in order for this event to be possible.  "hostile", "neutral", "ally".  Use "any" if any rep is allowed.
>
>**changed:int:**  How the reputation of the Clan changes as a result of this event.

***

### supplies:list[dict{str, various}]
>Dictates how this event changes the various supply pools of the clan.  If changing multiple supply pools, use a block for each pool.

```
        "supplies": [
            {
                "type": "",
                "trigger": [],
                "adjust": ""
            }
        ]
```

>**type:str:** indicates the supply being affected

| string                               | effect                                                           |
|--------------------------------------|------------------------------------------------------------------|
| freshkill                            | this event affects the freshkill supply                          |
| all_herb                             | this event affects the herb supply as a whole                    |
| any_herb                             | this event will choose a random individual herb supply to affect |
| insert link to list of possible herb | this event will affect the supply for herb named                 |

>**trigger:list[str]:** indicates when the event can trigger, include all possible trigger times

| string   | effect                                                                                                                   |
|----------|--------------------------------------------------------------------------------------------------------------------------|
| always   | triggers regardless of current supply amount (be careful with this, only use with "freshkill", "all_herb" and "any_herb" |
| low      | triggers when indicated supply is low (unable to support at least half of clan)                                          |
| adequate | triggers when indicated supply is adequate (can support at least half the clan, but is not enough for a full moon)       |
| full     | triggers when indicated supply is full (able to support all of clan for 1 moon, but not multiple moons)                  |
| excess   | triggers when indicated supply is at least twice the needed supply for 1 moon                                            |

>**adjust:str:** indicates how the supply should be adjusted

| string         | effect                                                      |
|----------------|-------------------------------------------------------------|
| reduce_eighth  | reduces indicated supply by 1/8th                           |
| reduce_quarter | reduces indicated supply by 1/4th                           |
| reduce_half    | reduces indicated supply by 1/2                             |
| reduce_full    | reduces indicated supply to 0                               |
| increase_#     | replace # with int, increases indicated supply by given int |

### future_event:list[dict{str, various}]

 [Using Future Events](future.md)
