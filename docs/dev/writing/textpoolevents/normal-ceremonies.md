# Normal Ceremonies

Ceremonies utilize the `TextPoolEvent` format.

## Usable Cat References

| abbreviation  | use                                                                                                                                                                                                                                                                                                                                                                                                                      |
|---------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `m_c`         | The main cat. This is the cat undergoing the ceremony. You can always assume that this cat is appropriate for a given ceremony (i.e. that the `m_c` for an apprentice ceremony is of an appropriate age and rank for that ceremony). This means that you do not need to specify constraints to ensure that they are appropriate (i.e. the `m_c` of our apprentice ceremony needs no `"age": ["adolescent"]` constraint). |                                                                                                 |
| `r_c#`        | A random cat: this cat is chosen at complete random and will not be m_c. You can specify constraints on this cat to require it to have certain attributes rather than being entirely random. The `#` is replaced with a number: 0-5. It's recommended to begin at 0 and increment as needed.                                                                                                                             | |      
| `past_deputy` | This is a ceremony-unique abbreviation and can only be used within *deputy* ceremonies. The cat who held the deputy position immediately prior to `m_c` will be this cat, even if dead or outside of the Clan (however, you can apply constraints as typical to ensure a certain sort of `past_deputy`.) If there is no past deputy to be used, then any ceremony requiring one will not be chosen.                      |                                                                                                                                                                                                                                                                                 |
| `n_c#`        | A newly generated or existing outsider/other clan cat: The `#` is replaced with a number: 0-6. It's recommended to begin at 0 and increment as needed. Generating new cats is not necessarily typical for ceremony events, however it is possible.                                                                                                                                                                       |

## Directory Structure
The relationship event directory is found in `resources/lang/en/events/ceremonies`.

Within this folder are multiple files:

| name                           | use                                                                                                                                                                         |
|--------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `apprentice.json`              | Ceremonies for cats becoming warrior apprentices.                                                                                                                           |
| `deputy.json`                  | Ceremonies for cats becoming deputies.                                                                                                                                      |
| `elder.json`                   | Ceremonies for cats retiring to become elders.                                                                                                                              |
| `leader.json`                  | Ceremonies for cats becoming leader (this does not include the life-receiving ceremony).                                                                                     |
| `mediator.json`                | Ceremonies for cats becoming mediators.                                                                                                                                     |
| `mediator_apprentice.json`     | Ceremonies for cats becoming mediator apprentices.                                                                                                                          |
| `medicine_cat.json`            | Ceremonies for cats becoming medicine cats.                                                                                                                                 |
| `medicine_cat_apprentice.json` | Ceremonies for cats becoming medicine cat apprentices.                                                                                                                      |
| `warrior.json`                 | Ceremonies for cats becoming warriors.                                                                                                                                      |
| `ceremony_traits.json`         | This does not include any ceremonies! Rather this holds the "honors" that replace the `r_h` text within a ceremony string. Each cat trait has a list of potential "honors". |

## Ceremony Event Format

### Minimum Required
> The smallest amount of information you're required to include in this format.

```json
{
    "event_id": "",
    "strings": [
        "m_c was promoted to deputy."
    ],
}
```

### Full Format

This event type uses the [TextPoolEvent Format](../textpoolevents/textpoolevent-format.md)

Any parameters with ceremony-specific notes are explained below.

### Disallowed Parameters

The following parameters from the TextPoolFormat are not used for Ceremonies:

- [frequency](../textpoolevents/textpoolevent-format.md#frequency-int)
- [outcome_art](../textpoolevents/textpoolevent-format.md#outcome_art-str)
- [outcome_art_clean](../textpoolevents/textpoolevent-format.md#outcome_art_clean-str)
- [required_cat_types](../textpoolevents/textpoolevent-format.md#required_cat_types-dictstr-listint)
- [patrol_temperament](../textpoolevents/textpoolevent-format.md#patrol_temperament-liststr)
- [exp_gained](../textpoolevents/textpoolevent-format.md#exp_gained-int)

***

### event_id: str
[Main event_id Notes](../textpoolevents/textpoolevent-format.md#event_id-str)

Generally, the ID tries to specify specific circumstances or themes of the ceremony. The rank of the ceremony is typically used as a prefix for this id.

* `app_no_mentor0`
* `warrior_unsure0`
* `deputy_clan_chosen1`

***
 
