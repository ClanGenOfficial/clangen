"""
This file is used to connect to Discord's Rich Presence API.
This allows the game to show up on your Discord profile.

Discord RPC is not required for the game to run.
If you do not have the pypresence module installed,
this file will not be used, and the game will run as normal.
"""
from time import time
from scripts.game_structure.game_essentials import game


status_dict = {
    "start screen": "At the start screen",
    "make clan screen": "Making a clan",
    "mediation screen": "Mediating a dispute",
    "patrol screen": "On a patrol",
    "profile screen": "Viewing a cat's profile",
    "ceremony screen": "Holding a ceremony",
    "starclan screen": "Viewing StarClan",
    "dark forest screen": "Viewing the Dark Forest",
    "med den screen": "In the medicine den",
    }

class _DiscordRPC():
    def __init__(self, client_id: str):
        self.rpc = None
        self.client_id = client_id
        self.connected = False
        self.start_time = round(time()*1000)
        self.rpc_supported = False
        # Check if pypresence is available.
        try:
            from pypresence import Presence, DiscordNotFound
            print("Discord RPC is supported")
        except ImportError:
            print("Pypresence not installed, Discord RPC isn't supported.")
            return
        # Check if Discord is running.
        try:
            self.rpc = Presence(self.client_id)
            print("Discord found!")
        except DiscordNotFound:
            print("Discord not running.")
            return
        # Try to connect.
        try:
            self.connect()
            print("Connected to discord!")
        except ConnectionError as e:
            print(f"Failed to connect to Discord: {e}")
            return
        # Only set when we're sure it works :O
        self.rpc_supported = True

    def connect(self):
        if self.rpc_supported:
            self.rpc.connect()
            self.connected = True
            self.update()

    def update(self):
        if self.connected:
            try:
                state_text = status_dict[game.switches['cur_screen']]
            except KeyError:
                state_text = "Leading the clan"

            clan_name = 'Loading...'
            cats_amount = 0
            if game.clan:
                clan_name =  f"{game.clan.name}clan"
                cats_amount = len(game.clan.clan_cats)
            self.rpc.update(
                state=state_text,
                details="Managing " + clan_name,
                large_image="170",
                large_text=f"Managing {cats_amount} cats",
                start=self.start_time
            )

    def close(self):
        if self.connected:
            self.rpc.close()
            self.connected = False
