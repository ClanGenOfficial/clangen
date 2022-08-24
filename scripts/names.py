import random
import os


class Name(object):
    special_suffixes = {"kitten": "kit", "apprentice": "paw", "medicine cat apprentice": "paw", "leader": "star"}
    normal_suffixes = [  # common suffixes
        "fur", "fur", "fur", "fur", "fur", "fur", "fur", "fur", "fur", "fur", 'fur', 'fur', 'pelt', "pelt", "pelt", "pelt", "pelt", "pelt", "pelt", "pelt", "pelt", "pelt", "tail", "tail", "tail",
        "tail", "tail", "tail", "tail", "tail", "claw", "claw", "claw", "claw", "claw", "claw", "claw", "foot", "foot", "foot", "foot", "foot", "whisker", "whisker", "whisker",
        "whisker", "heart", "heart", "heart", "heart", "heart", 'heart'

        # regular suffixes
        "acorn", "ash", "aster", "back", "beam", "bee", "belly", "berry", "bite", "bird", "blaze", "blink", "blossom", "bloom", "blotch", "bounce", "branch", "breeze", "briar",
        "bright", "brook", "burr", "bush", "call", "cloud", "clover", "coral", "creek", "cry", "dapple", "daisy", "dawn", "drift", "drop", "dusk", "dust", "ear", "ears", "eye",
        "eyes", "face", "fall", "fang", "feather", "fern", "fin", "fire", "fish", "flame", "flight", "flood", "flower", "frost", "gaze", "goose", "gorse", "grass", "hail", "hare",
        "hawk", "haze", "heather", "holly", "hollow", "ivy", "jaw", "jay", "jump", "kite", "lake", "larch", "leaf", "leap", "leg", "light", "lilac", "lily", "lotus", "mask",
        "mist", "moth", "moon", "mouse", "needle", "nettle", "night", "noise", "nose", "nut", "pad", "path", "patch", "petal", "pond", "pool", "poppy", "pounce", "puddle", "rapid",
        "rose", "rump", "run", "runner", "scar", "seed", "shade", "shadow", "shell", "shine", "sight", "skip", "sky", "slip", "snow", "song", "spark", "speck", "speckle", "spirit",
        "splash", "splashed", "spot", "spots", "spring", "stalk", "stem", "step", "stone", "storm", "streak", "stream", "strike", "stripe", "sun", "swipe", "swoop", "tail", "tree",
        "throat", "tuft", "watcher", "water", "whisper", "willow", "wind", "wing", "wish"]

    pelt_suffixes = {'TwoColour': ['patch', 'spot', 'splash', 'patch', 'spots'], 'Tabby': ['stripe', 'feather', 'leaf', 'stripe', 'shade'],
                     'Speckled': ['dapple', 'speckle', 'spot', 'speck'], 'Tortie': ['dapple', 'speckle', 'spot', 'dapple'], 'Calico': ['stripe', 'dapple', 'patch', 'patch']}

    normal_prefixes = ["Adder", "Alder", "Ant", "Apple", "Ash", "Acorn", "Arch", "Aspen", "Aster", "Bark", "Barley", "Bay", "Bee", "Badger", "Basil", "Bass", "Beetle",
                       "Beech", "Berry", "Bat", "Bayou", "Beaver", "Big", "Birch", "Bird", "Bite," "Bitter", "Bittern", "Bleak", "Blight", "Bliss", "Bloom", "Bluff", "Bog", "Bold",
                       "Borage", "Boulder", "Bounce", "Blossom", "Bracken", "Branch", "Brave", "Bramble", "Breeze", "Burdock", "Briar", "Bright", "Brindle", "Bristle",
                       "Broken", "Brook", "Brush", "Bubble", "Bubbling", "Buck", "Bug", "Bumble", "Buzzard", "Cedar", "Chaffinch", "Cherry", "Chestnut", "Chive", "Cicada",
                       "Cinder", "Cheetah", "Cinnamon", "Clay", "Cloud", "Clover", "Cobra", "Cold", "Crow", "Cedar", "Claw", "Clover", "Condor", "Conifer", "Copper", "Cone",
                       "Coyote", "Crab", "Crag", "Crane", "Creek", "Crested", "Cricket", "Crooked", "Crouch", "Crow", "Curl", "Curlew", "Curly", "Cypress", "Daisy", "Dapple",
                       "Dappled", "Dawn", "Dove", "Downy", "Drake", "Drought", "Dull", "Dusk", "Dust", "Dawn", "Dead", "Dew", "Doe", "Down", "Drift", "Duck", "Eagle", "Echo",
                       "Eel", "Egret", "Elm", "Ember", "Ermine", "Faded", "Fading", "Falcon", "Fallen", "Feather", "Fern", "Fennel", "Ferret", "Flame", "Flower", "Fallen",
                       "Fallow", "Fawn", "Fidget", "Fierce", "Fin", "Finch", "Flail", "Flutter", "Fir", "Flash", "Flax", "Fleck", "Fleet", "Flicker", "Flight", "Flint", "Flip",
                       "Fly", "Flood", "Flower", "Flurry", "Foam", "Forest", "Freckle", "Fringe", "Frog", "Frond", "Frost", "Furled", "Frozen", "Fuzzy", "Gander", "Gannet", "Gem",
                       "Giant", "Gill", "Goose", "Gorge", "Gorse", "Grass", "Gravel", "Grouse", "Gull", "Gust", "Hail", "Half", "Hare", "Harvest", "Hatch", "Hawk", "Hay", "Haze",
                       "Heath", "Heather", "Heavy", "Hen", "Heron", "Hickory", "Hill", "Hoarse", "Hollow", "Holly", "Hoot", "Hop", "Hope", "Hornet", "Hound", "Ice", "Ivy",
                       "Jagged", "Jasper", "Jay", "Jet", "Jump", "Juniper", "Kestrel", "Kink", "Kite", "Lake", "Larch", "Lark", "Laurel", "Lavender", "Leaf", "Leap", "Lichen",
                       "Leopard", "Light", "Lightning", "Lilac", "Lily", "Little", "Lizard", "Locust", "Log", "Long", "Lost", "Low", "Lynx", "Loud", "Mantis", "Maple", "Marigold",
                       "Marsh", "Marten", "Mole", "Moth", "Mouse", "Mallow", "Meadow", "Merry", "Midge", "Milk", "Mink", "Minnow", "Mint", "Mist", "Mistle", "Misty", "Mite",
                       "Mock", "Mole", "Moon", "Moor", "Morning", "Moss", "Mossy", "Moth", "Mottle", "Mottled", "Mouse", "Mud", "Mumble", "Murk", "Nacre", "Narrow", "Nectar",
                       "Needle", "Nettle", "Newt", "Night", "Nut", "Oak", "Oat", "Odd", "One", "Osprey", "Otter", "Owl", "Pale", "Pansy", "Panther", "Parsley", "Partridge",
                       "Patch", "Pear", "Peat", "Pebble", "Pepper", "Perch", "Petal", "Pheasant", "Plover", "Pigeon", "Pike", "Pine", "Piper", "Pod", "Poppy", "Posy", "Pounce",
                       "Prance", "Prickle", "Prim", "Puddle", "Python", "Quail", "Quick", "Quiet", "Quill", "Rabbit", "Raccoon", "Ragged", "Rambling", "Reed", "Ripple", "Ridge",
                       "Rift", "River", "Rain", "Raven", "Rat", "Rattle", "Robin", "Rock", "Rose", "Rowan", "Rubble", "Running", "Rush", "Roach", "Rot", "Rook", "Root", "Rye",
                       "Sage", "Sandy", "Scorch", "Sedge", "Sharp", "Shimmer", "Spring", "Strike", "Seed", "Shade", "Shell", "Short", "Shy", "Sky", "Slate", "Sleek", "Slight",
                       "Sloe", "Small", "Snail", "Sneeze", "Soft", "Song", "Spark", "Stoat", "Starling", "Shrew", "Smoke", "Snake", "Snip", "Soot", "Sparrow", "Speckle", "Spider",
                       "Scar", "Skip", "Stork", "Spire", "Sorrel", "Spike", "Splash", "Stag", "Swallow", "Swan", "Swamp", "Sweet", "Spotted", "Squirrel", "Storm", "Stone", "Swift",
                       "Tall", "Thistle", "Thrift", "Trout", "Tiger", "Tip", "Tulip", "Timber", "Twig", "Torn", "Tumble", "Turtle", "Thyme", "Vine", "Violet", "Vixen", "Vole",
                       "Web", "Wet", "Whisker", "Willow", "Wisteria", "Wasp", "Weasel", "Whirl", "Wild", "Yarrow", "Yew"]

    colour_prefixes = {'WHITE': ['White', 'White', 'Pale', 'Snow', 'Cloud', 'Milk', 'Hail', 'Frost', 'Ice', 'Sheep', 'Blizzard', 'Moon', 'Light', 'Bone'],
                       'PALEGREY': ['Grey', 'Silver', 'Pale', 'Cloud', 'Hail', 'Frost', 'Ice', 'Mouse', 'Bright', "Fog"],
                       'SILVER': ['Grey', 'Silver', 'Cinder', 'Ice', 'Frost', 'Rain', 'Blue', 'River', 'Blizzard', 'Bone'],
                       'GREY': ['Grey', 'Grey', 'Ash', 'Cinder', 'Rock', 'Stone', 'Shade', 'Mouse', 'Smoke', 'Shadow', "Fog", 'Bone'],
                       'DARKGREY': ['Grey', 'Shade', 'Raven', 'Crow', 'Stone', 'Dark', 'Night', 'Smoke', 'Shadow'],
                       'BLACK': ['Black', 'Black', 'Shade', 'Crow', 'Raven', 'Ebony', 'Dark', 'Night', 'Shadow', 'Scorch'],
                       'PALEGINGER': ['Sand', 'Yellow', 'Pale', 'Sun', 'Light', 'Lion', 'Bright', 'Honey', 'Daisy'],
                       'GOLDEN': ['Gold', 'Golden', 'Yellow', 'Sun', 'Light', 'Lightning', 'Thunder', 'Honey', 'Tawny', 'Lion', 'Dandelion'],
                       'GINGER': ['Red', 'Fire', 'Rust', 'Flame', 'Ember', 'Sun', 'Light', 'Rose', 'Rowan', 'Fox', 'Tawny', "Plum"],
                       'DARKGINGER': ['Red', 'Red', 'Fire', 'Rust', 'Flame', 'Oak', 'Shade', 'Russet', 'Rowan', 'Fox'],
                       'LIGHTBROWN': ['Brown', 'Pale', 'Light', 'Mouse', 'Dust', 'Sand', 'Bright', 'Mud', 'Hazel'],
                       'BROWN': ['Brown', 'Oak', 'Mouse', 'Dark', 'Shade', 'Russet', 'Stag', 'Acorn', 'Mud', "Deer"],
                       'DARKBROWN': ['Brown', 'Shade', 'Dark', 'Night', 'Russet', 'Rowan', 'Mud']}

    eye_prefixes = {'YELLOW': ['Yellow', 'Moon', 'Daisy', 'Honey', 'Light'], 'AMBER': ['Amber', 'Sun', 'Fire', 'Gold', 'Honey', 'Scorch'],
                    'HAZEL': ['Tawny', 'Hazel', 'Gold', 'Daisy', 'Sand'], 'PALEGREEN': ['Green', 'Pale', 'Mint', 'Fern', 'Weed'],
                    'GREEN': ['Green', 'Fern', 'Weed', 'Holly', 'Clover', 'Olive'], 'BLUE': ['Blue', 'Blue', 'Ice', 'Sky', 'Lake', 'Frost', 'Water'],
                    'DARKBLUE': ['Blue', 'Sky', 'Lake', 'Berry', 'Dark', 'Water', 'Deep'], 'BLUEYELLOW': ['Yellow', 'Blue', 'Odd', 'One', 'Moon'],
                    'BLUEGREEN': ['Green', 'Blue', 'Odd', 'One', 'Clover']}

    loner_names = ["Haku", "Pichi", "Poki", "Nagi", "Jubie", "Bonbon", "Beans", "Aurora", "Maleficent", "Luna", "Eclipse", "Sol", "Star", "George", "Nightmare", "Bagel", "Monster",
                   "Gargoyle", "Missile Launcher", "Rolo", "Rocket", "Void", "Abyss", "Vox", "Princess", "Noodle", "Duchess", "Cheesecake", "Callie", "Randy", "Ace", "Queeny",
                   "Freddy", "Stella", "Rooster", "Sophie", "Maverick", "Seamus", 'Meowyman', "Pickles", "Lacy", "Lucy", "Knox", "Lugnut", "Bailey", "Azula", "Lucky", "Sunny",
                   "Sadie", "Sox", "Bandit", "Onyx", "Quinn", "Grace", "Fang", "Ike", "Flower", "Whiskers", "Gust", "Peony", 'Human', "Minnie", "Buddy", "Mollie", "Jaxon",
                   "Dunnock", "Firefly", "Cheese", "Sandwich", "Spam", 'Brocolli', "Prickle", "Insect", "Grasshopper", "Coral", "Windy", "Sofa", "McChicken", "Katy Purry", 'Mop',
                   "Fishtail", "Roman", "Wishbone", "Nova", "Quimby", "Quest", "Nessie", "Niles", "Neil", "Nutella", "Nakeena", "Nuka", "Hughie", "Harvey", "Herc", "French",
                   "Finch", "Frannie", "Flutie", 'Purdy', "Free", "Glory", "Snek", "Indi", "Igor", "Jupiter", "Nintendo", "Jesse", "James", "Jethro", 'Shampoo', "Joker", "Jinx",
                   "Chaos", "Havoc", "Trouble", "Kingston", "King", "Kip", "Kong", "Ken", "Kendra", "Kisha", "Kermit", "Kelloggs", "Kodiak", "Klondike", "Ketchup", "KD", "Lupo",
                   "Luigi", "Lily", "Lora", "Lee", "Lex", "Lester", "Makwa", "Madi", "Minna", "Moxie", "Mucha", "Manda", "Monte", 'Riya', "Monzi", "Nisha", "Nemo", "Nitro", "Oops",
                   "O'Leary", "Ophelia", "Olga", "Oscar", "Owen", "Porsche", "Ping", "Pong", "Quinzee", "Quickie", "Quagmire", "Quake", "Quinoa", "Roomba", "Riot",
                   "Peanut Wigglebutt", "Ramble", "Rudolph", "Rum", "Reese", "Scotch", "Sneakers", "Schmidt", "Espresso", "Cocoa Puff", "Sonic", "Teufel", "Toni", "Toque",
                   "Tempest", "Turbo", "Tetris", "Triscuit", "Tumble", "Voltage", "Vinnie", "Vaxx", "Venture", "Vida", "Guinness", "Polly", "Piper", "Pepper", "Lakota", "Dakota",
                   "Bently", "Chinook", "Tiny", "Ula", "Union", "Uriel", "Orion", "Oakley", "Roselies", "Belle", "Benny", "Bumblebee", "Bluebell", "Chip", "Chocolate", "Cracker",
                   "Dave", "Dolly", "Egg", "Frito", "Frank", "Gibby", "Jack", "Jenny", "Juliet", "Joob", "John", "Jimmy", "Jude", "Kenny", "Tom", "Oreo", "Mocha", "Ninja",
                   "Cinderblock", "Pip", "Pipsqueak", "Milque", "Toast", "Molly Murder Mittens", "Flabby", "Crunchy", "Sorbet", "Vanilla", "Mint", "Niki", "Nikki", "Pocket",
                   "Tabbytha", "Gravy", "Potato", "Chewy", "Pumpernickel", "Pecan", "Old Man Sam", "Icecube", "Queso Ruby", "Pearl", "Jasper", "Stan", "Rose", "Mojo", "Kate",
                   "Carmen", "Mange", "Chase", "Socks", "Tabby", "Jay", "Charlie", "L", "Poopy", "Crunchwrap", "Meow-meow", "Bede", "Smores", "Evilface", "Nick", "Mitski", "Ash",
                   "Ah", "Violet", "Alcina", "Worm", "Monika", "Rat", "Bongo", "Bunny", "Viktor", "Steve", "Jewels", "Blu", "Rue", "Stinky", "Garnet", "Anita", "Sloane", "Emi",
                   "Vivienne", "Amber", "Moon", "Twilight", "River", "Glass", "Goose", "Hunter", "Amity", "Stripes", "Cowbell", "Rory", "Lobster", "Slug", "Starfish", "Salmon",
                   "Judy", "Johnny", "Kerry", "Evelyn", "Holly", "Bolt", "Millie", "Jessica", "Laku", "Dragonfly", "X’ek", "Silva", "Dreamy", "Decay", "Twister", "Shay", "Louis",
                   "Oleander", "Spots", "Cream", "Omlet", "Gizmo", "Feather", "Twix", "Silver,", "Ghost", "Wisp", "Obi Wan", 'Pikachu', "Mango", "Via", "Olivia", "Mr. Whiskers",
                   "Fluffy", "Shimmer", "Mimi", "Melody", "Leon", "Punk", "Mew", "Fern", "Marceline", "Whisper", "Skrunkly", "Stolas", "Rio", "Steven", "Pear", "Sekhmet", "Mellon",
                   "Ember", "Loona", "Saki", "Tiny", "Sandy", "Miles", "Mini", "Judas", "Zim", "Vinyl", "Rarity", "Trixie", "Sunset", "Anubis", "Armin", "Amy", "Alice", "Alec",
                   "Baphomet", "Bean", "Bastet", "Birb", "Burm", "Chrissy", "Cherry", "Chief", "Crow", "Carrie", "Calvin", "Cookie", "Catie", "Charm", "Crab", "Charles",
                   "Caroline", "Conan", "Cloud", "Charlie", "Cowboy", 'Burger', "Dune", "Dan", "Delilah", "Emerald", "Emy", "Erica", " Eddie", "Eda", "Ferret", "Fawn", "Fiver",
                   "Fallow", "Ferry", "Gamble", "Grain", "Gir", "Hop", "Hot Sauce", "Habanero", "Taco Bell", "Cheetoman"]

    if os.path.exists('saves/prefixlist.txt'):
        with open('saves/prefixlist.txt', 'r') as read_file:
            name_list = read_file.read()
            if_names = len(name_list)
        if if_names > 0:
            new_names = name_list.split('\n')
            for new_name in new_names:
                if new_name != '':
                    normal_prefixes.append(new_name)

    if os.path.exists('saves/suffixlist.txt'):
        with open('saves/suffixlist.txt', 'r') as read_file:
            name_list = read_file.read()
            if_names = len(name_list)
        if if_names > 0:
            new_names = name_list.split('\n')
            for new_name in new_names:
                if new_name != '':
                    normal_suffixes.append(new_name)

    def __init__(self, status="warrior", prefix=None, suffix=None, colour=None, eyes=None, pelt=None):
        self.status = status
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
