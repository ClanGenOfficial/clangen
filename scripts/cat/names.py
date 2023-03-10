import random
import os
import ujson

from scripts.datadir import get_save_dir


class Name():
    if os.path.exists('resources/dicts/names/names.json'):
        with open('resources/dicts/names/names.json') as read_file:
            names_dict = ujson.loads(read_file.read())

        if os.path.exists(get_save_dir() + '/prefixlist.txt'):
            with open(get_save_dir() + '/prefixlist.txt', 'r') as read_file:
                name_list = read_file.read()
                if_names = len(name_list)
            if if_names > 0:
                new_names = name_list.split('\n')
                for new_name in new_names:
                    if new_name != '':
                        if new_name.startswith('-'):
                            while new_name[1:] in names_dict["normal_prefixes"]:
                                names_dict["normal_prefixes"].remove(new_name[1:])
                        else:
                            names_dict["normal_prefixes"].append(new_name)

        if os.path.exists(get_save_dir() + '/suffixlist.txt'):
            with open(get_save_dir() + '/suffixlist.txt', 'r') as read_file:
                name_list = read_file.read()
                if_names = len(name_list)
            if if_names > 0:
                new_names = name_list.split('\n')
                for new_name in new_names:
                    if new_name != '':
                        if new_name.startswith('-'):
                            while new_name[1:] in names_dict["normal_suffixes"]:
                                names_dict["normal_suffixes"].remove(new_name[1:])
                        else:
                            names_dict["normal_suffixes"].append(new_name)

        if os.path.exists('saves/specialsuffixes.txt'):
            with open('saves/specialsuffixes.txt', 'r') as read_file:
                name_list = read_file.read()
                if_names = len(name_list)
            if if_names > 0:
                new_names = name_list.split('\n')
                for new_name in new_names:
                    if new_name != '':
                        if new_name.startswith('-'):
                            del names_dict["special_suffixes"][new_name[1:]]
                        elif ':' in new_name:
                            _tmp = new_name.split(':')
                            names_dict["special_suffixes"][_tmp[0]] = _tmp[1]


    def __init__(self,
                 status="warrior",
                 prefix=None,
                 suffix=None,
                 colour=None,
                 eyes=None,
                 pelt=None,
                 tortiepattern=None):
        self.status = status
        self.prefix = prefix
        self.suffix = suffix
        
        # Set prefix
        if prefix is None:
            named_after_appearance = not random.getrandbits(3)  # Chance for True is '1/8'.
            # Add possible prefix categories to list.
            possible_prefix_categories = []
            if eyes in self.names_dict["eye_prefixes"]:
                possible_prefix_categories.append(self.names_dict["eye_prefixes"][eyes])
            if colour in self.names_dict["colour_prefixes"]:
                possible_prefix_categories.append(self.names_dict["colour_prefixes"][colour])
            # Choose appearance-based prefix if possible and named_after_appearance because True.
            if named_after_appearance and possible_prefix_categories:
                prefix_category = random.choice(possible_prefix_categories)
                self.prefix = random.choice(prefix_category)
            else:
                self.prefix = random.choice(self.names_dict["normal_prefixes"])
                    
        # Set suffix
        while self.suffix is None or self.suffix == self.prefix.casefold() or str(self.suffix) in \
                self.prefix.casefold() and not str(self.suffix) == '':
            if pelt is None or pelt == 'SingleColour':
                self.suffix = random.choice(self.names_dict["normal_suffixes"])
            else:
                named_after_pelt = not random.getrandbits(3) # Chance for True is '1/8'.
                # Pelt name only gets used if there's an associated suffix.
                if named_after_pelt:
                    if pelt in ["Tortie", "Calico"] and tortiepattern in self.names_dict["tortie_pelt_suffixes"]:
                        self.suffix = random.choice(self.names_dict["tortie_pelt_suffixes"][tortiepattern])
                    elif pelt in self.names_dict["pelt_suffixes"]:
                        self.suffix = random.choice(self.names_dict["pelt_suffixes"][pelt])
                    else:
                        self.suffix = random.choice(self.names_dict["normal_suffixes"])
                else:
                    self.suffix = random.choice(self.names_dict["normal_suffixes"])

    def __repr__(self):
        if self.status in self.names_dict["special_suffixes"]:
            return self.prefix + self.names_dict["special_suffixes"][self.status]
        else:
            return self.prefix + self.suffix



names = Name()
