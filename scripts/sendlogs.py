from scripts.game_structure.image_button import UITextBoxTweaked
import requests
import os
import time
from scripts.housekeeping.datadir import get_log_dir
import ujson

def send_logs(token: str, progress: UITextBoxTweaked, callback: callable) -> None:
    """
    main log upload function
    """
    if not verify_token(token):
        progress.set_text("Invalid token, please try again.")
        time.sleep(5)
        callback("BADTOKEN")
        return

    upload_logs(token, progress, callback)


def verify_token(token: str) -> bool:
    """
    verifies the token is valid
    """
    with requests.get("https://silverpelt.lvna.me/logtoken/" + token) as response:
        if response.status_code == 200:
            return True
        else:
            return False

def upload_logs(token: str, progress: UITextBoxTweaked, callback: callable):
    """
    actually uploads the logs
    """
    progress.set_text("Uploading logs...")

    logs = os.listdir(get_log_dir())
    files = {}

    for log in logs:
        with open(os.path.join(get_log_dir(), log), 'r') as f:
            files[log] = f.read()


    req = requests.post("https://silverpelt.lvna.me/logs/", data=ujson.dumps(files), headers={'Content-Type': 'application/json', 'token': token})

    if req.status_code == 200:
        progress.set_text("Logs uploaded successfully!")
    else:
        progress.set_text("Failed to upload logs, please try again.")

    time.sleep(5)
    callback("DONE")
