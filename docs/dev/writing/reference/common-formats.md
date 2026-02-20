# Common Formats
Some events include parameters for things like history or relationships that are consistent across different event formats. Their documentation will link here when necessary.

## Writing Histories
Cats receive history text to go with each scar-able injury as well as possibly-fatal injury and direct deaths.  These histories show up in their profile.  Many event formats require you to include the history text if a cat is being injured or killed.  These typically refer to three different history types: `scar`, `reg_death`, `lead_death`.  Following are the guidelines for writing each:

| history type | guidelines                                                                                                                                                                                                                                                                            |
|--------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| scar         | This history is given to a cat who gains a scar from an injury gotten during the event.  ONLY INCLUDE if the injury being given is able to scar (i.e a bruise will not scar, but a claw-wound will scar).  This should be a single, full sentence specifying how the cat was scarred. |
| death        | This history is given to a cat who is either killed by the event or dies from an injury gotten during the event.  This should be a single, full sentence specifying how the cat died.  Try not to get too wordy with these.                                                           |
|

**Example of acceptable histories**
```json
{
    "scar": "m_c gained a scar from a fox.",
    "death": "m_c died from a fox bite."
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

| string         |                                                                                                                                                                                                      |
|----------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `patrol`       | If this is a patrol, you can use this to affect all cats within the patrol                                                                                                                           |
| `clan`         | The entire player Clan's feelings are affected                                                                                                                                                       |
| `some_clan`    | This will affect a random set of cats equalling 1/8th of the player Clan                                                                                                                             |
| `low_lawful`   | Use in conjunction with other tags to constrain the affected cats. **It cannot be used alone.** All tagged cats with a 0-8 lawfulness facet are affected. MUST BE LISTED AFTER NON-FACET TAGS.       |
| `high_lawful`  | Use in conjunction with other tags to constrain the affected cats. **It cannot be used alone.** All player Clan cats with a 9-16 lawfulness facet are affected. MUST BE LISTED AFTER NON-FACET TAGS. |
| `low_social`   | Use in conjunction with other tags to constrain the affected cats. **It cannot be used alone.** All player Clan cats with a 0-8 sociable facet are affected. MUST BE LISTED AFTER NON-FACET TAGS.    |
| `high_social`  | Use in conjunction with other tags to constrain the affected cats. **It cannot be used alone.** All player Clan cats with a 9-16 sociable facet are affected. MUST BE LISTED AFTER NON-FACET TAGS.   |
| `low_stable`   | Use in conjunction with other tags to constrain the affected cats. **It cannot be used alone.** All player Clan cats with a 0-8 stability facet are affected. MUST BE LISTED AFTER NON-FACET TAGS.   |
| `high_stable`  | Use in conjunction with other tags to constrain the affected cats. **It cannot be used alone.** All player Clan cats with a 9-16 stability facet are affected. MUST BE LISTED AFTER NON-FACET TAGS.  |
| `low_aggress`  | Use in conjunction with other tags to constrain the affected cats. **It cannot be used alone.** All player Clan cats with a 0-8 aggression facet are affected. MUST BE LISTED AFTER NON-FACET TAGS.  |
| `high_aggress` | Use in conjunction with other tags to constrain the affected cats. **It cannot be used alone.** All player Clan cats with a 9-16 aggression facet are affected. MUST BE LISTED AFTER NON-FACET TAGS. |

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

