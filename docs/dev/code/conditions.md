# Adding Conditions

New conditions must have their required information format added to either `resources/dicts/conditions/temporary_conditions` or `resources/dicts/conditions/permanent_conditions`. They should be sorted into the `minor.json`, `major.json`, and `severe.json` according to their severity.

## Temporary Condition Format

```json
    "name": {
        "severity": "",
        "duration": 0,
        "is_complication": false,
        "mortality": {
            "newborn": 0.0,
            "kitten": 0.0,
            "adolescent": 0.0,
            "young adult": 0.0,
            "adult": 0.0,
            "senior adult": 0.0,
            "senior": 0.0
        },
        "infectiousness": 0.0,
        "immune_system_effect": 0,
        "side_effect": {
            "condition": 0.0
        },
        "progression": {
            "condition": {
                "chance": 0.2,
                "when": "STATE",
                "allow_scar": false
            }
        },
        "risks": {
            "condition": 0.0
        },
        "treatment_strength": {
            "1": [],
            "2": [],
            "3": []
        }
        "possible_scars": []
    },
```

### Parameters

#### name: str
Internal code-name for the condition. This will not be seen in-game. 

***

#### severity: str
Can be `minor`, `major`, or `severe`. `minor` conditions will not prevent the cat from working. For temporary conditions, the difference between `major` and `severe` is mostly arbitrary and doesn't have gameplay effects beyond a display change in the medicine cat den. `major` or `severe` conditions **will** prevent the cat from working.

***

#### duration: int
The number of moons this condition will last

***

#### is_complication: bool
Set to True if this is a complication. A complication is a condition that cannot be given *except* as a risk of another condition (henceforth referred to as the "base" condition.) The base condition will not be able to fully heal until the complication is healed.

***

#### mortality: dict[str, float]
The percentage chance for this condition to kill each age group of cat. Percentages are written as floats (i.e. `0.1` is 10% chance to kill). If this condition shouldn't kill, then leave the dictionary empty: `"mortality": {}`

***

#### infectiousness: float
The percentage chance that this condition will pass onto another cat.

***

#### immune_system_effect: float
This can be used to make the cat more susceptible to infection from other conditions. It will be added to the percentage chance of other condition's infectiousness when that condition attempts to infect this cat. 

>For example:
>If this condition has an `immune_system_effect` of 0.1 and a second condition with an infectiousness of 0.5 attempts to infect our cat, then the chance of infection will be 0.6 (or 60%)

***

#### side_effect: dict[str, float]
A dictionary of potential side effects. A side effect is an additional condition that has a chance of being applied when a condition is given to cat.  

>For example:
> `cat_bite` has a `side_effect` of `blood_loss`. When a cat is given `cat_bite`, they might also gain `blood_loss`.

These are written with the key as the condition name and the value as the percentage chance to be applied, like so:

```json
"side_effect": {
    "torn_pelt": 0.2,
    "torn_ear": 0.2,
    "blood_loss": 0.4
}
```

***

#### progression: dict[str, float]
A dictionary of potential progressions. A progression is a new condition that the current condition can *become*. 

> For example:
> `whitecough` has a `progression` for `greencough`. When a cat has `whitecough`, there's a chance that it may become `greencough`. The cat will no longer have the `whitecough` condition, they will only have `greencough`.

These are written with the key as the condition name and the value as the percentage chance as well as the `State` required and if or not a scar can be given, like so:

```json
"progression": {
    "paralyzed": {
        "chance": 0.2,
        "when": "HEALED",
        "allow_scar": false
    }
    "weak_leg": {
        "chance": 0.4,
        "when": "CONTINUING",
        "allow_scar": true
    }
},
```
**Chance**
This is the percentage chance to occur. Set this to `2.0` if it should *always* occur. 

**State Requirements**
The `when` parameter is used to dictate which `State` the condition must be in for the progression to occur. Conditions can be in 5 states: `SKIPPED`, `FATAL`, `HEALED`, `REVEALED`, and `CONTINUING`.

- `SKIPPED` should never be used for this parameter, as it marks the condition as *nothing* should occur this moon. 
- `FATAL` means the condition will kill the cat this moon. Generally, there is no reason for progression to occur upon the cat dying.
- `HEALED` means the condition will heal this moon. This is commonly used for progressions that should be the *result* of a condition. For example: a mangled leg heals, but is permanently weakened.
- `REVEALED` is used when a congenital condition is *discovered* and becomes visible to the player. Generally, there is no reason for progression to occur here.
- `CONTINUING` is used when a cat simply continues to have the condition for this moon; no death, healing, or revealing. The majority of progressions happen in this state. This is also when risks have a chance to be gained.

**Allow Scar**
This allows you to dictate if progressing to this condition can come with a scar. Setting it to False means that no scar can be given at all. 

***

#### risks: dict[str, float]
A dictionary of potential risks. A risk is a new condition that the cat can be given by the current condition.

> For example:
> `bite_wound` has `an_infected_wound` in its `risks`. While a cat has `bite_wound`, they can gain the condition `an_infected_wound` at any time.

These are written with the key as the condition name and the value as the percentage chance to occur, like so:

```json
"risks": {
    "infection": 0.2,
    "festering_wound": 0.2
}
```

***

#### treatment_strength: dict[str, list[str]]
A dictionary of the various treatments for this condition. Each number category corresponds to the strength of that herb for this condition. Categories can be left empty, but must always be present.

A `treatment_strength` parameter could look like:
```json
"treatment_strength": {
    "1": [
        "cobwebs",
        "marigold",
        "tansy",
        "moss"
    ],
    "2": [],
    "3": [
        "poppy",
        "goldenrod",
        "burdock"
    ]
}
```

The [Herb Dictionary](../writing/reference/herbs.md) is available as a reference for what herbs are available and how they should be used in ClanGen.

***

#### possible_scars: list[str]
A list of possible scars that this condition can apply once healed.

!!! important
  Do not list scars that can be given by progressions that the cat can "heal" into. For example, do not list `NOPAW` as a possible scar for `mangled_leg`. `mangled_leg` is able to progress into `lost_leg`. `lost_leg` will list `NOPAW` as a scar and will give that scar IF the `mangled_leg` progresses into `lost_leg`.


***

## Permanent Condition Format
```json
    "name": {
        "severity": "",
        "can_be_congenital": false,
        "can_be_acquired": false,
        "requires_scar": false,
        "remove_on_death": true,
        "moons_until_discovery": 0,
        "mortality": {},
        "immune_system_effect": 0,
        "progression": {
            "condition": 0.0
        },
        "risks": {
            "condition": 0.0
        },
        "treatment_strength": {
            "1": [],
            "2": [],
            "3": []
        },
        "possible_scars": []
    },
```

### Parameters
#### name: str
Same as [temporary condition name](#name-str) 

***

#### severity: str
Can be `minor`, `major`, or `severe`. `major` and `severe` conditions can cause the cat to retire to the `elder` rank early. This chance is higher for `severe` conditions.

***

#### can_be_congenital: bool
Marks if this condition can be given at birth.

***

#### can_be_acquired: bool
Marks if this condition can be given later in life

***

#### requires_scar: bool
Marks if this condition can only be applied if the cat has a pre-requisite scar. Scars needed *must* be listed in [possible scars](#possible_scars-liststr-1). Defaults to False.

***

#### remove_on_death: bool
Marks if this condition will be removed from the cat upon death. Defaults to True.

***

#### moons_until_discovery: int
If this condition is congenital, this dictates how many moons the condition can "hide" before being noticed by the cat.

***

#### mortality: dict[str, float]
Same as [temporary condition mortality](#mortality-dictstr-float)

***

#### immune_system_effect: float
Same as [temporary condition immune_system_effect](#immune_system_effect-float)

***

#### progression: dict[str, float]
Same as [temporary condition progression](#progression-dictstr-float)

***

#### risks: dict[str, float]
Same as [temporary condition risks](#risks-dictstr-float)

***

#### treatment_strength: dict[str, list[str]]
Same as [temporary condition treatment_strength](#treatment_strength-dictstr-liststr)

***

#### possible_scars: list[str]
A list of possible scars given when the cat gains this condition.

***

## New Condition Checklist

- [ ] Add condition info dictionary to `resources/dicts/conditions/permanent_conditions` or `resources/dicts/conditions/temporary_conditions`
- [ ] Add display name to `lang/en/conditions/temporary_conditions.en.json` or `lang/en/conditions/permanent_conditions.en.json`
- [ ] If the condition can kill, add death strings to `lang/en/conditions/death_strings`
- [ ] If the condition is an illness or pest where its generation is linked to the seasons:
    - [ ] Add it to `condition_related.seasonal_chance` in `game_config.toml`
    - [ ] Add gain strings to `lang/en/conditions/gain_temporary_condition_strings`
- [ ] If the condition is temporary, add heal strings to `lang/en/conditions/healed_strings`
- [ ] If the condition is permanent and congenital, add reveal strings to `lang/en/conditions/reveal_condition_strings`
- [ ] If the condition has risks, add risk strings to `lang/en/conditions/risk_strings`
- [ ] If the condition can progress, add progression strings to `lang/en/conditions/progression_strings`