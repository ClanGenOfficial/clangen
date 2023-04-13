from scripts.progress_bar_updater import UIUpdateProgressBar
from scripts.game_structure.image_button import UITextBoxTweaked
import requests
import os
from scripts.datadir import get_log_dir

def send_logs(token: str, progressbar: UIUpdateProgressBar, callback: callable):
    progressbar.set_steps(100, "Verifying Token...", False, "%", 1)
    if not verify_token(token):
        callback("BADTOKEN")
        return
    progressbar.set_steps(100, "Sending Log 1...", False, "%", 1)
    
    upload_logs(token, progressbar, callback)


def verify_token(token: str) -> bool:
    with requests.get("https://bot.luna.clangen.io/logtoken/" + token) as response:
        if response.status_code == 200:
            return True
        else:
            return False

def upload_logs(token: str, progressbar: UIUpdateProgressBar, callback: callable):
    
    logs = os.listdir(get_log_dir())
    files = []
    logLength = []
    for i in range(len(logs)):
        progressbar.set_steps(100, "Sending Log " + str(i + 1) + "...", False, "%", 1)
        
        files.push( ( "file", open(get_log_dir() + "/" + logs[i], "rb") ) )
        