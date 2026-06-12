## clan_cats.json

The clan_cats is the data of every cat in the save file, including outsiders and dead cats.

**Formatting Cheat Sheet:**

* `[]` = lists. They signify that there can be more than one imported option
* `{}` = dicts. They hold complicated lists, and provide the ability to have more than one list in the dict
* `null` = no current option. Only one option in "quotes" can replace null
* `0` = A number. Only numeric options can be put here
* `false`/`true` = Determines whether the line's function is turned off (false) or on (true)

### Simplified Summary

By line, this part of the guide explains the clan_cats in as little detail as possible for those who need the refresher! I heavily recommend newer save file editors to read through the entire EXPANDED EXPLANATION section.

Some parts of this section might need you to read expanded explanation because I can't fit it in tables.

|  `Code`  |  Explanation  |  Additional Information  |
| :---- | :---- | :---- |
|  `"ID": "10"`,  |  Unique ID of a cat  |  Has to be a number  |
|  `"name_prefix": "Honey",`  |  First part of a cat's name  |  Cannot be empty  |
|  `"name_suffix": "stumble",`  |  Second part of a cat's name  |  Change to "name_suffix": "", if you don't want a suffix  |
|  `"specsuffix_hidden": false,`  |  Used to get rid of hardcoded role suffixes ("Star", "Kit", or "Paw")  |  Once set to true, uses "name_suffix"  |
|  `"gender": "female",`  |  Birth gender  |  "female" or "male"  |
|  `"gender_align": "female",`  |  Gender alignment. Can be a custom alignment (like "demiboy")  |  default options: "female", "male", "trans female", "trans male", "nonbinary"  |
|  `"pronouns": {"en":[]}, ` |  Pronouns the cat will use in text  |  Recommend changing while in game  |
| ` "birth_cooldown": 0,  `|  Pregnancy cooldown  |  Highest is 6 unless the game_config is edited  |
|  `"status": {[]},`  |  The standing a group status of a cat |  Please refer to expanded explanation for full details  |
|  `"dark_forest_affinity": 0`  |  The cat's affinity towards the dark forest. -# = less likely, +# = more likely |  Influences whether the cat goes to the DF when they die  |
|  `"starclan_affinity": 0`  |  The cat's affinity towards starclan. -# = less likely, +# = more likely |  Influences whether the cat goes to starclan when they die |
| ` "backstory": "clanborn",`  |  Cat's backstory  |  Options: [Backstories documentation](https://ClanGen.io/docs/dev/writing/reference/tag-lists/#backstories)  |
|  `"moons": 20, ` |  Age of the cat in moons  |  Age Ranges: [age & status](https://ClanGen.io/docs/dev/writing/reference/tag-lists/#age-and-status)  |
| ` "trait": "sneaky", ` |  Cat's trait  |  Options: [trait & skills](https://ClanGen.io/docs/dev/writing/reference/tag-lists/#traits-and-skills)  |
| ` "facets": "0,5,10,14", ` |  Facets determine what trait the cat has. null the line to regenerate `"facets": null,`  |  Ranges: [trait_ranges.json](https://github.com/ClanGenOfficial/ClanGen/blob/development/resources/dicts/traits/trait_ranges.json)  |
| ` "parent1": "329",`  |  First parent  |  If you want no biological parents, edit to be `null,`  |
| ` "parent2": null, ` |  Second parent. Referred to as parent.mate in code  |  Cannot have a parent in parent2 with no parent in parent1  |
| ` "adoptive_parents": [], ` |  Cats who adopted this cat  |  Would look like `"adoptive_parents": ["1","2"],`  |
| ` "mentor": null,`  |  Current mentor of the cat  |  Ex: `"mentor": "10",`  |
| ` "former_mentor": [] ` |  Former mentor(s) of the cat  |  Ex: `"former_mentor": ["10"],`  |
|  `"patrol_with_mentor: 0, ` |  Tracks how many times an apprentice patrolled with their mentor(s)  |  Used for mentor influence calculation  |
| ` "mate": [],`  |  Mate(s) of the cat  |  Ex: `"mate": ["70","80","34"],`   |
| ` "previous_mates": [], ` |  Previous mate(s) of the cat  |  Ex: `"previous_mates": ["70","80","34"],`   |
| ` "paralyzed": false, ` |  Tracks if this cat is paralyzed. Used to change sprite  |  Change to `true,` to make them paralyzed  |
|  `"no_kits": false, ` |  Personal toggle: Cannot have kits  |  Change to `true,` if applicable  |
| ` "no_retire": false,`  |  Personal toggle: Cannot retire  |  Change to `true,` if applicable  |
| ` "no_mates": false,`  |  Personal toggle: Cannot gain mates or romantic events  |  Change to `true,` if applicable  |

**Appearance**  
 Use [\[Dev Ver.\] Visual Sprite Guide](https://docs.google.com/spreadsheets/d/18T-VPGo4GJP35ECYnkzqKZThd6t8j7TwN97QspXtXY0/edit?gid=1808652489#gid=1808652489) for available options (unofficial resource)

[ Pixel Cat Creator ](https://cgen-tools.github.io/pixel-cat-maker/) is a great, unofficial resource to "preview" and build a sprite, similar to a customizer tool. May not have development options.

|  `Code ` |  Explanation  |  Additional Information  |
| :---- | :---- | :---- |
| ` "pelt_name": "Rosette",`  |  Pelt type, like "Classic", "SingleColour", etc  |  Always "Capitalized" (exceptions: TwoColour, SingleColour)  |
| ` "pelt_color": "DARKBROWN",`  |  Pelt Color, like "GOLDEN-BROWN", "SILVER", etc  |  Always "UPPERCASE"  |
| ` "pelt_length": "medium",`  |  Fur length. "short", "medium", "long"  |  Always "lowercase"  |
| ` "sprite_newborn": "newborn0",  `|  Sprite used for newborn age  |  "newborn{0-2}"  |
| ` "sprite_kitten": "kitten1",  `|  Sprite used for kitten age  |  "kitten{0-2}"  |
| ` "sprite_adolescent": "adolescent0", ` |  Sprite used for adolescent ages  |  "adolescent_short{0-2}" or "adolescent_long{0-2}"  |
| ` "sprite_adult": "adult_long2",`  |  Sprite used for adult ages  |  "adult_short{0-2}" or "adult_long{0-2}"  |
| ` "sprite_senior": "senior1", ` |  Sprite used for senior ages  |  "senior{0-2}"  |
| ` "sprite_para_adult": "para_adult_long0",` |  Adult sprite used for paralyzed cats  |  "para_adult_long0" or "para_adult_short0" |
| ` "eye_colour": "ORANGE",`  |  Eye color  |  Always "UPPERCASE"  |
| ` "eye_colour2": null,`  |  Second eye color used for heterochromia. When null, "eye_colour" is for both eyes  |  Always "UPPERCASE"  |
|  `"reverse": false, ` |  Flips the direction of the sprite.  |  Change to `true,` if applicable  |
|  `  "white_patches": "TIP", ` |  Cat's white patch. Change to `null,` if they don't have one  |  Always "UPPERCASE"  |
| ` "vitiligo": null, ` |  Vitiligo marking. Ex: `"vitiligo": "MOON",`  |  Always "UPPERCASE"  |
| ` "points": null,`  |  Colourpoint marking. Ex: `"points": "SEALPOINT",`  |  Always "UPPERCASE"  |
| ` "white_patches_tint": "gray", ` |  The tint applied to "white_patches". Change to `null,` if there's not one  |  Always "lowercase"  |
| ` "tortie_marking": null, ` |  Tortie marking choice. Ex: `"pattern": "ONE",`  |  Always "UPPERCASE"  |
| `"tortie_base": null, ` |  Tortie base pelt. Ex: `"tortie_base": "single",`  |  Always "lowercase". "TwoColor" and "SingleColour" are "single" for torties.  |
| ` "tortie_color": null,`  |  "pattern" pelt color. Ex: `"tortie_color": "GHOST",`  |  Always "UPPERCASE"  |
| ` "tortie_pattern": null, ` |  Tortie marking pelt type. Ex: `"tortie_pattern": "single",`  |  Always "lowercase". "TwoColor" and "SingleColour" are "single" for torties.  |
| ` "skin": "PEACH", ` |  Cat's skin. **Cannot** be null  |  Always "UPPERCASE"  |
| ` "tint": "gray",`  |  Tint applied to the whole cat. Change to `null,` if unneeded  |  Always "lowercase"  |

**MISC**

|  `Code`  |  Explanation  |  Additional Information  |
| :---- | :---- | :---- |
|  `"skill_dict": {}, ` |  Skills the cat has  |  "SKILL,Tier#,False/True". Refer to Expanded Explanation. Options: [trait & skills](https://ClanGen.io/docs/dev/writing/reference/tag-lists/#traits-and-skills)  |
| ` "scars": [],`  |  Cat's scars. Can have multiple: `"scars": ["ONE","TWO","THREE"],`  |  Always "UPPERCASE"  |
| ` "accessory": [],`  |  Accessory code. leave as `"accessory": [],` if there is none  |  Can have 2-3 accessories in game. `"accessory": ["JAY FEATHER","DESERT WILLOW"],`  |
| ` "experience": 321,`  |  Cat's experience. Determines how good they are in their role.  |  Highest is 321 - refer to Expanded Explanation for ranges  |
|  `"current_apprentice": [],`  |  Current apprentices of the cat  |  `"current_apprentice": ["1","2","3"],`  |
| ` "former_apprentices": [],`  |  Former apprentices of the cat |  `"former_apprentice": ["1","2","3"],`  |
|  `  "faded_offspring": [],`  |  Stores a list of faded offspring for family tree purposes  |  `"faded_offspring": ["1","11","111"],`  |
| ` "opacity": 100,`  |  Faded opacity of dead cats  |  Keep 100 when alive  |
| ` "prevent_fading": false,`  |  Personal toggle: Prevents fading for the cat  |  Change to `true,` if applicable  |
|  `"favourite": false,`  |  Favorites the cat. Yellow circle behind cat  |  Change to `true,` if applicable  |

### Expanded Explanation

For those who might need ALL the details for every line. It can be a long read, but to avoid player error, read carefully!

[       ← This should ALWAYS be at the start and end of the entire `JSON`

{       ← this should ALWAYS be at the start and end of a single cats code

`"ID": "3",`

The ID of a cat! All of these are unique numbers and **can't be shared between two cats in the clan.**

* Saves do not affect each other whatsoever. Therefore, you can have duplicate IDs shared between saves, but they CAN'T be duplicates in the SAME save.

`"name_prefix": "Silver",`

`"name_suffix": "stream",`

If you'd like to not have a suffix, the code would look like - `"name_suffix": ""`, instead

`"specsuffix_hidden": false,`

This is only used when kit, paw, or star is currently being used! It gets rid of the hard coded suffix and instead uses the "name_suffix" if changed to `true`

`"gender": "male",`

This is the birth sex of the cat! "male" or "female". Cannot be custom.

`"gender_align": "male",`

This is the gender a cat was not born with but aligns themselves as! This can be a custom alignment.

* All default ones: "male", "female", "trans male", "trans female", "non-binary"

!!! info
	 Custom gender alignments get they/them pronouns by default until the player manually changes them.
	 If "gender" and "gender_align" do not match, the cat is unable to transition gender naturally.

---
`"pronouns": {},`

These are the pronouns that are used for the cat in text. Such as she/her, he/him, they/them. The game does not interchangeably use both if a cat has more than one listed pronoun.

`"en": []` is the language that the pronouns are coded for.
    
- "subject": she, they, him. Example: "they went on a walk at the border".
- "object": her, them, his. Example: "m_c is worried about them."
- "poss": her, their, his. Example: "r_c is angry that m_c stole a piece of their fresh kill"
- "inposs": hers, theirs, his. Example: "r_c grunts that it was theirs in the first place."
- "self": herself, themself/themselves, himself. Example: "r_c gives themself a rough time about a mistake."
- "conju": This is for verbs. If a pronoun is directly responsible for changing the grammar in a sentence (They give vs She gives), then the value will be 2. Otherwise, the value will be 1
- "gender": Determines which pronoun set a cat gets based on their "gender" value.

!!! info
	 pronouns are recommended to be changed via the game > cat profile > personal tab > specify gender tab > edit pronouns

---

`"birth_cooldown": 0,`

This is a cooldown until a cat is able to become pregnant again. The highest number is 6 (this can be changed in the game_config). Counts down. 

* Example: "birth_cooldown": 1, = they have 1 moon left until they can get pregnant again

---

`"status": {},`

Everything that affects status is here. It also lists previous statuses, the clan they're currently in, and their afterlife information. ("dead", "exiled", "df", "outside", "dead_moons", "driven_out" are no longer separate values)

**"group_history": [ ]**: The information recording the cats ranks, past/current groups, etc
		
`"group": ""`: The "group" the cat belongs to/is affiliated with. 

* "group" will be a number. Look in your `clan.json` to see the number associated with a group. "1"=playerclan & "2"=starclan for example
* If they don't belong to a group (ex: kittypet), it'll be `null,`

`"rank": ""`: The "rank" of the cat. Essentially, this is what "status" used to be. 

* Available Ranks: [status documentation](https://ClanGen.io/docs/dev/writing/reference/tag-lists/#__tabbed_2_2)
* "rank" cannot be null

`"moons_as": 0`: The amount of moons the cat was/is the specific rank. It'll stay 0 if it's a previous status that has no recorded history 

* For example, your first leader and deputy would be a "warrior" for an unspecified amount of time aka 0.
* Used to calculate how many moons a cat has been in the afterlife if "group" is an afterlife
	
**"standing_history": [ ]**: The information regarding the cats standing with the clan(s).

`"group": "1"`: The "group" the cat has a standing with. If the cat isn't from a neighboring clan, this will likely only be player_clan ("1") and an afterlife group ("2"-"4") if they're dead

* "group" will be a number. Look in your `clan.json` to see the number associated with a group. "1"=playerclan & "2"=starclan for example
* "group" cannot be null

`"standing": []`: The current standing with the group. (can have multiple)

* "member" if the cat is currently affiliated with the group
* "known" if the cat is known to the group
* "exiled" if the cat was exiled from the group (only works for current groups)
* "lost" if the cat is currently lost (only works for current groups)
* "unknown" if the cat is unknown to the group
* "left" if the cat left the clan

`"near": true/false`: Tracks how close (in location) the cat is to the listed group. If they're false, they won't show on the cat list. This is the same function as the previous "driven_out".

---

`"dark_forest_affinity": 0,`

`"starclan_affinity": 0,`

Lago, PR 4005: "By default, a cat goes to where the guide is, but negative affinity with that afterlife may cause a cat to go to the opposite one instead. affinity is not currently modified anywhere in-game (not implemented as a feature)"

Affinity can either be a negative or positive number. Negative means the cat would be *less likely* to go into the afterlife, positive is *more likely* to go into the afterlife.

`"backstory": "abandoned4",`

Refer to [backstories documentation](https://ClanGen.io/docs/dev/writing/reference/tag-lists/#backstories) for all the available backstories!

* Cats outside the clan and dead outsiders have hardcoded backstories displayed no matter what is put here

`"moons": 23,`

This is the age of the cat. The age ranges are listing in the [game_config.toml](https://github.com/ClanGenOfficial/ClanGen/blob/development/resources/game_config.toml)

`"trait": "strange",`

This is the cat's personality trait. Refer to [trait documentation](https://ClanGen.io/docs/dev/writing/reference/tag-lists/#__tabbed_3_2) for all the available ones.

* While changing the trait, you need to also null the "facets" line underneath ("facets": null,) to regenerate new facets based on the trait you edited in.

---

`"facets": "6,12,0,15",`

These are the facets. Facets directly determine what trait the cat has depending on the numbers in the "facets" line. If you do not want to be specific, null the line `"facets": null,` to regenerate new ones.


**Using Facets**

Facets determine what trait the cat has. They affect how the cat interacts with their peers and goes toward the overall clan temperament. 

Facets operate on a range of 0-16 for each section. Facet ranges are stored in the [trait_ranges.json](https://github.com/ClanGenOfficial/ClanGen/blob/development/resources/dicts/traits/trait_ranges.json). This json tells you specifically which ranges are for each trait.

**SIMPLE STEPS**

1. Navigate to trait_ranges.json 
2. Search the file for the trait you're looking for. You're going to see four sections: "lawfulness", "sociability", "aggression", and "stability"
3. These sections have a range of numbers. For example, lawfulness for troublesome is [0, 8]. 0 is the minimum lawfulness, 8 is the max lawfulness for that trait.
4. Brainstorm which numbers you want for each section and put them in the "facets" line. 
5. Make sure you specify the trait in the "trait" line, otherwise it will randomize if the trait ranges are shared between traits.

For troublesome, it might look like below:
```json
"traits": "troublesome",
"facets": "1,4,8,5"
```


**Facet Influence**

Lawfulness:

* Low (less than 6) lawfulness makes a cat more likely to murder

Sociability:

* Leader and deputies (the mean) sociability facets increase the clan sociability
* All cats (the median) sociability facets increase the clan sociability

Aggression:

* High (more than 10) aggression makes a cat more likely to murder
* Leader and deputies (the mean) aggression facets increase the clan's aggression
* All cats (the median) aggression facets increase the clan's aggression

Stability:

* Low (less than 6) stability makes a cat more likely to murder
* (Less than 5) Is more likely to grieve cats 

All four sections influence the compatibility between cats. The closer the facets are between two cats, the more compatible they will become.

---


`"parent1": "30",`

`"parent2": "31",`

These are the birth parents! If you do not want them to have parents, or they don't have two biological ones, it'll look like this `"parent2": null,`

* If there's an ID listed in parent2 but nothing in parent1, the parent will not be recognized.
* Yes, siblings have to share a common parent

`"adoptive_parents": ["17"],`

If the cat so happens to not have an adoptive parent: `"adoptive_parents": [],`. If they have more than one: `adoptive_parents": ["17","20"],`

`"mentor": null,`

This is where the ID of the current mentor will go. If there is a mentor it'll look like `"mentor": "12",`

!!! tip
	 When adding or removing a mentor, also make sure to edit the mentor's "current_apprentice" line

`"former_mentor": ["22","23"],`

The mentor(s) a cat had in the past. If there isn't a former mentor for the cat: `"former_mentor": [],`

`"patrol_with_mentor": 0,`

Tracks the number of times an apprentice has patrolled with their mentor. Is used for calculating influence. The higher the number, the more the mentor influences the apprentice in either trait or skill

`"mate": ["90"],`

The current mate(s) of the cat. If there aren't mates for the cat: `"mate": [],`

!!! tip
	 When adding or removing a mate, also make sure to edit the mate's "mate" line

`"previous_mates": ["73"],`

Former mate(s). If there isn't a previous mate for the cat: `"previous_mates": [],`

`"paralyzed": false,`

Lets the game know that the cat is paralyzed and needs to use the exclusive paralyzed sprite.

`"no_kits": false,`

Personal toggle: prevents the cat from having kits.

`"no_retire": false,`

Personal toggle: prevents the cat from retiring.

`"no_mates": false,`

Personal toggle: prevents the cat from having mates or romantic events.

---

**Appearance**

Refer to [[dev ver.] Visual Sprite Guide](https://docs.google.com/spreadsheets/d/18T-VPGo4GJP35ECYnkzqKZThd6t8j7TwN97QspXtXY0/edit?gid=1808652489#gid=1808652489) for this section (unofficial resource).

* Pixel Cat Creator is a great, unofficial resource to "preview" a cats appearance.

`"pelt_name": "TwoColour",`

This is where the pelt name goes. Some examples: "Speckled", "Smoke", "SingleColour", "Singlestripe". This will always "Capitalized".

* If you wish to make a cat a tortie or calico, the code names are "Tortie" and "Calico", and you'll have to edit the tortie exclusive code down the file.

`"pelt_color": "GHOST",`

The pelt color of the cat. Examples: "GOLDEN-BROWN", "LIGHTGREY", "PALEGINGER". This is always be "UPPERCASE"

`"pelt_length": "long",`

This is the length of the pelt. "long", "medium", and "short" apply here. Long-hairs have different apprentice & adult poses, so make sure to double check the number.

`"sprite_newborn": "newborn0",`

`"sprite_kitten": "kitten1",`

`"sprite_adolescent": "adolescent2",`

`"sprite_adult": "adult_short2",`

`"sprite_senior": "senior2",`

`"sprite_para_adult": "para_adult_short0",`

These are the new names for your poses. You'll add in a choice instead of a number. The file [pose_sprite_data](https://github.com/ClanGenOfficial/ClanGen/blob/development/sprites/dicts/pose_sprite_data.json) in your sprites folder > dict folder lists the poses and their corresponding name. 

!!! tip
     The poses are stricter now for save conversion purposes, so you can't use poses outside of their intended grouping.

`"eye_colour": "GREEN",`

This is where the eye color goes. This will always be "UPPERCASE" and this section of the code cannot be `null`

`"eye_colour2": null,`

If you wish for your cat to have Heterochromia, replace null with a color: `"eye_colour2": "YELLOW",`

`"reverse": true,`

This refers to the cat's pose. It simply changes the original direction they're facing. 

`"white_patches": "DIVA",`

If you do not wish for a white patch for this cat: `"white_patches": null,`. This will always be "UPPERCASE".

`"vitiligo": null,`

If you wish for a cat to have a vitiligo marking, change the null to the name: `"vitiligo": "MOON",`. This will always be "UPPERCASE".

`"points": null,`

If you wish for a cat to have a colorpoint marking, change the null to the name: `"points": "SEALPOINT",`. This will always be "UPPERCASE" 

`"white_patches_tint": "offwhite",`

This is the tint of your white patch marking. `null` is used if there's not a tint applied to the patch.

`"tortie_marking": null,`

This is where you put the name of the Tortie marking you're using: `"tortie_marking": "ONE",`. This will always be "UPPERCASE".

`"tortie_base": null,`

This is the main base pelt name, aka this is what would usually go in "pelt_name" when a cat is not a tortie. For example, `"tortie_base": "single",` ("single" instead of "singlecolour" or "twocolour"). This will always be "lowercase"

`"tortie_color": null,`

This is the color applied to "tortie_marking": `"tortie_color": "GHOST",`. This will always be "UPPERCASE"

`"tortie_pattern": null,`

This is the pelt option for your marking, aka "tortie_marking" above. For example, `"tortie_pattern": "single",` ("single" instead of "singlecolour" or "twocolour"). This will always be "lowercase"

`"skin": "LIGHTBROWN",`

This is the skin color for the nose, paws, and ears if applicable. This cannot be null. This will always be "UPPERCASE"

`"tint": "blue",`

The tint that is applied to the full cat. If there isn't one, `null` is used.

---
```json
"skill_dict": {
    "primary": "RUNNER,27,False",
    "secondary": "SENSE,21,False",
    "hidden": null
},
```
!!! info
	 "hidden" is set to be removed from the game due to not having any function behind it.

This is the skill code. The format is as follows: "[SKILL],[skill tier],[True/False]"

* `True` signifies the skill being an interest, and can be changed. This is for kittens and apprentices. Change the skill to be "SKILL,0,True" if they're either group
* The "tier" signifies how good the cat is in their skill, and with each tier, the text changes to reflect that. "Tier" progresses as the cat ages, though the largest change is through graduation.


**Skill Tier ranges:**
```
Interest (kittens & apps): 0
Tier 1: 1 - 9
Tier 2: 10 - 19
Tier 3: 20 - 29
```
---
`"scars": ["ONE"],`

The scars the cat has. If they don't have any scars: `"scars": [],`. This is always "UPPERCASE"

`"accessory": [],`

A cat can have up to three accessories in development. Ex: `"accessory": ["JAY FEATHER", "DESERT WILLOW"],`. Always written as "UPPERCASE"

`"experience": 63,`

The experience of a cat. Determines how good they are at their job, and their successes in their activities would be partially determined by experience.

**Experience ranges:**
```
0 - untrained
1-50 - trainee
51-110 - prepared
111-170 - competent
171-240 - proficient
241-320 - expert
321 - master
```
`"current_apprentice": ["69"],`

This is if the cat has a current apprentice. Otherwise: `"current_apprentice": [],`. 

!!! tip
	 When removing a current apprentice, also go to the apprentice code to null their mentor line.

`"former_apprentices": ["72","1"],`

This is if the cat has a former apprentice. Otherwise: `"former_apprentice": [],`

!!! tip
	 When removing a former apprentice, also go to the apprentice code to get rid of the mentors mention in "former_mentor" line.

`"faded_offspring": [],`

Stores of a list of faded offspring for relation tracking purposes. Not recommended to be changed via save file editing. `"faded_offspring": ["10","111"],`

`"opacity": 100,`

I believe this is the fading opacity, aka how far they are in fading. The lower the number, the more faded this dead cat will be.

`"prevent_fading": false,`

Personal toggle: Disallows the particular cat to fade.

`"favourite": false,`

This refers to the favoriting feature in the game. Change to `"favourite": true` if you want the cat to be starred

},  ← Reminder that this closes off the cat's code! If this is the LAST cat in the json, there will not be a comma!

] ← Reminder that this will always be at the start and end of the ENTIRE json!

# Template

Holds a template of a cat's code for copy/pasting/editing purposes. All the values are either nulled, have empty quotes, or are zero-ed.

```json
    {
        "ID": "",
        "name_prefix": "",
        "name_suffix": "",
        "specsuffix_hidden": false,
        "gender": "",
        "gender_align": "",
        "pronouns": {},
        "birth_cooldown": 0,
        "status": {
            "group_history": [
                {
                    "group": "",
                    "rank": "",
                    "moons_as": 0
                }
            ],
            "standing_history": [
                {
                    "group": "",
                    "standing": [],
                    "near": true
                }
            ]
        },
        "dark_forest_affinity": 0,
        "starclan_affinity": 0,
        "backstory": "",
        "moons": 0,
        "trait": "",
        "facets": null,
        "parent1": null,
        "parent2": null,
        "adoptive_parents": [],
        "mentor": null,
        "former_mentor": [],
        "patrol_with_mentor": 0,
        "mate": [],
        "previous_mates": [],
        "paralyzed": false,
        "no_kits": false,
        "no_retire": false,
        "no_mates": false,
        "pelt_name": "",
        "pelt_color": "",
        "pelt_length": "",
        "sprite_newborn": "",
        "sprite_kitten": "",
        "sprite_adolescent": "",
        "sprite_adult": "",
        "sprite_senior": "",
        "sprite_para_adult": "",
        "eye_colour": "",
        "eye_colour2": null,
        "reverse": false,
        "white_patches": null,
        "vitiligo": null,
        "points": null,
        "white_patches_tint": null,
        "tortie_marking": null,
        "tortie_base": null,
        "tortie_color": null,
        "tortie_pattern": null,
        "skin": "",
        "tint": null,
        "skill_dict": {
            "primary": null,
            "secondary": null,
            "hidden": null
        },
        "scars": [],
        "accessory": [],
        "experience": 0,
        "current_apprentice": [],
        "former_apprentices": [],
        "faded_offspring": [],
        "opacity": 100,
        "prevent_fading": false,
        "favourite": false
    }
```

## Adding a Cat

Adding a cat to a save file is as simple as duplicating another cat's code, changing the listed ID of the duplicate, and adding the ID to `clan.json`'s `"clan_cats"` list. But what does that look like?

### editing clan_cats

Open your ``clan_cats.json`` with a text editor. You'll (hopefully) notice that every cat's information is within a dict (`{}`). When copying a cat's code, you'll copy from the first surrounding bracket `{` to the last surrounding bracket `}`, like how the template is above.

Then, go to the bottom of the file, and place a *comma* after the closing dict bracket `}` of the last cat in the file. Press enter to make an empty line, then paste your copied code.

Once your code is pasted, change `"ID"` to be a *unique number* not currently being used by another cat. This is what makes the added cat "individual".

Save the file, then go to a json validator website (such as jsonlint.com) to add in your edited ``clan_cats.json`` to confirm the file is valid with your edits.

### editing `clan.json`

If so, navigate back to your save files, and open `[clanname]`clan.json`` within your save folder. Scroll down until you find `"clan_cats"`. Add the *unique number* of the added cat to the list.

* Do not add spaces. `"clan_cats": "1,2,3,4,5",`

Once it is confirmed that the game runs, you can go back to ``clan_cats.json`` and edit any information of the new cat to make them unique. Use [`clan_cats.json`](#clan_catsjson) to make sure you're editing the file appropriately.

## Deleting a Cat

!!! warning
	 When deleting a cat, make sure you're deleting their ID from every file in the save to avoid future bugs/strange behavior. Also delete any exclusive files (ID_conditions, ID_history), as they will not delete themself.

!!! danger
     You CANNOT delete the cat listed as the instructor (your Starclan guide). They are required for the save to function.

Deleting a cat from a save file is a little complicated and leaves more room for error as you'll have to edit multiple files, depending on how involved the cat is in the save.

### editing clan_cats

Go into your save files, and open ``clan_cats.json``. Search for the cat you want to edit in the file. Make sure to write down their ID somewhere, so you don't forget.

There is a few main things you want to do in clan_cats: 

* *Delete the cat's information* from their beginning bracket `{` to their ending bracket `}`. Remove the ending comma `},` for the previous cat if the deleted cat was at the end of the file.
* ctrl + f (or the equivalent) and mass search their ID (ex: "10"), and *delete every mention of their ID manually*. Do not use an auto replace feature.
* If applicable, replace their ID with another cat. (ex: if they were a single parent to a litter, and you still want the litter to be littermates)

Once you're done removing the cat from ``clan_cats.json``, use a json validator such as jsonlint.com to check the formatting of the file, aka make sure it's still valid. If it is, head on to the next part.

### editing `clan.json`

Navigate to your `[clanname]`clan.json`` file. ctrl + f (or the equivalent) and mass search the deleted cats ID in `clan.json`. Delete any mentions manually.

Use the explanation of `clan.json` to make sure you're removing the ID appropriately.

### additional files

You will also have to delete their ID from every other file in the clan save. Most notably: 

- (expanded) nutrition_info.json
	- Causes a freshkill timeskip crash when there's a "nonexistent" ID listed
- pregnancy.json
	- To avoid a cat generating as pregnant
- (complete delete) ID_conditions, ID_history, and ID_relations if applicable
	- Avoids a cat generating with preexisting information
- Delete ID from other cats ID_relations
	- Avoids a cat generating with preexisting relationships, stuff like mate events that shouldn't happen

# Status "How-To's"

This is a section specifically for how to edit the "status" part of the clan_cats file to fit your particular needs with visual formatting examples.

## Other Clan Cats

To make an other clan cat, go to your ``clan_cats.json``. This is all we're going to change.

Make your new cat/navigate to your desired cat and scroll down to their status code.
```json
        "status": {
            "group_history": [
                {
                    "group": "1",
                    "rank": "warrior",
                    "moons_as": 0
                },
                {
                    "group": "1",
                    "rank": "leader",
                    "moons_as": 1
                }
            ],
            "standing_history": [
                {
                    "group": "1",
                    "standing": [
                        "member"
                    ],
                    "near": true
                }
            ]
        },
```

For this example, let's say I want to make this cat a previous leader from the "player_clan", and they're currently a warrior for Rockclan, which is group "5".

* You can figure out what group belongs to which other_clan through the `clan.json` `"used_group_IDs"` and `"other_clans"`

First, let's go with simple steps first. Removing them from the player clan requires changing "standing_history" to have "known". In this example, they're not a member due to belonging to another clan.

The change:
```json
            "standing_history": [
                {
                    "group": "1",
                    "standing": [
                        "known"
                    ],
                    "near": true
                }
            ]
```

Now, we'll make them a warrior for group "5". This requires changing both "group_history" and "standing_history". You'll basically copy what's already there, then edit to your desired outcome.

The change:
```json
        "status": {
            "group_history": [
                {
                    "group": "1",
                    "rank": "warrior",
                    "moons_as": 0
                },
                {
                    "group": "1",
                    "rank": "leader",
                    "moons_as": 0
                },
                {
                    "group": "5",
                    "rank": "warrior",
                    "moons_as": 5
                }
            ],
            "standing_history": [
                {
                    "group": "1",
                    "standing": [
                        "known"
                    ],
                    "near": true
                },
                {
                    "group": "5",
                    "standing": [
                        "member"
                    ],
                    "near": true
                }
            ]
        },
```

## Reviving a Cat

In the cat's status code, you're going to see "group": "["2"-"4"]" subsections in both group_history and standing_history. You want to delete each subsection. For example:

Before:
```json
        "status": {
            "group_history": [
                {
                    "group": "1",
                    "rank": "elder",
                    "moons_as": 0
                },
                {
                    "group": "1",
                    "rank": "medicine cat",
                    "moons_as": 5
                },
                {
                    "group": "2",
                    "rank": "medicine cat",
                    "moons_as": 1
                }
            ],
            "standing_history": [
                {
                    "group": "1",
                    "standing": [
                        "member",
                        "known"
                    ],
                    "near": true
                },
                {
                    "group": "2",
                    "standing": [
                        "member"
                    ],
                    "near": true
                }
            ]
        }
```

After:
```json
        "status": {
            "group_history": [
                {
                    "group": "1",
                    "rank": "elder",
                    "moons_as": 0
                },
                {
                    "group": "1",
                    "rank": "medicine cat",
                    "moons_as": 5
                }
            ],
            "standing_history": [
                {
                    "group": "1",
                    "standing": [
                        "member",
                        "known"
                    ],
                    "near": true
                }
            ]
        }
```

Once this has been deleted from the file, save your `clan_cats.json` and move to the cat's history file. History folder > ID_history.json matching the ID of the cat you just edited.

Inside the history file, scroll until you see the line "died_by": [], - delete all the dead event information within that section until it reads as "died_by": [],

For example, before:
```json
    "died_by": [
        {
            "involved": null,
            "text": "m_c died of a heart attack.",
            "moon": 5
        }
    ],
```

After:
```json
    "died_by": [],
```

## Killing a Cat

First, choose which afterlife the cat will go into after they die. "2" = starclan, "3" = dark forest, "4" = unknown residence. This will affect which current group you put them in.

In this example, I'll use "group": "2".

Before:
```json
        "status": {
            "group_history": [
                {
                    "group": null,
                    "rank": "kittypet",
                    "moons_as": 7
                },
                {
                    "group": "1",
                    "rank": "apprentice",
                    "moons_as": 0
                }
            ],
            "standing_history": [
                {
                    "group": "1",
                    "standing": [
                        "known",
                        "member"
                    ],
                    "near": true
                }
			]
        },
```

Add a new section to "group_history" and "standing_history" with the "group" being "2"/"3"/"4". After:
```json
        "status": {
            "group_history": [
                {
                    "group": null,
                    "rank": "kittypet",
                    "moons_as": 7
                },
                {
                    "group": "1",
                    "rank": "apprentice",
                    "moons_as": 0
                },
                {
                    "group": "2",
                    "rank": "apprentice",
                    "moons_as": 0
                }
            ],
            "standing_history": [
                {
                    "group": "1",
                    "standing": [
                        "known",
                        "member"
                    ],
                    "near": true
                },
          		{
                    "group": "2",
                    "standing": [
                        "member"
                    ],
                    "near": true
                }
            ]
        },
```

This will immediately make them part of the afterlife of your choice.

(expanded) To avoid bugs, remove the cat's ID from `nutrition_info.json` in your clan save folder. This makes sure the game doesn't try to "feed" them and crash you on moonskip.


Optionally, you can add a death message to the cat's history file "died_by". Like below: 

```json
    "died_by": [
        {
            "involved": null,
            "text": "m_c was killed by save file editing.",
            "moon": 10
        }
    ],
```

## Outsider Cats

To make an outsider cat, you'll just make their "group" for "group_history" null with an outsider rank, and "known" in "group_history"

An example of a kittypet outsider:
```json
        "status": {
            "group_history": [
                {
                    "group": null,
                    "rank": "kittypet",
                    "moons_as": 7
                }
            ],
            "standing_history": [
                {
                    "group": "1",
                    "standing": [
                        "known"
                    ],
                    "near": true
                }
            ]
        },
```

## Exile Cats

If you're trying to un-exile a cat, simply get rid of the `"exiled"` value in `"standing_history"` and `"group": null` section in `"group_history"`.

Before:
```json
        "status": {
            "group_history": [
                {
                    "group": null,
                    "rank": "kittypet",
                    "moons_as": 7
                },
                {
                    "group": "1",
                    "rank": "apprentice",
                    "moons_as": 0
                },
                {
                    "group": null,
                    "rank": "loner",
                    "moons_as": 0
                }
            ],
            "standing_history": [
                {
                    "group": "1",
                    "standing": [
                        "known",
                        "member",
                        "exiled"
                    ],
                    "near": true
                }
            ]
        },
```

Removing the `"group": null` section of group_history and `"exiled"` in standing history, you should be left with:

```json
        "status": {
            "group_history": [
                {
                    "group": null,
                    "rank": "kittypet",
                    "moons_as": 7
                },
                {
                    "group": "1",
                    "rank": "apprentice",
                    "moons_as": 0
                }
            ],
            "standing_history": [
                {
                    "group": "1",
                    "standing": [
                        "known",
                        "member"
                    ],
                    "near": true
                }
            ]
        },
```

If you're trying to manually exile a cat, you'll just do the opposite. Add a `"group": null,` section in `"group_history"` and the `"exiled"` value in your `"group": "1"` for `"standing_history"`.

## Lost Cats

If you're trying to get a lost cat back, simply get rid of the `"lost"` value in the `"standing_history"` of the cat, and the `"group": null` section in your group_history

Before:
```json
        "status": {
            "group_history": [
                {
                    "group": null,
                    "rank": "kittypet",
                    "moons_as": 7
                },
                {
                    "group": "1",
                    "rank": "apprentice",
                    "moons_as": 0
                },
                {
                    "group": null,
                    "rank": "loner",
                    "moons_as": 0
                }
            ],
            "standing_history": [
                {
                    "group": "1",
                    "standing": [
                        "known",
                        "member",
                        "lost"
                    ],
                    "near": true
                }
            ]
        },
```

After removing the `"group": null` section and `"lost"`:
```json
        "status": {
            "group_history": [
                {
                    "group": null,
                    "rank": "kittypet",
                    "moons_as": 7
                },
                {
                    "group": "1",
                    "rank": "apprentice",
                    "moons_as": 0
                }
            ],
            "standing_history": [
                {
                    "group": "1",
                    "standing": [
                        "known",
                        "member"
                    ],
                    "near": true
                }
            ]
        },
```

If you're trying to manually make a cat lost, you'll just do the opposite. Add a `"group": null,` section in `"group_history"` and the `"lost"` value in your `"group": "1"` for `"standing_history"`.

