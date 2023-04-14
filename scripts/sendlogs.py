from scripts.progress_bar_updater import UIUpdateProgressBar
from scripts.game_structure.image_button import UITextBoxTweaked
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
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
    return True
    with requests.get("https://bot.luna.clangen.io/logtoken/" + token) as response:
        if response.status_code == 200:
            return True
        else:
            return False

def upload_logs(token: str, progressbar: UIUpdateProgressBar, callback: callable):

    progressbar.set_steps(1, "Downloading update...", False, " MB", 1 / 1000 / 1000)
    progressbar.maximum_progress = 2
    
    logs = os.listdir(get_log_dir())
    files = {}
    logLength = []

    for log in logs:
        files[log] = open(get_log_dir() + "/" + log, "rb")

    encoder = MultipartEncoder(fields=files)
    def callbackf(monitor: MultipartEncoderMonitor):
        progressbar.progress = monitor.bytes_read

    monitor = MultipartEncoderMonitor(encoder, callbackf)
    progressbar.set_steps(1 / 1024, "Downloading update...", False, " MB", 1 / 1000 / 1000)
    progressbar.maximum_progress = int(monitor.len)

    req = requests.post("https://bot.luna.clangen.io/logs/", data=monitor, headers={'Content-Type': monitor.content_type, 'token': token})
    
    if req.status_code == 200:
        callback("SUCCESS")
    else:
        callback("ERROR")