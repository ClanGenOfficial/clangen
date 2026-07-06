# Cruel Season Cards

## Card JSON structure
The Card JSONs can be located in resources/dicts/cruel_season.

There are 4 different JSON files for each card category. When adding a card, consider the modifier and then add them to the category that best fits it.

### Categories

|   Category | Description|                                                                      
|------------|-----------------------------------------------------------------------------|
| Origin | Affects starting situation of the Clan, but has no ongoing effects. |
| Environment | Affects the world and its resources. This could be seasonal, prey/herbs based, or some sort of effect applied to the cats from the world around them. |
| Behavior | A change to how the cats themselves behave and interact with game mechanics. |
| Danger | An effect purely centered around hurting, killing, or otherwise placing the cats in dangerous situations.|

The structure for a singular card object is as follows:

```json
"card_name": {
    "card_art": "file_path",
    "modifiers": {
      "mod_name": 1 // value of the modifier
    }
  }
```

`card_art` will store the string for the art file path, in the format of "folder/art.png". Art files will be located in `resources/images/cruel_cards` <br> 
- ex. a behavior card art `sorrow.png` will be written as `behavior/sorrow.png`

The modifier name replacing `mod_name` should match the config it's repllacing, but written in dot notation <br> 
- ex. `["graduation"]["min_graduating_age"]` becomes `"graduation.min_graduating_age"`  

Modifier values should match the data type of the config it's replacing.

## Accessing The Modifiers

On clan initialization, the player will choose modifier cards. These cards will be added to the `cruel_cards` array in the save's corresponding clan.json file.

To access any modifiers in the game, use `get_config()` in `scripts/config.py`

### get_config(config_path)


`config_path` is the config that you want to access in `resources/game_config.toml`. This is passed as a string in dot notation. <br>  
  - ex. `["graduation"]["min_graduating_age"]` becomes `"graduation.min_graduating_age"`  

The function will first check the clan's `cruel_cards` array for a modifier name matching the `config_path` passed into it. If such a card does not exist, it will grab the modifier in `game_config.toml`. Then, it returns the value it finds.

