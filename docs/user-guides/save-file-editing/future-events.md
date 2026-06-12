!!! warning
     Future events can only be utilized as ShortEvents. Anything outside of that, such as pregnancy events, are not possible with future events.

Documentation based around future events and its options are part of the [writer's documentation](https://clangen.io/docs/dev/writing/future/).

Future Events give the game the ability to force short events in the future as a continuation from a previous short event or patrol. It also gives us, people who like to force things, the ability to force specific short events on specific cats based on our storylines for them. Such as murders, injuries, and more.

* There is a high chance that whatever is not caused by future events can be forced through utilizing the game_config's event debug.

Currently, future events are largely only used for murder reveals. However, it is possible to force an event that doesn't have an actual future event attached.

---

## future_events

Here is an example of what you might find in the future_events.json:

If you are unsure on how a future event would look like for your need, try to find an event with a future event already connected to it in the files, and build your edited future event based off it.

```json
[
    {
        "parent_event": "gen_death_murder_anymed2",
        "event_type": "misc",
        "pool": {
            "sub_type": [
                "murder_reveal"
            ]
        },
        "moon_delay": 8,
        "involved_cats": {
            "m_c": "1356",
            "mur_c": "1142",
            "r_c": "1319"
        }
    }
]
```

|  `Code`  |  Explanation  |
| :---- | :---- |
|  `"parent_event": ""`,  |  The ID of the event or patrol that caused this future event. Doesn't necessarily matter when editing in a future event. |
|  `"event_type": "misc"`,  |  The event type of the future event. (name of the file it comes from. `misc` folder would be `"event_type": "misc",`) |
|  `"pool": {}`,  |  The "pool" the future event can randomly choose from.  |
|  `"moon_delay": 8`,  |  The "gap" between when "parent_event" happened and when the future event will trigger. Counts down.  |
|  `"involved_cats": {}`,  |  The list of involved cats that will be mentioned in the future event.  |

"event_type" can be...

- `"misc"`: Could be events like murder 
- `"death"`: Any event that causes a death to trigger. Includes extinction events
- `"injury"`: Any event that causes an injury to trigger
- `"new_cat"`: Any event that generates a new cat

"pool" can include...

!!! tip
      If the sub_type is not specified, it'll pull from *every* event with the same "event_type"

- `"sub_type": []`: Could be types like murder_reveal, hidden_murder_reveal, etc. More than one sub_type can be used.
- `"event_id": []`: Specifying a specific future event(s) to trigger by ID, rather than a pool of events. Can be the same event ID as "parent_event"
- `""excluded_event_id": []`: Excluding a specific future event(s) to trigger by ID

One parameter must be utilized (commonly "sub_type"), but you can use more than one if your heart desires.

`"moon_delay"` can be anything, but if you want it to happen on the next moon, change it to 1. 

`"involved_cats"` are the cats IDs you want to be involved with the future event, along with their role.

---

### More examples

!!! warning
     This section doesn't go over every available combination. Do not be afraid to experiment with a test save beforehand.

Forcing a new cat event...

```json
[
    {
        "parent_event": "gen_new_cat_adoption_anylitter1",
        "event_type": "new_cat",
        "pool": {},
        "moon_delay": 8,
        "involved_cats": {
            "m_c": "13"
        }
    }
]

```

If you're searching to do an adoption event: since adoption isn't a "sub_type" event, you'll have to use "event_id". For example:

```json
[
    {
        "parent_event": "gen_new_cat_adoption_anylitter1",
        "event_type": "new_cat",
        "pool": {
            "event_id": [
                "gen_new_cat_adoption_anylitter1",
                "gen_new_cat_adoption_anywelcomingotherclanlitter1"
            ]
        },
        "moon_delay": 8,
        "involved_cats": {
            "m_c": "13"
        }
    }
]

```

Forcing a murder...

```json
[
    {
        "parent_event": "bch_death_murder_cliffdrop1",
        "event_type": "misc",
        "pool": {
            "sub_type": [
                "murder"
            ]
        },
        "moon_delay": 8,
        "involved_cats": {
            "m_c": "13",
            "r_c": "15"
        }
    }
]
```

!!! Tip
     (in my play testing) "m_c" is usually the victim and "r_c" is usually the murderer

Forcing a murder reveal...

```json
[
    {
        "parent_event": "gen_death_murder_anymed2",
        "event_type": "misc",
        "pool": {
            "sub_type": [
                "murder_reveal"
            ]
        },
        "moon_delay": 8,
        "involved_cats": {
            "m_c": "1356",
            "mur_c": "1142",
            "r_c": "1319"
        }
    }
]
```

!!! tip
     If you want to use hidden_murder_reveal, simply replace the sub_type from "murder_reveal" to "hidden_murder_reveal".

"mur_c" will be the only place you could specify the murderer specifically in the involved cats list. It does not work for the actual murder event itself - just reveals.

Forcing an injury...

```json
[
    {
        "parent_event": "gen_injury_clawwound_anymultiagemultistatusnotfightermultitraitothercatleader1",
        "event_type": "injury",
        "pool": {},
        "moon_delay": 2,
        "involved_cats": {
            "m_c": "15"
        }
    }
]
```

"m_c" will be the cat who is normally injured, "r_c" is the other cat mentioned.