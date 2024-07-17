import json
import math
import re


def multiply_numbers_in_string(s, multiplier):
    # Function to replace matched number with the floored multiplied value
    def replace(match):
        number = float(match.group())
        multiplied = math.floor(number * multiplier)
        return str(multiplied)

    # Use regex to find all numbers in the string
    return re.sub(r"(?<![#0x])(?<![#0X])-?\b\d+\.?\d*\b", replace, s)


def multiply_numbers(data, multiplier):
    if isinstance(data, dict):
        result = {}
        blacklist = ["prototype", "line_spacing"]
        for key, value in data.items():
            if key in blacklist:
                result[key] = value
            else:
                result[key] = multiply_numbers(value, multiplier)
        return result
    elif isinstance(data, list):
        return [multiply_numbers(element, multiplier) for element in data]
    elif isinstance(data, str):
        return multiply_numbers_in_string(data, multiplier)
    return data


def generate_screen_scale(output_file, multiplier):
    with open("resources/theme/fonts/master_text_scale.json", "r") as readfile:
        data = json.load(readfile)

    modified_data = multiply_numbers(data, multiplier)

    with open(output_file, "w") as writefile:
        json.dump(modified_data, writefile, indent=4)
