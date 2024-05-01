import io
import os
import zipfile
try: import ujson
except ImportError: import json as ujson

try:
    import tkinter
    import tkinter.filedialog
except: pass

from scripts.game_structure.game_essentials import game
from scripts.clan import Clan
from scripts.housekeeping.datadir import get_save_dir
import scripts.web as web

def filepicker_prompt(file_extensions: list[tuple]) -> str:
    top = tkinter.Tk()
    top.withdraw()
    file_path = tkinter.filedialog.askopenfilename(parent=top, filetypes=file_extensions)
    top.destroy()
    return file_path

def save_file_prompt(clan_name: str, file_extensions: list[tuple]) -> str:
    top = tkinter.Tk()
    top.withdraw()
    file_path = tkinter.filedialog.asksaveasfilename(parent=top, defaultextension=".zip", filetypes=file_extensions, initialfile=clan_name)
    top.destroy()
    return file_path

def export_clan() -> None:
    """Exports a clan's data to a zip file."""
    if web.is_web: return # to be added
    game.clan.save_clan()
    bytes = io.BytesIO()
    with zipfile.ZipFile(bytes, "w") as zf:
        zf.write(f"{get_save_dir()}/{game.switches['clan_list'][0]}clan.json")
        for dirname, subdirs, files in os.walk(f"{get_save_dir()}/{game.switches['clan_list'][0]}"):
            zf.write(dirname)
            for filename in files:
                zf.write(os.path.join(dirname, filename))
    
    extensions = [("Compressed file", ["*.zip"])]
    file_path = save_file_prompt(f"{game.switches['clan_list'][0]}clan", extensions)
    if not file_path: return
    with open(file_path, "wb") as file:
        file.write(bytes.getvalue())

def import_clan(): 
    """Imports a clan's data from a zip file."""
    if web.is_web: return # to be added
    extensions = [("Compressed file", ["*.zip"])]
    file_path = filepicker_prompt(extensions)
    # print(file_path, f"{game.switches['clan_list']=}")
    if not file_path: return
    if not isinstance(game.switches['clan_list'], list):
        game.switches['clan_list'] = []
    game.switches['clan_list'].insert(0, file_path.split("/")[-1].replace("clan.zip", ""))
    with zipfile.ZipFile(file_path, "r") as zf:
        zf.extractall(''.join(get_save_dir().split("/")[:-1]))
    clan = Clan()
    clan.switch_clans(game.switches['clan_list'][0])