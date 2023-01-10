#!/usr/bin/env python3
"""This is not a unittest scripts so mybe this shouldn't be in /tests/...
Alternatively to Python, the 'file' command on linux can also check encoding."""
import os


def test():
    """Iterate through all files in 'resources'
    and verify all characters are ascii decodable."""
    for (root, _, files) in os.walk("resources"):
        for file in files:
            if file.endswith(".json"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="ascii") as file_handle:
                    file_handle.read()
                print(f"VALID: {path}")


if __name__ == "__main__":
    test()
    print("Done, woo yeah woo yeah")
