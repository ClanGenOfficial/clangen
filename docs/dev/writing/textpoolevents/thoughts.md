# Thoughts
Thoughts utilize the `TextPoolEvent` format.

"Thoughts" are the line of text below a cat's name on their profile. They're meant to signify a current action or line of thinking that the cat is "currently" taking, essentially a snapshot into a cat's day-to-day life.

As such, these can be very personal, silly, or specific! It's a chance to add a lot of additional character to each cat.

However, we also don't give thoughts a ton of room on the profile. 

* Thoughts should be short and sweet, **less than 150 characters**.
* They are sentence fragments, with the cat's name on its profile assumed as the beginning of the sentence.
* They must begin with a capital letter and should have no punctuation at the end.

A valid thought:
`Is giving badger-rides to a kit`

An invalid thought:
`ExampleCat is giving badger-rides to a kit!`

!!! tip
    Within this doc you'll see references to a "main_cat" (`m_c`) and a "random_cat" (`r_c`). The thought will be appearing on the `m_c`'s profile, while the `r_c` will be a randomly chosen cat whom you can optionally include in the thought.

## Directory Structure
The thoughts directory is found in `resources/lang/en/thoughts`. Within this folder, you'll see multiple folders, each one containing a different category of thought.

Within the game, all cats take a new thought each timeskip. However, there are also special events within the game that may "replace" the cat's thought, such as death or exile. Typical timeskip thoughts are found in `while_alive` and `while_dead` (`is_guide` is also timeskip thoughts, but for a specific cat.) The rest of the folders are for those special event thoughts. Each folder contains `json` files of their associated thoughts.

| Directory              | Usage                                                                                                                                                                            | `json` Structure                                                                                                                                                                                                                                                                                                     |
|------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `is_guide`             | Thoughts that appear for the "guide cat"                                                                                                                                         | Guides can either be in the Dark Forest or StarClan, the guide's current location dictates which of these files their thought is pulled from                                                                                                                                                                         |
| `on_afterlife_change`  | Thoughts that appear when a dead cat is moved to a different afterlife                                                                                                           | The cat will pull a thought from the file matching their new afterlife                                                                                                                                                                                                                                               |
| `on_birth`             | Thoughts that appear after a cat is born                                                                                                                                         | Currently only houses `parent.json`. New parents will pull a thought from this file. If you'd like to add thoughts for the newborn, head to `while_alive/newborn.json`.                                                                                                                                              |
| `on_death`             | Thoughts that appear after a cat dies                                                                                                                                            | The cat will pull a thought from the folder matching the afterlife they join. If they're a leader and are only losing a life, they take a thought from `leader_life.json`. If they're *fully* dying, they take a thought from `leader_death.json`. All other cats pull from `general.json`                           |
| `on_exile`             | Thoughts that appear after a cat is exiled                                                                                                                                       | All cats pull from `general.json`                                                                                                                                                                                                                                                                                    |
| `on_grief_no_body`     | Thoughts that appear for grieving cats after a cat dies and has no retrievable body                                                                                              | All cats pull from `general.json`                                                                                                                                                                                                                                                                                    |
| `on_grief_toward_body` | Thoughts that appear for grieving cats after a cat dies and *has* a retrievable body                                                                                             | All cats pull from `general.json`                                                                                                                                                                                                                                                                                    |
| `on_join`              | Thoughts that appear for a cat who has just joined the Clan                                                                                                                      | All cats pull from `general.json`                                                                                                                                                                                                                                                                                    |
| `on_lost`              | Thoughts that appear for a cat who has just been lost from the Clan                                                                                                              | All cats pull from `general.json`                                                                                                                                                                                                                                                                                    |
| `on_meeting`           | Thoughts that appear for a cat who has just met, but not joined, the Clan                                                                                                        | If the cat is part of another Clan, they pull from `clancat.json`, otherwise they pull from `outsider.json`                                                                                                                                                                                                          |
| `on_rank_change`       | Thoughts that appear for a cat whose rank has just changed. Note that rank changes can happen OUTSIDE of ceremonies, so these thoughts should not reference a ceremony outright. | Cats will pull from the file matching their *current* status. Remember you can use `status_history` constraints to constrain the pool to cats who used to be certain ranks.  All cats will pull from `general.json`                                                                                                  |
| `while_alive`          | Thoughts that living cats will choose from upon timeskip                                                                                                                         | Cats will pull from the file matching their current status, if a cat is currently lost, they'll pull from the file in `while_lost` which matches with the status they had upon becoming lost. All cats (except newborns and lost cats) will pull from `general.json`. Clancats additionally draw from `clancat.json` |
| `while_dead`           | Thoughts that dead cats will choose from upon timeskip                                                                                                                           | Cats will pull from the folder matching their current afterlife, and the file matching the status they had upon death. All cats (except newborns and outsiders) will pull from `general.json`                                                                                                                        |

!!! tip
    Within `while_alive` and `while_dead`, thoughts should be placed in `general.json` if they apply to multiple statuses.

## Thought Format

### Minimum Required
>The smallest amount of information you're required to include in this format. 

```json
{
    "event_id": "test",
    "strings": [
        "Is thinking"
    ]
}
```

### Full Format

This event type uses the [TextPoolEvent Format](../textpoolevents/textpoolevent-format.md)

Any parameters with thought-specific notes are explained below.

### Disallowed Parameters

The following parameters from the TextPoolFormat are not used for Thoughts:

- [frequency](../textpoolevents/textpoolevent-format.md#frequency-int)
- [outcome_art](../textpoolevents/textpoolevent-format.md#outcome_art-str)
- [outcome_art_clean](../textpoolevents/textpoolevent-format.md#outcome_art_clean-str)
- [required_cat_types](../textpoolevents/textpoolevent-format.md#required_cat_types-dictstr-listint)
- [patrol_temperament](../textpoolevents/textpoolevent-format.md#patrol_temperament-liststr)
- [exp_gained](../textpoolevents/textpoolevent-format.md#exp_gained-int)
- [death](../textpoolevents/textpoolevent-format.md#death-listdict)
- [lost](../textpoolevents/textpoolevent-format.md#lost-listdict)
- [join](../textpoolevents/textpoolevent-format.md#join-listdict)


***

### event_id: str
[Main event_id Notes](../textpoolevents/textpoolevent-format.md#event_id-str)

Generally, the ID includes the condition, personality, age, and status of the main_cat, as well as the condition, personality, age, and status of any other cat mentioned.

* `paralyzed_gen_to_alive_gen`
* `insecure_apprentice`
* `general_formerclancat_dead_thoughts`

***

### involved_cats: dict[str: dict]
[Main involved_cats Notes](../textpoolevents/textpoolevent-format.md#involved_cats-dictstr-dict)

In thoughts, you are allowed to reference `m_c`, who is the "owner" of the thoughts, and `r_c`, who is a cat being referenced by the thought. 

***
