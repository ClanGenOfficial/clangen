import os
from typing import TYPE_CHECKING, Type

import ujson

from scripts.game_structure.game.save_load import safe_save
from scripts.game_structure.game.settings.settings import get_game_setting
from scripts.housekeeping.datadir import get_save_dir

if TYPE_CHECKING:
    from scripts.cat.cats import Cat
    from scripts.game_structure.game_essentials import Game

faded_ids = []
"""List of IDs of faded cats"""

cat_to_fade = []
"""Cats who have been faded since the last save"""


def save_cats(clanname, cat_class: Type["Cat"], game: "Game"):
    """Save the cat data."""

    directory = get_save_dir() + "/" + clanname
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Delete all existing relationship files
    if not os.path.exists(directory + "/relationships"):
        os.makedirs(directory + "/relationships")
    for f in os.listdir(directory + "/relationships"):
        os.remove(os.path.join(directory + "/relationships", f))

    save_faded_cats(clanname, cat_class, game)  # Fades cat and saves them, if needed

    clan_cats = []
    for inter_cat in cat_class.all_cats.values():
        cat_data = inter_cat.get_save_dict()
        clan_cats.append(cat_data)

        inter_cat.save_condition()

        if inter_cat.history:
            inter_cat.save_history(directory + "/history")
            # after saving, dump the history info
            inter_cat.history = None
        if not inter_cat.dead:
            inter_cat.save_relationship_of_cat(directory + "/relationships")

    safe_save(f"{get_save_dir()}/{clanname}/clan_cats.json", clan_cats)


def save_faded_cats(clanname, cat_class: Type["Cat"], game: "Game"):
    """Deals with fades cats, if needed, adding them as faded"""
    global cat_to_fade

    if cat_to_fade:
        directory = get_save_dir() + "/" + clanname + "/faded_cats"
        if not os.path.exists(directory):
            os.makedirs(directory)

    copy_of_info = ""
    for cat in cat_to_fade:
        inter_cat = cat_class.all_cats[cat]

        # Add ID to list of faded cats.
        faded_ids.append(cat)

        # If they have a mate, break it up
        if inter_cat.mate:
            for mate_id in inter_cat.mate:
                if mate_id in cat_class.all_cats:
                    cat_class.all_cats[mate_id].unset_mate(inter_cat)

        # If they have parents, add them to their parents "faded offspring" list:
        for x in inter_cat.get_parents():
            if x in cat_class.all_cats:
                cat_class.all_cats[x].faded_offspring.append(cat)
            else:
                parent_faded = add_faded_offspring_to_faded_cat(clanname, x, cat)
                if not parent_faded:
                    print(f"WARNING: Can't find parent {x} of {cat.name}")

        # Get a copy of info
        if get_game_setting("save_faded_copy"):
            copy_of_info += (
                ujson.dumps(inter_cat.get_save_dict(), indent=4)
                + "\n--------------------------------------------------------------------------\n"
            )

        # SAVE TO ITS OWN LITTLE FILE. This is a trimmed-down version for relation keeping only.
        cat_data = inter_cat.get_save_dict(faded=True)

        safe_save(f"{get_save_dir()}/{clanname}/faded_cats/{cat}.json", cat_data)

        # Remove the cat from the active cats lists
        game.clan.remove_cat(
            cat
        )  # todo: when catdirectory is added, this dependency injection can be removed

    cat_to_fade = []

    # Save the copies, flush the file.
    if get_game_setting("save_faded_copy"):
        with open(
            get_save_dir() + "/" + clanname + "/faded_cats_info_copy.txt",
            "a",
            encoding="utf-8",
        ) as write_file:
            if not os.path.exists(
                get_save_dir() + "/" + clanname + "/faded_cats_info_copy.txt"
            ):
                # Create the file if it doesn't exist
                with open(
                    get_save_dir() + "/" + clanname + "/faded_cats_info_copy.txt",
                    "w",
                    encoding="utf-8",
                ) as create_file:
                    pass

            with open(
                get_save_dir() + "/" + clanname + "/faded_cats_info_copy.txt",
                "a",
                encoding="utf-8",
            ) as write_file:
                write_file.write(copy_of_info)

                write_file.flush()
                os.fsync(write_file.fileno())


def add_faded_offspring_to_faded_cat(clanname, parent: str, offspring: str):
    """In order to siblings to work correctly, and not to lose relation info on fading, we have to keep track of
    both active and faded cat's faded offpsring. This will add a faded offspring to a faded parents file.
    """
    try:
        with open(
            get_save_dir() + "/" + clanname + "/faded_cats/" + parent + ".json",
            "r",
            encoding="utf-8",
        ) as read_file:
            cat_info = ujson.loads(read_file.read())
    except:
        print("ERROR: loading faded cat")
        return False

    cat_info["faded_offspring"].append(offspring)

    safe_save(f"{get_save_dir()}/{clanname}/faded_cats/{parent}.json", cat_info)

    return True
