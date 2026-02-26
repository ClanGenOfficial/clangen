# FutureEvents

## What is a Future Event?

Future events are special event blocks that can be added to the ShortEvent and Patrol outcome formats. They allow the writer to specify a ShortEvent that will be created in a given number of moons. Writers can even specify a larger pool of events for the future event to be chosen from.  Writers can also add multiple future events to a single event, meaning that one event could trigger multiple events!


!!! tip
    Currently, future events are removed from the "queue" if they go 12 moons without being able to display. For example, if an involved cat dies before the future event is able to display, then the event will no longer trigger and the player will never see it. A 12 moon buffer is provided so that any season-locked future events will have the opportunity to "wait" for their required season.

## FutureEvent Format

```json
"future_event": [
        {
        "event_type": "",
        "pool": {},
        "moon_delay": [1,1],
        "involved_cats": {}
        }
]
```

This parameter can be added to the end of ShortEvent and Patrol outcome formats.

!!! note
    The future event parameter is a *list*, this means that you could have multiple future event dictionaries contained within, each dictionary creating its own future event. 

### event_type:str

Specify which ShortEvent type the future event will be. 

> * death
* injury
* new_cat
* misc

!!! note
    Keep in mind that you can only choose one event type, so you cannot add events from multiple event types into the pool.

### pool:dict[list]

You can specify a whole pool of events to be chosen from. Only one event from this pool will be chosen as the future event. You can specify by `subtype`, `event_id`, or `excluded_event_id`. You do not need to include every parameter, but you must utilize at least one.

!!! important
    If you include subtypes, only events that have *all* the listed subtypes will be available.
    If you do not include subtypes, all events (that match `event_type`) will be available. Please be mindful!

```json
        "pool": {
            "subtype": []
            "event_id": []
            "excluded_event_id": []
        },
```

| Parameter           | Use                                                                    |
|---------------------|------------------------------------------------------------------------|
| `subtype`           | Events to be added to the pool will contain *all* subtypes specified.  |
| `event_id`          | Only events with the specified event_ids will be added to the pool.    |
| `excluded_event_id` | All events with the specified event_ids will be removed from the pool. |


### moon_delay:tuple[int, int]

This specifies how many moons must pass before the future event appears in game. Writers are able to specify a range `[x, y]` with `x` being the smallest possible delay and `y` being the largest possible delay.  One number will be picked between `x` and `y` to serve as the delay.  Setting both `x` and `y` as the same number will make that number the only option.

### involved_cats:dict[str, dict]

This specifies what cats can fill the roles within the future event. You can also use this to carry cats from the parent event into the future event. This is structured as a dictionary, with the **key** being the future event's cat role and the **value** being either a dictionary of constraints or a parent event's cat role.

Example of how this looks in use, the parent event for this hypothetical event is a murder event:
```json
    "involved_cats": {
        "m_c": "r_c",
        "mur_c": "m_c", 
        "r_c": { 
            "age": ["senior"] 
        }
    }
```

**"m_c": "r_c",**
> r_c is the random cat from the parent event. They will be m_c, or the main cat, in the future event. 

**"mur_c": "m_c"**
> m_c is the main cat from the parent event. They will be mur_c, or the murdered cat, in the future event.

!!! tip
    Any role used in the parent event can be used to carry a cat into the future event! For example, a new cat, `n_c:0`, from the parent event could be carried into the future event as `m_c` or any other possible role.

**"r_c": {...}** or **"r_c": null**
> In this line, we aren't carrying over any cat from the parent event. Instead, we're trying to find a new cat. We've decided this cat can only be a senior, so that constraint is added. A cat will be chosen from the currently living cats, excluding any cats already involved in this event. If we don't want to constrain this at all, we can leave it null or remove the parameter.

The cat constraints that can be utilized here are the same as [ShortEvents](shortevents.md#r_cdictstr-various), with a few exclusions. You cannot use `dies`, `backstory` or `relationship_status`.

!!! warning
    Keep in mind that if you constrain certain roles, you *need* to be certain that there is at least one possible event within the pool that will allow for those constraints.  For example, if you specify that r_c must be an elder with the CAMP skill, then there must be at least one event in the pool that allows r_c to be an elder with the CAMP skill.  If there is not, then a future event will never be chosen. 

!!! important
    In general it's best to keep cat constraints to a minimum. Remember that all the events in the pool will have their own cat constraints to match! The more constraints you add here, the more limited that pool will become. It's very easy to out-constrain yourself to the point of having no events possible.

## Example

Here's an example of a future event being utilized for a murder event.

```json
    {
        "event_id": "gen_death_murder_any1",
        "location": [ "any" ],
        "season": [
            "any"
        ],
        "sub_type": ["murder"],
        "tags": [],
        "weight": 20,
        "event_text": "m_c was murdered. The culprit is unknown.",
        "m_c": {
            "status": [
                "kitten",
                "apprentice",
                "warrior",
                "deputy",
                "medicine cat apprentice",
                "medicine cat",
                "mediator apprentice",
                "mediator",
                "elder"
            ],
            "dies": true
        },
        "r_c": {
            "age": ["adolescent", "young adult", "adult", "senior adult"],
            "status": [ "any" ]
        },
        "history": [{
            "cats": ["m_c"],
            "reg_death": "m_c was secretly murdered by r_c."
        }],
        "relationships": [
            {
                "cats_from": [
                    "r_c"
                ],
                "cats_to": [
                    "m_c"
                ],
                "values": [
                    "platonic"
                ],
                "amount": -15
            },
            {
                "cats_from": [
                    "r_c"
                ],
                "cats_to": [
                    "m_c"
                ],
                "values": [
                    "dislike"
                ],
                "amount": 15
            }
        ],
        "future_event": [
                {
                "event_type": "misc",
                "pool": {
                    "subtype": ["murder_reveal"]
                },
                "moon_delay": [1,10],
                "involved_cats": {
                    "m_c": "r_c",
                    "mur_c": "m_c",
                    "r_c": {
                        "age": ["any"]
                    }
                }
            }
        ]
    }
```