import random
import os
import ujson

from scripts.datadir import get_save_dir

from scripts.game_structure.game_essentials import game


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

        if os.path.exists(get_save_dir() + '/specialsuffixes.txt'):
            with open(get_save_dir() + '/specialsuffixes.txt', 'r') as read_file:
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
                 tortiepattern=None,
                 biome=None,
                 specsuffix_hidden=False):
        self.status = status
        self.prefix = prefix
        self.suffix = suffix
        self.specsuffix_hidden = specsuffix_hidden
        
        animals_look_again = False
        # Set prefix
        if prefix is None:
            # needed for random dice double animal checks
            animals_look_again = True
            named_after_appearance = not random.getrandbits(2)  # Chance for True is '1/4'
            named_after_biome = not random.getrandbits(3) # chance for True is 1/8
            # Add possible prefix categories to list.
            possible_prefix_categories = []
            if eyes in self.names_dict["eye_prefixes"]:
                possible_prefix_categories.append(self.names_dict["eye_prefixes"][eyes])
            if colour in self.names_dict["colour_prefixes"]:
                possible_prefix_categories.append(self.names_dict["colour_prefixes"][colour])
            if biome is not None and biome in self.names_dict["biome_prefixes"]:
                possible_prefix_categories.append(self.names_dict["biome_prefixes"][biome])
            # Choose appearance-based prefix if possible and named_after_appearance because True.
            if named_after_appearance and possible_prefix_categories and not named_after_biome:
                prefix_category = random.choice(possible_prefix_categories)
                self.prefix = random.choice(prefix_category)
            elif named_after_biome and possible_prefix_categories:
                prefix_category = random.choice(possible_prefix_categories)
                self.prefix = random.choice(prefix_category)
            else:
                self.prefix = random.choice(self.names_dict["normal_prefixes"])
                    
        # Set suffix
        while self.suffix is None or self.suffix == self.prefix.casefold() or str(self.suffix) in \
                self.prefix.casefold() and not str(self.suffix) == '' or self.prefix == "Wet" and self.suffix == "back":
            if not self.prefix:
                # needed for random dice double animal checks
                look_again = False
            if pelt is None or pelt == 'SingleColour':
                self.suffix = random.choice(self.names_dict["normal_suffixes"])
            else:
                named_after_pelt = not random.getrandbits(2) # Chance for True is '1/8'.
                named_after_biome_ = not random.getrandbits(3) # 1/8
                # Pelt name only gets used if there's an associated suffix.
                if named_after_pelt:
                    if pelt in ["Tortie", "Calico"] and tortiepattern in self.names_dict["tortie_pelt_suffixes"]:
                        self.suffix = random.choice(self.names_dict["tortie_pelt_suffixes"][tortiepattern])
                    elif pelt in self.names_dict["pelt_suffixes"]:
                        self.suffix = random.choice(self.names_dict["pelt_suffixes"][pelt])
                    else:
                        self.suffix = random.choice(self.names_dict["normal_suffixes"])
                elif named_after_biome_:
                    if biome in self.names_dict["biome_suffixes"]:
                        self.suffix = random.choice(self.names_dict["biome_suffixes"][biome])
                else:
                    self.suffix = random.choice(self.names_dict["normal_suffixes"])
        
        # Prevent triple letter names from joining prefix and suffix from occuring
        # Prevent double animal names (ex. Spiderfalcon)
        if self.suffix:
            possible_three_letter = (self.prefix[-2:] + self.suffix[0], self.prefix[-1] + self.suffix[:2])

            if all(i == possible_three_letter[0][0] for i in possible_three_letter[0]) or \
                    all(i == possible_three_letter[1][0] for i in possible_three_letter[1]):
                triple_letter = True

                MAX_ATTEMPT = 3
                while triple_letter and MAX_ATTEMPT > 0:
                    self.suffix = random.choice(self.names_dict["normal_suffixes"])
                    possible_three_letter = (self.prefix[-2:] + self.suffix[0], self.prefix[-1] + self.suffix[:2])    
                    if all(i == possible_three_letter[0][0] for i in possible_three_letter[0]) or \
                            all(i == possible_three_letter[1][0] for i in possible_three_letter[1]):
                        pass
                    else:
                        triple_letter = False
                MAX_ATTEMPT -= 1
            
            if not animals_look_again and self.prefix in self.names_dict["animal_prefixes"] and self.suffix in self.names_dict["animal_suffixes"]:
                replace_suffix = [i for i in self.names_dict["normal_suffixes"] if i not in self.names_dict["animal_suffixes"]]
                self.suffix = random.choice(replace_suffix)
        
        # this is mostly added for the name randomizer (double animal names)
        if animals_look_again and self.prefix in self.names_dict["animal_prefixes"] and self.suffix in self.names_dict["animal_suffixes"]:
            replace_prefix = [i for i in self.names_dict["normal_prefixes"] if i not in self.names_dict["animal_prefixes"]]
            self.prefix = random.choice(replace_prefix)

    def __repr__(self):
        if self.status in self.names_dict["special_suffixes"] and not self.specsuffix_hidden:
            return self.prefix + self.names_dict["special_suffixes"][self.status]
        else:
            if game.config['fun']['april_fools']:
                return self.prefix + 'egg'
            return self.prefix + self.suffix



names = Name()
