import os

import ujson
from shutil import move as shutil_move

from scripts.housekeeping.datadir import get_temp_dir


def safe_save(path: str, write_data, check_integrity=False, max_attempts: int = 15):
    """If write_data is not a string, assumes you want this
    in json format. If check_integrity is true, it will read back the file
    to check that the correct data has been written to the file.
    If not, it will simply write the data to the file with no other
    checks."""

    # If write_data is not a string,
    if type(write_data) is not str:
        _data = ujson.dumps(write_data, indent=4)
    else:
        _data = write_data

    dir_name, file_name = os.path.split(path)

    if check_integrity:
        if not file_name:
            raise RuntimeError(f"Safe_Save: No file name was found in {path}")

        temp_file_path = get_temp_dir() + "/" + file_name + ".tmp"
        i = 0
        while True:
            # Attempt to write to temp file
            with open(temp_file_path, "w", encoding="utf-8") as write_file:
                write_file.write(_data)
                write_file.flush()
                os.fsync(write_file.fileno())

            # Read the entire file back in
            with open(temp_file_path, "r", encoding="utf-8") as read_file:
                _read_data = read_file.read()

            if _data != _read_data:
                i += 1
                if i > max_attempts:
                    print(
                        f"Safe_Save ERROR: {file_name} was unable to properly save {i} times. Saving Failed."
                    )
                    raise RuntimeError(
                        f"Safe_Save: {file_name} was unable to properly save {i} times!"
                    )
                print(f"Safe_Save: {file_name} was incorrectly saved. Trying again.")
                continue

            # This section is reached is the file was not nullied. Move the file and return True

            shutil_move(temp_file_path, path)
            return
    else:
        os.makedirs(dir_name, exist_ok=True)
        with open(path, "w", encoding="utf-8") as write_file:
            write_file.write(_data)
            write_file.flush()
            os.fsync(write_file.fileno())
