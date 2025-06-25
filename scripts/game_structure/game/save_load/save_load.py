import os
from pathlib import Path
from shutil import move as shutil_move
from typing import Union, List

import ujson

from scripts.housekeeping.datadir import get_temp_dir, get_save_dir


def safe_save(
    path: Union[str, Path], write_data, check_integrity=False, max_attempts: int = 15
):
    """If write_data is not a string, assumes you want this
    in json format. If check_integrity is true, it will read back the file
    to check that the correct data has been written to the file.
    If not, it will simply write the data to the file with no other
    checks."""

    # If write_data is not a string,
    if type(write_data) is not str:
        _data = ujson.dumps(write_data, indent=4)
    else:
        _data = write_data

    dir_name, file_name = os.path.split(path)

    if check_integrity:
        if not file_name:
            raise RuntimeError(f"Safe_Save: No file name was found in {path}")

        temp_file_path = Path(get_temp_dir()) / (file_name + ".tmp")
        i = 0
        while True:
            # Attempt to write to temp file
            with open(temp_file_path, "w", encoding="utf-8") as write_file:
                write_file.write(_data)
                write_file.flush()
                os.fsync(write_file.fileno())

            # Read the entire file back in
            with open(temp_file_path, "r", encoding="utf-8") as read_file:
                _read_data = read_file.read()

            if _data != _read_data:
                i += 1
                if i > max_attempts:
                    print(
                        f"Safe_Save ERROR: {file_name} was unable to properly save {i} times. Saving Failed."
                    )
                    raise RuntimeError(
                        f"Safe_Save: {file_name} was unable to properly save {i} times!"
                    )
                print(f"Safe_Save: {file_name} was incorrectly saved. Trying again.")
                continue

            # This section is reached is the file was not nullied. Move the file and return True

            shutil_move(temp_file_path, path)
            return
    else:
        os.makedirs(dir_name, exist_ok=True)
        with open(path, "w", encoding="utf-8") as write_file:
            write_file.write(_data)
            write_file.flush()
            os.fsync(write_file.fileno())


def save_clanlist(loaded_clan=None, only_switch=False):
    """
    Save clanlist to file
    :param loaded_clan: currently loaded clan name
    :param only_switch: If true, don't save previous clan before switching
    :return: None
    """
    currentclan_path = Path(get_save_dir()) / "currentclan.txt"
    if loaded_clan:
        clanlist_path = Path(get_save_dir()) / "clanlist.txt"
        if clanlist_path.exists():
            # we don't need clanlist.txt anymore
            clanlist_path.unlink()

        if not only_switch:
            safe_save(currentclan_path, loaded_clan)
    else:
        if currentclan_path.exists():
            currentclan_path.unlink()


def read_clans():
    """
    Get clan data
    :return:
    """
    save_dir = Path(get_save_dir())
    clanlist_path = Path(get_save_dir()) / "clanlist.txt"
    """save_dir/clanlist.txt"""
    currentclan_path = Path(get_save_dir()) / "currentclan.txt"
    """save_dir/currentclan.txt"""

    # First, we need to make sure the saves folder exists
    if not save_dir.exists():
        save_dir.mkdir(parents=True)
        print("Created saves folder")
        return None

    # Now we can get a list of all the folders in the saves folder
    clan_list: List[str] = [d.name for d in save_dir.iterdir() if d.is_dir()]
    clan_list.sort()  # because iterdir doesn't guarantee an order, we guarantee alphabetical here

    # the Clan specified in saves/clanlist.txt should be first in the list
    # so that we can load it automatically
    if clanlist_path.exists():
        with open(clanlist_path, "r", encoding="utf-8") as f:
            loaded_clan = f.read().strip().splitlines()
            if loaded_clan:
                loaded_clan = loaded_clan[0]
            else:
                loaded_clan = None
        clanlist_path.unlink()
        if loaded_clan:
            safe_save(currentclan_path, loaded_clan)
    elif currentclan_path.exists():
        with open(currentclan_path, "r", encoding="utf-8") as f:
            loaded_clan = f.read().strip()
    else:
        loaded_clan = None

    if loaded_clan and loaded_clan in clan_list:
        clan_list.remove(loaded_clan)
        clan_list.insert(0, loaded_clan)

    # Now we can return the list of clans
    if not clan_list:
        print("No clans found")
        return None
    return clan_list
