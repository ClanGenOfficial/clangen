"""
This file is used to connect to Discord's Rich Presence API.
This allows the game to show up on your Discord profile.

Discord RPC is not required for the game to run.
If you do not have the pypresence module installed,
this file will not be used, and the game will run as normal.
"""
from time import time
import os
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
            # raise ImportError # uncomment this line to disable rpc without uninstalling pypresence
            from pypresence import Presence, DiscordNotFound
            print("Discord RPC is supported")
        except ImportError:
            print("Pypresence not installed, Discord RPC isn't supported.")
            print("To enable rpc, run 'pip install pypresence' in your terminal.")
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
            self.rpc_supported = True
            self.connect()
            print("Connected to discord!")
        except ConnectionError as e:
            print(f"Failed to connect to Discord: {e}")
            return

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

            try:
                img_str = f"{game.clan.biome}_{game.clan.current_season.replace('-', '')}_{game.clan.camp_bg}_{'dark' if game.settings['dark mode'] else 'light'}"
                img_text = game.clan.biome
            except AttributeError:
                print("Failed to get image string, game may not be fully loaded yet. Dont worry, it will fix itself. Hopefully.")
                img_str = "discord" # fallback incase the game isn't loaded yet
                img_text = "Clangen!!"
            
            # Example: beach_greenleaf_camp1_dark

            clan_name = 'Loading...'
            cats_amount = 0
            if game.clan:
                clan_name =  f"{game.clan.name}Clan"
                cats_amount = len(game.clan.clan_cats)
                clan_age = game.clan.age
            else:
                clan_name = 'Loading...'
                cats_amount = 0
                clan_age = 0
            self.rpc.update(
                state=state_text,
                details=f"Managing {clan_name} for {clan_age} moons" ,
                large_image=img_str.lower(),
                large_text=img_text,
                small_image="discord",
                small_text=f"Managing {cats_amount} cats",
                start=self.start_time,
                buttons=[{"label": "Join The Server", "url": "https://discord.gg/clangen"}],
            )

    def close(self):
        if self.connected:
            self.rpc.close()
            self.connected = False
            