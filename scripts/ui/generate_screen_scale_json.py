import json
import math
import os
import re


def _multiply_numbers_in_string(s, multiplier):
    # Function to replace matched number with the floored multiplied value
    def replace(match):
        number = float(match.group())
        multiplied = math.floor(number * multiplier)
        return str(multiplied)

    # Use regex to find all numbers in the string
    return re.sub(r"(?<![#0x])(?<![#0X])-?\b\d+\.?\d*\b", replace, s)


def _multiply_numbers(data, multiplier):
    if isinstance(data, dict):
        result = {}
        blacklist = ["prototype", "line_spacing", "colours"]
        for key, value in data.items():
            if key in blacklist:
                result[key] = value
            else:
                result[key] = _multiply_numbers(value, multiplier)
        return result
    elif isinstance(data, list):
        return [_multiply_numbers(element, multiplier) for element in data]
    elif isinstance(data, str):
        return _multiply_numbers_in_string(data, multiplier)
    return data


def generate_screen_scale(input_file, output_file, multiplier):
    with open(input_file, "r") as readfile:
        data = json.load(readfile)

    modified_data = _multiply_numbers(data, multiplier)

    if not os.path.exists(output_file):
        from pathlib import Path

        p = Path(output_file)
        os.makedirs(p.parent)
    with open(os.path.abspath(output_file), "w") as writefile:
        json.dump(modified_data, writefile, indent=4)
