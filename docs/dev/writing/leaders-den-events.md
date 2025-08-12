# Leader's den events

## Guidelines
The Leader's Den allows the player to choose ways to interact with other Clans and Outsiders each moon.  They can only choose one interaction per those two groups (one Clan interaction and one Outsider interaction.  After choosing an interaction, the interaction choice will be noted on screen.  Choices can be changed up until timeskip is made.  Upon timeskip, the chosen interaction event displays as a moon event.

Remember, these are moon events, so they need to stay relatively short and simple.  Keep it to 1-2 sentences, 3 at the absolute max.

!!! note "Important"
    There are two file folders for these jsons, the `fail` and the `success` folders.  Within those folders are an `outsider.json` and an `other_clan.json` file.  Failed interactions go within the relevant file of the `fail` folder.  Successful interactions go within the relevant file of the `success` folder.

## Other Clan Events
These should be flavored as occurring during the Gathering and should specify as such by mentioning the Gathering within the event. These are events where a cat is making a deliberate attempt to influence another Clan while acting as a representative for the player Clan. Event failure or success and consequential rel changes are noted in extra text that will be automatically appended to the end of the event.

!!! tip
    Clan tempers play a large role in the chance of success for these events.  The temper charts shown later on this page are a good way to visualize this.  The further away from each other two tempers are, the less likely an interaction between them is to succeed.

### Event Format
```json
    {
        "interaction_type": "",
        "event_text": "",
        "rel_change": 0,
        "m_c": {
            "status": [],
            "age": [],
            "trait": [],
            "skill": []
        },
        "player_clan_temper": [],
        "other_clan_temper": []
    }
```

***

#### interaction_type: str
> The type of interaction.  Each level of relationship with other clans has a matching positive and negative interaction type.  They are as follows:

- ally
    - negative: "offend"
    - positive: "praise"
- neutral
    - negative: "provoke"
    - positive: "befriend"
- hostile
    - negative: "antagonize"
    - positive: "appease"

***

#### event_text: str
> The event text string.  Uses same abbrs as moon events.  m_c for main cat, o_c for other_clan (NOT o_c_n)

#### rel_change: int
> How much this event changes the relationship with the other clan. 
>
>Negative interactions give negative rel changes on success, positive or no rel changes on failure.  Positive interactions give positive rel changes on success, negative or no rel changes on failure.  Generally, failure changes should not be larger than success changes.
>
> Remember that clan relations operate on a 1-30 scale, so even small changes have a fairly large impact.

!!! tip
    It can be fun to create events that require very specific skills or traits to trigger, but have a large impact (5+) on relations. Especially if a high skill level (SPEAKER,4 for example) is required. This also helps reward cats who have those high skills or skills like SPEAKER and MEDIATOR, which should really have a big impact at a Gathering.

***

#### m_c: dict[various]
> Dictates what cats are allowed to use this event.  If a parameter is not used, delete it.  The only thing that must be kept is the `"m_c": {}`.
```json
    "m_c": {
        "status": [],
        "age": [],
        "trait": [],
        "skill": []
    }
```
> **status: list[str]** - [status list](reference/tag-lists.md#__tabbed_2_1)  In addition to leader, the following statuses can be sent to the Gathering in the leader's stead: ["leader", "deputy", "medicine cat", "medicine cat apprentice"]

> **age: list[str]** - [age list](reference/tag-lists.md#__tabbed_2_1) Ages from adolescent to senior can be sent to the Gathering as per statuses listed above.  Kittens can never be sent to a Gathering.

> **trait: list[str]** - [trait list](reference/tag-lists.md#__tabbed_3_2)

> **skill: list[str]** - [skill list](reference/tag-lists.md#__tabbed_3_1)


***

#### player_clan_temper: list[str]
> List of allowed player clan temperaments.  Possible tempers are as follows:

|                 | low aggression | mid aggression | high aggression  |
|-----------------|----------------|----------------|------------------|
| **low social**  | cunning        | proud          | bloodthirsty     |
| **mid social**  | amiable        | stoic          | wary             |
| **high social** | gracious       | mellow         | logical          |

***

#### other_clan_temper: list[str]
> List of allowed other clan temperaments.  Possible tempers are same as above.

|                 | low aggression | mid aggression | high aggression  |
|-----------------|----------------|----------------|------------------|
| **low social**  | cunning        | proud          | bloodthirsty     |
| **mid social**  | amiable        | stoic          | wary             |
| **high social** | gracious       | mellow         | logical          |

***

## Outsider Events
These events are flavored as the Clan going out to deliberately interact with the chosen Outside, whether by killing, inviting, searching for, ect.  You could also flavor the event as the chosen Outsider doing something in response to what the Clan is trying to do to them (i.e. leaving the area after hearing the Clan's intentions, joining the Clan after hearing the Clan wants them, journeying closer after hearing reports from other Outsiders, ect.)

### Event Format
```json
{
    "interaction_type": "",
    "event_text": "",
    "reputation": [],
    "rep_change": 0,
    "m_c": {
        "status": [],
        "age": [],
        "trait": [],
        "skill": [],
        "new_thought": "",
        "relationships": [
            {
            "cats_from": [],
            "cats_to": [],
            "mutual": false,
            "values": [],
            "amount": 0
            }
        ]
    }
}
```

***

#### interaction_type: str
> The type of interaction this event corresponds to:

- "hunt"
    - the Clan attempts to hunt down and kill the Outsider
- "drive"
    - the Clan attempts to find and drive out the Outsider (mechanically, this makes the cat "invisible" to the player and prevents them from interacting with the Clan anymore)
- "invite"
    - the Clan attempts to find and invite the Outsider into the Clan
- "search"
    - LOST CATS ONLY, the Clan searches for a lost Clanmate

***

#### event_text: str
> The event text displayed to the player

***

#### reputation: list[str]
> The reputation the player Clan must have towards Outsiders.  Can be "any", "hostile", "neutral", or "welcoming.

***

#### rep_change: int
> How much the Clan's reputation towards Outsiders changes.  This can be a positive or negative number.  Outsider rep operates on a 1-100 scale with a smaller number being more hostile and a larger number being more welcoming.

***

#### m_c: dict{var}
> `m_c` in this event is the chosen Outsider cat.  This dict will provide constraints for which Outsiders can access this event as well as information for how the Outsider changes afterwards.  If a parameter is not used, delete it.  The only thing that must be kept is the `"m_c": {}`.

```json
    "m_c": {
    "status": [],
    "age": [],
    "trait": [],
    "skill": [],
    "new_thought": "",
    "kit_thought": "",
        "relationships": [
            {
            "cats_from": [],
            "cats_to": [],
            "mutual": false,
            "values": [],
            "amount": 0
            }
        ]
    }
```
> **status: list[str]** - list of statuses allowed: ["loner", "rogue", "kittypet", "exiled", "lost", "former clancat"].  Remember, "exiled" and "lost" cats were previously part of the Clan.

> **age: list[str]** - [age list](reference/tag-lists.md#__tabbed_2_1)  (yes, Outsider kittens could be chosen for these interactions)

> **trait: list[str]** - [trait list](reference/tag-lists.md#__tabbed_3_2)

> **skill: list[str]** - [skill list](reference/tag-lists.md#__tabbed_3_1)

> **new_thought: str** - The thought the Outsider will have on this moon as a result of the event.

> **kit_thought: str** - When an chosen Outsider has kittens they're caring for, the kittens will gain this thought as a result of the event.  Keep in mind, kittens will be brought with an Outsider caretaker who joins the Clan.  However, if an Outsider caretaker is *killed* by the Clan, the kittens will be left alone to continue living as Outsiders.

> **relationships: list[dict{var}]** - How relationships change as result of the event.  This operates exactly the same as [ShortEvent relationships dicts](https://github.com/ClanGenOfficial/clangen/wiki/%5BWriting%5D-%E2%80%90-ShortEvents#relationshipslistdictstr-various) EXCEPT that the only cat options are "m_c", "clan", and "some_clan".