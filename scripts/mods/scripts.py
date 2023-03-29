"""

USED VIA:
<top of script, below module comments, above imports>

"""


from .mods import modlist
import os
import importlib


def check_and_run(scriptname: str):
    for mod in modlist.get_mods():
        if os.path.exists(os.path.join(os.getcwd(), "mods", mod, scriptname)):
            _ = os.path.join(os.getcwd(), "mods", mod, scriptname)
            return True, importlib.import_module(_)
    return False, None