import os
import shutil
import subprocess
import zipfile

import requests as requests


def download_file(url):
    local_filename = url.split('/')[-1]
    os.makedirs('Downloads', exist_ok=True)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open('Downloads/' + local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return 'Downloads/' + local_filename


def has_update(version_number):
    action_url = "https://api.github.com/repos/archanyhm/clangen/actions/artifacts"
    result = requests.get(action_url)

    artifacts = result.json()['artifacts']

    for artifact in artifacts:
        run = artifact['workflow_run']

        if artifact['name'] != 'Clangen_macOS64.dmg':
            continue

        if run['head_branch'] != 'auto-update':
            continue

        if run['head_sha'].startswith(version_number) or version_number.startswith(run['head_sha']):
            return False
        else:
            return True


def fetch_latest_dev():
    zip_path = download_file("https://nightly.link/Thlumyn/clangen/workflows/build/development/Clangen_macOS64.dmg.zip")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall('Downloads')
    os.remove(zip_path)

    os.makedirs('Downloads/macOS_tempmount', exist_ok=True)
    os.system('hdiutil attach -nobrowse -mountpoint Downloads/macOS_tempmount Downloads/Clangen_macOS64.dmg')
    shutil.rmtree('/Applications/Clangen.app', ignore_errors=True)
    shutil.copytree('Downloads/macOS_tempmount/Clangen.app', '/Applications/Clangen.app')
    os.system('hdiutil detach Downloads/macOS_tempmount')


def get_version_info():
    if os.path.exists("commit.txt"):
        with open(f"commit.txt", 'r') as read_file:
            print("Running on pyinstaller build")
            VERSION_NUMBER = read_file.read()
            binary_release = True
    else:
        print("Running on source code")
        try:
            VERSION_NUMBER = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
        except:
            print("Failed to get git commit hash, using hardcoded version number instead.")
            print(
                "Hey testers! We recommend you use git to clone the repository, as it makes things easier for everyone.")
            print(
                "There are instructions at https://discord.com/channels/1003759225522110524/1054942461178421289/1078170877117616169")
    print("Running on commit " + VERSION_NUMBER)

    return VersionInfo(VERSION_NUMBER, os.path.exists("commit.txt"))


class VersionInfo:
    def __init__(self, version_number, is_binary):
        self.version_number = version_number
        self.is_binary = is_binary