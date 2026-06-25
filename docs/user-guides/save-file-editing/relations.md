Relation files are rather simple compared to the rest of the files.

## Explanation 
```json
[
    {
        "cat_from_id": "1727",
        "cat_to_id": "1109",
        "mates": false,
        "family": false,
        "romance": 24,
        "like": 0,
        "respect": -10,
        "comfort": 12,
        "trust": 0,
        "log": [],
        "no_longer_neutral": []
    }
]
```

Relation values can now go from -100 to 0 to 100. Excluding romance, which is 0 to 100.

Allowing relationships to go negative allows the developers to sort of squash some old relationship values together (dislike, jealousy, admiration).

- RelTier in [enums.py](https://github.com/ClanGenOfficial/clangen/blob/development/scripts/cat_relations/enums.py) has all the values by name. The values change every 20 points of relation.

| Code  | Description  |
|---|---|
| "cat_from_id": "1727",  |  This cat's feelings towards "cat_to_id". This is also the owner of the relations file. |
|   "cat_to_id": "1109", |  This is the cat who is being felt about. |
| "mates": false,  | If they are mates, this will be true. Allows "mate relation" events to trigger. |
| "family": false,  | If they are related in some way, this will be true. Allows "family relation" events to trigger.  |
|  "romance": 0, | Romantic feelings "cat_from_id" feels toward "cat_to_id"  |
| "like": 0,  | The dislike-like "cat_from_id" feels toward "cat_to_id"  |
|  "respect": 0, | The jealousy-respect "cat_from_id" feels toward "cat_to_id" |
|  "comfort": 0, | The discomfort-comfort "cat_from_id" feels toward "cat_to_id" |
|  "trust": 0, | The fear-trust "cat_from_id" feels toward "cat_to_id" |
|  "log": [], | A log of all relation events the cats had together. Logs can be custom texts |
|  "no_longer_neutral": [] | "no_longer_neutral" prevents the cats from being neutral in a value once they surpass a certain point. It'll then "skip" neutral status (-6 - 6) and go to the next tier in the relation value |

---

"no_longer_neutral" example:

```json
[
    {
        "cat_from_id": "209",
        "cat_to_id": "175",
        "mates": false,
        "family": false,
        "romance": 0,
        "like": 12,
        "respect": 0,
        "comfort": 12,
        "trust": 0,
        "log": [],
        "no_longer_neutral": [
            "like",
            "comfort"
        ]
    }
]
```

"like" and "comfort" have surpassed the neutral pool, therefore "no_longer_neutral" is triggered and added those values to its list.

---
