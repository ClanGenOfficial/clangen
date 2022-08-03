import random


class Name(object):
    special_suffixes = {"kitten": "kit", "apprentice": "paw", "medicine cat apprentice": "paw", "leader": "star"}
    normal_suffixes = [
        # common suffixes
        "fur", "fur", "fur", "fur", "fur", "fur", "fur", "fur", "fur", "fur",
        "pelt", "pelt", "pelt", "pelt", "pelt", "pelt", "pelt", "pelt", "pelt",
        "tail", "tail", "tail", "tail", "tail", "tail", "tail", "tail",
        "claw", "claw", "claw", "claw", "claw", "claw", "claw",
        "foot", "foot", "foot", "foot", "foot",
        "whisker", "whisker", "whisker", "whisker",
        "heart", "heart", "heart", "heart", "heart",

        # regular suffixes
        "acorn", "ash", "aster", "back", "beam", "bee", "belly", "berry", "bite",
        "bird", "blaze", "blink", "blossom", "bloom", "blotch", "bounce", "branch", "breeze", "briar", "bright",
        "brook", "burr", "bush", "call", "cloud", "clover", "coral", "creek", "cry", "dapple", "daisy",
        "dawn", "drift", "drop", "dusk", "dust", "ear", "ears", "eye", "eyes", "face", "fall", "fang",
        "feather", "fern", "fin", "fire", "fish", "flame", "flight", "flood", "flower",
        "frost", "gaze", "goose", "gorse", "grass", "hail", "hare", "hawk", "haze",
        "heather", "holly", "hollow", "ivy", "jaw", "jay", "jump", "kite", "lake", "larch", "leaf",
        "leap", "leg", "light", "lilac", "lily", "lotus", "mask", "mist", "moth", "moon", "mouse",
        "needle", "nettle", "night", "noise", "nose", "nut", "pad", "path", "patch", "petal",
        "pond", "pool", "poppy", "pounce", "puddle", "rapid", "rose", "rump", "run", "runner",
        "scar", "seed", "shade", "shadow", "shell", "shine", "sight", "skip", "sky", "slip", "snow",
        "song", "spark", "speck", "speckle", "spirit", "splash", "splashed", "spot", "spots", "spring",
        "stalk", "stem", "step", "stone", "storm", "streak", "stream", "strike", "stripe", "sun",
        "swipe", "swoop", "tail", "tree", "throat", "tuft", "watcher", "water", "whisper",
        "willow", "wind", "wing", "wish"]

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

    loner_names = ["Haku", "Pichi", "Poki", "Nagi", "Jubie", "Bonbon", "Beans", "Aurora", "Maleficent", "Luna",
                   "Eclipse", "Sol", "Star", "George", "Nightmare", "Bagel", "Monster", "Gargoyle", "Missile",
                   "Rolo", "Rocket", "Void", "Abyss", "Vox", "Princess", "Noodle", "Duchess", "Cheesecake", "Callie",
                   "Randy", "Ace", "Rook", "Queeny", "Freddy", "Stella", "Rooster", "Sophie", "Maverick", "Seamus",
                   "Pickles", "Lacy", "Lucy", "Knox", "Lugnut", "Bailey", "Azula", "Lucky", "Sunny", "Sadie", "Sox",
                   "Bandit", "Onyx", "Quinn", "Grace", "Fang", "Ike", "Flower", "Whiskers", "Gust", "Robin", "Peony",
                   "Minnie", "Buddy", "Mollie", "Jaxon", "Dunnock", "Thyme", "Firefly", "Cheese", "Sandwich", "Ivy",
                   "Prickle", "Insect", "Bumble", "Grasshopper", "Coral", "Bee", "Berry", "Soft", "Windy", "Sofa",
                   "Fishtail", "Roman", "Wishbone", "Nova", "Quimby", "Quest", "Nessie", "Niles", "Neil", "Nutella",
                   "Nakeena", "Nuka", "Hughie", "Harvey", "Herc", "French", "Finch", "Frannie", "Flutie", "Fire",
                   "Free", "Glory", "Ginger", "Indi", "Ice", "Igor", "Jupiter", "Juniper", "Jesse", "James", "Jethro",
                   "Joker", "Jinx", "Chaos", "Havoc", "Trouble", "Kingston", "King", "Kip", "Kong", "Ken", "Kendra",
                   "Kisha", "Kermit", "Kelloggs", "Kodiak", "Klondike", "Ketchup", "KD", "Lupo", "Luigi", "Lily",
                   "Lora", "Lee", "Lex", "Lester", "Makwa", "Madi", "Minna", "Moxie", "Mucha", "Manda", "Monte",
                   "Monzi", "Nisha", "Nemo", "Nitro", "Oops", "O'Leary", "Ophelia", "Olga", "Oscar", "Owen", "Porsche",
                   "Ping", "Pong", "Quinzee", "Quickie", "Quagmire", "Quake", "Quinoa", "Quail", "Roomba", "Riot",
                   "Ramble", "Rudolph", "Rum", "Rye", "Reese", "Snow", "Spruce", "Scotch", "Sneakers", "Schmidt",
                   "Sonic", "Teufel", "Toni", "Toque", "Tempest", "Turbo", "Tetris", "Triscuit", "Tumble", "Voltage",
                   "Vinnie", "Vaxx", "Venture", "Vida", "Guinness", "Polly", "Piper", "Pepper", "Lakota", "Dakota",
                   "Bently", "Chinook", "Tiny", "Ula", "Union", "Uriel", "Orion", "Oakley", "Roselies", "Belle", "Benny",
                   "Bumblebee", "Bluebell", "Chip", "Chocolate", "Cracker", "Dave", "Dolly", "Egg", "Frito", "Frank",
                   "Gibby", "Jack", "Jenny", "Juliet", "Joob", "John", "Jimmy", "Jude", "Kenny", "Tom", "Oreo", "Mocha",
                   "Ninja", "Rock", "Pip", "Pipsqueak", "Milque", "Toast", "Molly Murder Mittens", "Vulture", "Raven",
                   "Sorbet", "Vanilla", "Mint", "Niki", "Nikki", "Pocket", "Tabbytha", "Gravy", "Potato",
                   "Pumpernickel", "Pecan", "Old Man Sam", "Icecube", "Queso Ruby", "Pearl", "Jasper", "Stan", "Rose",
                   "Mojo", "Kate", "Carmen", "Mange", "Chase", "Socks", "Tabby", "Jay", "Charlie",
                   "Crunchwrap", "Meow-meow", "Bede", "Smores", "Evilface", "Nick", "Mitski", "Ash", "Ah", "Violet",
                   "Alcina", "Worm", "Monika", "Rat", "Bongo", "Bunny", "Viktor", "Steve", "Jewels", "Blu", "Rue",
                   "Stinky", "Garnet", "Anita", "Sloane", "Emi", "Vivienne", "Ambers", "Moon", "Twilight", "River",
                   "Glass", "Goose", "Hunter", "Amity", "Stripes", "Cowbell", "Rory", "Lobster", "Slug", "Starfish",
                   "Salmon", "Judy", "Johnny", "Kerry", "Evelyn", "Holly", "Bolt", "Millie", "Jessica", "Laku",
                   "Dragonfly", "X’ek", "Silva", "Dreamy", "Decay", "Twister", "Shay", "Louis", "Oleander", "Spots",
                   "Cream", "Omlet", "Gizmo", "Feather", "Twix", "Silver,", "Ghost", "Wisp,", "Obi Wan", "Pearl,",
                   "Mango", "Via", "Olivia", "Mr. Whiskers", "Fluffy", "Shimmer", "Mimi", "Melody", "Leon", "Punk",
                   "Mew", "Fern", "Marceline", "Whisper", "Skrunkly", "Stolas", "Rio", "Steven", "Pear", "Sekhmet",
                   "Mellon", "Ember", "Loona", "Saki", "Tiny", "Sandy", "Miles", "Mini", "Judas", "Zim", "Vinyl",
                   "Rarity", "Trixie", "Sunset", "Anubis", "Armin", "Amy", "Alice", "Alec", "Baphomet", "Bean",
                   "Bastet, Birb", "Bee", "Burm", "Chrissy", "Cherry", "Chief", "Crow", "Carrie", "Calvin", "Cookie",
                   "Catie", "Charm", "Crane", "Crab", "Charles", "Caroline", "Conan", "Cloud", "Charlie", "Cowboy",
                   "Dune", "Dan", "Dove", "Delilah", "Emerald", "Emy", "Erica", " Eddie", "Eda", "Ferret", "Fawn",
                   "Fallow", "Ferry", "Gamble", "Grain", "Gir", "Heron", "Hop", "Honey", "Hot Sauce", "Habanero"]

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
