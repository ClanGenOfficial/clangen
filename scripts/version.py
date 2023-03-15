import logging
import os
import subprocess
import sys


logger = logging.getLogger(__name__)


def get_version_info():
    if get_version_info.instance is None:
        is_source_build = False
        version_number = ""
        is_release = False

        game_root_directory = os.path.dirname(sys.argv[0])

        if os.path.exists(f"{game_root_directory}/commit.txt"):
            with open(f"{game_root_directory}/commit.txt", 'r', encoding="utf-8") as read_file:
                version_number = read_file.read()
                is_release = True
        else:
            is_source_build = True
            try:
                version_number = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
            except:
                logger.exception("Git CLI invocation failed")
            is_release = False
        get_version_info.instance = VersionInfo(is_source_build, is_release, version_number)
    return get_version_info.instance


get_version_info.instance = None


class VersionInfo:
    def __init__(self, is_source_build, is_release, version_number):
        self.is_source_build = is_source_build
        self.is_release = is_release
        self.version_number = version_number
