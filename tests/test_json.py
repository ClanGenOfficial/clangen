#!/usr/bin/env python3
# -*- coding: ascii -*-
"""

 Please do not put this *unittest* in the tests/unittest GitHub action.
 It is only for local use.
HOWEVER,
 Please keep the raw python script, so it can be run by the tests/encoding_test GitHub action.

"""
import os
import sys
import unittest

import ujson


def test():
    """Iterate through all files in 'resources'
    and verify all json files are valid"""
    failed = False
    for (root, _, files) in os.walk("./resources"):
        for file in files:
            if file.endswith(".json"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as file:
                    try:
                        contents = file.read()
                    except UnicodeDecodeError as e:
                        print(f"::error file={path}::File {path} is not utf-8 encoded")
                        print(e)
                        failed = True
                        continue

                try:
                    _ = ujson.loads(contents)
                except ujson.JSONDecodeError as e:
                    print(f"::error file={path}::File {path} is invalid json")
                    print(e)
                    failed = True
                    pass

    if failed:
        sys.exit(1)
    sys.exit(0)


# THE UNITTEST IS ONLY FOR LOCAL USE
# PLEASE DO NOT PUT THIS IN THE GITHUB ACTION
class TestJsonValidity(unittest.TestCase):
    """Test that all files are json decodable."""

    def test_encoding(self):
        """Test that all files are json decodable."""
        with self.assertRaises(SystemExit) as cm:
            test()
        self.assertEqual(cm.exception.code, 0)


if __name__ == "__main__":
    test()
