# Localization

!!! info "Disambiguation"
    This is the page for *writers and translators* using `i18n` to create or modify content for the game in a target language. If you're a developer, you'll want the [code localization page](../code/localization.md).

Localizing ClanGen can be broadly divided into two key sections: the UI and in-game content.

We use ISO 2-letter language codes for storing the language a player wants to use. This means that `en` is English, `fr` is French, `es` is Spanish, etc. Check online what the code is for the language you are planning to implement, as you'll need it in many places.

There is a helper Python script in `resources/lang` called `create_new_lang_files.py`. By changing the 2-letter code on `line 7` of the file and running it, it will automatically create and rename all the files you'll need to localize into that language. Unfortunately, it doesn't do the translating part for you :joy:

## Localizing in-game content

Despite the undertaking being much more massive, it requires much less explanation. If you have run `create_new_lang_files.py`, the structure is all good to go. Simply delete the contents of the files and replace it with translated content. See the relevant documentation elsewhere for details on how it all works.

!!! caution
    Ensure that you do not leave empty files as the program will not be able to detect that they're empty. If you wish to remove the files entirely, just delete them and ClanGen will backfill anything missing with the fallback language (English). Failure to do so may result in buggy games since there's not enough content to run.

Content does not have to solely be translation: due to the nature of the localization, unique content can be created in other languages. It does **not** need an English equivalent, and you do not have to consign yourself to an eternity of translating existing content - you'll spend enough time doing that for the UI.

Speaking of...

## Localizing the UI
For the UI, a module called `python-i18n` has been used, which may be familiar if you have worked on localizing in other programming languages. `i18n` files can be easily recognised by their unique naming convention: `filename.[ISO-code].json`. For example, `pelts.en.json` is an `i18n` file, but `snippet_collections.json` isn't.

`i18n` JSON files are a dictionary with a single key - the 2-letter code of the language you're localizing. This key should match the 2-letter code in the name of the file and the name of the overarching containing folder. Within that key, there is a dictionary that contains the values of the relevant strings.

### Structure of `i18n` JSON files

```json
{
    "[ISO code]": {
        "english_key_regular": "localized value",
        "english_key_count": {
            "one": "one localized value",
            "many": "%{count} localized values"
        },
        "english_key_keywords": "The leader, %{name}, endorses this message!"
    }
}
```
_Example `i18n` JSON file_

There are two main types of `i18n` string: basic and pluralized forms. Basic keys are just a string: this is what will display all the time, whenever that value is requested. Pluralized forms are dictionaries. Depending on the needs of the language you're translating into, there may be different sentence structures or wordings depending on the number of items in the sentence.

The possible keys for a pluralized value are `zero`, `one`, `some`, and `many`. The minimum that are required to ensure no errors occur are `one` and `many`. Sometimes, we use the pluralization module in some... unconventional ways.

!!! todo
    We really ought not do these crimes against pluralization. I was exhausted.

#### Crimes against Pluralization (or, where we use it weirdly)
| File name | Affected records | Quirks 
|--|--|--|
|`relationships.xx.json` | Labels | `one` is the basic level of relationship (e.g. "dislike"). `many` is the increased level (e.g. "hate")
| `cat/accessories.xx.json`| All | `zero` is what is displayed on the cat's profile. `one` and `many` are used in events when a cat gains that accessory.
|`cat/pelts.xx.json` | All pelt colors | `one` is used in "short" descriptions of the cat (on ProfileScreen). `many` is used in the Allegiances screen to give more detail.

## The `config.json` file

(Otherwise entitled, "how I lost my mind").

`config.json` gives you fine-grained control over some of the most frustrating aspects of generating content on-the-fly in other languages. In our case, you have more options regarding pronouns and the sentence structure for the Allegiances screen. We'll go over them in that order.

### Pronouns

#### sets
> `sets` contains a dictionary of `genderalign` keys and string integer values. The values correspond to the keys of `pronouns.xx.json` (the default available pronouns).
>
> It also includes `default`, as well as a series of `plural` keys. `default` is used for unrecognized `genderalign`s and as a general fallback if something unexpected happens. It is also the pronoun set used for faded cats.
>
> `plural` keys are used for gendered languages whose plurals vary depending on the composition of the group. Further control of the hierarchy of pluralization is available in [plural_rules](#plural_rules)

#### conju_count
> This is used for the custom pronouns screen to determine how many dropdown boxes to generate for conjugations.

#### gender_count
> This is used for the custom pronouns screen to determine how many dropdown boxes to generate for grammatical genders.

#### plural_rules
> Contains one key, `order`, which is itself a dictionary. The keys correspond to the grammatical gender of a cat, and the value matches the group in [sets](#sets) that it corresponds to.
>
> The current ruleset operates on a hierarchy: the plural pronoun will be the first item in the dictionary that any of the cats in the group qualify for. For example, there may be three grammatically female cats and one grammatically male - if male plural comes before female plural, the pluralization chosen will be male. If this is not appropriate for the target language, please reach out and we'll see if we can figure out a solution!

#### adj_default
> When using an {ADJ} label, it's possible that there may not be a cat to refer to within the statement (for example, when talking about a warrior generically). The adjective default determines which section of the label to use if no key is provided. 
>
> Example: `{ADJ/XXX/potato/potatoes/potat}`with an `adj_default` of `1` would return `potato`.

### description
Describing cats in Clangen is tricky, as we generate the sentences entirely on-the-fly based on their characteristics. The flexibility in this module may become a double-edged sword, as it's easy to overcomplicate in pursuit of the most natural-sounding sentences.

If in doubt, keep it simple. Stick to one sentence structure if possible.

#### ruleset
> `ruleset` is a dictionary. Permitted keys: `scarred`, `fur_length`, `pattern`, `color`, `cat`, `vitiligo`, `amputation`. These represent the key traits of a cat that are represented in the long description. Their order in the ruleset determines their display order.

> Example ruleset (taken from the English `config.json`):
```json
"ruleset": {
    "scarred": "",
    "fur_length": "",
    "pattern": ["color"],
    "cat": "",
    "vitiligo": "",
    "amputation": ""
}
```
> `pattern` here takes a list as an argument, with `color` appearing inside it. This allows us to represent things like `striped grey` or `dark-brown mackerel`, where the colour moves around relative to the pattern in the sentence.

!!! caution
    There is nothing stopping you from repeating things in the ruleset. Make sure that you remove a key if it is nested as a value, otherwise things might start looking strange.

#### groups
> This is a list of dictionaries. Full example (taken from the English `config.json`):
```json
"groups": [
    {
        "values": [0, 1],
        "format": ", ",
        "post_value": ", "
    },
    {
        "values": [2, 3],
        "format": " "
    },
    {
        "values": [4, 5],
        "format": "list",
        "pre_value": ", with "
    }
]
```
##### values
> **Required**
>
> List the indexes of each item that belongs in this group.

!!! caution "Warning"
    If the index of a given item is not included in one of the `values` blocks in `groups`, it **will not be displayed**. This is intended behaviour.

##### format
> **Required**
>
> What to connect each item in the group with.

##### pre_value
> *Optional*
>
> Added before the block of attributes.

##### post_value
> *Optional*
>
> Added after the block of attributes.