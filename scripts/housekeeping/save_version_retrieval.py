import os
from typing import DefaultDict

import ujson

from scripts.game_structure.game import switch_get_value, Switch
from scripts.game_structure.game.switches import switch_set_value
from scripts.housekeeping.datadir import get_save_dir


def get_version() -> dict:
    version_info = None
    if os.path.exists(
        get_save_dir() + "/" + switch_get_value(Switch.clan_list)[0] + "clan.json"
    ) or os.path.exists(
        get_save_dir() + "/" + switch_get_value(Switch.clan_list)[0] + "/clan.json"
    ):
        filename = (
            get_save_dir() + "/" + switch_get_value(Switch.clan_list)[0] + "/clan.json"
        )
        with open(
            filename,
            "r",
            encoding="utf-8",
        ) as read_file:  # pylint: disable=redefined-outer-name
            clan_data = ujson.loads(read_file.read())

        # Return Version Info.
        version_info = {
            "version_name": clan_data.get("version_name"),
            "version_commit": clan_data.get("version_commit"),
            "source_build": clan_data.get("source_build"),
        }

    elif os.path.exists(
        get_save_dir() + "/" + switch_get_value(Switch.clan_list)[0] + "clan.txt"
    ):
        switch_set_value(
            Switch.error_message,
            "TXT Clans are no longer supported. Please use an external tool to update your Clan to the modern format.",
        )
    else:
        switch_set_value(
            Switch.error_message, "There was an error loading the clan.json"
        )

    return version_info
