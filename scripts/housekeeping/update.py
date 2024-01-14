import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.parse
import zipfile
from enum import auto

import pgpy
import requests
from requests import Response
from strenum import StrEnum

from scripts.housekeeping.progress_bar_updater import UIUpdateProgressBar
from scripts.utility import quit
from scripts.housekeeping.version import get_version_info

use_proxy = False  # Set this to True if you want to use a proxy for the update check. Useful for debugging.


class UpdateChannel(StrEnum):
    STABLE = "stable"
    STABLE_TEST = "stable-test"
    DEVELOPMENT = "development"
    DEVELOPMENT_TEST = "development-test"


if use_proxy:
    proxies = {
        'http': 'http://127.0.0.1:8080',
        'https': 'http://127.0.0.1:8080',
    }
else:
    proxies = {}

latest_version = ""


def get_timeout() -> int:
    return 15


def configured_get_request(url: str, stream: bool = False) -> Response:
    return requests.get(url, stream=stream, proxies=proxies, verify=(not use_proxy), timeout=get_timeout())


def download_file(url: str):
    local_filename = url.split('/')[-1]
    os.makedirs('Downloads', exist_ok=True)
    with configured_get_request(url, stream=True) as response:
        response.raise_for_status()
        with open('Downloads/' + local_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    return 'Downloads/' + local_filename


def get_update_url():
    if get_update_url.value is None:
        fetch_url = "https://raw.githubusercontent.com/ClanGenOfficial/clangen/development/verification/update_api_url.txt"
        result = configured_get_request(fetch_url)
        get_update_url.value = result.text
    return get_update_url.value


get_update_url.value = None


def get_latest_version_number():
    global latest_version
    return latest_version


def has_update(update_channel: UpdateChannel):
    latest_endpoint = f"{get_update_url()}/v1/Update/Channels/{update_channel.value}/Releases/Latest"
    result = configured_get_request(latest_endpoint)

    result.raise_for_status()

    release_info = result.json()['release']
    latest_version_number = release_info['name']

    global latest_version
    latest_version = latest_version_number.strip()

    if get_version_info().version_number.strip() != latest_version_number.strip():
        print(f"Update available!")
        print(f"Current version: {get_version_info().version_number}")
        print(f"Newest version : {latest_version_number.strip()}")
        return True
    else:
        return False


def determine_platform_name() -> str:
    if platform.system() == 'Windows':
        if platform.architecture()[0][:2] == '32':
            return 'win32'
        elif platform.architecture()[0][:2] == '64':
            if platform.win32_ver()[0] == '10' or platform.win32_ver()[0] == '11':
                return 'win10+'
            else:
                return 'win64'
    elif platform.system() == 'Darwin':
        return 'macOS'
    elif platform.system() == 'Linux':
        if platform.libc_ver()[0] != 'glibc':
            raise RuntimeError()
        elif platform.libc_ver()[1] == '2.31':
            return 'linux2.31'
        elif platform.libc_ver()[1] == '2.35':
            return 'linux2.35'
        else:
            raise RuntimeError()

    raise RuntimeError()


def self_update(
        update_channel: UpdateChannel = UpdateChannel.DEVELOPMENT_TEST,
        progress_bar: UIUpdateProgressBar = None,
        announce_restart_callback: callable = None):
    print("Updating Clangen...")

    platform_name = determine_platform_name()

    response = configured_get_request(f"{get_update_url()}/v1/Update/Channels/{update_channel}/Releases/Latest/Artifacts/{platform_name}")

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

    download_file("https://raw.githubusercontent.com/ClanGenOfficial/clangen/development/verification/update_pubkey.asc")
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
        with zipfile.ZipFile("download.tmp") as zip_ref:
            zip_ref.extractall('Downloads')
        os.remove("download.tmp")
        shutil.copy("./Downloads/Clangen/resources/self_updater.exe", "./Downloads/self_updater.exe")
        announce_restart_callback()
        time.sleep(3)
        subprocess.Popen(
            ["./Downloads/self_updater.exe", "../"],
            cwd="./Downloads/",
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
        os._exit(1)
    elif platform.system() == 'Darwin':
        progress_bar.set_steps(11, "Installing update...")

        with zipfile.ZipFile("download.tmp") as zip_ref:
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

            if os.path.exists("/Applications/Clangen.app"):
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
        announce_restart_callback()
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
