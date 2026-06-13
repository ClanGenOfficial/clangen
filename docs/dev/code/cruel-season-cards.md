# Cruel Season Cards

## Card JSON structure
The Card JSONs can be located in resources/dicts/cruel_season.

There are 4 different JSON files for each card category. When adding a card, consider the modifier and then add them to the category that best fits it.

### Categories

|   Category | Description|                                                                      
|------------|-----------------------------------------------------------------------------|
| Origin | Affects starting situation of the Clan, but has no ongoing effects. |
| Environment | Affects the world and it's resources. This could be seasonal, prey/herbs based, or some sort of effect applied to the cats from the world around them. |
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

## Accessing The Modifiers

On clan initialization, the player will choose modifier cards. These cards will be added to the `cruel_cards` array in the save's corresponding clan.json file.

To access any modifiers in the game, use `get_config()` in `scripts/config.py`

### get_config(clan, config_path)

`clan` is the current Clan object.

`config_path` is the config that you want to access in `resources/game_config.toml`, passing in a string in dot notation to access the element. <br>
  - ex. `"graduation.min_graduating_age"`

The function will first check the clan's `cruel_cards` array for a modifier name matching the `config_path` passed into it. If such a card does not exist, it will grab the modifier in `game_config.toml`. Then, it returns the value it finds.

