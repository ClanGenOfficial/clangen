import os
import shutil
import subprocess
import sys
import urllib.parse
import zipfile
import tarfile
import platform

import pgpy
import requests as requests

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
        fetch_url = "https://raw.githubusercontent.com/archanyhm/clangen/auto-update/update_api_url.txt"
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


def self_update(release_channel='development-test'):

    print("Updating Clangen...")
    if platform.system() == 'Windows':
        if platform.architecture()[0][:2] == '32':
            artifact_name = 'win32'
        elif platform.architecture()[0][:2] == '64':
            artifact_name = 'win64'
            if platform.win32_ver()[0] == '10':
                artifact_name = 'win64_win10+'
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

    with open("download.tmp", 'wb') as fd:
        for chunk in response.iter_content(chunk_size=128):
            fd.write(chunk)

    decoded_signature = urllib.parse.unquote(encoded_signature)

    better_signature = decoded_signature.replace("-----BEGIN+PGP+SIGNATURE-----", "-----BEGIN PGP SIGNATURE-----")
    better_signature = better_signature.replace("-----END+PGP+SIGNATURE-----", "-----END PGP SIGNATURE-----")

    download_file("https://raw.githubusercontent.com/archanyhm/clangen/auto-update/update_pubkey.asc")

    key, _ = pgpy.PGPKey.from_file("./Downloads/update_pubkey.asc")

    # try:
    #     with open("./download.tmp", "rb") as fd:
    #         data = fd.read()
    #         signature = pgpy.PGPSignature.from_blob(better_signature)
    #         key.verify(data, signature)
    #     print("Signature check succeeded.")
    # except pgpy.errors.PGPError:
    #     print("Signature mismatch.")
    #     return

    print('Installing...')

    if platform.system() == 'Windows':
        pwsh = ''
        if shutil.which('pwsh') is not None:
            pwsh = shutil.which('pwsh')
        elif shutil.which('powershell') is not None:
            pwsh = shutil.which('powershell')
        else:
            print("Powershell not found. Please install it and try again")
            return
        with zipfile.ZipFile("download.tmp", 'r') as zip_ref:
            zip_ref.extractall('Downloads')
        os.remove("download.tmp")
        
        shutil.move("Downloads/Clangen", "../clangen_update")

        shutil.copy("resources/update.ps1", "../clangen_update_script.ps1")
        print("Clangen python application cannot continue to run while it is being updated.")
        print("Powershell will now be used to update Clangen.")
        print("A console window will open and close automatically. Please do not be alarmed.")

        print(" ".join([pwsh, "-ExecutionPolicy", "Bypass", "-File", "../clangen_update_script.ps1", "internal", os.getcwd()]))
        exit()
        subprocess.Popen([pwsh, "-ExecutionPolicy", "Bypass", "-File", "../clangen_update_script.ps1", "internal", os.getcwd()])

    elif platform.system() == 'Darwin':
        with zipfile.ZipFile("download.tmp", 'r') as zip_ref:
            zip_ref.extractall('Downloads')
        os.remove("download.tmp")

        os.makedirs('Downloads/macOS_tempmount', exist_ok=True)
        os.system('hdiutil attach -nobrowse -mountpoint Downloads/macOS_tempmount Downloads/Clangen_macOS64.dmg')
        shutil.rmtree('/Applications/Clangen.app.old', ignore_errors=True)
        shutil.move('/Applications/Clangen.app', '/Applications/Clangen.app.old')
        shutil.copytree('Downloads/macOS_tempmount/Clangen.app', '/Applications/Clangen.app')
        os.system('hdiutil detach Downloads/macOS_tempmount')
        shutil.rmtree('Downloads', ignore_errors=True)
        os.execv('/Applications/Clangen.app/Contents/MacOS/Clangen', sys.argv)

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
    exit(0)
