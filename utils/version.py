"""
Write a version.ini file
"""

import sys

from util import getCommandOutput


def main(
    version_number: str = None,
    release_channel: str = None,
    upstream: str = None,
    silent: bool = True,
):
    """
    Writes a version.ini file with the given version number, release channel, and upstream
    """
    if version_number is None:
        if not silent:
            print("Getting version number from git")
        try:
            version_number = getCommandOutput("git rev-parse HEAD").stdout.strip()
        except Exception as e:
            print(e)
            version_number = "unknown"
    if release_channel is None:
        if not silent:
            print("Defaulting release_channel to development")
        release_channel = "development"
    if upstream is None:
        if not silent:
            print("Getting upstream from git")
        try:
            origin = getCommandOutput("git remote get-url origin").stdout.strip()
            if origin.startswith("git@"):
                # git@github.com:ClanGenOfficial/clangen.git
                repo = origin.split(":")[1]
            else:
                # https://github.com/ClanGenOfficial/clangen.git
                repo = origin.replace("https://github.com/", "")
            upstream = repo.replace(".git", "")
        except Exception as e:
            print(e)
            upstream = "unknown"

    if not silent:
        print(f"Version: {version_number}")
        print(f"Release channel: {release_channel}")
        print(f"Upstream: {upstream}")

    with open("version.ini", "w", encoding="utf-8") as f:
        f.write(
            f"""[DEFAULT]
version_number={version_number}
release_channel={release_channel}
upstream={upstream}"""
        )

    if not silent:
        print("version.ini written")


if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        print(
            "Usage: version.py [-s] [-v <version_number>] [-r <release_channel>] [-u <upstream>]"
        )
        sys.exit(0)

    _version_number = None
    _release_channel = None
    _upstream = None
    _silent = False
    if "-v" in sys.argv:
        _version_number = sys.argv[sys.argv.index("-v") + 1]
    if "-r" in sys.argv:
        _release_channel = sys.argv[sys.argv.index("-r") + 1]
    if "-u" in sys.argv:
        _upstream = sys.argv[sys.argv.index("-u") + 1]
    if "-s" in sys.argv:
        _silent = True

    main(
        version_number=_version_number,
        release_channel=_release_channel,
        upstream=_upstream,
        silent=_silent,
    )
