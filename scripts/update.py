import os
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import zipfile
import platform

import pgpy
import requests as requests

from scripts.version import get_version_info


use_proxy = False # Set this to True if you want to use a proxy for the update check. Useful for debugging.


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


def has_update():
    latest_endpoint = "https://clangen-update-api-beta.archanyhm.dev/Update/Channels/development/Releases/Latest"
    result = requests.get(latest_endpoint, proxies=proxies, verify=(not use_proxy))

    release_info = result.json()['release']
    latest_version_number = release_info['name']

    if get_version_info().version_number.strip() != latest_version_number.strip():
        print(f"Update available!\nCurrent version: {get_version_info().version_number.strip()}\nNewest version : {latest_version_number.strip()}")
        return True
    else:
        return False
# a

def self_update(release_channel='development'):
    _ = {
        'Windows': [ 'win32', 'win64', 'win10+' ],
        'Linux': [ 'linux2.31', 'linux2.35' ],
        'Darwin': [ 'macOS' ]
    }
    artifact_name = _[platform.system()]
    if len(artifact_name) == 1:
        artifact_name = artifact_name[0]
    else:
        for name in artifact_name:
            print("TODO: Implement multi-arch support.")
    response = requests.get(f"https://clangen-update-api-beta.archanyhm.dev/Update/Channels/{release_channel}/Releases/Latest/Artifacts/{artifact_name}", proxies=proxies, verify=(not use_proxy))
    encoded_signature = response.headers['x-gpg-signature']

    with open("download.tmp", 'wb') as fd:
        for chunk in response.iter_content(chunk_size=128):
            fd.write(chunk)

    decoded_signature = urllib.parse.unquote(encoded_signature)

    better_signature = decoded_signature.replace("-----BEGIN+PGP+SIGNATURE-----", "-----BEGIN PGP SIGNATURE-----")
    better_signature = better_signature.replace("-----END+PGP+SIGNATURE-----", "-----END PGP SIGNATURE-----")

    download_file("https://raw.githubusercontent.com/archanyhm/clangen/auto-update/update_pubkey.asc")

    key, _ = pgpy.PGPKey.from_file("./Downloads/update_pubkey.asc")

    try:
        with open("./download.tmp", "rb") as fd:
            data = fd.read()
            signature = pgpy.PGPSignature.from_blob(better_signature)
            key.verify(data, signature)
        print("Signature check succeeded.")
    except pgpy.errors.PGPError:
        print("Signature mismatch.")
        return

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
    exit(0)
