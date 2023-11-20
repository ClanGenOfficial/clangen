import logging
import os
import subprocess
import sys
from importlib.util import find_spec
from configparser import ConfigParser
from platformdirs import user_data_dir
logger = logging.getLogger(__name__)

VERSION_NAME = "0.9.0"
# This is saved in the Clan save-file, and is used for save-file converstion.
SAVE_VERSION_NUMBER = 3


def get_version_info():
    if get_version_info.instance is None:
        is_source_build = False
        version_number = VERSION_NAME
        release_channel = False
        upstream = ""
        is_itch = False
        is_sandboxed = False
        is_thonny = False
        git_installed = False

        if not getattr(sys, 'frozen', False):
            is_source_build = True

        if find_spec("thonny") is not None:
            is_thonny = True

        if os.path.exists("version.ini"):
            version_ini = ConfigParser()
            version_ini.read("version.ini", encoding="utf-8")
            version_number = version_ini.get("DEFAULT", "version_number")
            release_channel = version_ini.get("DEFAULT", "release_channel")
            upstream = version_ini.get("DEFAULT", "upstream")
        else:
            try:
                version_number = subprocess.check_output(
                    ['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
                git_installed = True
            except:
                logger.exception("Git CLI invocation failed")

        if "--launched-through-itch" in sys.argv or "LAUNCHED_THROUGH_ITCH" in os.environ:
            is_itch = True

        if "itch-player" in user_data_dir().lower():
            is_sandboxed = True

        get_version_info.instance = VersionInfo(
            is_source_build, release_channel, version_number, upstream, is_itch, is_sandboxed, git_installed, is_thonny)
    return get_version_info.instance


get_version_info.instance = None


class VersionInfo:
    def __init__(self, is_source_build: bool, release_channel: str, version_number: str, upstream: str, is_itch: bool, is_sandboxed: bool, git_installed: bool, is_thonny: bool):
        self.is_source_build = is_source_build
        self.release_channel = release_channel
        self.version_number = version_number
        self.upstream = upstream
        self.is_itch = is_itch
        self.is_sandboxed = is_sandboxed
        self.is_thony = is_thonny
        self.git_installed = git_installed

    def is_dev(self) -> bool:
        if self.release_channel != "stable":
            return True
        else:
            return False
