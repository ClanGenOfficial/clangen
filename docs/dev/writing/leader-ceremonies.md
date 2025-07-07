# Leader ceremonies

## Guidelines
- If using dialogue quotes, put a `\` before the `"` to allow it to work within a json.
- Event text should be 400 character max, with 250 characters preferred (these counts aren't strict, as pronoun tags do artificially inflate them)
- We have two versions of ceremonies! The StarClan and the Dark Forest.  Which one is used is determined by where the Clan's dead guide is residing.  Focus on the SC ceremonies, as they'll be seen most often, but when possible try to create Dark Forest versions of your SC ceremonies.
    - Dark Forest ceremonies are held in `lead_ceremony_df.json`
    - StarClan ceremonies are held in `lead_ceremony_sc.json`
- Ceremonies are structured as:
    1. Intro
    2. 9 separate life events
        - If 9 dead cats are not available, any excess lives are given by an `Unknown Blessing` event
    3. Outro
- Each life giving event must include a virtue that the life represents.  

### Replacement Text:
| abbreviation | use                                                    |
|--------------|--------------------------------------------------------|
| `c_n`        | clan name                                              |
| `m_c`        | leader's old name                                      |
| `m_c_star`   | leaders new name                                       |
| `r_c`        | life giver's name                                      |
| `[life_num]` | number of un-assigned lives (use in Unknown Blessings) |
| `[virtue]`   | random virtue chosen from given virtue list            |

***
### Format

#### Outro and Intro events
```json
    "unique ID": {
        "tags": [],
        "lead_trait": [],
        "text": []
    }
```

#### Life Giving events

```json
    "unique ID": {
        "tags": [],
        "lead_trait": [],
        "star_trait": [],
        "rank": [],
        "life_giving": [
            {
                "text": "",
                "virtue": []
            }
        ]
    }
```

#### unique ID: str
> This is the ID needs to be a unique string. Try using ctrl+F to check if the ID you want to use is already in use.  Generally this should contain identifying information about the traits or ranks of the cats specified within.

***

#### tags: list[str]
> tags available are:

| tag                  | use                                                                                                                                                                      |
|----------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `"new_clan"`         | Used for intros and outros of newly created Clans. You can pair this with the guide tag to create events in which the guide cat meets the leader for the first time.     |
| `"guide"`            | To specify that the life giver of the event is the guide.  Keep in mind that, upon clan creation, the guide is the only cat available to give lives to the first leader. |
| `"old_leader"`       | To specify that the life giver of the event is the oldest leader in StarClan.                                                                                            |
| `"unknown_blessing"` | To specify that this life giving event is for anonymous spirits to give un-assigned lives to the leader.  STAR TRAIT AND RANK CANNOT BE USED IN THESE EVENTS.            |
| `"leader_parent"`    | To specify that the life giver is the parent of the new leader                                                                                                           |
| `"leader_child"`     | To specify that the life giver is the child of the leader                                                                                                                |
| `"leader_mate"`      | To specify that the life giver is the mate of the leader                                                                                                                 |

***

#### lead_trait: list[str]
> A list of traits that the new leader must have for this event to be available

***

#### star_trait: list[str]
> A list of traits that the life giver must have for this event to be available

***

#### rank: list[str]
> A list of ranks that the life giver's rank must be within for this event to be available

***

#### text: list[str]
> A list of possible outro or intro texts for that event. 

***

#### life_giving: list[dict{str[var]}]
> Each dict within this list is a possible text choice for that event, only one will be chosen from this list.  The virtue list holds possible virtues to be randomly chosen from for the replacement text within that event.
```json
        {
            "text": "",
            "virtue": []
        }
```