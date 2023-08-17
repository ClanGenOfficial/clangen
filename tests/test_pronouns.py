"""

 Please dont put this *unittest* in the tests/unittest github action.
HOWEVER
 Please keep the raw python script and the unittest, so it can be run by the tests/pronoun_test github action.

This test checks that pronoun tags are formated correctly, 

"""
import os
import sys
import ujson
import unittest
from scripts.cat.cats import Cat
from scripts.utility import process_text
import re

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

def test():
    """Iterate through all files in 'resources'
    and verify that any detected pronoun tags are 
    formatted correctly."""
    failed = False
    failedFiles = []
    
    # Note - we are replacing with a singular-conjugated pronoun,
    # to ensure that we are catching cases where only one verb conjugation
    # was provided - since singular-conjugation
    # should be the second provided conjugation. 
    _r = ("name", Cat.default_pronouns[1])
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
        "mur_c": _r
    }
    
    for x in range(0, 11):
        replacement_dict[f"n_c:{x}"] = _r
    
    for (root, _, files) in os.walk("resources"):
        for file in files:
            if file.endswith(".json") and file != "credits_text.json":
                path = os.path.join(root, file)
                
                if not test_replacement_failure(path, replacement_dict):
                    failed = True
                    failedFiles.append(path)
                
    if failed:
        # Set the GITHUB_OUTPUT environment variable to the list of failed files
        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ["GITHUB_OUTPUT"], "a") as handle:
                print(f"files={':'.join(failedFiles)}", file=handle)
        else:
            print(f"files={':'.join(failedFiles)}")
        sys.exit(1)
    else:
        sys.exit(0)



def test_replacement_failure(path: str, repl_dict: dict) -> bool:
    """ Reads in a file, and finds strings, and runs pronoun replacment on those strings. 
    Returns False if there were any issues with the pronoun replacement, or if the
    json is incorrectly formatted. """
    
    success = True
    
    with open(path, "r") as file:
        try:
            contents = ujson.loads(file.read())
        except ujson.JSONDecodeError as _e:
            print(f"::error file={path}::File {path} is invalid json")
            print(_e)
            return False
        
    for _str in get_all_strings(contents):
        try:
            processed = process_text(_str, repl_dict, True)
        except (KeyError, IndexError) as _e:
            print(f"::error file={path}: \"{_str}\" contains invalid pronoun or verb tags.")
            print(_e)
            success = False
        else: 
            ## This test for any pronoun or verb tag fragments that might have
            ## sneaked through. This is most likely caused by using the incorrect type of
            ## brackets
            if re.search(r"\{PRONOUN|\(PRONOUN|\{VERB|\(VERB", processed):
                print(f"::error file={path}: \"{_str}\" contains pronoun tag fragments after replacment")
                success = False
            
    return success

    
def get_all_strings(data):
    """ Will take any combination of list and dicts, 
    and extract all strings, including dictionary keys. 
    Recursive. """
    
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
            test()
        self.assertEqual(cm.exception.code, 0)
