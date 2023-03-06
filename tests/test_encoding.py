#!/usr/bin/env python3
# -*- coding: ascii -*-
"""This is not a unittest scripts so mybe this shouldn't be in /tests/...
Alternatively to Python, the 'file' command on linux can also check encoding.

This test isn't because we can't use utf-8 characters, but because we shouldn't
use them accidentally without explicitly setting the encoding.

Suggested commands to find the offending character:
file -i old_file.txt
iconv -cf utf-8 -t ascii -o old_file.txt new_file.txt
diff old_file.txt new_file.txt"""
import os
import sys
import difflib


def test():
    """Iterate through all files in 'resources'
    and verify all characters are ascii decodable."""
    output = ""
    for (root, _, files) in os.walk("."):
        for file in files:
            if file.endswith(".json") or file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as handle_utf8:
                    utf_read = handle_utf8.readlines()
                with open(path, "r", encoding="ascii", errors="replace") as handle_ascii:
                    ascii_read = handle_ascii.readlines()

                # Get difference
                result = difflib.context_diff(utf_read, ascii_read)
                if result:
                    tmp_output = ""
                    for diff in result:  # Exit if the reads differ
                        tmp_output += diff
                    if tmp_output:
                        output += f"\nFile {path} isn't ascii decodable!!\n"
                        output += tmp_output
    if output.strip():
        sys.exit(output)


if __name__ == "__main__":
    test()
