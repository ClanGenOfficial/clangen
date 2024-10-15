import os
import platform

from scripts.housekeeping.version import get_version_info


def setup_data_dir():
    os.makedirs(get_data_dir(), exist_ok=True)
    try:
        os.makedirs(get_save_dir(), exist_ok=True)
        os.makedirs(get_temp_dir(), exist_ok=True)
    except FileExistsError:
        print("Macos ignored exist_ok=true for save or temp dict, continuing.")
        pass
    os.makedirs(get_log_dir(), exist_ok=True)
    os.makedirs(get_cache_dir(), exist_ok=True)
    os.makedirs(get_saved_images_dir(), exist_ok=True)

    # Windows requires elevated permissions to create symlinks.
    # The OpenDataDirectory.bat can be used instead as "shortcut".
    if platform.system() != "Windows":
        if os.path.exists("game_data"):
            os.remove("game_data")
        if not get_version_info().is_source_build:
            os.symlink(get_data_dir(), "game_data", target_is_directory=True)


def get_data_dir():
    if get_version_info().is_source_build:
        return "."

    from platformdirs import user_data_dir

    if get_version_info().is_dev():
        return user_data_dir("ClanGenBeta", "ClanGen")
    return user_data_dir("ClanGen", "ClanGen")


def get_log_dir():
    return get_data_dir() + "/logs"


def get_save_dir():
    return get_data_dir() + "/saves"


def get_cache_dir():
    return get_data_dir() + "/cache"


def get_temp_dir():
    return get_data_dir() + "/.temp"


def get_saved_images_dir():
    return get_data_dir() + "/saved_images"
