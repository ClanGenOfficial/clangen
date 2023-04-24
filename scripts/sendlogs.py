from scripts.game_structure.image_button import UITextBoxTweaked
import requests
import os
from scripts.datadir import get_log_dir

def send_logs(token: str, progress: UITextBoxTweaked, callback: callable):
    if not verify_token(token):
        callback("BADTOKEN")
        return
    
    upload_logs(token, progress, callback)


def verify_token(token: str) -> bool:
    with requests.get("https://bot.luna.clangen.io/logtoken/" + token) as response:
        if response.status_code == 200:
            return True
        else:
            return False

def upload_logs(token: str, progress: UITextBoxTweaked, callback: callable):

    progress.set_text("Uploading logs...")
    
    logs = os.listdir(get_log_dir())
    files = {}

    for log in logs:
        with open(os.path.join(get_log_dir(), log), 'rb') as f:
            files[log] = f.read()


    req = requests.post("https://bot.luna.clangen.io/logs/", data=files, headers={'token': token})
    
    if req.status_code == 200:
        callback("SUCCESS")
    else:
        callback("ERROR")
