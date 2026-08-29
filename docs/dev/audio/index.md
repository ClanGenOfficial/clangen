# Basic
ClanGen's audio is split into three classes: `Music`, `Ambiance`, `Sound`. These are jointly controlled by the `AudioManager`, which should be accessed in the code via `game.audio`.

Using `game.audio` you can `start`, `check`, `mute`, and `unmute` the audio as a whole. More fine control can be attained by accessing the individual classes via `game.audio` (for example, `game.audio.music` to control the music.)

# Sound
`game.audio.sound` handles the sound effects. 

New sound effects can be added to the `resources/audio/sounds` folder. To link the sound to a specific trigger it must be added to `resources/audio/sounds.json` dictionary. The keys of this dictionary are the trigger name, while their value is a list of possible sounds for that trigger. When the trigger occurs, a random sound will be chosen from the list. 

`UIImageButtons` can be given a `sound_id` parameter, this is how we link triggers to buttons. By default, all buttons use the `button_press` sound. Hover sounds cannot be changed at this time.

Of course, sounds can also be triggered by the code at any time using the `play` function. We don't currently utilize this, but it could be used creatively in the future.

# Ambiance
`game.audio.ambiance` handles the ambient sounds.

We currently utilize a layered approach to ambiance. We have a base track, camp overlay, and season overlay. The base will play constantly, shuffling through its possible tracks. The camp and season overlays will play on a randomised timer, adding some necessary variety.

New ambiance is added to its matching folder in `resources/audio/ambiance`. Separate folders are provided for each biome and for seasonal ambiance (which isn't biome specific). The `resources/audio/ambiance.json` is used to create our track lists. Seasonal tracks should be added to their respective seasonal lists. Each biome has an individual dictionary containing a `"base"` list. If a camp has specific ambiances, then it will be given an entry in this dictionary with the key as its name (with spaces replaced by `_`).

!!! note
    If modifying the ambiance code, it's important to note that it utilizes the `pygame.mixer.music` class for its base track and sound channels for the overlays.

# Music
`game.audio.music` handles the music.

When not on the main menu, ClanGen plays music at random intervals.

New music is added to the `resources/audio/music` folder. `resources/audio/music.json` holds the playlist information. `menu_playlist` will only play on the main menu (this includes game settings, saves, and making a new Clan). We currently have a general playlist along with some seasonal playlists. New playlists can be added for missing seasons and biomes without additional coding.

!!! note
    Our music system utilized sound channels just like the sound effect system. This means that each track is loaded into memory. Care should be taken when modifying the music code that tracks are always being removed from memory once done playing to avoid excessive memory use.