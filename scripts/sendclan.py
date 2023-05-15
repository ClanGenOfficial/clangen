from scripts.game_structure.image_button import UITextBoxTweaked
import requests
import os
import zipfile
import time
from scripts.housekeeping.datadir import get_save_dir, get_temp_dir
from scripts.game_structure.game_essentials import game
import ujson

def send_clan(token: str, progress: UITextBoxTweaked, callback: callable) -> None:
    """
    main log upload function
    """
    if not verify_token(token):
        progress.set_text("Invalid token, please try again.")
        time.sleep(5)
        callback("BADTOKEN")
        return

    upload_save(token, progress, callback)


def verify_token(token: str) -> bool:
    """
    verifies the token is valid
    """
    with requests.get("https://silverpelt.lvna.me/clantoken/" + token) as response:
        if response.status_code == 200:
            return True
        else:
            return False

def upload_save(token: str, progress: UITextBoxTweaked, callback: callable):
    """
    actually uploads the save
    """
    progress.set_text("Uploading save...")

    # zip up the current save
    with zipfile.ZipFile(os.path.join(get_temp_dir(), "save.zip"), 'w') as savezip:
        for root, dirs, files in os.walk(os.path.join(get_save_dir(), game.clan.name)):
            for file in files:
                savezip.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), get_save_dir()))
        savezip.write(os.path.join(get_save_dir(), f"{game.clan.name}clan.json"), f"{game.clan.name}clan.json")
        savezip.write(os.path.join(get_save_dir(), "currentclan.txt"), "currentclan.txt")
            
    # upload the save
    with open(os.path.join(get_temp_dir(), "save.zip"), 'rb') as f:
        req = requests.post("https://silverpelt.lvna.me/save/", files={'file': f}, headers={'token': token})
    
    if req.status_code == 200:
        progress.set_text("Save uploaded successfully!")
    else:
        progress.set_text("Failed to upload save, please try again.")

    os.remove(os.path.join(get_temp_dir(), "save.zip"))

    time.sleep(5)
    callback("DONE")
