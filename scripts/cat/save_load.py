import os
from pathlib import Path
from typing import TYPE_CHECKING, Type, List

import ujson

from scripts.game_structure.game.save_load import safe_save
from scripts.game_structure.game.settings.settings import game_setting_get
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

    directory = Path(get_save_dir()) / clanname
    history_dir = directory / "history"
    relationships_dir = directory / "relationships"

    if not directory.exists():
        directory.mkdir(parents=True)

    # Delete all existing relationship files
    if not relationships_dir.exists():
        relationships_dir.mkdir()
    for f in relationships_dir.glob("*.json"):
        f.unlink()

    save_faded_cats(clanname, cat_class, game)  # Fades cat and saves them, if needed

    clan_cats = []
    for inter_cat in cat_class.all_cats.values():
        cat_data = inter_cat.get_save_dict()
        clan_cats.append(cat_data)

        inter_cat.save_condition()

        if inter_cat.history:
            inter_cat.save_history(history_dir)
            # after saving, dump the history info
            inter_cat.history = None
        if not inter_cat.dead:
            inter_cat.save_relationship_of_cat(relationships_dir)

    safe_save(f"{get_save_dir()}/{clanname}/clan_cats.json", clan_cats)


def save_faded_cats(clanname, cat_class: Type["Cat"], game: "Game"):
    """Deals with fades cats, if needed, adding them as faded"""
    global cat_to_fade

    fade_cat_dir = Path(get_save_dir()) / clanname / "faded_cats"

    if cat_to_fade:
        if not fade_cat_dir.exists():
            fade_cat_dir.mkdir()

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
        if game_setting_get("save_faded_copy"):
            copy_of_info += (
                ujson.dumps(inter_cat.get_save_dict(), indent=4)
                + "\n--------------------------------------------------------------------------\n"
            )

        # SAVE TO ITS OWN LITTLE FILE. This is a trimmed-down version for relation keeping only.
        cat_data = inter_cat.get_save_dict(faded=True)
        cat_path = fade_cat_dir / f"{cat}.json"
        safe_save(cat_path, cat_data)

        # Remove the cat from the active cats lists
        game.clan.remove_cat(
            cat
        )  # todo: when catdirectory is added, this dependency injection can be removed

    cat_to_fade = []

    # Save the copies, flush the file.
    if game_setting_get("save_faded_copy"):
        faded_info_copy_path = (
            Path(get_save_dir()) / clanname / "faded_cats_info_copy.txt"
        )
        if not faded_info_copy_path.exists():
            # Create the file if it doesn't exist
            with open(
                faded_info_copy_path,
                "w",
                encoding="utf-8",
            ):
                pass

        with open(
            faded_info_copy_path,
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
    faded_parent_path = (
        Path(get_save_dir()) / clanname / "faded_cats" / (parent + ".json")
    )
    try:
        with open(
            faded_parent_path,
            "r",
            encoding="utf-8",
        ) as read_file:
            cat_info = ujson.loads(read_file.read())
    except IOError:
        print("ERROR loading faded cat (file read error)")
        return False
    except ujson.JSONDecodeError:
        print("ERROR: loading faded cat (invalid JSON)")
        return False

    cat_info["faded_offspring"].append(offspring)

    safe_save(faded_parent_path, cat_info)

    return True


def add_cat_to_fade_id(cat_id):
    cat_to_fade.append(cat_id)


def get_faded_ids():
    return faded_ids + cat_to_fade


def load_faded_cat_ids(clanname):
    global faded_ids
    fade_cat_dir = Path(get_save_dir()) / clanname / "faded_cats"
    if not fade_cat_dir.exists():
        faded_ids = []
        return
    faded_ids = [f.stem for f in fade_cat_dir.glob("*.json")]
    return
