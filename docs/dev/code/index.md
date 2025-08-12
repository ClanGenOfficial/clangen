# Basic
This will cover the basic information for code.

## General tips
### Ways to find things in the codebase if you don’t know where they are
* ctrl + shift + F (search all files in project for keywords)
* ctrl + click (follow function calls and class initializations to their definitions)
* if you’re trying to find code for what happens on a screen in response to clicking something, check the screen’s handle_event() function for what code runs when that button is pressed
* keep playing around with fixing bugs or adding new features. Eventually you’ll develop an intuition for where things will probably be in the codebase

## Bug Reporting

See [report a bug](../../report-a-bug.md).
## Game Config
The [game config](https://github.com/ClanGenOfficial/clangen/blob/development/resources/game_config.toml), found in 
resources/game_config.toml, holds several developmental settings that are used within ClanGen. These settings are 
used to control chances of certain events happening, relationship values, patrol generation, and more.

Please see the game config file for more details. What settings do is specified in the file.
