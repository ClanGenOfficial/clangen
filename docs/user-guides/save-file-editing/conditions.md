
!!! warning
     Conditions files do not generate for cats who don't currently have an applied condition. If none of the cats have conditions, the conditions folder will not generate either.

The conditions folder holds all applied conditions (injuries, illnesses, and permanent conditions) within the playerclan. This folder and its files are what you'll edit if you want to create cats with disabilities or if you want a cat to be pregnant.

## Formatting

Conditions are complex, and so are their files. People struggle to understand the formatting involved, so I'll briefly share what tends to help me.

The conditions file is boiled down to three main components:

- `{}`: the dict holding all the information in the file. This has to be at the beginning `{` and end `}` of the json for it to properly work
- `"condition type": {}`: the dict holding all the relevant conditions for the *specific condition type*.
    - You cannot, for example, have `"illnesses": {}` present twice in the file. If you have two illness conditions, they'll both go within the one condition type section.
- `"condition name": {}`: the dict holding all the relevant information for the *specific condition*.
    - This will be stuff like "one bad eye", "paralyzed", "weak leg" under the relevant "condition type", which in this case would be `"permanent condition": {}`

When adding to the same dict, you need to remember your commas and the placement of your brackets. Remember to utilize [jsonlint.com](https://jsonlint.com/) to check if the formatting is correct.

## Condition Templates

Every type of condition has their own coding, so make sure you're applying the correct condition to the correct template! 

For example, "one bad eye" is a permanent condition. You cannot use the template for injuries for "one bad eye". Otherwise, it will not recognize the condition and it'll be missing vital information.

### Illnesses

```json
   "illnesses": {
        "condition name": {
            "severity": "",
            "mortality": 0,
            "infectiousness": 0,
            "duration": 0,
            "moon_start": 0,
            "risks": [],
            "event_triggered": false
        }
    }
```

### Injuries

```json
    "injuries": {
        "condition name": {
            "severity": "",
            "mortality": 0,
            "duration": 0,
            "moon_start": 0,
            "illness_infectiousness": [],
            "risks": [],
            "complication": null,
            "cause_permanent": [],
            "event_triggered": false,
            "potential_scars": []
        }
    }
```

### Permanent Conditions

```json
   "permanent conditions": {
        "condition name": {
            "severity": "",
            "born_with": false,
            "moons_until": 0,
            "moon_start": 0,
            "mortality": 0,
            "illness_infectiousness": [],
            "risks": [],
            "complication": null,
            "event_triggered": false,
            "moons_with": 0
        }
    }
```

## Condition Code

Here is a section that explains the conditions code line by line for each specific condition type. Yes, there are differences!

#### Risks

What do risks look like? Risk have three main components:

- `{}`: the dict holding the individual risk information
- `"name"`: the name of the risk
- `"chance"`: the chance of the risk occurring (1/number)

```json
    "risks": [
        {
            "name": "sore",
            "chance": 20
        }
    ],
```

If you want to add more than one risk to the condition, place a comma after the `}` ending bracket and add on. For example:

```json
    "risks": [
        {
            "name": "sore",
            "chance": 20
        },
        {
            "name": "dehydrated",
            "chance": 20
        }
    ],
```

Some conditions have their own default risks connected to them. However, you can theoretically apply additional risks to the condition (that it normally wouldn't have) if your heart desires.

### Explaining illnesses

| Code  | Description  |
|---|---|
| "severity": "severe"  | "severe" and "major" disallow the cat from working. "minor" means they are still allowed to work.  |
| "mortality": 20,  |  "Mortality" is the chance (1/number) of a cat dying from this condition based on age. Setting the mortality to 0 means the cat will not die from the condition. |
| "infectiousness": 0,  | The chance (1/number) of this condition spreading to other cats. 0 = not infectious |
| "duration": 1,  | A count-down to how many moons until the condition heals.  |
|  "moon_start": 1, | The clan age moon the condition developed on.  |
| "risks": [],  |  Additional "small" Additional "small" conditions that may be given during the duration of the condition. |
|  "event_triggered": false, | Should be left as false if save file editing. |

Illnesses have their own information for every individual condition. Please reference the file [illnesses.json](https://github.com/ClanGenOfficial/clangen/blob/release_0.13.0/resources/dicts/conditions/illnesses.json) within resources > dicts > conditions when adding conditions to a cat

### Explaining injuries

| Code  | Description  |
|---|---|
| "severity": "severe"  | "severe" and "major" disallow the cat from working. "minor" means they are still allowed to work.  |
| "mortality": 20,  |  "Mortality" is the chance (1/number) of a cat dying from this condition based on age. Setting the mortality to 0 means the cat will not die from the condition. |
| "duration": 1,  | A count-down to how many moons until the condition heals.  |
|  "moon_start": 1, | The clan age moon the condition developed on.  |
| "illness_infectiousness": [],  | Unused code, please keep empty |
| "risks": [],  |  Additional "small" conditions that may be given during the duration of the condition. |
| "complication": null,  | Used in the situation where the condition is infected or festering. Add the condition "an infected wound" or "a festering wound" into illnesses, then add the corresponding "infected"/"festering" to replace null,  |
| "cause_permanent": [],  | Possible given permanent conditions when an injury heals. Looks like "cause_permanent": ["lost a leg"],  |
|  "event_triggered": false, | Should be left as false if save file editing. |
|  "potential_scars": [] | A list of potential scars the cat can get from this condition once it heals. "potential_scars": ["HALFTAIL","NOTAIL"]. |

Injuries have their own information for every individual condition. Please reference the file [injuries.json](https://github.com/ClanGenOfficial/clangen/blob/release_0.13.0/resources/dicts/conditions/injuries.json) within resources > dicts > conditions when adding conditions to a cat

### Explaining Permanent Conditions

| Code  | Description  |
|---|---|
| "severity": "severe"  | Unlike other conditions, this is used to track if a cat should retire. "minor" = will not retire, "major" = may retire, "severe" = will retire. This does not apply if "cats do not retire automatically" is toggled on. |
| "born_with": true,  |  Tracks if the cat was born with the perm condition. Only perm conditions specifying "sometimes" or "always" within the congenital line can be set to true. |
| "moons_until": 1,  | Determines if the conditions need to be revealed. "born_with": true conditions are the only ones with a reveal event, so keep 0 (zero) if "born_with": false.  |
|  "moon_start": 1, | The clan age moon the condition developed on. If "born_with": true, keep at 0 (zero).  |
| "mortality": 0, |  "Mortality" is the chance (1/number) of a cat dying from this condition based on age. Setting the mortality to 0 means the cat will not die from the condition.   |
| "illness_infectiousness": [],  | Unused code, please keep empty |
| "risks": [],  |  Additional "small" conditions that may be given during the duration of the condition. |
| "complication": null,  | Used in the situation where the condition is infected or festering. Add the condition "an infected wound" or "a festering wound" into illnesses, then add the corresponding "infected"/"festering" to replace null,  |
|  "event_triggered": false, | Should be left as false if save file editing. |
| "moons_with": 0,  | Tracks how many moons the cat had the perm condition, unused. |

Permanent conditions have their own information for every individual condition. Please reference the file [permanent_conditions.json](https://github.com/ClanGenOfficial/clangen/blob/release_0.13.0/resources/dicts/conditions/permanent_conditions.json) within resources > dicts > conditions when adding conditions to a cat

## Adding Conditions

!!! warning
     If you do not have a conditions folder, you will have to create one. If the specific cat does not have a conditions file, you will need to make one for them.


Here I'll explain how to add conditions to cats with a few situations in mind.

All relevant condition information, like what conditions have risks, what mortality's it has, ect, is located in resources > dicts > conditions folder. These examples will be pulling from those files to make the conditions game accurate.

Make sure to use a json validator, such as jsonlint.com, to validate the file before you open the game in case the formatting is incorrect.

### File already has a condition

#### Adding to a condition type

When adding to a condition type that already exists in the file, all you're doing is just adding a new section of "condition name": {} to the third to last bracket. 

For example, this cat already has "fleas" and I want to add "heat stroke" - both of these are illnesses, so they'll both go within "illnesses": {}

Before editing:
```json
{
    "illnesses": {
        "fleas": {
            "severity": "minor",
            "mortality": 0,
            "infectiousness": 15,
            "duration": 4,
            "moon_start": 4,
            "risks": [
                {
                    "name": "torn pelt",
                    "chance": 20
                }
            ],
            "event_triggered": false
        }
    }
}
```

Copy the fleas section from `"fleas": {` to the ending bracket `}`. Add a comma after the third to last `}` bracket, then paste.

After: 
```json
{
    "illnesses": {
        "fleas": {
            "severity": "minor",
            "mortality": 0,
            "infectiousness": 15,
            "duration": 4,
            "moon_start": 4,
            "risks": [
                {
                    "name": "torn pelt",
                    "chance": 20
                }
            ],
            "event_triggered": false
        },
        "fleas": {
            "severity": "minor",
            "mortality": 0,
            "infectiousness": 15,
            "duration": 4,
            "moon_start": 4,
            "risks": [
                {
                    "name": "torn pelt",
                    "chance": 20
                }
            ],
            "event_triggered": false
        }
    }
}
```

Now edit the new section for the condition you want. Go to the [conditions code information](https://github.com/ClanGenOfficial/ClanGen/tree/development/resources/dicts/conditions) and use the information to edit the copied section to reflect the condition you want. For example, heat stroke would look like this:

```json
        ....
        },
        "heat stroke": {
            "severity": "severe",
            "mortality": 20,
            "infectiousness": 0,
            "duration": 1,
            "moon_start": 4,
            "risks": [],
            "event_triggered": false
        }
    }
}
```

#### Adding another condition type

If the file doesn't already have the condition type for the condition you want to add, then you'll have to add it along with the condition.

For example, I want to add a permanent condition to a cat who already has fleas, which is an illness. I cannot add a permanent condition to "illnesses": {}, so I must add "permanent conditions": {}

Before editing:
```json
{
    "illnesses": {
        "fleas": {
            "severity": "minor",
            "mortality": 0,
            "infectiousness": 15,
            "duration": 4,
            "moon_start": 4,
            "risks": [
                {
                    "name": "torn pelt",
                    "chance": 20
                }
            ],
            "event_triggered": false
        }
    }
}
```

Copy from the templates provided [here](#condition-templates) for the condition type you want to add (this case, "permanent conditions"). Put a comma after the second to last bracket `}`, and paste the template:

```json
{
    "illnesses": {
        "fleas": {
            "severity": "minor",
            "mortality": 0,
            "infectiousness": 15,
            "duration": 4,
            "moon_start": 4,
            "risks": [
                {
                    "name": "torn pelt",
                    "chance": 20
                }
            ],
            "event_triggered": false
        }
    },
    "permanent conditions": {
        "condition name": {
            "severity": "",
            "born_with": false,
            "moons_until": 0,
            "moon_start": 0,
            "mortality": 0,
            "illness_infectiousness": [],
            "risks": [],
            "complication": null,
            "event_triggered": false,
            "moons_with": 0
        }
    }
}
```

Now edit the new section for the condition you want. Go to the [conditions code information](https://github.com/ClanGenOfficial/ClanGen/tree/development/resources/dicts/conditions) and use the information to edit the copied section to reflect the condition. For example, paralyzed would look like this:

```json
    ....
    },
    "permanent conditions": {
        "paralyzed": {
            "severity": "severe",
            "born_with": false,
            "moons_until": 0,
            "moon_start": 4,
            "mortality": 0,
            "illness_infectiousness": [],
            "risks": [
                {
                    "name": "an infected wound",
                    "chance": 60
                },
                {
                    "name": "torn pelt",
                    "chance": 30
                },
                {
                    "name": "sore",
                    "chance": 20
                },
                {
                    "name": "joint pain",
                    "chance": 20
                }
            ],
            "complication": null,
            "event_triggered": false,
            "moons_with": 0
        }
    }
}
```

### Adding to an empty file

If there wasn't a condition in the file, then that probably means you had to create a condition file. If so, make sure it's named `ID_conditions`, it's a .json file type, and it's within the conditions folder.

!!! tip
     It's easier to duplicate a JSON file from elsewhere, rename it, move to the desired location, and delete the contents. Many programs do not provide the option to create .json files.

Open the file and put `{}` into the file first. This is your holding dict that'll hold everything else in the file.

```json
{}
```

Put your curser in the middle of the {|} and press enter twice until there's an empty line between the two of them.

```json
{

}
```

Copy from the [templates provided](#condition-templates) and paste it in the empty line.

For example:
```json
{
    "permanent conditions": {
        "condition name": {
            "severity": "",
            "born_with": false,
            "moons_until": 0,
            "moon_start": 0,
            "mortality": 0,
            "illness_infectiousness": [],
            "risks": [],
            "complication": null,
            "event_triggered": false,
            "moons_with": 0
        }
    }
}
```

Now edit the new section for the condition you want. Go to the [conditions code information](https://github.com/ClanGenOfficial/ClanGen/tree/development/resources/dicts/conditions) and use the information to edit the copied section to reflect the condition you want.

Example with "lost a leg":
```json
{
    "permanent conditions": {
        "lost a leg": {
            "severity": "major",
            "born_with": false,
            "moons_until": 0,
            "moon_start": 10,
            "mortality": 0,
            "illness_infectiousness": [],
            "risks": [
                {
                    "name": "an infected wound",
                    "chance": 70
                },
                {
                    "name": "phantom pain",
                    "chance": 20
                },
                {
                    "name": "sore",
                    "chance": 20
                }
            ],
            "complication": null,
            "event_triggered": false,
            "moons_with": 0
        }
    }
}
```

## Deleting conditions

Deleting a condition is very simple. 

Find the condition file in the conditions folder that uses the cats ID.

!!! info
     If the condition you want to delete is the only condition in the file, you can safely delete the file entirely. Right click the conditions file and click "delete".

If the condition is the only one present in the condition type, do the following:

Let's say I want to get rid of fleas. Before editing:
```json
{
    "illnesses": {
        "fleas": {
            "severity": "minor",
            "mortality": 0,
            "infectiousness": 15,
            "duration": 4,
            "moon_start": 4,
            "risks": [
                {
                    "name": "torn pelt",
                    "chance": 20
                }
            ],
            "event_triggered": false
        }
    },
    "permanent conditions": {
        "lost a leg": {
            "severity": "major",
            "born_with": false,
            "moons_until": 0,
            "moon_start": 10,
            "mortality": 0,
            "illness_infectiousness": [],
            "risks": [
                {
                    "name": "an infected wound",
                    "chance": 70
                },
                {
                    "name": "phantom pain",
                    "chance": 20
                },
                {
                    "name": "sore",
                    "chance": 20
                }
            ],
            "complication": null,
            "event_triggered": false,
            "moons_with": 0
        }
    }
}
```

From "illnesses" until the bracket with the comma `},`, delete until it looks like below:
```json
{
    "permanent conditions": {
        "lost a leg": {
            "severity": "major",
            "born_with": false,
            "moons_until": 0,
            "moon_start": 10,
            "mortality": 0,
            "illness_infectiousness": [],
            "risks": [
                {
                    "name": "an infected wound",
                    "chance": 70
                },
                {
                    "name": "phantom pain",
                    "chance": 20
                },
                {
                    "name": "sore",
                    "chance": 20
                }
            ],
            "complication": null,
            "event_triggered": false,
            "moons_with": 0
        }
    }
}
```
---

If the condition is not the only one in the condition type, do the following:

Let's say I want to delete heat stroke from the file. 

Because it's not the only condition in "illnesses", I will delete only "heat stroke": {} and the comma above it:

```json
{
    "illnesses": {
        "fleas": {
            "severity": "minor",
            "mortality": 0,
            "infectiousness": 15,
            "duration": 4,
            "moon_start": 4,
            "risks": [
                {
                    "name": "torn pelt",
                    "chance": 20
                }
            ],
            "event_triggered": false
        },
        "heat stroke": {
            "severity": "severe",
            "mortality": 20,
            "infectiousness": 0,
            "duration": 1,
            "moon_start": 4,
            "risks": [],
            "event_triggered": false
        }
    }
}
```

After:

```json
{
    "illnesses": {
        "fleas": {
            "severity": "minor",
            "mortality": 0,
            "infectiousness": 15,
            "duration": 4,
            "moon_start": 4,
            "risks": [
                {
                    "name": "torn pelt",
                    "chance": 20
                }
            ],
            "event_triggered": false
        }
    }
}
```


# Editing pregnancies

This is a separate section due to having to edit multiple files but do not fret, it is easy work.

When editing pregnancies, there are two files involved: the pregnancy.json and the cats condition file. 

## Adding pregnancy

### Conditions file

!!! warning
     If you do not have a conditions folder, you will have to create one. If the specific cat does not have a conditions file, you will need to make one for them.

Find or create the conditions file for the cat. Unsure what their ID is? Go to the clan_cats, search their prefix (or information that makes them unique), then use the "ID" connected to them.

Using the instructions provided previously for [adding a condition](#adding-conditions), input the following code:

If you have to also add the condition type "injuries": {}:
```json
    "injuries": {
        "pregnant": {
            "severity": "major",
            "mortality": 40,
            "duration": 2,
            "moon_start": 1,
            "illness_infectiousness": [],
            "risks": [],
            "complication": null,
            "cause_permanent": [],
            "event_triggered": false,
            "potential_scars": []
        }
    }
```

If you already have an "injuries" section and only need to add the condition:
```json
        "pregnant": {
            "severity": "major",
            "mortality": 40,
            "duration": 2,
            "moon_start": 1,
            "illness_infectiousness": [],
            "risks": [],
            "complication": null,
            "cause_permanent": [],
            "event_triggered": false,
            "potential_scars": []
        }
```

When the code is put into the file, edit the `mortality` and `moon_start` to reflect the age and clan age moon. You can find the information for pregnancies [here](https://github.com/ClanGenOfficial/ClanGen/blob/development/resources/dicts/conditions/injuries.json).

Use a json validator such as jsonlint.com to check your formatting of the file before you proceed. If it's valid, head to the next step: pregnancy.json.

### pregnancy.json

!!! warning
     When this file is not in use, it will simply hold `{}`. Do not delete these brackets or the file itself - it is required for start up!

This file holds pregnancy information such as how many kittens the cat would get and who's the second parent.

Example of a pregnancy:
```json
   "54": {
        "second_parent": null,
        "moons": 1,
        "amount": 6
    }
```

| Code  | Description  |
|---|---|
| "54": {}  | The ID of the cat who is pregnant.  |
| "second_parent": null  | The second parent (parent2). This is used both for genetics and family trees. If it's set as `null`, only the pregnant cats genetics will be used to build the kittens appearance |
| "moons": 1,  |  How many moons the cat has been pregnant. You can set to 0 to randomize "amount" |
| "amount": 6  | How many kittens the birth event will generate once the pregnancy is over. Can be any number  |

#### Empty file

Put your curser in the middle of the {|} and press enter twice until there's an empty line between the two of them.

```json
{

}
```

Copy from the example above and paste within the empty line like so:

```json
{
    "54": {
        "second_parent": null,
        "moons": 1,
        "amount": 6
    }
}
```

Edit the code to reflect the outcome you want.

Use a json validator like jsonlint.com to check the formatting of the file.

#### Existing pregnancy

If there's already a pregnancy in the file, simple follow below:

Put a comma after the second to last bracket `}` in the file and paste the example above like so:

Before edits:
```json
{
    "54": {
        "second_parent": null,
        "moons": 1,
        "amount": 6
    }
}
```

After editing
```json
{
    "54": {
        "second_parent": null,
        "moons": 1,
        "amount": 6
    },
    "100": {
        "second_parent": "120",
        "moons": 1,
        "amount": 1
    }
}
```

Use a json validator like jsonlint.com to check the formatting of the file, then run the game and make sure you're edits are working as intended!

## Deleting pregnancy

### Conditions file

You'll simply delete the pregnant injury condition from the file.

If "pregnant" is the only condition in the file, you can safely delete the file entirely and proceed to the next step. If not, follow one of the situational examples below.

If there's more than one injury:

Before editing:
```json
{
    "injuries": {
        "claw-wound": {
            "severity": "major",
            "mortality": 50,
            "duration": 3,
            "moon_start": 1,
            "illness_infectiousness": [],
            "risks": [
                {
                    "name": "an infected wound",
                    "chance": 5
                }
            ],
            "complication": null,
            "cause_permanent": [],
            "event_triggered": false,
            "potential_scars": []
        },
        "pregnant": {
            "severity": "major",
            "mortality": 40,
            "duration": 2,
            "moon_start": 1,
            "illness_infectiousness": [],
            "risks": [],
            "complication": null,
            "cause_permanent": [],
            "event_triggered": false,
            "potential_scars": []
        }
    }  
}
```

After removing pregnancy from the injuries condition type:
```json
{
    "injuries": {
        "claw-wound": {
            "severity": "major",
            "mortality": 50,
            "duration": 3,
            "moon_start": 1,
            "illness_infectiousness": [],
            "risks": [
                {
                    "name": "an infected wound",
                    "chance": 5
                }
            ],
            "complication": null,
            "cause_permanent": [],
            "event_triggered": false,
            "potential_scars": []
        }
    }
}
```

---

If "pregnant" is the only condition under injuries and there's another condition type present:

Before editing:
```json
{
    "injuries": {
        "pregnant": {
            "severity": "major",
            "mortality": 40,
            "duration": 2,
            "moon_start": 1,
            "illness_infectiousness": [],
            "risks": [],
            "complication": null,
            "cause_permanent": [],
            "event_triggered": false,
            "potential_scars": []
        }
    },
    "illnesses": {
        "fleas": {
            "severity": "minor",
            "mortality": 0,
            "infectiousness": 15,
            "duration": 4,
            "moon_start": 4,
            "risks": [
                {
                    "name": "torn pelt",
                    "chance": 20
                }
            ],
            "event_triggered": false
        }
    }
}
```

After removing "pregnant" and "injuries":
```json
{
    "illnesses": {
        "fleas": {
            "severity": "minor",
            "mortality": 0,
            "infectiousness": 15,
            "duration": 4,
            "moon_start": 4,
            "risks": [
                {
                    "name": "torn pelt",
                    "chance": 20
                }
            ],
            "event_triggered": false
        }
    }
}
```

Once the pregnant condition is removed, put your edited json file into a json validator, such as jsonlint.com, to check your formatting. If it's not valid, validate the file with the help of the website.

### pregnancy.json

!!! warning
     When this file is not in use, it will simply hold `{}`. Do not delete these brackets or the file itself - it is required for start up!

You'll simply remove the pregnancy information for the ID of the cat you removed the pregnant condition from. 

If it's the only pregnancy in the file:

Before Editing:
```json
{
    "54": {
        "second_parent": null,
        "moons": 1,
        "amount": 6
    }
}
```

After:
```json
{}
```

---

If there's more than one pregnancy in the file:

Before editing:
```json
{
    "54": {
        "second_parent": null,
        "moons": 1,
        "amount": 6
    },
    "100": {
        "second_parent": "120",
        "moons": 1,
        "amount": 1
    }
}
```

After:
```json
{
    "54": {
        "second_parent": null,
        "moons": 1,
        "amount": 6
    }
}
```

Use a json validator such as jsonlint.com to confirm the json file is valid before proceeding. If it is, run the game and check your changes!