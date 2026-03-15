import os, re

import ujson


# CHANGE THIS TO MAKE NEW LANGUAGE
lang = "debug"


def process_json_file(input_path, output_path, lang):
    with open(input_path, "r", encoding="utf-8") as file:
        data = ujson.load(file)

    if "en" in data:
        if lang == "debug":
            data = recursive_potatofy(data)
        data = {lang: data["en"]}
    else:
        data = data

    with open(output_path, "w", encoding="utf-8") as file:
        ujson.dump(data, file, indent=4)


pattern = re.compile(r"%{[^}]+}|[^%]+|%")


def recursive_potatofy(debug_data):
    """
    Recursively replace any non-variable words with the word "potato".
    Replace variable words with the variable name and then the unchanged variable
    :param debug_data:
    :return:
    """
    if isinstance(debug_data, dict):
        return {k: recursive_potatofy(v) for k, v in debug_data.items()}
    else:
        return debug_potatofy(debug_data) if isinstance(debug_data, str) else debug_data


def debug_potatofy(text: str) -> str:
    out = []

    for m in pattern.finditer(text):
        s = m.group(0)
        if s.startswith("%{"):
            bare = s.removeprefix("%{").removesuffix("}")
            out.append(bare + ": " + s + ",")
    if not out:
        out.append("potato")
    else:
        out[-1] = out[-1].removesuffix(",")

    return " ".join(out).strip()


# Folder setup
file_dir = os.path.dirname(os.path.realpath("__file__"))


input_folder = os.path.join(file_dir, "en")
output_folder = os.path.join(file_dir, lang)

os.makedirs(output_folder, exist_ok=True)

for root, _, files in os.walk(input_folder):
    relative_path = os.path.relpath(root, input_folder)
    target_folder = os.path.join(output_folder, relative_path)
    os.makedirs(target_folder, exist_ok=True)

    for filename in files:
        if filename.endswith(".json"):
            if ".en." in filename:
                # Rename the file by replacing "en" with "po"
                new_filename = filename.replace(".en", f".{lang}")
                input_path = os.path.join(root, filename)
                output_path = os.path.join(target_folder, new_filename)
            else:
                input_path = os.path.join(root, filename)
                output_path = os.path.join(target_folder, filename)

            process_json_file(input_path, output_path, lang)

print("All JSON files processed!")
