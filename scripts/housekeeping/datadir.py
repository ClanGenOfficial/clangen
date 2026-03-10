import os
import platform
import subprocess
import logging

from scripts.housekeeping.version import get_version_info
from scripts.housekeeping.platform import IS_IOS, user_data_dir

logger = logging.getLogger(__name__)


def setup_data_dir():
    data_dir = get_data_dir()
    os.makedirs(data_dir, exist_ok=True)
    
    # iOS Migration: Move local files to iCloud if needed
    if IS_IOS and "Documents" in data_dir and "/private/var/mobile/Library/Mobile Documents/" in data_dir:
        local_dir = os.path.join(os.environ.get("HOME", "."), "Documents")
        # If iCloud 'saves' doesn't exist but local 'saves' does, migrate!
        if not os.path.exists(os.path.join(data_dir, "saves")) and os.path.exists(os.path.join(local_dir, "saves")):
            print(f"Migrating local data to iCloud...")
            import shutil
            for item in os.listdir(local_dir):
                s = os.path.join(local_dir, item)
                d = os.path.join(data_dir, item)
                try:
                    if os.path.isdir(s):
                        shutil.copytree(s, d, dirs_exist_ok=True)
                        shutil.rmtree(s)
                    else:
                        shutil.copy2(s, d)
                        os.remove(s)
                except Exception as e:
                    print(f"Error migrating {item}: {e}")
            print("Migration complete!")

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
    if IS_IOS:
        if get_version_info().is_dev():
            return user_data_dir("ClanGenBeta", "ClanGen")
        return user_data_dir("ClanGen", "ClanGen")

    if get_version_info().is_source_build:
        return "."

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


def open_data_dir():
    if platform.system() == "Darwin":
        subprocess.Popen(["open", "-R", get_data_dir()])
    elif platform.system() == "Windows":
        os.startfile(get_data_dir())  # pylint: disable=no-member
    elif platform.system() == "Linux":
        try:
            subprocess.Popen(["xdg-open", get_data_dir()])
        except OSError:
            logger.exception("Failed to call to xdg-open.")


def open_url(url: str):
    if platform.system() == "Darwin":
        subprocess.Popen(["open", "-u", url])
    elif platform.system() == "Windows":
        os.system(f'start "" {url}')
    elif platform.system() == "Linux":
        subprocess.Popen(["xdg-open", url])
