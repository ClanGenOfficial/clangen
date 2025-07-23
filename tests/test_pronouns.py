"""

 Please do not put this *unittest* in the tests/unittest GitHub action.
HOWEVER,
 Please keep the raw python script and the unittest, so it can be run by the tests/pronoun_test GitHub action.

This test checks that pronoun tags are formated correctly, 

"""

import os
import re
import sys
import unittest
import ujson


os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat.cats import Cat
from scripts.game_structure.localization import get_new_pronouns
from scripts.utility import process_text


def _test():
    """Iterate through all files in 'resources'
    and verify that any detected pronoun tags are
    formatted correctly."""
    failed = False
    failed_files = []

    # Note - we are replacing with a singular-conjugated pronoun,
    # to ensure that we are catching cases where only one verb conjugation
    # was provided - since singular-conjugation
    # should be the second provided conjugation.
    _r = ("Name", get_new_pronouns("female")[0])
    replacement_dict = {
        "m_c": _r,
        "r_c": _r,
        "r_c1": _r,
        "r_c2": _r,
        "n_c": _r,
        "app1": _r,
        "app2": _r,
        "app3": _r,
        "app4": _r,
        "app5": _r,
        "app6": _r,
        "p_l": _r,
        "s_c": _r,
        "(mentor)": _r,
        "l_n": _r,
        "dead_par1": _r,
        "dead_par2": _r,
        "p1": _r,
        "p2": _r,
        "(deadmentor)": _r,
        "(previous_mentor)": _r,
        "mur_c": _r,
        "c_n": _r,
        "o_c_n": _r,
        "lead_name": _r,
        "dep_name": _r,
        "med_name": _r,
        "cat_tag": _r,
    }

    for x in range(0, 11):
        replacement_dict[f"n_c:{x}"] = _r

    for root, _, files in os.walk("resources"):
        for file in files:
            if file.endswith(".json") and file not in (
                "credits_text.json",
                "clansettings.json",
                "gamesettings.json",
            ):
                path = os.path.join(root, file)

                if not _test_replacement_failure(path, replacement_dict):
                    failed = True
                    failed_files.append(path)

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


def _test_replacement_failure(path: str, repl_dict: dict) -> bool:
    """Reads in a file, and finds strings, and runs pronoun replacment on those strings.
    Returns False if there were any issues with the pronoun replacement, or if the
    json is incorrectly formatted."""

    success = True
    with open(path, "r", encoding="utf-8") as file:
        try:
            contents = ujson.loads(file.read())
        except ujson.JSONDecodeError as _e:
            print(f"::error file={path}::File {path} is invalid json")
            print(_e)
            return False

    for _str in get_all_strings(contents):
        try:
            processed = process_text(
                text=_str, cat_dict=repl_dict, raise_exception=True
            )
        except (KeyError, IndexError) as _e:
            print(
                f'::error file={path}: "{_str}" contains invalid pronoun or verb tags.'
            )
            print(_e)
            success = False
        else:
            # This tests for any pronoun or verb tag fragments that might have
            # snuck through. This is most likely caused by using the incorrect type of
            # brackets
            if re.search(r"\{PRONOUN|\(PRONOUN|\{VERB|\(VERB|\{ADJ|\(ADJ", processed):
                print(
                    f'::error file={path}: "{_str}" contains pronoun tag fragments after replacment'
                )
                success = False

            # This tests for any pronoun or verb that is incorrectly capitalized
            # excludes ellipses (i.e. ... and . . .) but includes regular colons
            # includes ? and ! always (e.g. "...!" is included).
            # DOES NOT check the start of the string for capitalization
            elif (
                re.search(r"(?<!\.\.)(?<!\.\s\.\s)\.\s+[a-z]", processed) is not None
                or re.search(r"[?!]\s+[a-z]", processed) is not None
            ):
                print(f'::error file={path}: Capitalization errors in "{_str}"')
                success = False

    return success


def get_all_strings(data):
    """Will take any combination of list and dicts,
    and extract all strings, including dictionary keys.
    Recursive."""

    all_strings = []

    if isinstance(data, list):
        for _x in data:
            all_strings.extend(get_all_strings(_x))
    elif isinstance(data, dict):
        for _x in data:
            all_strings.extend(get_all_strings(data[_x]))
            all_strings.extend(get_all_strings(_x))

    elif isinstance(data, str):
        all_strings.append(data)

    return all_strings


class TestPronouns(unittest.TestCase):
    """Test for some common pronoun tagging errors in resources"""

    def test_pronouns(self):
        """Test that all files are ascii decodable."""
        with self.assertRaises(SystemExit) as cm:
            _test()
        self.assertEqual(cm.exception.code, 0)
