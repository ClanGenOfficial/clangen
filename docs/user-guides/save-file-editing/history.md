The history files of a cat log important events such as their apprenticeship influence, death message, murder, and more. While parts of this file is back-end, most of it is text shown in the history tab of a cat.

Big thanks to Sel's Emberclan for their extensive examples of the history files.

## Beginning

The code "beginning" involves the circumstances of the cat's initial generation. When a cat is generated for the first time, "beginning" is what is changed.

"beginning", for example, generates the text such as:

!!! quote "Beginning Text"
      *"Melodystar was born into the Clan where she currently resides. She was born on moon 572 during Leaf-fall."*

```json
    "beginning": {
        "clan_born": true,
        "birth_season": "Leaf-fall",
        "age": 0,
        "moon": 67
    },
```

`"clan_born": true,`

"clan_born" tracks whether the cat was born into the player clan or if they were generated as an outsider. If they are an outsider (including other clan cats), "clan_born" will always be set to `false`.

`"birth_season": "Leaf-fall",`

Birth season is only detailed IF the cat is born within the clan. If not, it'll always be `null`.

`"age": 0,`

This is the age the cat was when they generated initially. If "clan_born" is set to true, this with always be zero (0). Otherwise, it'll be the age the cat was when they generated. (ex: "age": 12,)

`"moon": 67`

This details the clan's age when the cat was generated.

---

### Clan Founders

You might notice that your clan founders (the cats who you chose while creating the clan) will have a blank beginning (`"beginning": {},`). "beginning" will only be generated if the cat was generated moon 1 and beyond.

- Once "beginning" is blank, the game will assume the cat is a clan founder, and will set their information appropriately.

---

## mentor_influence

!!! warning
     This part of the guide does not go in detail on the natural process of mentor influencing. Please search for another guide or ask the community.

Mentors can influence the trait and/or skill of their apprentice. When the apprentice is influenced, this part of their history is changed to reflect that. 

Influence also changes the text of their graduation ceremony and the details in their history tab. 

!!! quote "Graduation Text"
     *"She was mentored by Sproutrush. Sproutrush influenced her to be more likely to be ready for a fight, interact with others, and break rules that don't suit her."*

It is good to note that "mentor_influence" has **two stages** of generation: influenced and still an apprentice, and influenced and graduated.

Influenced and still an apprentice:

```json
    "mentor_influence": {
        "trait": {
            "1411": {
                "lawfulness": -5
            }
        },
        "skill": {
            "1411": {
                "HUNTER": 9
            }
        }
    },
```

Influenced and graduated:

```json
    "mentor_influence": {
        "trait": {
            "34": {
                "sociability": -3,
                "stability": -5,
                "aggression": -2,
                "strings": [
                    "be cold towards others",
                    "make impulsive decisions",
                    "try to avoid violence"
                ]
            }
        },
        "skill": {}
    },
```

`"strings"` is the text that is applied to the history tab based what has been influenced. Each influence applies ONE string. This is generated with the graduation event naturally, but you can apply strings early in theory.

- For example, if the apprentice had 3 facets and 1 skill influenced, there would be 4 individually applied strings.

You can find the strings for traits: [history.py](https://github.com/ClanGenOfficial/ClanGen/blob/development/scripts/cat/history.py) - `facet_influence_text`

You can find the strings for skills: [history.py](https://github.com/ClanGenOfficial/ClanGen/blob/development/scripts/cat/history.py) - `skill_influence_text`

### Editing

#### "trait": {}

```json
    "mentor_influence": {
        "trait": {
            "34": {
                "sociability": -3,
                "stability": -5,
                "aggression": -2,
                "strings": [
                    "be cold towards others",
                    "make impulsive decisions",
                    "try to avoid violence"
                ]
            }
        },
        "skill": {}
    },
```

`"trait"` is the influence directed toward the apprentices *facets*. Facets are a string of numbers that make up the cat's trait, and they influence which trait the cat has.

- the facets are "sociability", "stability", "aggression", and "lawfulness". [#how-facets-reflect-on-the-trait](https://ClanGen.io/docs/dev/writing/reference/trait-dictionary/#how-facets-reflect-on-the-trait)

`"34": {}` is the ID of the mentor who is influencing this specific change onto the apprentice. Keep in mind that more than one mentor can influence the apprentice.

```json
    "34": {
        "sociability": -3,
        "stability": -5,
        "aggression": -2,
        "strings": [
            "be cold towards others",
            "make impulsive decisions",
            "try to avoid violence"
        ]
    }
```

Let's look specifically at the trait influences here. Trait influences are formatted as followed:

`"ID": {}`: ID of the mentor causing this influence.

`"facetname"`: +/-# of how much it will change. For precaution’s sake, influence for traits should not pass 10/-10

`"strings": []`: the flavor text determined by the above influence. You can find the strings for traits: [history.py](https://github.com/ClanGenOfficial/ClanGen/blob/development/scripts/cat/history.py) - `facet_influence_text`

---

If you want to make more than one mentor influence the trait, you'll add another ID to the "trait" dict like below:

```json
"trait": {
    "34": {
        "sociability": -3,
        "stability": -5,
        "aggression": -2,
        "strings": [
            "be cold towards others",
            "make impulsive decisions",
            "try to avoid violence"
        ]
    },
    "100": {
        "aggression": 2,
        "strings": [
            "defend {PRONOUN/m_c/poss} beliefs"
        ]
    }
},
"skill": {}
```

---

#### "skill": {}

```json
    "skill": {
        "1273": {
            "CAMP": 15,
            "strings": [
                "caring for camp"
            ]
        }
    },
```

"skill" is the influence the mentor has on a skill.

"skill" is only influenced if the mentor and the apprentice share the same Skillpath. If they do, the mentor will improve the skill.

- "Skillpath": Skill paths are connected to specific skills. TEACHER, for example, is the best mentor skill because they're connected to every Skillpath except for supernatural.
- Skillpath's are found in [skills.py](https://github.com/ClanGenOfficial/ClanGen/blob/development/scripts/cat/skills.py) - class Skillpath and influence_flags

Save file editing, in theory, overrides the above logic. You can influence the skill however you like in this file, whether the mentor shares a Skillpath with the apprentice or not.

```json
    "1273": {
        "CAMP": 15,
        "strings": [
            "caring for camp"
        ]
    }
```

Let's specifically look at the "skill" influence here.

`"ID": {}`: The ID of the mentor who is causing this influence.

`"SKILLNAME"`: This is skill being influenced and the "level" the skill will be once they graduate.

- The below ranges numbers are what's available to put into the influence.

```
Interest (kittens & apps): 0
Tier 1: 1 - 9
Tier 2: 10 - 19
Tier 3: 20 - 29
```

`"strings": []`: the flavor text determined by the above influence. You can find the strings for skills: [history.py](https://github.com/ClanGenOfficial/ClanGen/blob/development/scripts/cat/history.py) - `skill_influence_text`

## app_ceremony

This part of the code will only generate if the cat had a graduation ceremony. Otherwise, this will be left blank: `"app_ceremony": {}`.

!!! quote "Ceremony Text"
     *..."When she graduated, she was honored for her thoughtfulness. She graduated at 12 moons old."*

```json
    "app_ceremony": {
        "honor": "insight",
        "graduation_age": 11,
        "moon": 689
    },
```

`"honor": "insight"`: the "honor" string is based on the trait they are given during the ceremony, aka the product of the "trait" influence in "mentor_influence".

- The honor strings are found in [ceremony_traits.json](https://github.com/ClanGenOfficial/ClanGen/blob/development/resources/lang/en/events/ceremonies/ceremony_traits.json)
- IF they were not influenced, "honor" will be randomized based on the current trait.

`"graduation_age": 11,`: The age the cat was when they graduated.

`"moon": 689`: The clan age moon they graduated on.

## lead_ceremony

"lead_ceremony" is generated directly when a cat is promoted to "leader". The text generated is based on the cats in the afterlife giving them their lives.

The lead_ceremony is a large chunk of text. All sentences used in the ceremony are separate flavor texts puzzled together to make the ceremony, so there isn't a clear "format" for leader ceremonies. They can, however, be customized.

Previous leaders keep their lead_ceremony text! So long as they have their history file, you can look at previous ceremonies through there.

Lead ceremony texts are in game folder > resources > lang > en > events

## afterlife_acceptance

Added in 0.13, this part of the history doesn't have an implemented feature just yet (purely flavor text until further notice). It is connected to the clan_cats.json afterlife affinity's.

afterlife_acceptance text and their ID's are found in [afterlife.en.json](https://github.com/ClanGenOfficial/ClanGen/blob/development/resources/lang/en/cat/afterlife.en.json)

Based on the cat's afterlife affinity's in clan_cats.json and if they're a kitten rank, they'll generate with an "afterlife_acceptance" text when they die.

- Until the feature is fleshed out in how affinity is applied, the cats will get default texts based on where the afterlife guide currently is (starclan or dark forest)

`"afterlife_acceptance": "starclan_default_2"` 

!!! quote "Afterlife Text"
     *"The life Stoatnoise lived led to the stars, inevitably."*

## possible_history

Essentially, this part of the file holds the potential generated text a cat might get due to a condition gained from an event/patrol. If there is not a possible history, it'll be blank. `"possible_history": {},`

Every event and patrol has the opportunity to make custom death and scar texts based on where the condition originated from. In the example below, "broken bone" originated from falling off a cliff. 

When this condition duration is over, and if it rolls into death or a scar, then the game will pull from these texts instead of the default.

```json
    "possible_history": {
        "broken bone": {
            "death_text": "m_c died from {PRONOUN\/m_c\/poss} 
            wounds after falling off a cliff.",
            "scar_text": "m_c was scarred when 
            {PRONOUN\/m_c\/subject} fell off a cliff.",
            "other_cat": "104"
        }
    },
```

`"broken bone": {}`: The connected condition to the possible text.

`"death_text"`: The text that will be given if this cat dies due to the condition. It would be transferred to "died_by".

`"scar_text"`: The text that will be given if this cat is scarred due to the condition recovering. It would be transferred to "scar_events".

`"other_cat"`: Tracks whether a cat was involved in the condition event. If r_c is used, the ID/cat listed here will be mentioned. If not, it'll be null. `"other_cat": null`

You might be looking at the pronoun stuff and wondering what it is. These are the tags that makes plugging correct pronouns in text possible. [Pronoun Tags](https://ClanGen.io/docs/dev/writing/reference/pronoun-tags/)

---

Naturally, possible_history would likely only have one condition listed at a time, unless the cat is extremely unlucky with ClanGen's RNG. However, if you'd like to add more than one to "possible_history":

```json
    "possible_history": {
        "condition name": {
            "death_text": "",
            "scar_text": "",
            "other_cat": null
        },
        "condition name": {
            "death_text": "",
            "scar_text": "",
            "other_cat": null
        }
    },
```

Simply place a comma after the second to last bracket `}` in the file, then add a new condition and it's text afterward.

---

## died_by

"died_by" is the function that keeps track of the cats death history text.

!!! quote "Death Text"
     *"This cat died from old age."*

```json
    "died_by": [
        {
            "involved": "182",
            "text": "m_c died of old age.",
            "moon": 297
        }
    ],
```

`"involved": "182",`: Tracks if a cat was involved in the death event. If r_c is used within the text, it'll pull the ID/cat listed here. If there isn't an involved cat, the line will be null. `"involved": null,`

`"text"`: This is the death text you see in the history file. `m_c` is the cat that owns the history file.

`"moon": 297`: The clan age moon the cat died on.

---

For cats outside of the leader, they'll only have one text in "died_by" (naturally). However, the functionality of leaders allows more than one text.

For example:

```json
    "died_by": [
        {
            "involved": "28",
            "text": "m_c lost a life when {PRONOUN\/m_c\/subject} 
            {VERB\/m_c\/were\/was} swept away by a flood.",
            "moon": 49
        },
        {
            "involved": "44",
            "text": "m_c lost a life when {PRONOUN\/m_c\/subject} 
            defended r_c from a fox.",
            "moon": 82
        },
        {
            "involved": "11",
            "text": "m_c lost a life when {PRONOUN\/m_c\/subject} 
            died of old age.",
            "moon": 94
        }
    ],
```

---

## scar_events

When a cat gets a scar from an event, the text of how it happened will be logged here.

```json
    "scar_events": [
        {
            "involved": "3",
            "text": "m_c was scarred by a Twoleg trap.",
            "moon": 21
        }
    ],
```

`"involved": "182",`: Tracks if a cat was involved in the scar event. If r_c is used within the text, it'll pull the ID/cat listed here. If there isn't an involved cat, the line will be null. `"involved": null,`

`"text"`: This is the scar text you see in the history file. `m_c` is the cat that owns the history file.

`"moon": 297`: The clan age moon the cat died on.

---

You can have multiple scar events. For example:

```json
    "scar_events": [
        {
            "involved": "3",
            "text": "m_c was scarred by a Twoleg trap.",
            "moon": 21
        },
        {
            "involved": null,
            "text": "m_c was scarred by a bite wound.",
            "moon": 100
        }
    ],
```

## Murder

Murder code! Stores all information relating to a murder. This code will change for both the murderer and victim, so when save file editing, be sure to edit BOTH the murderer and victims histories.

- If you do not wish for this cat to have a murder history, change the line to be "murder": {} (no comma at the end!)

Murder code changes depending on whether the murder was revealed. Make sure you're using the correct example for the situation you want, otherwise histories may error.

### Unrevealed Murderer

```json
    "murder": {
        "is_murderer": [
            {
                "victim": "189",
                "revealed": {
                    "to_clan": false,
                    "aware_individuals": []
                },
                "moon": 1
            }
        ]
    }
```

`"murder": {}`: The start of the murder code. Holds both victim and murder information.

`"is_murderer": [],`: The beginning of the code for a murderer.

`"victim": "27",`: ID of their victim.

`"revealed": {},`: Tracks if the murder was revealed, and by who

- `"to_clan": true,`: True if the whole clan is aware of the murder, false if not. If this is true, it overrides the list in "aware_individuals".
- `"aware_individuals": []`: The individuals who know about the murder, but is a "secret" to the rest of the clan.

`"moon": 7`: The clan moon age in which the cat murdered the victim.


### Revealed murder

Example for revealed to clan:
```json
    "murder": {
        "is_murderer": [
            {
                "victim": "50",
                "revealed": {
                    "to_clan": true,
                    "aware_individuals": []
                },
                "moon": 130
            }
        ]
    }
```

Example for revealed to individual cats:
```json
    "murder": {
        "is_murderer": [
            {
                "victim": "50",
                "revealed": {
                    "to_clan": false,
                    "aware_individuals": [
                        "10",
                        "101"
                    ]
                },
                "moon": 130
            }
        ]
    }
```


`"murder": {}`: The start of the murder code. Holds both victim and murder information.

`"is_murderer": [],`: The beginning of the code for a murderer.

`"victim": "27",`: ID of their victim.

`"revealed": {},`: Tracks if the murder was revealed, and by who

- `"to_clan": true,`: True if the whole clan is aware of the murder, false if not. If this is true, it overrides the list in "aware_individuals".
- `"aware_individuals": []`: The individuals who know about the murder, but is a "secret" to the rest of the clan.

`"moon": 7,`: The clan moon age in which the cat murdered the victim.


### Unrevealed murder victim
Reminder that you have to make the victim deceased through the clan_cats and died_by code in the history file. "Planning" murders should be done through future events.

```json
    "murder": {
        "is_victim": [
            {
                "murderer": "185",
                "revealed": {
                    "to_clan": false,
                    "aware_individuals": []
                },
                "text": "m_c was secretly murdered by Gravelspeckle.",
                "unrevealed_text": null,
                "moon": 1
            }
        ]
    }
```

`"murder": {}`: The start of the murder code. Holds both victim and murder information.

`"is_victim": [],`: The beginning of the code for a victim of a murder.

`"murderer": "185",`: ID of the murderer

`"revealed": {},`: Tracks if the murder was revealed, and by who

- `"to_clan": true,`: True if the whole clan is aware of the murder, false if not. If this is true, it overrides the list in "aware_individuals".
- `"aware_individuals": []`: The individuals who know about the murder, but is a "secret" to the rest of the clan.

`"text"`: The text that would be shown in the history of the victim. Usually it's "m_c was secretly murdered by [murderer]" but it can be custom.

`"moon": 7,`: The clan moon age in which the cat was murdered.


### Revealed murder victim
Reminder that you have to make the victim deceased through the clan_cats and died_by code in the history file. "Planning" murders should be done through future events.

```json
    "murder": {
        "is_victim": [
            {
                "murderer": "27",
                "revealed": {
                    "to_clan": true,
                    "aware_individuals": []
                },
                "text": "m_c was pushed under a monster by Ratspot.",
                "moon": 82
            }
        ]
    }
```

`"murder": {}`: The start of the murder code. Holds both victim and murder information.

`"is_victim": [],`: The beginning of the code for a victim of a murder.

`"murderer": "185",`: ID of the murderer

`"revealed": {},`: Tracks if the murder was revealed, and by who

- `"to_clan": true,`: True if the whole clan is aware of the murder, false if not. If this is true, it overrides the list in "aware_individuals".
- `"aware_individuals": []`: The individuals who know about the murder, but is a "secret" to the rest of the clan.

`"text"`: The text that would be shown in the history of the victim. This will usually match the "died_by" text.

`"moon": 7,`: The clan moon age in which the cat was murdered.

---