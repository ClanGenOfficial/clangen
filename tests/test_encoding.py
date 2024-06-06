#!/usr/bin/env python3
# -*- coding: ascii -*-
"""

 Please do not put this *unittest* in the tests/unittest GitHub action.
 It is only for local use.
HOWEVER,
 Please keep the raw python script, so it can be run by the tests/encoding_test GitHub action.

Alternatively to Python, the 'file' command on linux can also check encoding.

This test isn't because we can't use utf-8 characters, but because we shouldn't
use them accidentally without explicitly setting the encoding.

Suggested commands to find the offending character:
file -i old_file.txt
iconv -cf utf-8 -t ascii -o old_file.txt new_file.txt
diff old_file.txt new_file.txt"""
import difflib
import os
import sys
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"


def test():
    """Iterate through all files in 'resources'
    and verify all characters are ascii decodable."""
    failed = False
    failed_files = []
    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".json") or file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as handle_utf8:
                    utf_read = handle_utf8.readlines()
                with open(
                    path, "r", encoding="ascii", errors="replace"
                ) as handle_ascii:
                    ascii_read = handle_ascii.readlines()

                # Get difference
                result = difflib.context_diff(utf_read, ascii_read)
                if result:
                    tmp_output = ""
                    for diff in result:  # Exit if the reads differ
                        tmp_output += diff
                    if tmp_output:
                        failed = True
                        failed_files.append(path)
                        print(
                            f"::error file={path}::File {path} contains non-ascii characters"
                        )
                        print(f"::group::Diff of {path}")
                        print(tmp_output)
                        print("::endgroup::")

    if failed:
        # Set the GITHUB_OUTPUT environment variable to the list of failed files
        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ["GITHUB_OUTPUT"], "a") as handle:
                print(f"files={':'.join(failed_files)}", file=handle)
        else:
            print(f"files={':'.join(failed_files)}")
        sys.exit(1)
    else:
        sys.exit(0)


# THE UNITTEST IS ONLY FOR LOCAL USE
# PLEASE DO NOT PUT THIS IN THE GITHUB ACTION
class TestEncoding(unittest.TestCase):
    """Test that all files are ascii decodable."""

    def test_encoding(self):
        """Test that all files are ascii decodable."""
        with self.assertRaises(SystemExit) as cm:
            test()
        self.assertEqual(cm.exception.code, 0)


def fix():

    skipped = True

    # files = ['./resources/buttons_small.json']
    files = os.environ["FILES"].split(":")

    replace = {
        "\\u2026": "...",  # ellipsis but not the same as ...
        "\\u00F1": "n",  # n with tilde
        # PLEASE TELL LUNA WHEN YOU FIND MORE THAT BREAK IT
    }

    for file in files:
        with open(file, "r", encoding="utf-8") as handle:
            content = handle.read()

        for key, value in replace.items():
            oldkey = key
            key = bytes(key, "ascii").decode("unicode-escape")
            if key in content:
                skipped = False
                content = content.replace(key, value)
                print(f"Replacing {oldkey}({key}) with {value} in {file}")

                with open(file, "w", encoding="utf-8") as handle:
                    handle.write(content)

    if skipped:
        sys.exit(1)  # fail so we tell the runner not to make an empty pr
    sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] == "test":
            test()
        elif sys.argv[1] == "fix":
            fix()
        else:
            print("Unknown argument. Use 'test' or 'fix'. Running 'test' instead.")
            test()
    else:
        test()
