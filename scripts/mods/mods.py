# pylint: disable=line-too-long
"""

mods? what else do you want me to say?

""" # pylint: enable=line-too-long


import os


def get_all_mods():
    """
    Returns a list of all mods in the mods folder
    This does not take priority into account
    """
    mods = []
    for mod in os.listdir(os.path.join(os.getcwd(), "mods")):
        if os.path.isdir(os.path.join(os.getcwd(), "mods", mod)):
            mods.append(mod)
    return mods

def get_real_mods():
    """
    Verifies that all mods are valid
    """

    required_folders = ["resources", "scripts", "sprites"]

    mods = get_all_mods()

    for mod in mods:
        modvalid = False

        dircontents = os.listdir(os.path.join(os.getcwd(), "mods", mod))

        for folder in required_folders:
            if folder in dircontents:
                modvalid = True

        if not modvalid:
            print(f"Mod {mod} has no overriden resources, scripts, or sprites. It will be ignored.")
            mods.remove(mod) # pylint: disable=modified-iterating-list

    return mods





def get_mods():
    """
    Returns a list of all mods in the mods folder
    This takes priority into account
    This takes toggling into account
    """
    # TODO: priority
    return get_real_mods()
