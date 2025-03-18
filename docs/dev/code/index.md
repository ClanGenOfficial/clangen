# Basic
This will cover the basic information for code.

## General tips
### Ways to find things in the codebase if you don’t know where they are
* ctrl + shift + F (search all files in project for keywords)
* ctrl + click (follow function calls and class initializations to their definitions)
* if you’re trying to find code for what happens on a screen in response to clicking something, check the screen’s handle_event() function for what code runs when that button is pressed
* keep playing around with fixing bugs or adding new features. Eventually you’ll develop an intuition for where things will probably be in the codebase

## Bug Reporting
### Form
This form will be used to create bug reports in the repo in the future.

**Type:** (only select one)

* UI - anything to do with the user interface. Maybe a button is not working, or the way some assets are formatted seems to be off.
* Sprite - an issue with the art in the game
* Code - general bugs related to how the game runs and responds to you. 
* Typo - misspellings or incorrect grammar - IMPORTANT: this type of "bugs" are collected in the [typo tracking issue](https://github.com/ClanGenOfficial/clangen/issues/1818)

**Describe the bug**
ex.: This bug implies that the cat is never ....

**Grade:** (only select one)

* Game-breaking - a bug that makes it impossible to play the game
* Dire - Still playable, but a major feature is broken
* Important - The bug has a large affect on the gameplay, but is not urgent
* Regular - A typical bug that should be seen to soon, but doesn’t necessarily break the game or inhibit the player
* Non-vital - This bug can easily be ignored and does not have a large impact on play
* Unimportant - This bug has little to no impact on play. 

**Reproduce**
Steps to reproduce the behavior:

1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Patrol ID + Outcome Print (if applicable):**

**Screenshots:**
If applicable, add screenshots to help explain your problem.

**Commit # or Game Version Number:**

**Additional context**
Add any other context about the issue here.

## Game Config
The [game config](https://github.com/ClanGenOfficial/clangen/blob/development/resources/game_config.json), found in 
resources/game_config.json, holds several developmental settings that are used within ClanGen. These settings are 
used to control chances of certain events happening, relationship values, patrol generation, and more.

**The first set of settings control relationship values.**

`"in_decrease_value":{
"low": 8,
"medium": 12,
"high": 16
}`

This sets the exact relationship value changes after interactions. Interactions, found in the relationships tab, can have a high, medium, or low effect on cats. These effects can be positive or negative.

`"max_interaction": 5`

This sets the max amount of interactions a cat can have each moon.

`"max_interaction_special": 8`

This sets the max amount of interactions a cat with a special role (leader, deputy, medicine cat, or mediator) can have each moon.

`"compatibility_effect": 5`

This sets the positive or negative effect that interactions will have on other cats based on their personalities. Some personalities are compatible with each other, some are neutral, some are not compatible. 

`"passive_influence_div": 1.5`

This setting helps set a buff for interactions that increases other values other than the main value. For example, if a cat has a positive romantic interaction with another cat, their platonic like and comfort levels will also increase, and their dislike will decrease. Increasing this setting's value will decrease the buff.

`"chance_for_neutral": 10`

This setting sets how high the chance is to make the interaction neutral instead of negative or positive. 1/chance
			
`"chance_of_special_group": 8`

Often when a group event is happening, only a special group is used, which is defined in group_types.json. 1/chance

`"chance_romantic_not_mate": 15`

This is the base chance of an romantic interaction with another cat, when a cat has a mate. 1/chance