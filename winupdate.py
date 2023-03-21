import os
import shutil
import time

time.sleep(5)

for filename in os.listdir('./'):
    if filename.endswith("winupdate.exe") or filename.endswith("winupdate") or filename.endswith("Downloads"):
        continue

    if os.path.isfile(filename) or os.path.islink(filename):
        os.remove(filename)
    else:
        shutil.rmtree(filename)

for filename in os.listdir("Downloads/Clangen"):
    if filename.endswith("winupdate") or filename.endswith("winupdate.exe"):
        continue

    if os.path.isfile(f"Downloads/Clangen/{filename}") or os.path.islink(f"Downloads/Clangen/{filename}"):
        shutil.copy(f"Downloads/Clangen/{filename}", "./")
    else:
        shutil.copytree(f"Downloads/Clangen/{filename}", "./", dirs_exist_ok=True)

shutil.rmtree("Downloads")