import random
import os


class Name(object):
    special_suffixes = {"kitten": "kit", "apprentice": "paw", "medicine cat apprentice": "paw", "leader": "star"}
    normal_suffixes = [  # common suffixes
        "fur", "fur", "fur", "fur", "fur", "fur", "fur", "fur", "fur", "fur", 'fur', 'fur', 'pelt', "pelt", "pelt", "pelt", "pelt", "pelt", "pelt", "pelt", "pelt", "pelt", "tail", "tail", "tail",
        "tail", "tail", "tail", "tail", "tail", "claw", "claw", "claw", "claw", "claw", "claw", "claw", "foot", "foot", "foot", "foot", "foot", "whisker", "whisker", "whisker",
        "whisker", "heart", "heart", "heart", "heart", "heart", 'heart',

        # regular suffixes
        "acorn", "ash", "aster", "back", "beam", "bee", "belly", "berry", "bite",
        "bird", "blaze", "blink", "blossom", "bloom", "blotch", "bounce", "branch", "breeze", "briar",
        "brook", "burr", "bush", "call", "cloud", "clover", "coral", "creek", "cry", "dance", "dapple", "daisy",
        "dawn", "dew", "drift", "drop", "dusk", "dust", "eagle", "ear", "ears", "eye", "eyes", "face", "fall", "fang",
        "falcon", "feather", "fern", "fin", "fire", "fish", "flame", "flight", "flood", "flower",
        "frost", "fog", "frog", "furze", "gaze", "goose", "gorse", "grass", "hail", "hare", "hawk", "haze", "heron",
        "heather", "holly", "hollow", "horse", "ice", "ivy", "jaguar", "jaw", "jay", "jump", "kestrel", "kite", "lake", "larch", "leaf",
        "leap", "leg", "light", "lilac", "lily", "lion", "lotus", "lynx", "mask", "mist", "moth", "moon", "mouse",
        "needle", "nettle", "newt", "night", "noise", "nose", "pad", "path", "patch", "petal",
        "pond", "pool", "poppy", "pounce", "puddle", "rapid", "ripple", "rose", "rump", "run", "runner",
        "scar", "seed", "shade", "shadow", "shell", "shine", "sight", "skip", "sky", "slip", "snow", "smog",
        "song", "spark", "speck", "speckle", "spirit", "splash", "splashed", "spot", "spots", "spring",
        "stalk", "stem", "step", "stone", "storm", "streak", "stream", "strike", "stripe", "sun",
        "swipe", "swoop", "tail", "talon", "tiger", "tree", "thicket", "throat", "thorn", "thrush", "tooth", "toad", "tuft",
        "wave", "watcher", "water", "whisper", "whiskers", "willow", "wind", "wing", "wish",
        "flip", "loop", "curl", "catcher", "catch", "chase", "bone", "chirp", "crouch", "crest", "dash", "drizzle", "flash",
        "flail", "flare", "hoot", "mouth", "muzzle", "nest", "rise", "ridge", "rattle", "roar", "rumble", "screech",
        "sap", "drip", "thistle", "shiver", "chill", "trail", "wisp", "whistle", "gale", "fisher", "tang", "char",
        "petrel", "plover", "martin", "tern", "carp", "bream", "flow", "torrent", "moss", "lichen", "sprout", "burn",
        "air", "breath", "blur", "wuther", "drought", "tusk", "cheetah", "leopard", "sting", "howl", "peak", "hiss", "prowl",
        "swing", "sizzle", "dream", "snarl", "scale", "prance", "lash", "snout", "coil"]

    pelt_suffixes = {'TwoColour': ['patch', 'spot', 'splash', 'patch', 'spots', 'panda'],
                     'Tortie': ['blossom', 'dapple', 'speckle', 'spot', 'spots', 'dapple', 'lynx', 'jaguar', 'drizzle'],
                     'Calico': ['stripe', 'dapple', 'patch', 'spots', 'patch', 'lynx']}

    normal_prefixes = ["Adder", "Alder", "Ant", "Apple", "Ash", "Acorn", "Arch", "Aspen", "Bat", "Bark", "Bay", "Bee",
                       "Badger", "Bear", "Beetle", "Beech", "Berry", "Big", "Birch", "Bird", "Bloom", "Boulder", "Bounce", "Blaze",
                       "Blossom", "Boar", "Bracken", "Branch", "Brave", "Bramble", "Briar", "Bright", "Brindle", "Bristle",
                       "Breeze", "Broken", "Brook", "Bug", "Bumble", "Buzzard", "Cactus", "Camel", "Cherry", "Chestnut", "Chive", "Cinder",
                       "Cinnamon", "Cloud", "Cold", "Cobra", "Crow", "Cedar", "Claw", "Cliff", "Clover", "Copper", "Cone",
                       "Creek", "Cricket", "Crooked", "Crouch", "Curl", "Curly", "Cypress", "Dapple", "Dappled", "Dove", "Dusk",
                       "Dust", "Damp", "Dawn", "Dead", "Dew", "Doe", "Down", "Drift", "Duck", "Eagle", "Echo", "Eel", "Elm",
                       "Ember", "Freckle", "Fringe", "Feather", "Fern", "Fennel", "Ferret", "Flame", "Flower", "Faded", "Fading",
                       "Falcon", "Fallen", "Fallow", "Fawn", "Fin", "Finch", "Fish", "Flail", "Flip", "Flutter", "Fir", "Frog", "Frond", "Flash",
                       "Flax", "Fleet", "Flicker", "Flint", "Fly", "Flight", "Furz", "Fuzzy", "Goat", "Goose", "Gorse",
                       "Grass", "Gravel", "Gull", "Hail", "Hare", "Hay", "Hatch", "Half", "Hawk", "Heather", "Heavy", "Heron", "Hickory", "Hill",
                       "Hollow", "Hoot", "Hog", "Hop", "Hope", "Horse", "Hound", "Holly", "Hush", "Ivy", "Jade", "Jagged", "Jay", "Jump", "Juniper",
                       "Kestrel", "Kink", "Kite", "Lake", "Lark", "Larch", "Lavender", "Leaf", "Lichen", "Leopard",
                       "Lightning", "Lily", "Lizard", "Log", "Lotus", "Lost", "Low", "Lynx", "Little", "Long", "Loud", "Maggot", "Marsh",
                       "Marigold", "Marten", "Maple", "Mole", "Moth", "Mouse", "Mallow", "Mellow", "Meadow", "Midge", "Minnow",
                       "Mink", "Mint", "Mist", "Mistle", "Misty", "Morning", "Moss", "Mossy", "Mottle", "Mountain", "Mud", "Muddy", "Mumble",
                       "Nectar", "Night", "Nettle", "Nut", "Needle", "Newt", "Oat", "Odd", "Oak", "One", "Otter", "Osprey", "Ox", "Owl",
                       "Parsley", "Patch", "Pear", "Petal", "Pebble", "Perch", "Pigeon", "Pike", "Pine", "Pod", "Pool", "Poppy",
                       "Pounce", "Prickle", "Puddle", "Quail", "Quick", "Quiet", "Rabbit", "Raccoon", "Ragged", "Reed", "Ripple", "Ridge",
                       "River", "Rain", "Raven", "Rat", "Robin", "Rock", "Rose", "Rowan", "Rubble", "Running", "Rush",
                       "Rook", "Root", "Rye", "Sable", "Sage", "Sandy", "Scorch", "Silent", "Sea", "Sedge", "Shallow", "Sharp", "Shimmer", "Shine", "Shining",
                       "Sloe", "Slow", "Smog", "Spring", "Strike", "Seed", "Silent", "Shade", "Shell", "Short", "Shy", "Sky", "Sleek", "Slight",
                       "Small", "Snail", "Sneeze", "Soft", "Somber", "Song", "Spark", "Stoat", "Starling", "Stumpy", "Shrew", "Smoke", "Skunk",
                       "Snake", "Snip", "Soot", "Sparrow", "Speckle", "Spider", "Sprout", "Spruce", "Scar", "Skip", "Stork", "Spire",
                       "Sorrel", "Spike", "Splash", "Stag", "Swallow", "Swan", "Swamp", "Sweet", "Spotted", "Squirrel",
                       "Storm", "Stone", "Swift", "Tall", "Talon", "Tangle", "Tansy", "Thorn", "Thicket", "Thistle", "Thrift", "Thrush", "Trout",
                       "Tiger", "Tulip", "Timber", "Twig", "Toad", "Torn", "Tumble", "Turtle", "Tree", "Vine", "Violet", "Viper", "Vixen",
                       "Vole", "Wave", "Web", "Wet", "Whisker", "Willow", "Wasp", "Weasel", "Whirl", "Wild", "Wolf", "Yarrow", "Yew", "Yucca",
                       "Panther", "Jaguar", "Civet", "Bass", "Cave", "Chill", "Dance", "Basil", "Burr", "Bubble", "Wool",
                       "Bush", "Butterfly", "Carrot", "Coyote", "Cobweb", "Dog", "Dragonfly", "Drizzle", "Drizzled", "Flood", "Gorge", "Flare",
                       "Hive", "Horn", "Hawthorn", "Jasmine", "Emerald", "Gem", "Jewel", "Crystal", "Jackdaw", "Lilac", "Laurel", "Moor",
                       "Nest", "Pond", "Primrose", "Pumpkin", "Quill", "Rising", "Rosemary", "Rattle", "Roar", "Roaring", "Rumbling", "Shatter", "Stem",
                       "Stalking", "Sap", "Drip", "Tadpole", "Shiver", "Tremble", "Tunnel", "Valley", "Vulture", "Wisp", "Whistle", "Wren", "Wood",
                       "Hurricane", "Tornado", "Whirlpool", "Gale", "Torrent", "Current", "Shark", "Oyster", "Orca", "Whale", "Dolphin",
                       "Pink", "Velvet", "Salt", "Pepper", "Wheat", "Turkey", "Chickadee", "Pheasant", "Grouse", "Ibis", "Crane", "Egret", "Humming",
                       "Ostrich", "Savannah", "Macaw", "Parrot", "Albatross", "Cormorant", "Pelican", "Petrel", "Plover", "Martin", "Tern", "Bull",
                       "Carp", "Bream", "Herring", "Flounder", "Shrimp", "Crab", "Tuna", "Mullet", "Buffalo", "Hyena", "Caracal", "Forest", "Jungle",
                       "Canopy", "Margay", "Maroon", "Charr", "Peach", "Clam", "Cockle", "Squid", "Octopus", "Conch", "Abalon", "Urchin", "Salmon", "Cucumber",
                       "Mustard", "Cyan", "Teal", "Peacock", "Crocodile", "Alligator", "Scorpion", "Leech", "Raspberry", "Flamingo", "Carnation", "Eggplant",
                       "Grape", "Lemon", "Lime", "Orchid", "Seal", "Pewter", "Magma", "Lava", "Tea", "Artichoke", "Spice", "Burn",
                       "Blood", "Air", "Cornflower", "Peat", "Peanut", "Walnut", "Pecan", "Turquoise", "Twilight", "Noon", "Silk", "Puff", "Puffin", "Papaya",
                       "Bronze", "Monkey", "Cape", "Gulf", "Blur", "Blurry", "Blurred", "Wuther", "Land", "Dune", "Desert", "Dry", "Drought", "Bill", "Tusk",
                       "Antelope", "Tapir", "Koala", "Moose", "Panda", "Elk", "Gemsbok", "Opossum", "Okapi", "Ocelot", "Musk", "Oryx", "Sloth", "Cheetah",
                       "Froggy", "Sting", "Stinger", "Howl", "Peak", "Hiss", "Melody", "Hoof", "Spur", "Prowl", "Prowling", "Dream", "Dreamy", "Scale",
                       "Prance", "Addax", "Balm", "Iris", "Indigo"]

    colour_prefixes = {'WHITE': ['White', 'White', 'Pale', 'Snow', 'Cloud', 'Milk', 'Hail', 'Frost', 'Ice',
                                 'Sheep', 'Blizzard', 'Moon', 'Light', 'Ivory', 'Egg', 'Foam', 'Bone', 'Cotton', 'Wool',
                                 'Pearl', 'Pearly', 'Crystal', 'Avalanche'],
                       'PALEGREY': ['Grey', 'Silver', 'Pale', 'Cloud', 'Hail', 'Frost', 'Ice', 'Mouse', 'Bright', 'Mist',
                                    'Fog', 'Ivory', 'Foam', 'Bone', 'Moon'],
                       'SILVER': ['Grey', 'Silver', 'Cinder', 'Ice', 'Frost', 'Rain', 'Blue', 'River', 'Blizzard', 'Ivory',
                                  'Pewter', 'Moon'],
                       'GREY': ['Grey', 'Grey', 'Ash', 'Cinder', 'Rock', 'Stone', 'Shade', 'Mist', 'Misty', 'Pewter',
                                'Mouse', 'Smoke', 'Shadow', 'Fog', 'Slate'],
                       'DARKGREY': ['Grey', 'Shade', 'Raven', 'Crow', 'Stone', 'Dark', 'Night', 'Smoke', 'Shadow', 'Dusk', 'Slate', 'Pepper',
                                    'Char', 'Charred', 'Burn', 'Burnt'],
                       'BLACK': ['Black', 'Black', 'Shade', 'Crow', 'Coal', 'Raven', 'Ebony', 'Dark', 'Night', 'Charcoal',
                                 'Shadow', 'Scorch', 'Dusk', 'Storm', 'Slate', 'Bat', 'Sable', 'Panther', 'Pepper', 'Char', 'Charred',
                                 'Burn', 'Burnt', 'Onyx', "Midnight", "Skunk"],
                       'PALEGINGER': ['Sand', 'Sandy', 'Yellow', 'Pale', 'Sun', 'Light', 'Lion', 'Bright', 'Honey', 'Daisy', 'Dawn',
                                      'Ivory', 'Egg', 'Bone', 'Pearl', 'Pearly', 'Wheat', 'Peach', 'Beige'],
                       'GOLDEN': ['Gold', 'Golden', 'Yellow', 'Sun', 'Light', 'Lightning', 'Thunder', 'Honey', 'Tawny',
                                  'Lemon', 'Lion', 'Dandelion', 'Dawn', 'Wheat', 'Mustard', 'Ochre'],
                       'GINGER': ['Red', 'Fire', 'Rust', 'Flame', 'Ember', 'Sun', 'Light', 'Rose', 'Rowan', 'Fox', 'Crimson',
                                  'Tawny', 'Plum', 'Carrot', 'Magma', 'Lava', 'Ochre', 'Tangerine', 'Apricot', 'Scarlet'],
                       'DARKGINGER': ['Red', 'Red', 'Fire', 'Rust', 'Flame', 'Oak', 'Shade', 'Russet', 'Rowan', 'Fox', 'Maroon', 'Magma', 'Lava',
                                      'Tangerine', 'Burn', 'Burnt', 'Crimson', 'Scarlet'],
                       'LIGHTBROWN': ['Brown', 'Pale', 'Light', 'Mouse', 'Dust', 'Sand', 'Sandy', 'Bright', 'Mud', 'Hazel', 'Dawn', 'Egg'],
                       'BROWN': ['Brown', 'Bark', 'Oak', 'Mouse', 'Dark', 'Shade', 'Russet', 'Stag', 'Acorn', 'Mud', 'Turkey', 'Quail',
                                 'Muddy', 'Deer', 'Dusk', 'Wood', 'Timber', 'Tan'],
                       'DARKBROWN': ['Brown', 'Bark', 'Shade', 'Dark', 'Night', 'Russet', 'Rowan', 'Mud', 'Muddy',
                                     'Dusk', 'Wood', 'Timber', 'Char', 'Charred', 'Burn', 'Burnt', 'Tan']}
                                     
    marking_prefixes = {'Solid': ['Claw', 'Tall', 'One', 'Rain', 'Apple', 'Beech', 'Gorse', 'Hawk', 'Feather', 'Ivy', 'Jay', 'Kestrel',
                                  'Leaf', 'Moss', 'Owl', 'Petal', 'Thistle', 'Vole', 'Shrew', 'Yew'],
                        'Ticked': ['Striped', 'Stripe', 'Shade', 'Shaded', 'Drizzle', 'Wild'],
                        'Tabby': ['Striped', 'Feather', 'Leaf', 'Stripe', 'Shade', 'Tiger', 'Drizzle'],
                        'Speckled': ['Blossom', 'Dappled', 'Speckle', 'Spot', 'Spotted', 'Ripple', 'Jaguar', 'Leopard', 'Cheetah' 'Drizzle'],
                        'Marbled': ['Striped', 'Feather', 'Stripe', 'Shade', 'Jaguar', 'Leopard', 'Cheetah', 'Drizzle'],
                        'Rosette': ['Striped', 'Feather', 'Leaf', 'Stripe', 'Shade', 'Tiger', 'Drizzle'],
                        'TickedAbyss': ['Striped', 'Stripe', 'Shade', 'Shaded', 'Drizzle', 'Wild']}

    eye_prefixes = {'YELLOW': ['Yellow', 'Moon', 'Daisy', 'Honey', 'Light', 'Dawn', 'Lemon', 'Dandelion', 'Wheat', 'Mustard'],
                    'AMBER': ['Amber', 'Sun', 'Fire', 'Gold', 'Honey', 'Scorch', 'Copper', 'Ochre', 'Bronze'],
                    'HAZEL': ['Tawny', 'Hazel', 'Gold', 'Daisy', 'Sand', 'Jasmine'],
                    'PALEGREEN': ['Green', 'Pale', 'Mint', 'Fern', 'Weed', 'Basil', 'Chive', 'Jasmine', 'Turquoise'],
                    'GREEN': ['Green', 'Fern', 'Weed', 'Holly', 'Leaf', 'Clover', 'Olive', 'Jade', 'Basil', 'Emerald'],
                    'BLUE': ['Blue', 'Blue', 'Ice', 'Sky', 'Lake', 'Frost', 'Water', 'Pool', 'Rain', 'Sea', 'Wave', 'Foam'],
                    'DARKBLUE': ['Blue', 'Sky', 'Lake', 'Berry', 'Dark', 'Water', 'Deep', 'Pool', 'Rain', 'Sea', 'Wave'],
                    'BLUEYELLOW': ['Yellow', 'Blue', 'Odd', 'One', 'Moon', 'Spire', 'Rainbow', 'Half', 'Gem', 'Jewel'],
                    'BLUEGREEN': ['Green', 'Blue', 'Odd', 'One', 'Clover', 'Spire', 'Rainbow', 'Half', 'Gem', 'Jewel']}

    loner_names = ["Haku", "Pichi", "Poki", "Nagi", "Jubie", "Bonbon", "Beans", "Aurora", "Maleficent", "Luna",
                   "Eclipse", "Sol", "Star", "George", "Nightmare", "Bagel", "Monster", "Gargoyle", "Missile Launcher",
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
                   "Ramble", "Rudolph", "Rum", "Rye", "Reese", "Snow", "Sprout", "Spruce", "Scotch", "Sneakers", "Schmidt",
                   "Sonic", "Teufel", "Toni", "Toque", "Tempest", "Turbo", "Tetris", "Triscuit", "Tumble", "Voltage",
                   "Vinnie", "Vaxx", "Venture", "Vida", "Guinness", "Polly", "Piper", "Pepper", "Lakota", "Dakota",
                   "Bently", "Chinook", "Tiny", "Ula", "Union", "Uriel", "Orion", "Oakley", "Roeseii", "Belle", "Benny",
                   "Bumblebee", "Bluebell", "Chip", "Chocolate", "Cracker", "Dave", "Dolly", "Egg", "Frito", "Frank",
                   "Gibby", "Jack", "Jenny", "Juliet", "Joob", "John", "Jimmy", "Jude", "Kenny", "Tom", "Oreo", "Mocha",
                   "Ninja", "Rock", "Pip", "Pipsqueak", "Milquetoast", "Molly Murder Mittens", "Vulture", "Raven",
                   "Sorbet", "Vanilla", "Mint", "Niki", "Nikki", "Pocket", "Tabbytha", "Gravy", "Potato",
                   "Pumpernickel", "Pecan", "Old Man Sam", "Icecube", "Queso", "Ruby", "Pearly", "Jasper", "Stan", "Rose",
                   "Mojo", "Kate", "Carmen", "Mange", "Sir Earl Picked the Third", "Socks", "Tabby", "Jay", "Charlie",
                   "Crunchwrap", "Meow-meow", "Bede", "Smores", "Evilface", "Nick", "Mitski", "Ash", "Ah", "Violet",
                   "Alcina", "Worm", "Monika", "Rat", "Bongo", "Bunny", "Viktor", "Steve", "Jewels", "Blu", "Rue",
                   "Stinky", "Garnet", "Anita", "Sloane", "Emi", "Vivienne", "Ambers", "Moon", "Twilight", "River",
                   "Glass", "Goose", "Hunter", "Amity", "Stripes", "Cowbell", "Rory", "Lobster", "Slug", "Starfish",
                   "Salmon", "Judy", "Johnny", "Kerry", "Evelyn", "Holly", "Bolt", "Millie", "Jessica", "Laku",
                   "Dragonfly", "X’ek", "Silva", "DreamyDecay", "Twister", "Shay", "Louis", "Oleander", "Spots",
                   "Cream", "Omlet", "Gizmo", "Feather", "Twix", "Silver", "Ghost", "Wisp", "Obi Wan", "Pearl,",
                   "Mango", "Via", "Olivia", "Mr. Whiskers", "Fluffy", "Shimmer", "Mimi", "Melody", "Leon", "Punk",
                   "Mew", "Fern", "Marceline", "Whisper", "Skrunkly", "Stolas", "Rio", "Steven", "Pear", "Sekhmet",
                   "Mellon", "Ember", "Loona", "Saki", "Tiny", "Sandy", "Miles", "Mini", "Judas", "Zim", "Vinyl",
                   "Rarity", "Trixie", "Sunset", "Anubis", "Armin", "Amy", "Alice", "Alec", "Baphomet", "Bean",
                   "Bastet, Birb", "Bee", "Burm", "Chrissy", "Cherry", "Chief", "Crow", "Carrie", "Calvin", "Cookie",
                   "Catie", "Charm", "Crane", "Crab", "Charles", "Caroline", "Conan", "Cloud", "Charlie", "Cowboy",
                   "Dune", "Dan", "Dove", "Delilah", "Emerald", "Emy", "Erica", " Eddie", "Eda", "Ferret", "Fawn",
                   "Fallow", "Ferry", "Gramble", "Grain", "Gir", "Herron", "Hop", "Honey", "Hot Sauce", "Habanero",
                   "Ivory", "Mountain", "Rusty", "Wolf", "Bear", "Ocelot", "Gorilla", "Caramel", "Caracal", "Okapi",
                   "Bob", "Chase", "Pancake", "Bacon", "Toast", "Butter", "Hawthorn", "Jasmine", "Esmeralda", "Pinecone",
                   "Duke", "Prince", "Queen", "Queenie", "Lady", "Tadpole", "Typhoon", "Tsunami", "Velvet", "Cashmere",
                   "Africa", "America", "Tuna", "Peach", "Diamond", "Sapphire", "Amethyst", "Peridot", "Jellyfish", "Lollipop",
                   "Bubble Gum", "Gum", "Lemondrop", "Orange", "Steel", "Hammer", "Saw", "Anchor", "Sail", "Sailor", "Captain",
                   "Harbor", "Port", "Iron", "Cider", "Taffy", "Marshmellow", "Cotton Candy", "Sugar", "Sugar Rush", "Eggnog",
                   "Pineapple", "Pen Pineapple Apple Pen", "Banana", "Pudding", "Banana Bread", "Cyber", "Corn", "Denim", "Aang",
                   "Maya", "Phoenix", "Dragon", "Gryphon", "Navy", "Azure", "Space", "Neptune", "Aries", "Saturn", "Demeter", "Aphrodite",
                   "Eros", "Pluto", "Cupid", "Baby", "Kylo Ren", "Darth Vader", "Taco", "Tortilla", "R2D2", "C3PO", "Espresso", "Latte",
                   "Coffee", "Syrup", "Umber", "Tomato", "Moccasin", "Chiffon", "Goldenrod", "Sepia", "India", "Sienna", "Prancer", "Billy"]

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

    def __init__(self, status="warrior", prefix=None, suffix=None, colour=None, eyes=None, pelt=None, markings=None):
        self.status = status
        if prefix is None:
            if colour is None and eyes is None and markings is None:
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
            elif markings is None:
                a = random.randint(0, 5)
                if a != 1:
                    self.prefix = random.choice(self.normal_prefixes)
                else:
                    self.prefix = random.choice(self.marking_prefixes[markings])
            else:
                a = random.randint(0, 7)
                if a == 1:
                    self.prefix = random.choice(self.colour_prefixes[colour])
                elif a == 2:
                    self.prefix = random.choice(self.eye_prefixes[eyes])
                elif a == 3:
                    self.prefix = random.choice(self.marking_prefixes[markings])
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
