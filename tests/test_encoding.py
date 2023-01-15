#!/usr/bin/env python3
"""This is not a unittest scripts so mybe this shouldn't be in /tests/...
Alternatively to Python, the 'file' command on linux can also check encoding.

This test isn't because we can't use utf-8 characters, but because we shouldn't
use them accidentally without explicitly setting the encoding.

Suggested commands to find the offending character:
file -i file.txt
iconv -cf utf-8 -t ascii -o old_file.txt new_file.txt
diff old_file.txt new_file.txt"""
import os
import sys


def test():
    """Iterate through all files in 'resources'
    and verify all characters are ascii decodable."""
    for (root, _, files) in os.walk("."):
        for file in files:
            if file.endswith(".json") or file.endswith(".py"):
                path = os.path.join(root, file)

                with open(path, "r", encoding="utf-8") as handle_utf8:
                    utf_read = handle_utf8.read()

                with open(path, "r", encoding="ascii") as handle_ascii:
                    ascii_read = ""
                    for _ in range(len(utf_read)):
                        try:
                            ascii_read += handle_ascii.read(1)
                        except UnicodeDecodeError:
                            line = ascii_read.count("\n")
                            ascii_len = len(ascii_read)
                            snippet = ascii_read[ascii_len - 20 : ascii_len + 20]
                            sys.exit(f"Failed decode line {line} of {path}\n"
                                     f"Last valid snippet: \"{ascii_read[-50:]}\"")

                print(f"VALID: {path}")


if __name__ == "__main__":
    test()
    print("Done, woo yeah woo yeah")
