import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse
import zipfile
import tarfile
import platform
import pathlib

import pgpy
import requests as requests

from scripts.game_structure.image_button import UITextBoxTweaked
from scripts.progress_bar_updater import UIUpdateProgressBar
from scripts.utility import quit
from scripts.version import get_version_info




use_proxy = False  # Set this to True if you want to use a proxy for the update check. Useful for debugging.

if use_proxy:
    proxies = {
        'http': 'http://127.0.0.1:8080',
        'https': 'http://127.0.0.1:8080',
    }
else:
    proxies = {}


def download_file(url):
    local_filename = url.split('/')[-1]
    os.makedirs('Downloads', exist_ok=True)
    with requests.get(url, stream=True, proxies=proxies, verify=(not use_proxy)) as r:
        r.raise_for_status()
        with open('Downloads/' + local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return 'Downloads/' + local_filename


def get_update_url():
    if get_update_url.value is None:
        fetch_url = "https://raw.githubusercontent.com/archanyhm/clangen/auto-update/verification/update_api_url.txt"
        result = requests.get(fetch_url)
        get_update_url.value = result.text
    return get_update_url.value


get_update_url.value = None

def has_update():
    latest_endpoint = f"{get_update_url()}/v1/Update/Channels/development-test/Releases/Latest"
    result = requests.get(latest_endpoint, proxies=proxies, verify=(not use_proxy))

    release_info = result.json()['release']
    latest_version_number = release_info['name']

    if get_version_info().version_number.strip() != latest_version_number.strip():
        print(
            f"Update available!\nCurrent version: {get_version_info().version_number}\nNewest version : {latest_version_number.strip()}")
        return True
    else:
        return False


def self_update(release_channel='development-test', progress_bar: UIUpdateProgressBar = None, progress_text: UITextBoxTweaked = None, asdf = None):
    print("Updating Clangen...")
    if platform.system() == 'Windows':
        if platform.architecture()[0][:2] == '32':
            artifact_name = 'win32'
        elif platform.architecture()[0][:2] == '64':
            artifact_name = 'win64'
            # if platform.win32_ver()[0] == '10' or platform.win32_ver()[0] == '11':
            #     artifact_name = 'win10+'
    elif platform.system() == 'Darwin':
        artifact_name = 'macOS'
    elif platform.system() == 'Linux':
        if platform.libc_ver()[0] != 'glibc':
            print("Unsupported libc.")
            return
        elif platform.libc_ver()[1] == '2.31':
            artifact_name = 'linux2.31'
        elif platform.libc_ver()[1] == '2.35':
            artifact_name = 'linux2.35'
        else:
            print("Unsupported libc version.")
            return

    response = requests.get(
        f"{get_update_url()}/v1/Update/Channels/{release_channel}/Releases/Latest/Artifacts/{artifact_name}",
        proxies=proxies, verify=(not use_proxy))
    encoded_signature = response.headers['x-gpg-signature']

    print("Verifying...")

    length = response.headers.get('Content-Length')

    progress_bar.set_steps(int(length) / 1024, "Downloading update...", False, " MB", 1 / 1000 / 1000)
    progress_bar.maximum_progress = int(length)

    with open("download.tmp", 'wb') as fd:
        for chunk in response.iter_content(chunk_size=1024):
            fd.write(chunk)
            progress_bar.advance()

    progress_bar.set_steps(9, "Verifying update...")

    decoded_signature = urllib.parse.unquote(encoded_signature)
    progress_bar.advance()

    better_signature = decoded_signature.replace("-----BEGIN+PGP+SIGNATURE-----", "-----BEGIN PGP SIGNATURE-----")
    progress_bar.advance()

    better_signature = better_signature.replace("-----END+PGP+SIGNATURE-----", "-----END PGP SIGNATURE-----")
    progress_bar.advance()

    download_file("https://raw.githubusercontent.com/archanyhm/clangen/auto-update/verification/update_pubkey.asc")
    progress_bar.advance()

    key, _ = pgpy.PGPKey.from_file("./Downloads/update_pubkey.asc")
    progress_bar.advance()

    try:
        with open("./download.tmp", "rb") as fd:
            progress_bar.advance()

            data = fd.read()
            progress_bar.advance()

            signature = pgpy.PGPSignature.from_blob(better_signature)
            progress_bar.advance()

            key.verify(data, signature)
            progress_bar.advance()
        print("Signature check succeeded.")
    except pgpy.errors.PGPError:
        print("Signature mismatch.")
        return

    print('Installing...')

    if platform.system() == 'Windows':
        # pwsh = ''
        # if shutil.which('pwsh') is not None:
        #     pwsh = shutil.which('pwsh')
        # elif shutil.which('powershell') is not None:
        #     pwsh = shutil.which('powershell')
        # else:
        #     print("Powershell not found. Please install it and try again")
        #     return
        with zipfile.ZipFile("download.tmp", 'r') as zip_ref:
            zip_ref.extractall('Downloads')
        os.remove("download.tmp")

        path = pathlib.Path(os.getcwd()).parent.absolute()

        # shutil.copy("resources/update.ps1", "../clangen_update_script.ps1")
        # print("Clangen python application cannot continue to run while it is being updated.")
        # print("Powershell will now be used to update Clangen.")
        # print("A console window will open and close automatically. Please do not be alarmed.")

        #subprocess.Popen("./winupdate.exe", cwd=os.getcwd(), close_fds=True, creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_BREAKAWAY_FROM_JOB)

        shutil.copy("./Downloads/Clangen/self_updater.exe", "./Downloads/self_updater.exe")
        asdf()
        time.sleep(3)
        subprocess.Popen(["./Downloads/self_updater.exe", "../"], cwd="./Downloads/", close_fds=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        os._exit(1)

    elif platform.system() == 'Darwin':
        progress_bar.set_steps(11, "Installing update...")

        with zipfile.ZipFile("download.tmp", 'r') as zip_ref:
            progress_bar.advance()

            zip_ref.extractall('Downloads')
            progress_bar.advance()

        os.remove("download.tmp")
        progress_bar.advance()

        with tempfile.TemporaryDirectory() as mountdir:
            progress_bar.advance()

            os.system(f'hdiutil attach -nobrowse -mountpoint {mountdir} Downloads/Clangen_macOS64.dmg')
            progress_bar.advance()

            shutil.rmtree('/Applications/Clangen.app.old', ignore_errors=True)
            progress_bar.advance()

            shutil.move('/Applications/Clangen.app', '/Applications/Clangen.app.old')
            progress_bar.advance()

            shutil.copytree(f'{mountdir}/Clangen.app', '/Applications/Clangen.app')
            progress_bar.advance()

            shutil.rmtree('Downloads', ignore_errors=True)
            progress_bar.advance()

            os.system(f'hdiutil detach {mountdir}')
            progress_bar.advance()

            os.rmdir(mountdir)
            progress_bar.advance()
        asdf()
        time.sleep(3)
        os.execv('/Applications/Clangen.app/Contents/MacOS/Clangen', sys.argv)
        quit()

    elif platform.system() == 'Linux':
        current_folder = os.getcwd()
        with tarfile.open("download.tmp", 'r') as tar_ref:
            tar_ref.extractall('Downloads')
        os.remove("download.tmp")
        shutil.move("Downloads/Clangen", "../clangen_update")
        shutil.rmtree(current_folder, ignore_errors=True)
        shutil.move("../clangen_update", current_folder)
        os.chmod(current_folder + "/Clangen", 0o755)
        os.execv(current_folder + "/Clangen", sys.argv)
        quit()
