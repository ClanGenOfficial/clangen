"""
Wrapper around the web platform to make it easier to work with
"""
# pylint: disable=no-member
import asyncio
import os
import platform
import shutil

from scripts.housekeeping.datadir import get_data_dir, get_save_dir

is_web = platform.system() == 'Emscripten'
class window:
    """
    Shim to get around the fact that the web platform doesn't have a filesystem
    """

    @staticmethod
    def get(key):
        """
        Get a key
        """
        if not is_web:
            return
        return platform.window[key]

    @staticmethod
    def set(key, value):
        """
        Set a key
        """
        if not is_web:
            return
        platform.window[key] = value

def reload():
    """
    Reload the window
    """
    if not is_web:
        return
    platform.window.location.reload()

def pushdb():
    """
    Push the filesystem to IndexedDB
    """
    if not is_web:
        return
    platform.window.FS.syncfs(False, platform.window.console.log)

def pulldb():
    """
    Pull the filesystem from IndexedDB
    """
    if not is_web:
        return
    platform.window.FS.syncfs(True, platform.window.console.log)

def evalWindow(code):
    """
    Evaluate code on the window
    """
    if not is_web:
        return
    platform.window.eval(code)

async def init_idbfs():
    """
    Load the idbfs type and mount it
    """
    if not is_web:
        return
    evalWindow("window.fs_loaded = false")
    with open("resources/idbfs.js", "r", encoding="utf-8") as f:
        evalWindow(f.read())

    evalWindow("""
    FS.mount(window.IDBFS, {'root': '.'}, '""" + get_data_dir() + """')
    FS.syncfs(true, (err) => {
        if (err) {console.log(err)}
        else {
            console.log('IndexedDB mounted and synced!')
            window.fs_loaded = true
        }
    })

    window.onbeforeunload = async ()=>{
        FS.syncfs(false, (err) => {console.log(err)})
    }
    """)

    while window.get("fs_loaded") is False:
        print("Waiting for fs to load...")
        await asyncio.sleep(0.1)

def migrate_localstorage():
    """
    Migrate legacy web saves to IndexedDB
    """
    if platform.window.localStorage.getItem("hasMigrated") is None:
        print("Migrating from localStorage to IndexedDB")

        for i in range(platform.window.localStorage.length):
            key = platform.window.localStorage.key(i)
            value = platform.window.localStorage.getItem(key)

            if key in ['hasMigrated', '/', 'currentclan', 'clanlist.txt', '__test__']:
                continue
            os.makedirs(os.path.dirname(f"{get_save_dir()}/{key}"), exist_ok=True)
            with open(f"{get_save_dir()}/{key}", "w", encoding="utf-8") as f:
                f.write(value)
        platform.window.localStorage.setItem("hasMigrated", "true")

        pushdb()
        print("Migration complete!")

def freeMemory():
    """
    Removes all files in /tmp and /data/data/clangen/assets except for required game files
    """
    whitelisted_files = [
        'main.py',
        'changelog.txt',
        'version.ini',
        'sprites',
        'scripts',
        'resources',
        'languages',
    ]
    if not is_web:
        return
    for file in os.listdir('/tmp'):
        os.remove('/tmp/' + file)

    for file in os.listdir('.'):
        if file in whitelisted_files:
            continue
        if os.path.isdir(file):
            shutil.rmtree(file)
        else:
            os.remove(file)

def setDownloadLogsCallback(callback):
    """
    Sets a callback to download logs
    """
    if not is_web:
        return
    platform.window.downloadLogsCallback = callback

def error(e):
    """Displays an error message to the loader"""
    print(e)
    if not is_web:
        return
    try:
        platform.window.gameError(str(e))
    except Exception as e:
        print(e)

def notifyFinishLoading():
    """Notifies the loader that the game has finished loading"""
    if not is_web:
        return
    try:
        platform.window.gameReady()
    except Exception as e:
        print(e)

async def promiseToAsync(promise):
    """
    Converts a promise to an async function
    """
    def then(f):
        nonlocal result
        result = f
    result = None
    promise.then(then)

    while result is None:
        await asyncio.sleep(0.1)
    return result

def uploadFile(filename):
    if not is_web:
        return
    platform.window.MM.download(filename)

async def downloadFile(filename, accept = None):
    if not is_web:
        return
    newFileName = await promiseToAsync(platform.window.files.upload(filename, accept))
    
    return newFileName

def closeGracefully():
    if not is_web:
        return
    platform.window.closeGracefully()