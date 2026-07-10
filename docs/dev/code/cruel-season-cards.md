# Cruel Season Cards
The Cruel Season game mode allows the player to choose specific difficulty modifiers in the form of cards. This documentation instructs developers on how to add new cards to the game.

Cards currently leverage the modifiers found in `game_config.toml` to change the game's behavior.  If developers have a new card they'd like to add, its desired behavior needs to be possible through modifying values in `game_config.toml`. 

Developers are welcome to add new values to the config to help facilitate new cards. However, keep in mind that the priority should be to avoid intense tangling of the code as a result of adding card behaviors.

## Card JSON structure
The Card JSONs can be located in `resources/dicts/cruel_season`.

There are 4 different JSON files for each card category. When adding a card, consider the modifier and then add them to the category that best fits it.

### Categories

| Category    | Description                                                                                                                                           |                                                                      
|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| Origin      | Affects starting situation of the Clan, but has no ongoing effects.                                                                                   |
| Environment | Affects the world and its resources. This could be seasonal, prey/herbs based, or some sort of effect applied to the cats from the world around them. |
| Behavior    | A change to how the cats themselves behave and interact with game mechanics.                                                                          |
| Danger      | An effect purely centered around hurting, killing, or otherwise placing the cats in dangerous situations.                                             |

The structure for a singular card object is as follows:

```json
"card_name": {
    "card_art": "file_path",
    "modifiers": {
      "mod_name": 1 // value of the modifier
    }
  }
```

`card_art` will store the string for the art file path, in the format of `"folder/art.png"`. Art files will be located in `resources/images/cruel_cards` <br> 
- ex. a behavior card art `sorrow.png` will be written as `behavior/sorrow.png`

The modifier key replacing `mod_name` should match the config it's replacing, but written in dot notation. <br> 
- ex. `["graduation"]["min_graduating_age"]` becomes `"graduation.min_graduating_age"`  

Modifier values should match the data type of the config it's replacing.

## Conflicting Cards
Some cards will conflict each other. To remedy this, we store groups of conflicting cards in `resources\dicts\cruel_season\card_conflicts.json`.
Upon card selection, the game will check if the card attempting to be selected is in a conflict group with any existing card.

Each key in the `card_conflicts.json` should be a descriptive name of the nature of the conflict. For example, if multiple cards are modifying the beginning make-up of the Clan (all kittens, all apprentices, all elders, etc.) then the key could be something like `"starting_members"`. The value of that key is then a list of all card IDs that conflict with each other.

This example would be written like this in the dict:
```json
 "starting_members": ["all_kittens", "all_apprentices", "all_elders"]
```
Upon adding a new card, consider what is being modified and check the `card_conflicts.json` to see if it would belong in any of the existing groups, or make a new group if necessary.

## Accessing The Modifiers

On Clan initialization, the player will choose modifier cards. These cards will be added to the `cruel_cards` array in the save's corresponding `clan.json` file.

To access any modifiers in the game, use `get_config()` in `scripts/config.py`.

### get_config(config_path)

`config_path` is the config that you want to access in `resources/game_config.toml`. This is passed as a string in dot notation. <br>  
  - ex. `["graduation"]["min_graduating_age"]` becomes `"graduation.min_graduating_age"`  

The function will first check the clan's `cruel_cards` array for a modifier name matching the `config_path` passed into it. If such a card does not exist, it will grab the modifier in `game_config.toml`. Then, it returns the value it finds.

## Card Display

### Art

If no custom art is available for your new card, you may use one of the existing ones as a placeholder until an artist can create a custom image.  The game will crash if you do not assign art to your card.

### Name and Description

Name and description must be added to the localization files found in `resources/lang/en/cruel_season`. The key should be the `card_name` for both the name and description files. 