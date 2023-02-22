## INFO:
# This file is used to connect to Discord's Rich Presence API.
# This allows the game to show up on your Discord profile.
#
# Discord RPC is not required for the game to run.
# If you do not have the pypresence module installed, this file will not be used, and the game will run as normal.




from scripts.game_structure.game_essentials import game
from time import time


class _DiscordRPC():
    def __init__(self, client_id: str):
        self.rpc = None
        self.client_id = client_id
        self.connected = False
        self.start_time = round(time()*1000)

        try:
            from pypresence import Presence
            print("Discord RPC is supported")
            self.rpc = Presence(self.client_id)
            self.rpc_supported = True
        except ImportError:
            self.rpc_supported = False
            pass


        self.connect()

    def connect(self):
        if self.rpc_supported:
            self.rpc.connect()
            self.connected = True
            self.update()
    
    def update(self):
        if self.connected:
            state_text = ""
            match game.switches['cur_screen']:
                case "start screen":
                    state_text = "At the start screen"
                case "make clan screen":
                    state_text = "Making a clan"
                case "mediation screen":
                    state_text = "Mediating a dispute"
                case "patrol screen":
                    state_text = "On a patrol"
                case "profile screen":
                    state_text = "Viewing a cat's profile"
                case "ceremony screen":
                    state_text = "Holding a ceremony"
                case "starclan screen":
                    state_text = "Viewing StarClan"
                case "dark forest screen":
                    state_text = "Viewing the Dark Forest"
                case "med den screen":
                    state_text = "In the medicine den"
                case _:
                    state_text = "Leading the clan"

            clan_name = ''
            if game.clan.name == '':
                clan_name = 'Loading...'
            else:
                clan_name =  game.clan.name + "clan"
            self.rpc.update(
                state=state_text, 
                details="Managing " + clan_name, 
                large_image="170", 
                large_text="Managing " + str(len(game.clan.clan_cats)) + " cats",
                start=self.start_time
            )

    def close(self):
        if self.connected:
            self.rpc.close()
            self.connected = False
