# pylint: disable=line-too-long
"""

mods? what else do you want me to say?

""" # pylint: enable=line-too-long


import os

from scripts.datadir import get_mods_dir


def get_all_mods():
    """
    Returns a list of all mods in the mods folder
    This does not take priority into account
    """
    mods = []
    for mod in os.listdir(get_mods_dir()):
        if os.path.isdir(os.path.join(get_mods_dir(), mod)) and mod != ".modsettings.json":
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

        dircontents = os.listdir(os.path.join(get_mods_dir(), mod))


        # God bless anyone who has to read this
        overwritten_scripts = {}
        for folder in required_folders:
            if folder in dircontents:
                _dircontents = os.listdir(os.path.join(get_mods_dir(), mod, folder))
                if _dircontents:
                    modvalid = True
                    if folder == "scripts":
                        _overwritten_scripts = []
                        for file in _dircontents:
                            if os.path.isdir(os.path.join(get_mods_dir(), mod, folder, file)):
                                for _file in os.listdir(os.path.join(get_mods_dir(), mod, folder, file)):
                                    if _file.endswith(".py"):
                                        _overwritten_scripts.append(os.path.join(file, _file))
                            if file.endswith(".py"):
                                _overwritten_scripts.append(file)
                        overwritten_scripts[mod] = _overwritten_scripts

        for mod, scripts in overwritten_scripts.items():
            print(f"Mod {mod} overwrites the following scripts: {', '.join(scripts)}")


        if not modvalid:
            print(f"Mod {mod} has no overriden resources, scripts, or sprites. It will be ignored.")
            mods.remove(mod) # pylint: disable=modified-iterating-list

    return mods




class modList():
    """
    TODO: docs
    """
    def __init__(self):
        self._mods = get_real_mods()
        self.mods = self.sort(self._mods, should_reread=True)

    def sort(self, mods_to_sort=[], should_reread=False, should_rewrite=False):
        """
        reads <mods-dir>/.modsettings.txt
        each line is a mod
        the first mod is the highest priority
        if a mod is not in the file, it is assumed to be the lowest priority, and is appended to the end # pylint: disable=line-too-long

        If should_rewrite is True, it will *always* rewrite the file
        if false, it will only rewrite if it needs to
        """
        if mods_to_sort == []:
            return mods_to_sort
        if not os.path.exists(os.path.join(get_mods_dir(), ".modsettings.txt")):
            self.write_modsettings(mods_to_sort)
            return mods_to_sort.sort() # a-z

        sorted_mods = []
        if should_reread:
            with open(os.path.join(get_mods_dir(), ".modsettings.txt"), "r", encoding='ascii') as file: # pylint: disable=line-too-long
                prefs = file.readlines()
        else:
            prefs = self.mods # read the already sorted mods list, and sort it again
        for mod in prefs:
            mod = mod.strip()
            if mod in mods_to_sort:
                sorted_mods.append(mod)
            elif mod.startswith("-") and mod[1:] in mods_to_sort:
                sorted_mods.append(mod)
            else:
                print(f"Mod {mod} is not installed. It will be removed")
                should_rewrite = True

        for mod in mods_to_sort:
            if mod not in sorted_mods:
                sorted_mods.append(mod)
                should_rewrite = True

        if should_rewrite:
            self.write_modsettings(sorted_mods)
        self.mods = sorted_mods
        return sorted_mods

    def write_modsettings(self, mods):
        """
        THIS SHOULD ALWAYS BE CALLED AFTER SORTING
        Preferrably, use self.sort(should_rewrite=True)
        writes <mods-dir>/.modsettings.txt
        """
        with open(os.path.join(get_mods_dir(), ".modsettings.txt"), "w", encoding='ascii') as file:
            file.write("\n".join(mods))

    def add(self, mod):
        """
        Adds a mod to the list
        """
        if mod in self.mods:
            return
        self.mods.append(mod)
        self._mods.append(mod)
        self.sort(should_rewrite=True)

    def remove(self, mod):
        """
        Removes a mod from the list
        """
        if mod not in self.mods:
            return
        self.mods.remove(mod)
        self._mods.remove(mod)

    def get_mods(self):
        """
        Returns a list of mods
        """
        
        # disabled mods are prefixed with a -

        _ = []
        for mod in self.mods:
            if not mod.startswith("-"):
                _.append(mod)
        return _
    

    def toggle_mod(self, mod):
        """
        Toggles a mod on or off
        """
        if mod not in self.mods:
            return
        if mod.startswith("-"):
            self.mods.remove(mod)
            self.mods.append(mod[1:])
            print('a')
        else:
            self.mods.remove(mod)
            self.mods.append(f"-{mod}")
        self.sort(self.mods, should_rewrite=True)
    
    def move_up(self, mod):
        """
        Moves a mod up in the list
        """
        if mod not in self.mods:
            return
        if self.mods.index(mod) == 0:
            return
        self.mods.remove(mod)
        self.mods.insert(self.mods.index(mod)-1, mod)
        self.sort(self.mods, should_rewrite=True)
    
    def move_down(self, mod):
        """
        Moves a mod down in the list
        """
        if mod not in self.mods:
            return
        if self.mods.index(mod) == len(self.mods)-1:
            return
        _ = self.mods.index(mod)+1
        self.mods.remove(mod)
        self.mods.insert(_, mod)
        self.sort(self.mods, should_rewrite=True)
    
    def move_up(self, mod):
        """
        Moves a mod up in the list
        """
        if mod not in self.mods:
            return
        if self.mods.index(mod) == 0:
            return
        _=self.mods.index(mod)-1
        self.mods.remove(mod)
        self.mods.insert(_, mod)
        self.sort(self.mods, should_rewrite=True)


modlist = modList()