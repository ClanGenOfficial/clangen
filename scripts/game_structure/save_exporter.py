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
from scripts.housekeeping.datadir import get_save_dir, get_data_dir
import scripts.web as web
from scripts.web import downloadFile, uploadFile, is_web

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
    game.clan.save_clan()
    bytes = io.BytesIO()
    with zipfile.ZipFile(bytes, "w") as zf:
        zf.write(f"{get_save_dir()}/{game.clan.name}clan.json")
        for dirname, subdirs, files in os.walk(f"{get_save_dir()}/{game.clan.name}"):
            zf.write(dirname)
            for filename in files:
                zf.write(os.path.join(dirname, filename))
    
    extensions = [("Compressed file", ["*.zip"])]
    if not is_web:
        file_path = save_file_prompt(f"{game.clan.name}clan", extensions)
        if not file_path: return
        with open(file_path, "wb") as file:
            file.write(bytes.getvalue())
    else:
        with open(f"/tmp/{game.clan.name}clan.zip", "wb") as file:
            file.write(bytes.getvalue())
        uploadFile(f"/tmp/{game.clan.name}clan.zip")
        os.remove(f"/tmp/{game.clan.name}clan.zip")

async def import_clan(): 
    """Imports a clan's data from a zip file."""
    extensions = [("Compressed file", ["*.zip"])]
    clan_name = None
    zip_path = None
    if not is_web:
        zip_path = filepicker_prompt(extensions)
        if not zip_path: return
        clan_name = zip_path.split("/")[-1].replace("clan.zip", "")
    else:
        zip_path = "/tmp/import.zip"
        clan_name = await downloadFile(zip_path)
    
    if not clan_name: return
    if not zip_path: return
    if not isinstance(game.switches['clan_list'], list):
        game.switches['clan_list'] = []
    # pylint: disable=no-member
    if clan_name not in game.switches['clan_list']:
        game.switches['clan_list'].insert(0, clan_name)
    with zipfile.ZipFile(zip_path, "r") as zf:
        # zf.extractall(''.join(get_save_dir().split("/")[:-1]))
        print(get_data_dir())
        zf.extractall(get_data_dir())
    clan = Clan()
    clan.switch_clans(game.switches['clan_list'][0])
