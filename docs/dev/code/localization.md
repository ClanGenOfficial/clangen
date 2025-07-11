# Localization

!!! info "Disambiguation"
    This is the page for *developers* using `i18n` to create or modify code. If you're a writer or translator, you'll want the [writing localization page](../writing/localization.md).

Ensure you have read and are familiarised with the writing equivalent of this page, (linked above), especially the section called [Localizing the UI](../writing/localization.md#localizing-the-ui), as it explains many concepts that will be relevant in this section.

## Basic usage

What is `i18n`, really? Short answer: a slightly intelligent dictionary. At its most basic, `i18n.t()` finds the relevant string in the requested file for the given locale and returns it. That's it. Here's an example of that in use.

```pycon
>>> print(i18n.t("docs.demo.hello_world"))
hello world
```
_Example usage_

Our UI is automatically hooked up to `i18n`, so in very simple cases you shouldn't have to call the function at all. We'll discuss more details on the differences [in the relevant section](#using-i18n-in-ui-components).

### Providing strings to i18n
_(AKA, dot notation)_

To help organise the dictionary into relevant groups, `i18n` works on a folder structure of JSON files. The root folder is the two-letter ISO code for the target language (`en` for English), which does not need to be included in the name.

Example: If I want to reference the string "general settings", used in the settings screen. It currently lives in `screens/settings.en.json` (again, ignoring all the bits before and including the `en` folder). To make this readable to `i18n`, remove the `.en.json` part. We now have `screens/settings`, which references the entire file. To get the specific item we want, add the relevant key afterward: `screens/settings/general`, in this case.

`i18n` uses dot notation to indicate file hierarchy. Therefore, replace all the slashes with dots: `screens.settings.general` is the final key that `i18n` needs to translate that string.

You **must** include the full file location, starting from the ISO code. Failing to do so means that i18n will return the key rather than your shiny value.

### Variables in `i18n`

It's easy enough to hardcode something like the following:
```pycon
name1 = "Stinkypaw"
name2 = "Silverpelt"
print(name1 + " gives the ball to " + name2 + ".")
>>> Stinkypaw gives the ball to Silverpelt.
```

However, this falls apart when you translate it to another language with a different word order. If we want to insert variables into sentences whilst allowing translations to move where they are, we need variables.

Here's an example from `general.en.json`:

```json
{
    "cats_mate": "%{name}'s mate"
}
```

If we look at where `cats_mate` is called, we see the following:

```python
i18n.t("general.cats_mate", name=other_cat.name)
```

This means that at runtime, `%{name}` is replaced with the value of `other_cat.name`. Multiple variables can be used in a string, just ensure their names are unique. Define them after the first in the same manner.

```python
i18n.t("docs.demo.multivar", foo="foo", bar="bar", baz="baz")
```

Summary: to make a variable, declare it in the JSON file and ensure that the `i18n` call supplies the value when requested (see later sections for doing this direct in the UI). 

Any alphabetical string can be used as a variable name (may also allow numbers, I can't remember). It must also be passed in as a string. There is, however, one notable exception.

#### The "count" variable, AKA Pluralization

For the basics of pluralization, see [Structure of `i18n` files](../writing/localization.md#structure-of-i18n-json-files).

The `count` variable is special. It can be used to present different versions of the same string when plurals are involved. It must be supplied as an integer to function correctly.

Without the `count` variable and `i18n`, a function may look like this:

```python
num_apples = int(input("How many apples u want?"))
if num_apples == 0:
    print("I have no apples.")
elif num_apples == 1:
    print("I have 1 apple.")
elif num_apples <= 5:
    print("I have a few apples, about " + str(num_apples) + ".")
else:
    print("I have so many apples hELP")
```

With pluralization support, however, it becomes this:

```python
import i18n

num_apples = int(input("How many apples u want?"))
print(i18n.t("docs.demo.num_apples", count=num_apples))
```


The matching JSON for this would be:
```json
{
    "num_apples": {
        "zero": "I have no apples.",
        "one": "I have 1 apple.",
        "some": "I have a few apples, about %{count}.",
        "many": "I have so many apples hELP"
    }
}
```

These are the only four possible keys for pluralization.
- `zero` is a value of **exactly** 0.
- `one` is a value of **exactly** 1.
- `some` is less than or equal to 5. 
- `many` is the default/fallback value if none of the other criteria are met, and as such is the only non-optional key.

Also notice how, even though the number of apples is always provided, it is only given to the viewer in the `some` value. `count` can be used completely invisibly for pluralization.

## Using `i18n` in UI components

As it is built in, `i18n` is accessible immediately through any of our UI components without needing to call it explicitly. An example is shown below.

```python
continue_button = UISurfaceImageButton(
    ui_scale(pygame.Rect((70, 310), (200, 30))),
    "buttons.continue",
    [...],
)
```
_Truncated for relevance, taken from `scripts/screens/StartScreen.py`, v0.12.x_

### Using variables (UI)

To use variables, add the `text_kwargs` argument to any element that supports it. This takes a dictionary and automatically unpacks it to supply to the `i18n` function.

```python
self.clan_info["age"] = pygame_gui.elements.UITextBox(
    "screens.events.age",
    [...],
    text_kwargs={"count": game.clan.age},
)
```
_Truncated for relevance, taken from `scripts/screens/EventsScreen.py`, v0.12.x`

The `text_kwargs` argument can also be used with the `set_text` function.

```python
self.clan_info["age"].set_text(
    "screens.events.age", 
    text_kwargs={"count": game.clan.age}
)
```
_Taken from `scripts/screens/EventsScreen.py`, v0.12.x_

!!! info
    If you are only supplying a `count` variable, your IDE may raise a warning that `text_kwargs` expects values of type `string`. Ignore it in this instance. If you are supplying multiple key-value items, ensure `count` is not first - the warning usually goes away.

## Advanced `i18n` features

### Nesting calls

Because of how complicated some of the things we do are, it is sometimes necessary to nest calls. This is often used when we have labels for an item, such as the Clan season.

!!! warning "Bad practice"
    Note that this is generally considered bad practice, as it removes flexibility from translations (which is the whole point of `i18n`!). Wherever possible, it is best to have multiple translated strings rather than chaining or nesting `i18n` calls. In this case, repetition is not your enemy!

```python
self.clan_info["season"] = pygame_gui.elements.UITextBox(
    "screens.events.season",
    [...],
    text_kwargs={"season": i18n.t(game.clan.current_season)},
)
```
_Truncated for relevance_