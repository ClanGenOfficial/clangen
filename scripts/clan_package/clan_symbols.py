from random import choice

from scripts.cat.sprites.load_sprites import sprites


def clan_symbol_sprite(clan, return_string=False, force_light=False):
    """
    returns the clan symbol for the given clan_name, if no symbol exists then random symbol is chosen
    :param clan: the clan object
    :param return_string: default False, set True if the sprite name string is required rather than the sprite image
    :param force_light: Set true if you want this sprite to override the dark/light mode changes with the light sprite
    """
    if not clan.chosen_symbol:
        possible_sprites = []
        for sprite in sprites.clan_symbols:
            name = sprite.strip("1234567890")
            if f"symbol{clan.name.upper()}" == name:
                possible_sprites.append(sprite)
        if possible_sprites:
            clan.chosen_symbol = choice(possible_sprites)
        else:
            # give random symbol if no matching symbol exists
            print(
                f"WARNING: attempted to return symbol, but there's no clan symbol for {clan.name.upper()}. "
                f"Random chosen."
            )
            clan.chosen_symbol = choice(sprites.clan_symbols)

    if return_string:
        return clan.chosen_symbol
    else:
        return sprites.get_symbol(clan.chosen_symbol, force_light=force_light)
