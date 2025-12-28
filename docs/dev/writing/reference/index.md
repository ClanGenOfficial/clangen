# Reference 
This page contains formatting information that is generally utilized across all event formats and should be treated as a main reference.

## Pronoun Tags

There are three kinds of pronoun tag: `PRONOUN`, `VERB` and `ADJ` tags.

#### A note on plural pronouns
Though less relevant in English, the ability to specify plural pronouns is provided. The format is slightly different:
```
{PRONOUN/PLURAL/m_c+r_c/subject/CAP}
{VERB/PLURAL/m_c+r_c/conju_0/conju_1/[...]/conju_n}
{ADJ/PLURAL/m_c+r_c/gender_0/gender_1/[...]/gender_n}
```
The addition of `PLURAL` immediately following the tag identifier signals that it's a plural pronoun and to use the relevant system. Each cat that is to be referred to by the plural must be referenced in this block, separated by a `+`. Otherwise, the system is the same as below for singular pronouns.

### PRONOUN
A `PRONOUN` tag has three main sections: the `PRONOUN` identifier, the relevant cat, and which pronoun is being requested. There is an optional modifier at the end - `CAP` - that is used to signal that the requested pronoun should be capitalized.

Example:
```
{PRONOUN/m_c/subject}
{PRONOUN/m_c/subject/CAP}
```
Permitted pronouns and their English equivalents:

| Pronoun   | English equivalent       |
|-----------|--------------------------|
| `subject` | he/she/they              |
| `object`  | him/her/them             |
| `poss`    | his/her/their            |
| `inposs`  | his/hers/theirs          |
| `self`    | himself/herself/themself |

### VERB
A `VERB` tag has a technically-infinite number of sections depending on the language, but in English it has four sections: the `VERB` identifier, the relevant cat, and the options for each conjugation in the language (in the case of English, plural and singular conjugations).

Example:
```
{VERB/m_c/were/was}
```

!!! caution
    Pay close attention to the order of verbs. In English, **plural conjugation is first**.

### ADJ
Not especially relevant for English, the `ADJ` tag exists to allow items in a sentence to be referred to with the correct grammatical gender. An English example of gendered words could be actor/actress.

Example:
```
{ADJ/m_c/parent/father/mother}
```


## Writing Histories
Cats receive history text to go with each scar-able injury as well as possibly-fatal injury and direct deaths.  These histories show up in their profile.  Many event formats require you to include the history text if a cat is being injured or killed.  These typically refer to three different history types: `scar`, `reg_death`, `lead_death`.  Following are the guidelines for writing each:

| history type | guidelines                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
|--------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| scar         | This history is given to a cat who gains a scar from an injury gotten during the event.  ONLY INCLUDE if the injury being given is able to scar (i.e a bruise will not scar, but a claw-wound will scar).  This should be a single, full sentence specifying how the cat was scarred.                                                                                                                                                                                                                                                                                                                                                                               |
| reg_death    | This history is given to a non-leader cat who is either killed by the event or dies from an injury gotten during the event.  This should be a single, full sentence specifying how the cat died.  Try not to get too wordy with these.                                                                                                                                                                                                                                                                                                                                                                                                                              |
| lead_death   | This history is given to a leader cat who is either killed by the event or dies from and injury gotten during the event.  This should be a sentence fragment.  Leaders are able to die multiple times, so on their profiles their deaths are listed in one single sentence.  This sentence is formatted as such: "[leader name] lost a life when they [lead_death sentence fragment]" with each following death being added on to create a list with a comma between each item (and the last list item being added with an "and").  Your lead_death text must be able to work within this grammar format and should not include punctuation at the end of the text. |

**Example of acceptable histories**
```json
{
    "scar": "m_c gained a scar from a fox.",
    "reg_death": "m_c died from a fox bite.",
    "lead_death": "died from a fox bite"
}
```

## Writing Relationship Changes
These blocks indicate a change in the involved cats' relationships. You can include multiple blocks within the list to change a variety of relationships.

```json
{
    "cats_from": [],
    "cats_to": [],
    "mutual": false,
    "values": [],
    "amount": 5,
    "log": {}
}
```

### cats_from:list[str]
A list of the cats whose relationship values are being changed. You are changing how these cats feel towards the cats_to group.

### cats_to:list[str]
A list of the cats who are the target of cats_from's feelings. 

**Possible Abbreviations:**
For `cats_from` and `cats_to` you may use any of cat abbreviations already utilized within the event format you are adding to, in addition to the following:

| string         |                                                                            |
|----------------|----------------------------------------------------------------------------|
| `patrol`       | If this is a patrol, you can use this to affect all cats within the patrol |
| `clan`         | The entire player Clan's feelings are affected                             |
| `some_clan`    | This will affect a random set of cats equalling 1/8th of the player Clan   |
| `low_lawful`   | All player Clan cats with a 0-8 lawfulness facet are affected              |
| `high_lawful`  | All player Clan cats with a 9-16 lawfulness facet are affected             |
| `low_social`   | All player Clan cats with a 0-8 sociable facet are affected                |
| `high_social`  | All player Clan cats with a 9-16 sociable facet are affected               |
| `low_stable`   | All player Clan cats with a 0-8 stability facet are affected               |
| `high_stable`  | All player Clan cats with a 9-16 stability facet are affected              |
| `low_aggress`  | All player Clan cats with a 0-8 aggression facet are affected              |
| `high_aggress` | All player Clan cats with a 9-16 aggression facet are affected             |

### mutual:bool
Optional. Controls if the relation effect will be applied in both directions. Defaults to False.

| bool    |                                                                                                                                             |
|---------|---------------------------------------------------------------------------------------------------------------------------------------------|
| `true`  | Relationship effects will be applied in both directions. Equivalent to repeating the relation block with "cats_from" and "cats_to" swapped. |
| `false` | Default. Relationship effects will be applied in a single direction.                                                                        |

### values:list[str]
The relationship types that will be changed.

| string    | effect                                                                                                                                                                                                               |
|-----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `romance` | Romance is affected. Be careful with this one! There is no automatic check to ensure the cats are potential mates. See "tags" and ensure that the correct tags are added, and "cats_to" and "cats_from" are correct. |
| `like`    | Like is affected                                                                                                                                                                                                     |
| `comfort` | Comfort is affected                                                                                                                                                                                                  |
| `trust`   | Trust is affected                                                                                                                                                                                                    |
| `respect` | Respect is affected.                                                                                                                                                                                                 |

### amount:int
The amount that the chosen relationship types will change by. 8 is a low amount, 16 is a high amount.

### log:dict[str]
The string that will display within the relationship logs. A string can be specified for both the `cats_from` and `cats_to` groups. 

!!! tip "Writing Logs"
    When writing a log string, you can utilize the same abbreviations that you have already used within the event format. You can also use the abbreviations `from_cat` and `to_cat` to utilize names and pronouns for individual cats within their respective groups, which is handy when you've indicated a change should occur across multiple cats. For example: "to_cat was part of the patrol that invited n_c:0 to c_n." would appear in the log as "PatrolCat was part of the patrol that invited NewCat to ExampleClan."

```json
"log": {
    "cats_from": "",
    "cats_to": ""
}
```

**cats_from**: This string will be added to the relationship logs of all cats in cats_from.

**cats_to**: This string will be added to the relationship logs of all cats in cats_to.

!!! warning "If the change is mutual..."
    The `cats_to` log will only be used if the relationship change is `mutual`. If the relationship change is `mutual`, but no `cats_to` log was specified, then all involved cats will use the given `cats_from` log.

!!! warning "If no logs are given..."
    If no logs are provided at all, then the event's text will be used. In the case of patrols, a default "These cats interacted" string will be used.

