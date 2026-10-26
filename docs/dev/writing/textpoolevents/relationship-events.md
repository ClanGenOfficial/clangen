# Relationship Events

Relationship Events utilize the `TextPoolEvent` format.

Relationship Events are events that occur each timeskip that are focused entirely on influencing the relationships between certain cats. 

These should be fairly short, like all timeskip events. Less than 300 characters, with shorter being better, is preferred.

## Usable Cat References

| abbreviation | use                                                                                                                                                                                                                                                                                                                           |
|--------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `m_c`        | The main cat of the event. Their relationship towards other cats will be affected the most by the event.                                                                                                                                                                                                                      |
| `r_c`        | The second cat within a two-cat event. `m_c`'s relationship towards `r_c` will be changing in the event.                                                                                                                                                                                                                     |
| `r_c{#}`     | If multiple cats other than `m_c` will be present, use this tag instead of `r_c` to denote them. For example `"m_c avoids joining r_c1 and r_c2's conversation."`. The numbering of these abbreviations should begin at `1` and increment upwards.                                                                            |
| `multi_cat`  | If multiple cats other than `m_c` are present and they're all being affected in the exact same way, then you can use this tag to insert a list of their names into the event. For example `"m_c spends time with multi_cat."` will appear to the player as `"Examplecat spends time with Blankpelt, Someclaw, and Otherfur."` |


## Directory Structure
The relationship event directory is found in `resources/lang/en/events/relationship_events`.

Within this folder are 3 folders:

| name                   | use                                                                   |
|------------------------|-----------------------------------------------------------------------|
| `group_interactions`   | holds events that include 3 or more cats                              |
| `normal_interactions`  | the general 2-cat interactions that are most common in the game       |
| `joining_interactions` | these are special events only triggered when a new cat joins the Clan |

Within `normal_interactions` and `joining_interactions` are folders for each relationship value: `comfort`, `like`, `respect`, `romance`, `trust`. This value will be the "main" value affected by the events inside that folder.

There's one more layer of folders after this one. These dictate the strength of the effect on the "main" value: `low`, `medium`, or `high`.

From there, each folder contains a `negative.json` and `positive.json`. Events the decrease the "main" value will go in `negative.json` and events that increase the "main" value will go into `positive.json`.

Altogether this might look like `normal_interations/comfort/medium/negative.json`.

`group_interactions` is unique. It skips the first layer of folders dictating relationship value as its nature in affecting many relationships at once means determining a "main" value is difficult. Instead, consider how large of a relationship change is being made and whether it's largely positive or negative.

!!! important
    While there are other files within `relationship_events` beyond just the 3 interaction folders listed, these do NOT contain events using the format that will be explained in this documentation.

## Relationship Event Format

### Minimum Required
>The smallest amount of information you're required to include in this format. 

```json
{
    "event_id": "test",
    "strings": [
        "m_c spent time chatting with r_c."
    ]
}
```

### Full Format

This event type uses the [TextPoolEvent Format](../textpoolevents/textpoolevent-format.md)

Any parameters with relationship event-specific notes are explained below.

### Disallowed Parameters

The following parameters from the TextPoolFormat are not used for Relationship Events:

- [frequency](../textpoolevents/textpoolevent-format.md#frequency-int)
- [outcome_art](../textpoolevents/textpoolevent-format.md#outcome_art-str)
- [outcome_art_clean](../textpoolevents/textpoolevent-format.md#outcome_art_clean-str)
- [required_cat_types](../textpoolevents/textpoolevent-format.md#required_cat_types-dictstr-listint)
- [patrol_temperament](../textpoolevents/textpoolevent-format.md#patrol_temperament-liststr)
- [exp_gained](../textpoolevents/textpoolevent-format.md#exp_gained-int)

***

### event_id: str
[Main event_id Notes](../textpoolevents/textpoolevent-format.md#event_id-str)

Generally, the ID tries to specify the main relationship value being affected, the intensity of the affect, and the type of effect; along with any other identifiers that might indicate a unique aspect of the events contained within.

* `like_inc_med1`
* `like_to_app_inc_med1`
* `trust_for_leader_de_high1`

***

### tags: list[str]
[Main tags Notes](../textpoolevents/textpoolevent-format.md#tags-liststr)

!!! note
    You do not need to use the `romance` tag for events intended to be romantic. These are already filtered as necessary.

***

### relationship_changes:list[dict[str, various]]
[Main relationship_changes Notes](../textpoolevents/textpoolevent-format.md#relationship_changeslistdictstr-various)

The ONLY `cats_from` and `cats_to` parameters allowed here are the ones you have defined in `involved_cats`. Exclusionary tags and facet tags shouldn't be used. Logs are unnecessary as we always use the chosen event string for the logs. 

!!! caution
    As noted in [Directory Structure](#directory-structure), `normal_interactions` and `welcoming_interactions` events are already categorized according the values they will affect, as well as the size of the effect. You *do not* need to include those effects in this dict. They are applied *automatically* from `m_c` to `r_c`. 
    
    So, if an event is in `comfort/mid/decrease` then you do not need to change the comfort amount from `m_c` to `r_c`. **However**, if you wish to change the comfort from `r_c` to `m_c`, then you *do* need to use this parameter to do so.

    Events in `group_interactions` are exempt from this. For those you will have to dictate every single intended change to the relationships.

***
