import random


class Name(object):
    special_suffixes = {"kitten": "kit", "apprentice": "paw", "medicine cat apprentice": "paw", "leader": "star"}
    normal_suffixes = ["fur", "fur", "fur", "fur", "pelt", "pelt", "pelt", "heart", "heart", "heart",
                       "tail", "tail", "tail", "fang", "wing", "wing", "wing",
                       "feather", "whisker", "whisker", "whisker", "leg", "foot", "foot", "breeze", "claw", "claw",
                       "cloud", "flower", "fern", "willow", "frost", "jaw",
                       "leaf", "light", "nose", "eye", "petal", "pool", "shade", "shine", "song", "step",
                       "storm", "stream", "thorn", "throat", "tooth", "tuft", "blaze", "wind", "poppy", "moon",
                       "jay", "hawk", "heather", "flight", "fall", "ear", "belly", "berry", "bird",
                       "branch", "brook", "ash", "creek", "dawn", "drop", "dusk", "fire", "gorse", "hail", "leap",
                       "shell", "beam", "bee", "briar", "burr", "bush", "eyes", "face", "fin", "fish", "haze",
                       "mask", "mist", "mouse", "pad", "pounce", "puddle", "runner", "scar", "seed", "sight", "skip",
                       "sky", "slip", "song", "spirit", "spring", "stalk", "stem", "strike", "stone", "swoop", "talon",
                       "thistle", "toe", "needle", "watcher", "wish", "whisper"]

    pelt_suffixes = {'TwoColour': ['patch', 'spot', 'splash', 'patch', 'spots'],
                     'Tabby': ['stripe', 'feather', 'leaf', 'stripe', 'shade'],
                     'Speckled': ['dapple', 'speckle', 'spot', 'speck'],
                     'Tortie': ['dapple', 'speckle', 'spot', 'dapple'],
                     'Calico': ['stripe', 'dapple', 'patch', 'patch']}

    normal_prefixes = ["Adder", "Alder", "Ant", "Apple", "Ash", "Acorn", "Arch", "Aspen", "Bark", "Bay", "Bee",
                       "Badger", "Beetle", "Beech", "Berry", "Big", "Birch", "Bird", "Bloom", "Boulder", "Bounce",
                       "Blossom", "Bracken", "Branch", "Brave", "Bramble", "Briar", "Bright", "Brindle", "Bristle",
                       "Broken", "Brook", "Bug", "Bumble", "Buzzard", "Cherry", "Chestnut", "Chive", "Cinder",
                       "Cinnamon", "Cloud", "Cold", "Crow", "Cedar", "Claw", "Clover", "Copper", "Cone",
                       "Creek", "Cricket", "Crooked", "Crouch", "Curl", "Curly", "Cypress", "Dapple", "Dove", "Dusk",
                       "Dust", "Dawn", "Dead", "Dew", "Doe", "Down", "Drift", "Duck", "Eagle", "Echo", "Eel", "Elm",
                       "Ember", "Freckle", "Fringe", "Feather", "Fern", "Fennel", "Ferret", "Flame", "Flower", "Fallen",
                       "Fallow", "Fawn", "Fin", "Finch", "Flail", "Flutter", "Fir", "Frog", "Frond", "Flash", "Flax",
                       "Fleet", "Flicker", "Flint", "Flip", "Fly", "Fuzzy", "Goose", "Gorse", "Grass", "Gravel", "Gull",
                       "Hail", "Hare", "Hay", "Hatch", "Half", "Hawk", "Heather", "Heavy", "Heron", "Hickory", "Hill",
                       "Hollow", "Hoot", "Hop", "Hope", "Hound", "Holly", "Ivy", "Jagged", "Jay", "Jump", "Juniper",
                       "Kestrel", "Kink", "Kite", "Lake", "Lark", "Larch", "Lavender", "Leaf", "Lichen", "Leopard",
                       "Lightning", "Lily", "Lizard", "Log", "Lost", "Low", "Lynx", "Little", "Long", "Loud", "Marsh",
                       "Marigold", "Maple", "Mole", "Moth", "Mouse", "Mallow", "Meadow", "Midge", "Milk", "Minnow",
                       "Mint", "Mist", "Mistle", "Misty", "Morning", "Moss", "Mossy", "Mottle", "Mud", "Mumble",
                       "Nectar", "Night", "Nettle", "Nut", "Needle", "Newt", "Oat", "Odd", "Oak", "One", "Otter", "Owl",
                       "Parsley", "Patch", "Pear", "Petal", "Pebble", "Perch", "Pigeon", "Pike", "Pine", "Pod", "Poppy",
                       "Pounce", "Prickle", "Quail", "Quick", "Quiet", "Rabbit", "Ragged", "Reed", "Ripple", "Ridge",
                       "River", "Rain", "Raven", "Rat", "Robin", "Rock", "Rose", "Rowan", "Rubble", "Running", "Rush",
                       "Rook", "Root", "Rye", "Sage", "Sandy", "Scorch", "Sedge", "Sharp", "Shimmer", "Spring",
                       "Strike", "Seed", "Shade", "Shell", "Short", "Shy", "Sky", "Slate", "Sleek", "Slight", "Sloe",
                       "Small", "Snail", "Sneeze", "Soft", "Song", "Spark", "Stoat", "Starling", "Shrew", "Smoke",
                       "Snake", "Snip", "Soot", "Sparrow", "Speckle", "Spider", "Scar", "Skip", "Stork", "Spire",
                       "Sorrel", "Spike", "Splash", "Stag", "Swallow", "Swan", "Swamp", "Sweet", "Spotted", "Squirrel",
                       "Storm", "Stone", "Swift", "Tall", "Thistle", "Thrift", "Trout", "Tiger", "Tulip", "Timber",
                       "Twig", "Torn", "Tumble", "Turtle", "Vine", "Violet", "Vixen", "Vole", "Web", "Wet", "Whisker",
                       "Willow", "Wasp", "Weasel", "Whirl", "Wild", "Yarrow", "Yew"]

    colour_prefixes = {'WHITE': ['White', 'White', 'Pale', 'Snow', 'Cloud', 'Milk', 'Hail', 'Frost', 'Ice',
                                 'Sheep', 'Blizzard', 'Moon', 'Light'],
                       'PALEGREY': ['Grey', 'Silver', 'Pale', 'Cloud', 'Hail', 'Frost', 'Ice', 'Mouse', 'Bright',
                                    "Fog"],
                       'SILVER': ['Grey', 'Silver', 'Cinder', 'Ice', 'Frost', 'Rain', 'Blue', 'River', 'Blizzard'],
                       'GREY': ['Grey', 'Grey', 'Ash', 'Cinder', 'Rock', 'Stone', 'Shade',
                                'Mouse', 'Smoke', 'Shadow', "Fog"],
                       'DARKGREY': ['Grey', 'Shade', 'Raven', 'Crow', 'Stone', 'Dark', 'Night', 'Smoke', 'Shadow'],
                       'BLACK': ['Black', 'Black', 'Shade', 'Crow', 'Raven', 'Ebony', 'Dark', 'Night',
                                 'Shadow', 'Scorch'],
                       'PALEGINGER': ['Sand', 'Yellow', 'Pale', 'Sun', 'Light', 'Lion', 'Bright', 'Honey', 'Daisy'],
                       'GOLDEN': ['Gold', 'Golden', 'Yellow', 'Sun', 'Light', 'Lightning', 'Thunder', 'Honey', 'Tawny',
                                  'Lion', 'Dandelion'],
                       'GINGER': ['Red', 'Fire', 'Rust', 'Flame', 'Ember', 'Sun', 'Light', 'Rose', 'Rowan', 'Fox',
                                  'Tawny', "Plum"],
                       'DARKGINGER': ['Red', 'Red', 'Fire', 'Rust', 'Flame', 'Oak', 'Shade', 'Russet', 'Rowan', 'Fox'],
                       'LIGHTBROWN': ['Brown', 'Pale', 'Light', 'Mouse', 'Dust', 'Sand', 'Bright', 'Mud', 'Hazel'],
                       'BROWN': ['Brown', 'Oak', 'Mouse', 'Dark', 'Shade', 'Russet', 'Stag', 'Acorn', 'Mud', "Deer"],
                       'DARKBROWN': ['Brown', 'Shade', 'Dark', 'Night', 'Russet', 'Rowan', 'Mud']}

    eye_prefixes = {'YELLOW': ['Yellow', 'Moon', 'Daisy', 'Honey', 'Light'],
                    'AMBER': ['Amber', 'Sun', 'Fire', 'Gold', 'Honey', 'Scorch'],
                    'HAZEL': ['Tawny', 'Hazel', 'Gold', 'Daisy', 'Sand'],
                    'PALEGREEN': ['Green', 'Pale', 'Mint', 'Fern', 'Weed'],
                    'GREEN': ['Green', 'Fern', 'Weed', 'Holly', 'Clover', 'Olive'],
                    'BLUE': ['Blue', 'Blue', 'Ice', 'Sky', 'Lake', 'Frost', 'Water'],
                    'DARKBLUE': ['Blue', 'Sky', 'Lake', 'Berry', 'Dark', 'Water', 'Deep'],
                    'BLUEYELLOW': ['Yellow', 'Blue', 'Odd', 'One', 'Moon'],
                    'BLUEGREEN': ['Green', 'Blue', 'Odd', 'One', 'Clover']}

    def __init__(self, status="warrior", prefix=None, suffix=None, colour=None, eyes=None, pelt=None):
        self.status = status  # warrior, kitten, leader or apprentice
        if prefix is None:
            if colour is None and eyes is None:
                self.prefix = random.choice(self.normal_prefixes)
            elif eyes is None:
                a = random.randint(0, 5)
                if a != 1:
                    self.prefix = random.choice(self.normal_prefixes)
                else:
                    self.prefix = random.choice(self.colour_prefixes[colour])
            elif colour is None:
                a = random.randint(0, 5)
                if a != 1:
                    self.prefix = random.choice(self.normal_prefixes)
                else:
                    self.prefix = random.choice(self.eye_prefixes[eyes])
            else:
                a = random.randint(0, 7)
                if a == 1:
                    self.prefix = random.choice(self.colour_prefixes[colour])
                elif a == 2:
                    self.prefix = random.choice(self.eye_prefixes[eyes])
                else:
                    self.prefix = random.choice(self.normal_prefixes)

        else:
            self.prefix = prefix

        if suffix is None:
            loop = True
            while loop:
                if pelt is None or pelt == 'SingleColour':
                    self.suffix = random.choice(self.normal_suffixes)
                else:
                    a = random.randint(0, 7)
                    if a == 1:
                        self.suffix = random.choice(self.pelt_suffixes[pelt])
                    else:
                        self.suffix = random.choice(self.normal_suffixes)
                if self.suffix != self.prefix.lower():
                    loop = False
        else:
            self.suffix = suffix

    def __repr__(self):
        if self.status in ["deputy", "warrior", "medicine cat", "elder"]:
            return self.prefix + self.suffix
        else:
            return self.prefix + self.special_suffixes[self.status]


names = Name()
