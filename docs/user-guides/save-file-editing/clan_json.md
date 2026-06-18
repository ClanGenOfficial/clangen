## clan.json
(including a simplified summary by line for those who need a refresher)

The `clan.json` holds information about a clan save, such as other_clan information and camp biome.

**Formatting Cheat Sheet:**

* `[]` = lists. They signify that there can be more than one imported option
* `{}` = dicts. They hold complicated lists, and provide the ability to have more than one list in the dict
* `null` = no current option. Only one option in "quotes" can replace null
* `0` = A number. Only numeric options can be put here
* `false`/`true` = Determines whether the line's function is turned off (false) or on (true)

### Simplified Explanation

For those who need a refresher of the file, but don't need all the details. Users who are new to editing save files, I heavily recommend reading through the expanded explanation section!

|  `Code ` |  Explanation  |  Additional Information  |
| :---- | :---- | :---- |
|  `"clanname": "Fuzz",`  |  Prefix/name of the save.  |  The name of the save. If you change this, you'll have to also change the `clan.json` and clan save folders name.  |
|  `"displayname": "Fuzz",`  |  Prefix/name of the clan.  |  The name that is displayed in the game for the clan. Only has to be changed here  |
|  `"clanage": 2,`  |  The number of moonskips for this clan  | Changing the number does not revert the save or add changes |
|  `"biome": "Plains",`  |  The biome of this clan. "Plains", "Mountainous", "Beach", "Forest"  |  Affects camp background, text, prey, and herb chances  |
|  `"camp_bg": "camp1",`  |  Where you'll edit your desired camp background within the saves biome  |  Refer to expanded explanation for more detail.  |
|  `"clan_symbol": "symbolTREMBLE0",`  |  The symbol for the player clan  |  Refer to Changing Clan Symbols for instructions  |
|  `"gamemode": "expanded",`  |  "classic" or "expanded"  |  Cannot change a save from "expanded" to "classic" without additional editing.  |
|  `"used_group_IDs": {},`  |  The number IDs for every group of cats  |  if you're adding a new other clan, you'll have to add a new other_clan ID  |
|  `"last_focus_change": null,`  |  When a focus (warrior den activity) is changed, it'll list the moonskip of said change here  |  Ex: `"last_focus_change": 4,`  |
|  `"clans_in_focus": [],`  |  Lists selected outside clans involved in a focus (warrior den activity)  |  Ex: `"clans_in_focus": ["Moss"],`  |
|  `"instructor": "35",`  |  The ID of the StarClan Guide  |  Has to be a dead cat, doesn't have to be in StarClan (can be banished to DF)  |
|  `"reputation": 80,`  |  The relationship player clan has with outside cats  |  1-100, refer to expanded explanation for more detail.  |
|  `"mediated": [],`  |  Records which pairs of cats were mediated  |  EX: `"mediated": [["10,"22"]],`  |
|  `"starting_season": "Newleaf",`  |  The season the clan started on when generated.   |  "Newleaf", "Greenleaf", "Leaf-fall", "Leaf-bare"  |
|  `"temperament": ["stoic", "eager"],`  |  "Personality" of the player clan. In order ["aggression/sociability", "lawfulness/stability"]  |  Calculated based on facets, the player needs to manually change cats facets. Refer to Changing Clan Temperaments   |
|  `"custom_pronouns": {},`  |  The area where custom pronouns are stored for the save  |  Refer to expanded explanation  |
|  `"leader": "21",`  |  The ID of the clan's current leader.   |  Edit to `null,` for no leader  |
| ` "leader_lives": 9,`  |  The amount of lives the current leader has. 1-9 only  |  Deletes itself when "leader" is null, be careful to add it back when adding a leader through editing  |
|  `"leader_predecessors": 0,`  |  Amount of dead previous leaders before the current one was appointed  |  |
|  `"deputy": "13"`  |  The ID of the clan's current deputy  |  Edit to `null,` for no deputy  |
|`  "deputy_predecessors": 0,`  |  Amount of dead previous deputies before the current one was appointed  |  |
| ` "med_cat": "11"`  |  The ID of the senior medicine cat (usually the med cat you chose when creating the clan)  |  Edit to `null,` if there are no medicine cats or med apprentices in the clan  |
|  `"med_cat_number": 0,`  |  The amount of medicine cats & med apprentices in the clan   |  This line EXCLUDES the senior med cat listed for "med_cat" Ex: have 7 med cats, edit this line to be 6  |
|  `"med_cat_predecessors": 0`,  |  Amount of dead previous senior medicine cats  |  |
|  `"clan_cats": "1,2,3",`  |  List of all used IDs in the `clan_cats.json` file  |  This includes EVERY cat in the file, doesn't matter if they're clancat or outside  |
|  `"faded_cats": "", ` |  List of IDs for faded_cats, if necessary toggles are on  |  faded_cats do not have connected code, so they're separated |
| ` "patrolled_cats": [], ` |  Lists which IDs have patrolled on the current moonskip to avoid cats working more than once  |  |
|  `"other_clans": [{}],` | The other_clan information, like ID, name, and symbol | refer to expanded explanation |
|  `"war": {},`  |  Information regarding war  |  Refer to expanded explanation  |

### Expanded Explanation

{ << --- this is ALWAYS be at the start and end of this json!

`"clanname": "Fuzz",`

This is the save name. You can change the save name here, but make sure to rename the clan save folder and the `clan.json` to correspond with this change

`"display_name": "Fuzz",`

This is the clan name that is displayed in game. You only need to change this line.

`"clanage": 2,`

This is the clan age, aka your moonskip count for this save.

* Editing this number does not reverse changes to the save files. Once you saved a moonskip, only manually reversing info gets it back to whatever it was previously

`"biome": "Plains",`

This is for the biome you chose for the camp location. The options: "Plains", "Mountainous", "Forest", "Beach"

* Has to be "Capitalized"

`"camp_bg": "camp1",`

This indicates what camp you chose within the biome. To figure out what number is connected to what camp, head to resources / images / camp_bg / your selected biome and choose which camp background you want. The number will be in the png name

* So let's say for example, I want the tunnels camp for plains. The name is "greenleaf_camp2_dark", so I would replace the line with `"camp_bg": "camp2"`

`"clan_symbol": "symbolTREMBLE0",`

This is the symbol you chose while making your clan. "symbol{PREFIX}{#}" < in simple terms. Use [\[Dev Ver.\] Visual Sprite Guide](https://docs.google.com/spreadsheets/d/18T-VPGo4GJP35ECYnkzqKZThd6t8j7TwN97QspXtXY0/edit?gid=1808652489#gid=1808652489) for the available symbols.

`"gamemode": "expanded",`

This can be "classic" or "expanded". An expanded save cannot move over to classic (without further editing), but classic can become expanded
```
"used_group_IDs": {
    "1": "player_clan",
    "2": "starclan",
    "3": "unknown_residence",
    "4": "dark_forest",
    "5": "other_clan"
},
```

* These are the IDs for all the groups present in the save. When editing your clan_cats, the numbers to the left would be what you'd put in "status": {} for "group"
* The first 4 IDs (player clan and afterlives) will always stay the same across saves, unless edited by the player

`"last_focus_change": null,`

Warrior Den activity. This is listing the clan age moon of when the warriors' den focus was changed. If there was not a recorded change, it'll be null

* So, "last_focus_change": 10, If you changed to focus on "helping other clans" on clan moon ten (10). 

`"clans_in_focus": [],`

Warrior Den activity. This lists the other clans' names for focuses that revolve around other clans, like raiding. 

* `"clans_in_focus": ["Poppy"],` < Make sure it lists a clan that actually exists in "other_clans"

`"instructor": "35",`

This is the ID for the StarClan Guide! The guide has to be dead, but doesn't necessarily have to be in starclan

`"reputation": 80,`

This is the reputation your clan has with outside cats. Affects how likely outsiders interact with your clan (patrols, events, leader's den, etc), as well as *how* they interact

1-29: "Hostile" reputation. This range will very rarely make outside cats show up

30-70: "Neutral" reputation.

71-100: "Welcoming" reputation. 

Cannot be a negative number - only within the 1-100 range

`"mediated": [],`

The grouping list of cats IDs who have been mediated for that moon through the mediator activity. It'll be listed within [],

* this is to ensure cats can't be mediated more than once in a moon. `"mediated": [["10","14"],["90","1"]]`

`"starting_season": "Newleaf",`

This tells you which season the clan started out with. If you wish to change this, replace with either of these options: "Newleaf", "Greenleaf", "Leaf-fall", "Leaf-bare"

`"temperament": ["stoic", "eager"],`

This is the temperament of your clan. Widely based on the facets of the clan, mostly the sociability and aggression facet.

* If you wish to have another temperament, these are the options. It is NOT this easy though, so refer to Changing Clan Temperaments 

|  xx  |  low_aggression  |  mid_aggression  |  high_aggression  |
| ----- | :---- | :---- | :---- |
|  low_social   |  "cunning"  |  "proud"  |  "bloodthirsty"  |
|  mid_social  |  "amiable"  |  "stoic"  |  "wary"  |
|  high_social   |  "gracious"  |  "mellow"  |  "logical"  |

| xx | low_stability | mid_stability |high_stability |
| ----- | :---- | :---- | :---- |
| low_lawful  | "chaotic" | "mercurial" | "calculating" |
| mid_lawful | "eager" |"observant" | "adaptable" |
| high_lawful  | "decisive" | "methodical" | "steadfast" |

`"version_name": 3,`

`"version_commit": "ca341af0fecf2eb6cd353db456c2bf03089f9653",`

`"source_build": true,`

The lines remembering what version/commit its updated to, and if it is a source build. Will update on its own - do not edit.
```
"custom_pronouns": [
    {
        "name": "",
        "subject": "blue",
        "object": "blues",
        "poss": "blues",
        "inposs": "bluers",
        "self": "blueself",
        "conju": 2,
        "ID": "custom1"
    }
],
``` 

These are the custom pronouns you made for cats in the current save. They'll be listed here as a resource for the save to grab onto and apply to other cats if applicable.

* These do NOT move across saves (though you can copy and paste them to other `clan.json`s)
* If you wish to save pronouns permanently, this is the file path to add pronouns to: resources -> dicts -> pronouns.json

`"leader": "21",`

ID of the leader! If you wish to make another cat leader, simply change the "ID" and the cats statuses

* Edit to hold null if the clan does not have a leader. `"leader": null,`

`"leader_lives": 9,`

This is the current number of lives the leader listed above has. You can lower this number, but 9 is as far as it goes without weird behavior

* Sometimes, if you don't have a leader currently assigned, this line will disappear. If you're adding a new leader through save file editing, you'll have to re-add this line.

`"leader_predecessors": 0,`

This is the number of cats who were leaders before the previous listed one was appointed. 

* For example, maybe you have 5 generations of cats. Throughout that time, you had 4 leaders excluding the one you have now. "leader_predecessors": 4, would be the line. 

`"deputy": "23",`

This is the ID of the deputy. If you wish to make another cat deputy, simply change the "ID" and the cats statuses

* Edit to hold null if the clan does not have a deputy. `"deputy": null,`

`"deputy_predecessors": 0,`

This is the number of cats who were deputies before the previous listed one was appointed. Refer to the leader example for predecessors

`"med_cat": "27",`

This is the ID of the "elder" medicine cat, typically the cat you chose while starting the clan. Do not put more than one medicine cat's ID here.

* IF you don't have a medicine cat or medicine cat apprentice, edit to be null. `"med_cat": null,`

`"med_cat_number": 0,`

This is the number of medicine cats within the clan, excluding the ID within the med_cat line. 

* For example, if you have 5 medicine cats, drop the number to 4.

`"med_cat_predecessors": 0,`

This is the number of cats who were the "senior" medicine cats ("med_cat") before the previous listed ones were appointed. Refer to the leader example for predecessors

`"clan_cats": "23,21,27,35,36,19,20,22,24,25,26,28,29,30,31,32,33,34,37,38,39",`

This is the ID list for cats within the `clan_cats.json`. Do not add spaces between the numbers

* If you add or delete an ID from clan_cats, they also need to be added or deleted from here.

`"faded_cats": "",`

This is the ID list of cats who died and faded over time.

* Example: `"faded_cats": "1,2,3",`

`"patrolled_cats": [],`

Lists the cats who have been on a patrol for that moon. Their ID's would be listed within [], 
* This is to make sure one cat doesn't patrol more than once.

---
```
"other_clans": [
    {
        "group_ID": "5",
        "name": "Swift",
        "relations": 8,
        "temperament": ["stoic", "eager"],
        "chosen_symbol": "symbolSWIFT0"
    }
],
```
This holds all the other clans information necessary for them to function in the game. You need at least one other clan, and the maximum (before things start acting strange) is 5

* If you're adding or deleting other clans, you'll have to also add and/or delete their ID from the `"used_group_IDs"` list

**"group_ID"**: ID of the clan, used in clan_cats "status" groups

**"name"**: The Prefix of the other clan. -clan is hardcoded

**"relations"**: The relationship between the player clan and other clan. 0 to 20 -- lower number = worse relations

* Above or equal to 17 is an ally, above 7 and under 17 is neutral, and under 7 is hostile.

**"temperament"**: The same choices the player clan has! You do not need to change facets

* It's good to note that temperaments are *in order*. The first temperament listed is the aggression/sociability scale, the second one is the lawfulness/stability

**"chosen_symbol"**: The same choices the player clan has! Symbols generate to be the same as the clan's name. "symbol[PREFIX][#]". Use [\[Dev Ver.\] Visual Sprite Guide](https://docs.google.com/spreadsheets/d/18T-VPGo4GJP35ECYnkzqKZThd6t8j7TwN97QspXtXY0/edit?gid=1808652489#gid=1808652489) for the available symbols.

---
```
"war": {
    "at war": false,
    "enemy": null,
    "duration": 0
}
```
This is the WAR line. If you want to change it, so this clan is at war with your clan, change the following. 

* "At_war": true, "enemy": "[name of other clan]", "duration": 1
* You cannot be at war with more than one clan!


} << --- this is ALWAYS be at the start and end of this json

### Changing Clan Temperament

* If you'll like to see the calculating code for clan temperament yourself, you'll search for `def temperament(self):` in scripts > clan.py

Changing the Clan Temperament is more involved than simply changing the listed type in the `clan.json`. Instead, the clan temperament is based on the facets of the cats within the player clan. If you want to change the temperament, you need to manually change all four facets of the clan cats.

#### Temperament Table

This is a table showing where the first temperament options stand on how "social" and "aggressive" they are.

| xx | low_aggression | mid_aggression |high_aggression |
| ----- | :---- | :---- | :---- |
| low_social  | "cunning" | "proud" | "bloodthirsty" |
| mid_social | "amiable" |"stoic" | "wary" |
| high_social  | "gracious" | "mellow" | "logical" |

This is the table showing where the second temperament options stand on how "stable" and "lawful" they are.

| xx | low_stability | mid_stability |high_stability |
| ----- | :---- | :---- | :---- |
| low_lawful  | "chaotic" | "mercurial" | "calculating" |
| mid_lawful | "eager" |"observant" | "adaptable" |
| high_lawful  | "decisive" | "methodical" | "steadfast" |

"Stoic" and "observant" are the default temperaments given when the game is unable to calculate the temperaments (no leader, no deputy, no medicine cats, etc)

* The range of your temperaments are 11-0. 11 is the highest, 7 is the medium, and anything below 7 is the lowest.

#### Calculating

**Afterlife temperaments:** calculated based off the guides facets and high ranked cats (leader, deputy, medicine cats)

**Clan temperaments:**

!!! tip
     When referring to facets in this context, we are separating the four numbers and grouping them together. So aggression goes with aggression and onward. You're not adding all four numbers, then finding the mean/median.

The temperament for the player clan is calculated through multiplication, mean, and median of each type of facet. 

* Leader's facets are multiplied by 3, and deputies by 2.
* Medicine cats facets are calculated to find the median
* the rest of the cats (so every cat in the player clan that is not the leader, deputy, or a medicine cat) is calculated to find the median

Once all those are calculated, then they find the mean of all of those numbers to get the total.

##### For example

Facets are formatted as [aggression, sociability, lawfulness, stability]. Each number is separated from each other.

If we are calculating the leaders influence, we'd multiply all four numbers by 3. "3,2,8,10" > [3*3], [2*3], [8*3], [10*3] > "9,6,24,30"

Same with deputy. We'd multiply all four numbers by 2. "1,2,9,5" > [1*2], [2*2], [9*2], [5*2] > "2,4,18,10"

Let's say we only have one medicine cat. We wouldn't do anything with their facets (use them as is). If we have multiple, we'll calculate the median between all of them. 

Aggression: 1 1 8 14 = 1 + 8 = 9/2 = 4.5
... and so forth with the rest of them

You'll do the same for other clan cats within the player clan. Calculate their median.

With the total numbers, calculate the mean:

Aggression [leader: 9] + [deputy: 2] + [medicine cats: 4.5] + [clan_cats: 9] = 24.5/4 = 6.1 (we'll round to 6)
... and so forth with the rest of them

If you want to change the temperament of your clan, you will need to change the facets and calculate them to make sure they fit the vision that you have. Sometimes, just changing the leader, deputy, and medicine cats is enough of a change but other times, you'll have to go further.