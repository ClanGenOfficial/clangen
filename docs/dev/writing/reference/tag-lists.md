
# Tag Lists
Our events generally require writers to "tag" certain attributes.  These "tags" are fairly universal across all events, so the lists are held here to serve as quick reference.

## Exclusionary Tags
Some tags can be made exclusionary by prefixing them with `-`. For example:
```json
"trait": ["-calm"]
```
This would allow any cat with a trait that *isn't* `calm`.

As this is allowed in some but *not all* tags, parameters that allow exclusionary tags will be linked to this section. If a parameter *doesn't* link here, then exclusionary tags are not allowed.

!!! caution
    For most parameters, there's no use in including both exclusionary and non-exclusionary values. Such as in our example, where we exclude `calm`. All other traits are automatically available, since they aren't `calm`, so we don't need to tag any non-exclusionary values. If we were to use two tags like this: `"trait": ["-calm", "arrogant"]` to specify that `arrogant` is required and `calm` is disqualifying, then we might as well just remove `-calm`. The `arrogant` tag on its own will automatically disqualify `calm` cats.

    Where you can expect to utilize both types of values are in parameters with more intermixed tagging. For example, relationship constraints. Here, we may wish to specify that a pair of cats must NOT be child/parent as well as have the `dislikes` tier. As such we would tag: `["-child/parent", "dislikes"]`. This mixes exclusionary and non-exclusionary in a logical manner. 


### Locations
>This controls the biome and camp the event appears in. If the event can appear in any location, use "any".  If you would like the event to occur in specific biomes, but do not want to restrict it to certain camps, then add the plain biome names.  If you would like the event to occur in specific camps, you can specify the camps by extending the biome name accordingly: `"biome:{camp1_camp2_camp3}"`.  In practice, this may look like the following examples: `"mountainous:camp1"`, `"beach:camp2_camp4"`, `"plains:camp1_camp2_camp3"`.  You can utilize [exclusionary tags](tag-lists.md#exclusionary-tags).

| string        | use                              |
|---------------|----------------------------------|
| "mountainous" | appears in the mountainous biome |
| "plains"      | appears in the plains biome      |
| "forest"      | appears in the forest biome      |
| "beach"       | appears in the beach biome       |
| "wetlands"    | appears in the wetlands biome    |
| "desert"      | appears in the desert biome      |
| "any"         | appears in any biome             |

Please have a look at the [full biome differences list](biomes.md) when thinking about writing patrols. 

## General Tags
These tags are used for more general filtering purposes.

| string    | use                                                                                                                      |
|-----------|--------------------------------------------------------------------------------------------------------------------------|
| classic   | event only occurs in classic mode                                                                                        |
| no_body   | use for death events only, this indicates that the dead body is not retrievable and cannot be referenced in grief events |
| clan_wide | if this is a murder reveal, use this tag to denote this event as informing the ENTIRE Clan of the murder.                |
| romance   | marks event as being between two cats who are allowed romantic relations                                                 |
| adoption  | marks event as being an adoption                                                                                         |

> **Tags To Indicate Present Statuses** - Sometimes you may want to indicate in event text that other cats of a certain status as present in addition to m_c and r_c (perhaps m_c and r_c are watching kits play, or discussing the progress of apprentices, or complaining about tending to elders.) These tags can be used to ensure that there are cats of the mentioned status currently living within the Clan, this helps prevent situation where cats are watching nonexistent kits or other such impossibilities. Keep in mind that all of these tags check for the presence of *at least* 2 cats of the indicated status.

| string        | use                                                                                                                                                            |
|---------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| clan:{status} | event only occurs if the clan has at least 2 cats with the given status (do not include curly brackets in tag, tag should look something like: "clan:newborn") |
| clan:apps     | event only occurs if the clan has living apps, this includes ALL types of apps (medicine, mediator, and warrior)                                               |


> **Leader Specific Tags** - since leaders can have 9 lives, it's helpful to have tags that indicate how an event is influenced by those lives.

| leader event tag | use                                                                                                                                        |
|------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| all_lives        | indicates the death event will take all the remaining lives                                                                                |
| some_lives       | indicates the death event will take multiple lives, but that it will not take *all* lives. The leader will still be alive after the event. |
| lives_remain     | indicates that the death event can only occur if the leader has multiple lives left. This leader will still be alive after the event.      |
| high_lives       | this event will only occur if the leader has 7-9 lives left                                                                                |
| mid_lives        | this event will only occur if the leader has 4-6 lives left                                                                                |
| low_lives        | this event will only occur if the leader has 1-3 lives left                                                                                |

!!! tip
    Leader death events that are not tagged with `all_lives` or `some_lives` will take 1 life by default.

> **Patrol Specific Tags**
> 
| tag                   | use                                                                                                                                                                                                                                                                                                                   |
|-----------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| "romance"             | Marks the patrol as a romance patrol. Romance patrols are special, and are filtered to require patrol leader (p_l) and random cat (r_c) to to be potential mates or current mates. If any outcomes have effects on romantic-like, make sure this tag has been added, and the romantic-like is applied to p_l and r_c. |
| "rom_two_apps"        | Does nothing on its own. When "romance" present, check for potential mate or current mate between app1 and app2, rather than p_l and r_c                                                                                                                                                                              |
| "all_mentored"        | Checks if all apprentices (no matter if medicine cat or warrior) within a patrol has a mentor.                                                                                                                                                                                                                        |
| "app{index}_mentored" | First checks if the app number (IE: app1, app2, app3, and so forth) is mentioned in patrol text, then checks if the specific apprentice assigned to the abbreviation has a mentor.                                                                                                                                    |
| "disaster"            | These patrols are only possible when mass extinction is turned ON. Used to mark patrols where the entire patrol can die or become lost.                                                                                                                                                                               |
| "new_cat"             | Used to mark when a new cat can join during this patrol. Marking these patrols allows for better balancing.                                                                                                                                                                                                           |
| "halloween"           | Used to mark patrols that should only occur around halloween                                                                                                                                                                                                                                                          |
| "april_fools"         | Used to mark patrols that should only occur on april fools                                                                                                                                                                                                                                                            |
| "new_years"           | Used to mark patrols that should only occur on new years.                                                                                                                                                                                                                                                             |


## Conditions and Scars

=== "Taggable Injury Pools"

    > | **INJURY POOL NAME** | **INJURIES**                                                            |
    |----------------------|-------------------------------------------------------------------------|
    | `battle_injury`      | `claw-wound`, `cat bite`, `mangled leg`, `mangled tail`, `torn pelt`    |
    | `minor_injury`       | `sprain`, `sore`, `bruises`, `scrapes`                                  |
    | `blunt_force_injury` | `broken bone`, `broken back`, `head damage`, `broken jaw`               |
    | `hot_injury`         | `heat exhaustion`, `heat stroke`, `dehydrated`                          |
    | `cold_injury`        | `shivering`, `"frostbite" `                                               |
    | `big_bite_injury`    | `bite-wound`, `broken bone`, `torn pelt`, `mangled leg`, `mangled tail` |
    | `small_bite_injury`  | `bite-wound`, `torn ear`, `torn pelt`, `scrapes`                        |
    | `beak_bite`          | `beak bite`, `torn ear`, `scrapes`                                      |
    | `rat_bite`           | `rat bite`, `torn ear`, `torn pelt`                                     |

    > If you’d like a patrol to have an injury from one of the injury pools above, use the pool name (i.e. "battle_injury" for injuries from other cats) instead of the injury.  Think we need another pool? Let the senior developers know in the discord developer areas and let's talk.  We can have many pools, there's no limit!


===  "Injuries"

     > | Injuries                 | Allowed within events? | Capable of scarring? |
    |--------------------------|:------------------------:|:----------------------:|
    | `blood loss`             | :x:                    | :x:                  |
    | `tick bites`             | :fontawesome-solid-check:     | :x:                  |
    | `claw-wound`             | :fontawesome-solid-check:     | :fontawesome-solid-check:   |
    | `bite-wound`             | :fontawesome-solid-check:     | :fontawesome-solid-check:   |
    | `cat bite`               | :fontawesome-solid-check:     | :fontawesome-solid-check:   |
    | `beak bite`              | :fontawesome-solid-check:     | :fontawesome-solid-check:   |
    | `snake bite`             | :fontawesome-solid-check:     | :fontawesome-solid-check:   |
    | `quilled by a porcupine` | :fontawesome-solid-check:     | :fontawesome-solid-check:   |
    | `rat bite`               | :fontawesome-solid-check:     | :fontawesome-solid-check:   |
    | `mangled leg`            | :fontawesome-solid-check:     | :fontawesome-solid-check:   |
    | `mangled tail`           | :fontawesome-solid-check:     | :fontawesome-solid-check:   |
    | `broken jaw`             | :fontawesome-solid-check:     | :fontawesome-solid-check:   |
    | `broken bone`            | :fontawesome-solid-check:     | :fontawesome-solid-check:   |
    | `sore`                   | :fontawesome-solid-check:     | :x:                  |
    | `phantom pain`           | :x:                    | :x:                  |
    | `bruises`                | :fontawesome-solid-check:     | :x:                  |
    | `scrapes`                | :fontawesome-solid-check:     | :x:                  |
    | `cracked pads`           | :fontawesome-solid-check:     | :x:                  |
    | `small cut`              | :fontawesome-solid-check:     | :x:                  |
    | `sprain`                 | :fontawesome-solid-check:     | :x:                  |
    | `bee sting`              | :fontawesome-solid-check:     | :x:                  |
    | `joint pain`             | :fontawesome-solid-check:     | :x:                  |
    | `dislocated joint`       | :fontawesome-solid-check:     | :x:                  |
    | `torn pelt`              | :fontawesome-solid-check:     | :x:                  |
    | `torn ear`               | :fontawesome-solid-check:     | :fontawesome-solid-check:   |
    | `water in their lungs`   | :fontawesome-solid-check:     | :x:                  |
    | `shivering`              | :fontawesome-solid-check:     | :x:                  |
    | `frostbite`              | :fontawesome-solid-check:     | :fontawesome-solid-check:   |
    | `burn`                   | :fontawesome-solid-check:     | :x:                  |
    | `severe burn`            | :fontawesome-solid-check:     | :fontawesome-solid-check:   |
    | `shock`                  | :fontawesome-solid-check:     | :x:                  |
    | `lingering shock`        | :fontawesome-solid-check:     | :x:                  |
    | `dehydrated`             | :fontawesome-solid-check:     | :x:                  |
    | `head damage`            | :fontawesome-solid-check:     | :x:                  |
    | `damaged eyes`           | :fontawesome-solid-check:     | :fontawesome-solid-check:   |
    | `broken back`            | :fontawesome-solid-check:     | :fontawesome-solid-check:   |
    | `poisoned`               | :fontawesome-solid-check:     | :x:                  |
    | `headache`               | :fontawesome-solid-check:     | :x:                  |
    | `severe headache`        | :fontawesome-solid-check:     | :x:                  |
    | `pregnant`               | :x:                    | :x:                  |
    | `recovering from birth`  | :x:                    | :x:                  |

===  "Illnesses"

    > | Illness                | Allowed within events? |
    |------------------------|:------------------------:|
    | `fleas`                | :fontawesome-solid-check:     |
    | `seizure`              | :fontawesome-solid-check:     |
    | `diarrhea`             | :fontawesome-solid-check:     |
    | `running nose`         | :fontawesome-solid-check:     |
    | `kittencough`          | :fontawesome-solid-check:     |
    | `whitecough`           | :fontawesome-solid-check:     |
    | `greencough`           | :fontawesome-solid-check:     |
    | `yellowcough`          | :fontawesome-solid-check:     |
    | `redcough`             | :fontawesome-solid-check:     |
    | `an infected wound`    | :x:                    |
    | `a festering wound`    | :x:                    |
    | `carrionplace disease` | :fontawesome-solid-check:     |
    | `heat stroke`          | :fontawesome-solid-check:     |
    | `heat exhaustion`      | :fontawesome-solid-check:     |
    | `stomachache`          | :fontawesome-solid-check:     |
    | `constant nightmares`  | :fontawesome-solid-check:     |
    | `grief stricken`       | :x:                    |
    | `malnourished`         | :x:                    |
    | `starving`             | :x:                    |

===  "Permanent Conditions"

    > !!! important
        Generally we want to avoid giving a permanent condition to a cat. Instead, you should give them a condition that can lead to permanence (e.g. give 'broken back' instead of 'paralyzed')
    > | crooked jaw          |
    |----------------------|
    | lost a leg           |
    | born without a leg   |
    | weak leg             |
    | twisted leg          |
    | lost their tail      |
    | born without a tail  |
    | paralyzed            |
    | raspy lungs          |
    | wasting disease      |
    | blind                |
    | one bad eye          |
    | failing eyesight     |
    | partial hearing loss |
    | deaf                 |
    | constant joint pain  |
    | seizure prone        |
    | allergies            |
    | constantly dizzy     |
    | recurring shock      |
    | lasting grief        |
    | persistent headaches |
    

=== "Scars"

    >| `ONE`          |
    |----------------|
    | `TWO`          |
    | `THREE`        |
    | `TAILSCAR`     |
    | `SNOUT`        |
    | `CHEEK`        |
    | `SIDE`         |
    | `THROAT`       |
    | `TAILBASE`     |
    | `BELLY`        |
    | `LEGBITE`      |
    | `NECKBITE`     |
    | `FACE`         |
    | `MANLEG`       |
    | `BRIGHTHEART`  |
    | `MANTAIL`      |
    | `BRIDGE`       |
    | `RIGHTBLIND`   |
    | `LEFTBLIND`    |
    | `BOTHBLIND`    |
    | `BEAKCHEEK`    |
    | `BEAKLOWER`    |
    | `CATBITE`      |
    | `RATBITE`      |
    | `QUILLCHUNK`   |
    | `QUILLSCRATCH` |
    | `HINDLEG`      |
    | `BACK`         |
    | `QUILLSIDE`    |
    | `SCRATCHSIDE`  |
    | `BEAKSIDE`     |
    | `CATBITETWO`   |
    | `FOUR`         |
    | `LEFTEAR`      |
    | `RIGHTEAR`     |
    | `NOTAIL`       |
    | `HALFTAIL`     |
    | `NOPAW`        |
    | `NOLEFTEAR`    |
    | `NORIGHTEAR`   |
    | `NOEAR`        |
    | `SNAKE`        |
    | `TOETRAP`      |
    | `BURNPAWS`     |
    | `BURNTAIL`     |
    | `BURNBELLY`    |
    | `BURNRUMP`     |
    | `FROSTFACE`    |
    | `FROSTTAIL`    |
    | `FROSTMITT`    |
    | `FROSTSOCK`    |
    | `TOE`          |
    | `SNAKETWO`     |

    > !!! tip
        If you would like a visual reference for how each scar appears on the sprite, please check the [Scar Visual Guide](https://docs.google.com/spreadsheets/d/18T-VPGo4GJP35ECYnkzqKZThd6t8j7TwN97QspXtXY0/edit#gid=1080597059).


## Backstories
You can use either the backstory pool name, or an individual backstory name.  When using a backstory pool, please be sure to check that all the backstories contained within will have text suitable for your needs.  You can find the backstory text within `resources/dicts/lang/en/cat/backstories.json`.

You can utilize [#exclusionary tags](#exclusionary-tags).

| **BACKSTORY POOL NAMES**     | **BACKSTORIES**                                                                                                                                                                                    |
|------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `clan_founder_backstories`   | `clan_founder`                                                                                                                                                                                     |
| `clanborn_backstories`       | `clanborn`                                                                                                                                                                                         |
| `outsider_roots_backstories` | `outsider_roots1`, `outsider_roots2`                                                                                                                                                               |
| `half_clan_backstories`      | `halfclan1`, `halfclan2`                                                                                                                                                                           |
| `loner_backstories`          | `loner1`, `loner2`, `loner3`, `loner4`, `refugee2`, `tragedy_survivor4`, `guided3`, `refugee5`, `wandering_healer2`                                                                                |
| `rogue_backstories`          | `rogue1`, `rogue2`, `rogue3`, `refugee4`, `tragedy_survivor2`, `guided2`, `refugee5`, `wandering_healer1`                                                                                          |
| `kittypet_backstories`       | `kittypet1`, `kittypet2`, `kittypet3`, `kittypet4`, `refugee3`, `tragedy_survivor3`, `guided1`, `refugee6`                                                                                         |
| `former_clancat_backstories` | `otherclan1`, `otherclan2`, `otherclan3`, `ostracized_warrior`, `disgraced1`, `disgraced2`, `disgraced3`, `retired_leader`, `refugee1`, `tragedy_survivor1`, `medicine_cat`, `guided4`, `refugee5` |
| `healer_backstories`         | `medicine_cat`, `wandering_healer1`, `wandering_healer2`                                                                                                                                           |
| `orphaned_backstories`       | `orphaned1`, `orphaned2`, `orphaned3`, `orphaned4`, `orphaned5`, `orphaned6`                                                                                                                       |
| `abandoned_backstories`      | `abandoned1`, `abandoned2`, `abandoned3`, `abandoned4`                                                                                                                                             |
| `outsider_backstories`       | `outsider1`, `outsider2`, `outsider3`                                                                                                                                                              |

## Age and Status

=== "Ages"

    > * `newborn`
    * `kitten`
    * `adolescent`
    * `young adult`
    * `adult`
    * `senior adult`
    * `senior`

    > You can utilize [#exclusionary tags](#exclusionary-tags).


=== "Basic Statuses"

    > * `newborn`
    * `kitten`
    * `apprentice`
    * `mediator apprentice`
    * `medicine cat apprentice`
    * `warrior`
    * `mediator`
    * `medicine cat`
    * `deputy`
    * `leader`
    * `elder`
    * `any`

    > You can utilize [#exclusionary tags](#exclusionary-tags).

=== "Affiliation Statuses"

    > * `kittypet`
    * `loner`
    * `rogue`
    * `clancat`

!!! important
    
    Not all statuses are utilized in all formats, please check the relevant event format guide for information on what statuses are or are not valid.

## Groups
You can utilize [exclusionary tags](#exclusionary-tags).

| tag                 | use                                                                                                                                      |
|---------------------|------------------------------------------------------------------------------------------------------------------------------------------|
| `match:{cat}`       | Ensures this cat will match with the given cat. For example, the tag `match:r_c` will require this cat to be in the same group as `r_c`. |
| `no_group`          | This cat is not part of any group.                                                                                                       |
| `afterlife`         | This cat must be part of one of the afterlives (StarClan, Unknown Residence, or Dark Forest)                                             |
| `player_clan`       | This cat must be part of the player_clan                                                                                                 |
| `other_clan`        | This cat must be part of a non-player clan                                                                                               |
| `starclan`          | This cat must be part of StarClan                                                                                                        |
| `unknown_residence` | This cat must be part of the Unknown Residence                                                                                           |
| `dark_forest`       | This cat must be part of the Dark Forest                                                                                                 |

## Standings

| tag       | meaning                                               |
|-----------|-------------------------------------------------------|
| `left`    | cat voluntarily left the group                        |
| `lost`    | cat became forcibly separated from the group          |
| `exiled`  | cat was forced out of the group intentionally         |

## Traits and Skills
You can utilize [#exclusionary tags](#exclusionary-tags). They function the same way as non-exclusionary tags. For example, when you write "SWIMMER,2", a cat must be a good swimmer or above. If you write "<b>-</b>SWIMMER,2" a cat *cannot* be a good swimmer or above.

=== "Skills"

    > !!! note
        Remember, skills are formatted as `SKILL,#`.  For example, `TEACHER,1` is `quick to help` and `SPEAKER,4` is `eloquent speaker`.

    > | **SKILL,**       | **1**                            | **2**                     | **3**                    | **4**                          |
    |------------------|:----------------------------------:|:---------------------------:|:--------------------------:|:--------------------------------:|
    | **TEACHER**     | `quick to help`                 | `good teacher`           | `great teacher`         | `excellent teacher`           |
    | **HUNTER**      | `moss-ball hunter`              | `good hunter`            | `great hunter`          | `renowned hunter`             |
    | **FIGHTER**     | `avid play-fighter`             | `good fighter`           | `formidable fighter`    | `unusually strong fighter`     |
    | **RUNNER**      | `never sits still`              | `fast runner`            | `incredible runner`     | `fast as the wind`            |
    | **CLIMBER**     | `constantly climbing`           | `good climber`           | `great climber`         | `impressive climber`          |
    | **SWIMMER**     | `splashes in puddles`           | `good swimmer`           | `talented swimmer`      | `fish-like swimmer`           |
    | **SPEAKER**     | `confident with words`          | `good speaker`           | `great speaker`         | `eloquent speaker`            |
    | **MEDIATOR**    | `quick to make peace`           | `good mediator`          | `great mediator`        | `skilled mediator`             |
    | **CLEVER**      | `quick witted`                  | `clever`                 | `very clever`           | `incredibly clever`            |
    | **INSIGHTFUL**  | `careful listener`              | `helpful insight`        | `valuable insight`      | `trusted advisor`              |
    | **SENSE**       | `oddly observant`               | `natural intuition`      | `keen eye`              | `unnatural senses`             |
    | **KIT**         | `active imagination`            | `good kitsitter`         | `great kitsitter`       | `beloved kitsitter`           |
    | **STORY**       | `lover of stories`              | `good storyteller`       | `great storyteller`     | `masterful storyteller`        |
    | **LORE**        | `interested in Clan history`    | `learner of lore`        | `lore keeper`           | `lore master`                  |
    | **CAMP**        | `picky nest builder`            | `steady paws`            | `den builder`           | `camp keeper`                  |
    | **HEALER**      | `interested in herbs`           | `good healer`            | `great healer`          | `fantastic healer`             |
    | **STAR**        | `curious about StarClan`        | `connection to StarClan` | `deep StarClan bond`    | `unshakable StarClan link`    |
    | **DARK**        | `interested in the Dark Forest` | `Dark Forest affinity`   | `deep Dark Forest bond` | `unshakable Dark Forest link` |
    | **OMEN**        | `interested in oddities`        | `omen seeker`            | `omen sense`            | `omen sight`                   |
    | **DREAM**       | `restless sleeper`              | `strange dreamer`        | `dream walker`          | `dream shaper`                 |
    | **CLAIRVOYANT** | `oddly insightful`              | `somewhat clairvoyant`   | `fairly clairvoyant`    | `incredibly clairvoyant`       |
    | **PROPHET**     | `fascinated by prophecies`      | `prophecy seeker`        | `prophecy interpreter`  | `prophet`                      |
    | **GHOST**       | `morbid curiosity`              | `ghost sense`            | `ghost sight`           | `ghost speaker`                |

=== "Traits"

    > !!! note
        See the [trait dictionary](trait-dictionary.md) for further information on each trait and the desired "feel" of the personality.
    >
    >  * `troublesome`
    * `lonesome`
    * `fierce`
    * `bloodthirsty`
    * `cold`
    * `childish`
    * `playful`
    * `charismatic`
    * `bold`
    * `daring`
    * `nervous`
    * `righteous`
    * `insecure`
    * `strict`
    * `compassionate`
    * `thoughtful`
    * `ambitious`
    * `confident`
    * `adventurous`
    * `calm`
    * `careful`
    * `faithful`
    * `loving`
    * `loyal`
    * `responsible`
    * `shameless`
    * `sneaky`
    * `strange`
    * `vengeful`
    * `wise`
    * `arrogant`
    * `competitive`
    * `grumpy`
    * `cunning`
    * `oblivious`
    * `gloomy`
    * `sincere`
    * `flamboyant`
    * `rebellious`



## Snippet Lists
> These abbreviations can be used to insert items from snippet lists into your text. Using an abbr will add 1-3 random items from the given snippet list, formatted as a written list (i.e. `item1, item2, and item3`). 
> 
>The following table also displays certain categories within each snippet list that you can call. To call these categories, you can just add the category after the snippet list abbr, like so: `prophecy_list_sight`.  You can even specify multiple categories, like so: `prophecy_list_sight_touch`.  If you do not add a category, then every category will be used. 

> Full snippet lists are found in `resources/dicts/snippet_collections.json`.  Feel free to add more options into these lists!

| Snippet       | Sight                     | Sound                     | Smell                     | Emotion                   | Touch                     | Taste                     |
|---------------|---------------------------|---------------------------|---------------------------|---------------------------|---------------------------|---------------------------|
| prophecy_list | :fontawesome-solid-check: | :fontawesome-solid-check: | :fontawesome-solid-check: | :fontawesome-solid-check: | :fontawesome-solid-check: | :x:                       |
| omen_list     | :fontawesome-solid-check: | :fontawesome-solid-check: | :fontawesome-solid-check: | :fontawesome-solid-check: | :fontawesome-solid-check: | :x:                       |
| clair_list    | :x:                       | :fontawesome-solid-check: | :fontawesome-solid-check: | :fontawesome-solid-check: | :fontawesome-solid-check: | :fontawesome-solid-check: |
| dream_list    | :x:                       | :x:                       | :x:                       | :x:                       | :x:                       | :x:                       |
| story_list    | :x:                       | :x:                       | :x:                       | :x:                       | :x:                       | :x:                       |


=== "prophecy_list"

    > Use this for amorphous, dreamy concepts.
    
    > | Sense group | Examples                                                                                   |
    |-------------|--------------------------------------------------------------------------------------------|
    | sight       | blood pooling on the ground, a bird's feather, and a ghostly pair of eyes                        |
    | sound       | a kit's mewl, the rushing sound of a river, and a dying promise                                  |
    | smell       | the smell of the medicine-cat den, the scent of someone long dead, and the scent of another Clan |
    | emotional   | the excitement of an apprentice, the feeling of flight, and a half-remembered promise            |
    | touch       | the brush of a pelt against their own, a tail twining with their own, and the warmth of a parent |
    

=== "omen_list"

    > Use this for more physical ideas: odd and meaningful but still grounded in reality.
    
    > | Sense group | Examples                                                                                        |
    |-------------|-------------------------------------------------------------------------------------------------|
    | sight       | a five-pointed leaf, a split acorn, and a dew-covered spider's web                                    |
    | sound       | a whispering on the wind, the sound of a cat no longer there, and the rustle of wind through the grass    |
    | smell       | the scent of spoiled queen's milk, the scent of a long-dead cat, and pine sap scent strong in the air |
    | emotional   | a pervasive feeling of dread, the imprint of fangs on skin, and the feeling of a hidden onlooker      |
    | touch       | the wind whistling past a claw raised in anger, the ache of fatique as eyes close for good, and an endless cold that seeps into their bones                                                                |


=== "clair_list"

    > Use this for amorphous, unclear things that already happened/could happen.
    
    > | Sense group | Examples                                                                                                |
    |-------------|---------------------------------------------------------------------------------------------------------|
    | sound       | the rumble of many paws on the ground, a betrayal on the wind, and distant wails of grief                     |
    | smell       | the smell of kittypet food, the smell of dirt baked by the sun, and a strange acidic scent                    |
    | emotional   | blood spilt in battle, the ache of an elder's bones, and oozing corruption                                    |
    | touch       | deathly still air, tails entwining, and paws heavy with blood                                                 |
    | taste       | the bitter taste of poppy seeds, the lingering taste of iron on the tongue, and the volatile taste of berries |


=== "dream_list"

    > Use this for dreams. These tend to be shorter, one word or phrase ideas.

    > * <i>Examples:</i> faith, excitement, parental pride, wishing on a star


=== "story_list"

    > Use this to pull the name of a story, in the vein of Aesop's Fables. Possible stories are automatically adjusted to the player's biome.

    > * <i>Examples:</i> The Cougar's Claws, The Cat Who Became a Porcupine, The Dead's Token

***

## Relationship Tiers
> These tags are used to indicate what tier of a relationship type cat1 has toward cat2. Basic tags will allow the tagged tier and greater tiers (i.e. tagging `dislike` will allow `dislike`, `hate`, and `loathe`), while appending `_only` to the end of a tag will restrict the constraint to allow just that tier (i.e. tagging `dislike_only` will allow `dislike`). You can use multiple `_only` tags to allow multiple tiers (i.e. [`dislike_only`, `hate_only`] will allow `dislike` and `hate`) and you can always mix and match these as needed (i.e. [`enjoys`, `doubts_only` `considers`] checks for three different types).

|             | Like        | Respect        | Trust         | Comfort        | Romance        |
|-------------|-------------|----------------|---------------|----------------|----------------|
| Extreme Neg | `loathe`    | `resents`      | `discredits`  | `runs_from`    | -              |
| Mid Neg     | `hates`     | `envies`       | `distrusts`   | `fears`        | -              |
| Low Neg     | `dislikes`  | `begrudges`    | `doubts`      | `avoids`       | -              |
| Neutral     | `knows_of`  | `acknowledges` | `observes`    | `considers`    | `uninterested` |
| Low Pos     | `likes`     | `praises`      | `listens_to`  | `relates_to`   | `fancies`      |
| Mid Pos     | `enjoys`    | `respects`     | `trusts`      | `understands`  | `adores`       |
| Extreme Pos | `cherishes` | `admires`      | `confides_in` | `knows_deeply` | `loves`        |


***

## Interpersonal Relationships
> These tags are used to indicate a type of Interpersonal relationship involved cats should have. These are meant for use as m_c's relationship with r_c's, or, in the case of patrols, p_l's relationship toward the other cat. 

| string            |                                    | Patrol Use Specifics                   |
|-------------------|------------------------------------|----------------------------------------|
| `siblings`        | cat1 and cat2 are siblings         | all cats are siblings                  |
| `littermates`     | cat1 and cat2 are littermates      | all cats are littermates               |
| `mates`           | cat1 and cat2 are mates            | all cats are mates                     |
| `parent/child`    | cat1 is the parent of cat2         | only for use in 2-cat patrols          |
| `child/parent`    | cat1 is the child of cat2          | only for use in 2-cat patrols          |
| `app/mentor`      | cat1 is the apprentice of cat2     | only for use in 2-cat patrols          |
| `mentor/app`      | cat1 is the mentor of cat2         | only for use in 2-cat patrols          |

You can utilize [#exclusionary tags](#exclusionary-tags).

!!! warning
    Within ShortEvents, these should only be used in m_c's relationship constraints. 

!!! warning
    Most formats utilizing these tags will be treated as a requirement list rather than a pool of possibilities. If you constrain a patrol to "child/parent", "app/mentor" the relationship between the cats <i>must</i> meet both criteria i.e. a parent who is the mentor to their apprentice child. Refer back to specific documentation of type of writing content you are adding to see if it is an exception to the rule. 

***

## Clan Temperaments
> These tags are used to indicate what type of Clan can receive an event.

|                 | low aggression | mid aggression | high aggression  |
|-----------------|----------------|----------------|------------------|
| **low social**  | cunning        | proud          | bloodthirsty     |
| **mid social**  | amiable        | stoic          | wary             |
| **high social** | gracious       | mellow         | logical          |


|                 | low stability | mid stability | high stability |
|-----------------|---------------|---------------|----------------|
| **low lawful**  | chaotic       | mercurial     | calculating    |
| **mid lawful**  | eager         | observant     | adaptable      |
| **high lawful** | decisive      | methodical    | steadfast      |