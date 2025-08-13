"""
This file is used to connect to Discord's Rich Presence API.
This allows the game to show up on your Discord profile.

Discord RPC is not required for the game to run.
If you do not have the pypresence module installed,
this file will not be used, and the game will run as normal.
"""

import asyncio
import threading
from time import time

from scripts.game_structure.game.settings import game_setting_get
from scripts.game_structure.game.switches import switch_get_value, Switch
from scripts.game_structure import game

status_dict = {
    "start screen": "At the start screen",
    "make clan screen": "Making a Clan",
    "mediation screen": "Mediating a dispute",
    "patrol screen": "On a patrol",
    "profile screen": "Viewing a cat's profile",
    "ceremony screen": "Holding a ceremony",
    "starclan screen": "Viewing StarClan",
    "dark forest screen": "Viewing the Dark Forest",
    "med den screen": "In the medicine den",
}


class _DiscordRPC(threading.Thread):
    def __init__(self, client_id: str, daemon: bool):
        super().__init__(daemon=daemon)
        self._rpc = None
        self._client_id = client_id
        self._connected = False
        self._start_time = round(time() * 1000)
        self._rpc_supported = False
        self._event_loop = asyncio.new_event_loop()

        self.start_rpc = threading.Event()
        self.update_rpc = threading.Event()
        self.close_rpc = threading.Event()

    def run(self):
        self.start_rpc.wait()
        self.get_rpc()
        self.connect()
        while not self.close_rpc.is_set():
            self.update_rpc.wait()
            self.update()
        self.close()

    def get_rpc(self):
        # Check if pypresence is available.
        if not game_setting_get("discord"):
            return
        try:
            # raise ImportError # uncomment this line to disable rpc without uninstalling pypresence
            from pypresence import Presence, DiscordNotFound

            print("Discord RPC is supported")
        except ImportError:
            print("Pypresence not installed, Discord RPC isn't supported.")
            print("To enable rpc, run 'pip install pypresence' in your terminal.")
            return
        # Check if Discord is running.
        try:
            self._rpc = Presence(client_id=self._client_id, loop=self._event_loop)
            print("Discord found!")
        except DiscordNotFound:
            print("Discord not running.")
            return
        # Try to connect.
        try:
            self._rpc_supported = True
            self.connect()
            print("Connected to discord!")
        except ConnectionError as e:
            print(f"Failed to connect to Discord: {e}")

    def connect(self):
        if self._rpc_supported:
            try:
                self._rpc.connect()
            except BaseException as e:
                self._rpc_supported = False
                print(f"Failed to connect to Discord: {e}")
                return
            self._connected = True
            self.update()

    def update(self):
        if self._connected:
            try:
                state_text = status_dict[switch_get_value(Switch.cur_screen)]
            except KeyError:
                state_text = "Leading the Clan"

            try:
                img_str = (
                    f"{game.clan.biome}_{game.clan.current_season.replace('-', '')}_"
                    f"{game.clan.camp_bg}_{'dark' if game_setting_get('dark mode') else 'light'}"
                )
                img_text = game.clan.biome
            except AttributeError:
                print(
                    "Failed to get image string, game may not be fully loaded yet. "
                    "Don't worry, it will fix itself. Hopefully."
                )
                img_str = "discord"  # fallback incase the game isn't loaded yet
                img_text = "Clangen!!"

            # Example: beach_greenleaf_camp1_dark

            if game.clan:
                clan_name = f"{game.clan.displayname}Clan"
                cats_amount = len(game.clan.clan_cats)
                clan_age = game.clan.age
            else:
                clan_name = "Loading..."
                cats_amount = 0
                clan_age = 0
            try:
                self._rpc.update(
                    state=state_text,
                    details=f"Managing {clan_name} for {clan_age} moons",
                    large_image=img_str.lower(),
                    large_text=img_text,
                    small_image="discord",
                    small_text=f"Managing {cats_amount} cats",
                    start=self._start_time,
                    buttons=[
                        {
                            "label": "Join The Server",
                            "url": "https://discord.gg/clangen",
                        }
                    ],
                )
            except BaseException:  # pylint: disable=broad-except
                print("Discord rpc had issue updating, disabling...")
                self._rpc_supported = False
                self._connected = False
                self._rpc = None
        self.update_rpc.clear()

    def close(self):
        if self._connected:
            self._rpc.close()
            self._connected = False
