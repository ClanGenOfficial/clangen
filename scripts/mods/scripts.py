"""

USED VIA:
<top of script, below module comments, above imports>

from scripts.mods.scripts import check_and_run
_ = check_and_run(__file__)
if _ is not '':
    import importlib
    return importlib.import_module(_.replace(os.sep, ".").replace(".py", ""))
else:
    del check_and_run
    del _
"""


from .mods import modlist
import os
import importlib


def check_and_run(scriptname: str) -> str:
    for mod in modlist.get_mods():
        if os.path.exists(os.path.join(os.getcwd(), "mods", mod, scriptname)):
            _ = os.path.join("mods", mod, scriptname)
            return _
    return ''