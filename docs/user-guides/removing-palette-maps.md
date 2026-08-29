# Removing Palette Mapping

Currently, ClanGen utilizes palette mapping for their collar sprites. This is a method of recoloring that allows ClanGen to create many colorways with less work. However, it's best suited to pixel art and thus isn't ideal for high-res sprite mods. If you're interested in turning off this palette mapping for your mod, this guide will tell you how! This only requires `.json` file editing and no real coding.

!!! important "Save Conversion"
    It's important to note that this **will** lead to pre-mod saves error-ing sprites that include collars. Save conversion can be set up, but that won't be covered in this guide. It may be best to inform your users of the issue and provide instructions for how they can save-edit any pre-mod files they intend to use.

## The Spritesheet

Prior to palette mapping being added, collars were separated into three different spritesheets. Now, they're all held in `acc_collars.png` and we'll have to continue with that single spritesheet. This guide won't cover how to separate the sheet into multiple again, as that's more complex. So ensure all your collar accs are together in the single `acc_collars.png` sheet.

## `collar_sprite_data.json`

First, let's modify the `collar_sprite_data.json`, found in `sprites/dicts`. Set the `palette_map` value to `false`.

Next, remove the `style_data` entry altogether.  We're going to replace it with `sprite_list`, which will be a list of lists.

The json should look like this:
```json
{
    "spritesheet": "acc_collars",
    "palette_map": false,
    "sprite_list": [
        [
            "row 1 collars"
        ],
        [
            "row 2 collars"
        ],
        [
            "ect."
        ]
    ]
}
```
Each list within `sprite_list` corresponds to a row of the spritesheet. Inside, list the names of the collars as they should appear within save files. If the first row of your spritesheet was a red bow, blue bow, and yellow bow, then the `sprite_list` should appear as:

```json
    "sprite_list": [
        [
            "RED_BOW", 
            "BLUE_BOW", 
            "YELLOW_BOW"
        ],
        [
            "row 2 collars"
        ],
        [
            "ect."
        ]
    ]
```

!!! tip
    While collar names can be anything, it's best to make them simple and recognizable. All caps and underscores instead of spaces is a common save file convention used for ClanGen.

## Display Names

Next, we need to change how the accessory names are displayed. Head to the `accessories.en.json` file in `resources/lang/en/cat`.

You can remove the collar accessory entries held within, if you like, but they shouldn't interfere as long as your collar names are unique from them.

You can add your new collars at the bottom with the following format:
```json
"COLLAR_NAME": {
    "zero": "name displayed on cat profile",
    "many": "plural name used in event text",
    "one": "singular name used in event text"
}
```

With that, your collars should work and appear in game! If you're encountering errors, be sure to check that your edits aren't missing any commas, quotations, or brackets.