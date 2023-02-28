import random
import os


class Name():
    special_suffixes = {
        "kitten": "kit",
        "apprentice": "paw",
        "medicine cat apprentice": "paw",
        "mediator apprentice": "paw",
        "leader": "star"
    }
    normal_suffixes = [  # common suffixes
        "fur", "fur", "fur", "fur", "fur", "fur", "fur", "fur", "fur", "fur", 'fur', 'fur', 'fur',
        "tuft", "tuft", "tuft", "tuft", "tuft", "tooth", "tooth", "tooth", "tooth", "tooth",
        'pelt', "pelt", "pelt", "pelt", "pelt", "pelt", "pelt", "pelt", "pelt", "pelt", "pelt", "pelt", "pelt",
        "tail", "tail", "tail", "tail", "tail", "tail", "tail", "tail", "claw", "claw", "claw", "claw", "claw", "claw", "claw",
        "foot", "foot", "foot", "foot", "foot", "whisker", "whisker", "whisker", "whisker", "whisker", "whisker",
        "heart", "heart", "heart", "heart", "heart", "heart", "heart", "heart", "heart", 'heart',

        # regular suffixes
        "acorn", "ash", "aster", "back", "bark", "beam", "bee", "belly", "berry", "bite", "bird", "blaze", "blink", "bloom", 
        "blossom", "blotch", "bounce", "bracken", "branch", "breeze", "briar", "bright", "brook", "burr", "burrow", "bush", "call",
        "catcher", "cloud", "clover", "crawl", "creek", "cry", "dapple", "daisy", "dawn", "drift", "drop", "dusk", "dust",
        "ear", "ears", "eater", "eye", "eyes", "face", "fall", "fang", "fawn", "feather", "fern", "fin", "fire", "fish", "flake",
        "flame", "flight", "flick", "flood", "flower", "fox", "frost", "gaze", "goose", "gorse", "grass", "hail", "hare", "hawk", "haze",
        "heather", "hollow", "holly", "horse", "ice", "ivy", "jaw", "jay", "jump", "kite", "lake", "larch", "leaf", "leap", 
        "leaves", "leg", "light", "lightning", "lilac", "lily", "lotus", "mask", "mark", "minnow", "mist", "moth", "moon", "moss", "mouse",
        "muzzle", "needle", "nettle", "night", "noise", "nose", "nut", "pad", "patch", "path", "peak", "petal", "plume", "pond",
        "pool", "poppy", "pounce", "puddle", "rain", "rapid", "ripple", "river", "roar", "rose", "rump", "run", "runner", "scar",
        "scratch", "seed", "shade", "shadow", "shell", "shine", "sight", "skip", "sky", "slip", "snout", "snow", "song", "spark",
        "speck", "speckle", "spirit", "splash", "spot", "spots", "spring", "stalk", "stem", "step", "stone", "storm", "streak",
        "stream", "strike", "stripe", "sun", "swipe", "swoop", "talon", "tooth", "thistle", "thorn", "throat", "toe", "tree", 
        "throat", "watcher", "water", "wave", "whisper", "whistle", "willow", "wind", "wing", "wish"
    ]

    pelt_suffixes = {
        'TwoColour': ['patch', 'spot', 'splash', 'patch', 'spots'],
        'Tabby': ['stripe', 'feather', 'leaf', 'stripe', 'shade'],
        'Marbled': ['stripe', 'feather', 'leaf', 'stripe', 'shade'],
        'Speckled': ['dapple', 'speckle', 'spot', 'speck', 'freckle'],
        'Bengal': ['dapple', 'speckle', 'spots', 'speck', 'freckle'],
        'Tortie': ['dapple', 'speckle', 'spot', 'dapple'],
        'Rosette': ['dapple', 'speckle', 'spots', 'dapple', 'freckle'],
        'Calico': ['stripe', 'dapple', 'patch', 'patch'],
        'Smoke': ['fade', 'dusk', 'dawn', 'smoke'],
        'Ticked': ['spots', 'pelt', 'speckle', 'freckle'],
        'Mackerel': ['stripe', 'feather', 'leaf', 'stripe', 'fern'],
        'Classic': ['stripe', 'feather', 'leaf', 'stripe', 'fern'],
        'Sokoke': ['stripe', 'feather', 'leaf', 'stripe', 'fern'],
        'Agouti': ['back', 'pelt', 'fur'],
        'Singlestripe': ['stripe', 'streak', 'back', 'shade', "stem", "shadow"]
    }

    tortie_pelt_suffixes = {
        'tortiesolid': ['dapple', 'speckle', 'spots', 'splash'],
        'tortietabby': ['stripe', 'feather', 'leaf', 'stripe', 'shade', 'fern'],
        'tortiebengal': ['dapple', 'speckle', 'spots', 'speck', 'fern', 'freckle'],
        'tortiemarbled': ['stripe', 'feather', 'leaf', 'stripe', 'shade', 'fern'],
        'tortieticked': ['spots', 'pelt', 'speckle', 'freckle'],
        'tortiesmoke': ['fade', 'dusk', 'dawn', 'smoke'],
        'tortierosette': ['dapple', 'speckle', 'spots', 'dapple', 'fern', 'freckle'],
        'tortiespeckled': ['dapple', 'speckle', 'spot', 'speck', 'freckle'],
        'tortiemackerel': ['stripe', 'feather', 'fern', 'shade'],
        'tortieclassic': ['stripe', 'feather', 'fern'],
        'tortiesokoke': ['stripe', 'feather', 'fern', 'shade', 'dapple'],
        'tortieagouti': ['back', 'pelt', 'fur', 'dapple', 'splash']
    }

    normal_prefixes = [
        'Adder', 'Alder', 'Ant', 'Antler', 'Apple', 'Apricot', 'Arc', 'Arch', 'Aspen', 'Aster', 
        'Badger', 'Barley', 'Basil', 'Bass', 'Bay', 'Bayou', 'Beam', 'Bear', 'Beaver', 'Bee', 'Beech', 'Beetle', 'Berry',
        'Big', 'Birch', 'Bird', 'Bite', 'Bitter', 'Bittern', 'Blizzard', 'Bloom',
        'Blossom', 'Blotch', 'Bluebell', 'Bluff', 'Bog', 'Borage', 'Bough', 'Boulder', 'Bounce', 'Bracken', 'Bramble', 
        'Brave', 'Breeze', 'Briar', 'Bright', 'Brindle', 'Bristle', 'Broken', 'Brook', 'Broom', 'Brush', 'Bubbling', 'Buck',
        'Bug', 'Bumble', 'Burdock', 'Burr', 'Bush', 'Buzzard', 'Carp', 'Cave', 'Cedar', 'Chaffinch', 'Chasing', 'Cherry',
        'Chestnut', 'Chive', 'Cicada', 'Claw', 'Clay', 'Clear', 'Cliff', 'Clover', 'Condor', 
        'Cone', 'Conifer', 'Cougar', 'Cow', 'Coyote', 'Crag', 'Crane', 'Creek', 'Cress', 'Crested', 'Cricket', 'Crooked',
        'Crouch', 'Curl', 'Curlew', 'Curly', 'Cypress', 'Dahlia', 'Daisy', 'Damp', 'Dancing', 'Dandelion', 'Dapple', 'Dappled',
        'Dawn', 'Deer', 'Dew', 'Doe', 'Dog', 'Down', 'Downy', 'Drift', 
        'Drizzle', 'Dry', 'Duck', 'Dusk', 'Eagle', 'Echo', 'Egret', 'Elder', 'Elm', 
        'Ermine', 'Falcon', 'Fallen', 'Falling', 'Fallow', 'Fawn', 'Feather', 'Fennel', 'Fern', 
        'Ferret', 'Fidget', 'Fin', 'Finch', 'Fir', 'Fish', 'Flail', 'Flash', 'Flax', 'Fleck', 'Fleet', 'Flicker', 
        'Flight', 'Flint', 'Flip', 'Flood', 'Flower', 'Flutter', 'Fly', 'Fog', 'Forest', 'Freckle', 'Fringe',
        'Frog', 'Frond', 'Furled', 'Furze', 'Fuzzy', 'Gale', 'Gander', 'Gannet', 'Garlic', 'Goose',
        'Gorge', 'Gorse', 'Grass', 'Gravel', 'Grouse', 'Gull', 'Gust', 'Hail', 'Half', 'Hare',
        'Hatch', 'Haven', 'Hawk', 'Hay', 'Hazel', 'Heath', 'Heavy', 'Heron', 'Hill', 'Hollow', 'Holly',
        'Honey', 'Hoot', 'Hop', 'Hope', 'Hornet', 'Hound', 'Iris', 'Ivy', 'Jackdaw', 'Jagged', 'Jay', 'Jump', 'Juniper', 'Kestrel',
        'Kink', 'Kite', 'Lake', 'Larch', 'Lark', 'Laurel', 'Lavender', 'Leaf', 'Leap', 'Leopard', 'Lichen', 'Light',
        'Lightning', 'Lilac', 'Lily', 'Lion', 'Little', 'Lizard', 'Locust', 'Long', 'Lotus', 'Loud', 'Low', 'Lynx', 
        'Mallow', 'Mantis', 'Maple', 'Marigold', 'Marsh', 'Marten', 'Meadow', 'Midge', 
        'Milk', 'Milkweed', 'Mink', 'Minnow', 'Mistle', 'Mite', 'Mole', 'Moon', 'Moor', 'Morning', 'Moss', 
        'Mossy', 'Moth', 'Mottle', 'Mottled', 'Mouse', 'Mumble', 'Murk', 'Myrtle', 'Nectar', 'Needle', 'Nettle',
        'Newt', 'Nut', 'Oat', 'Odd', 'One', 'Orange', 'Osprey', 'Pansy', 'Panther', 'Parsley', 'Partridge', 'Patch', 'Peak', 
        'Pear', 'Peat', 'Perch', 'Petal', 'Pheasant', 'Pigeon', 'Pike', 'Pine', 'Pink', 'Piper', 'Plover', 'Plum', 'Pod',
        'Pond', 'Pool', 'Poppy', 'Posy', 'Pounce', 'Prance', 'Prickle', 'Prim', 'Primrose', 'Puddle', 'Quail', 'Quick',
        'Pop', 'Quiet', 'Quill', 'Rabbit', 'Raccoon', 'Ragged', 'Rain', 'Rat', 'Rattle', 'Raven', 'Reed',
        'Ridge', 'Rift', 'Ripple', 'River', 'Roach', 'Rook', 'Root', 'Rose', 'Rosy', 'Rowan', 'Rubble',
        'Running', 'Rush', 'Rye', 'Sage', 'Scorch', 'Sedge', 'Seed', 'Shard', 'Sharp', 'Sheep', 
        'Shell', 'Shimmer', 'Shining', 'Shivering', 'Short', 'Shrew', 'Shy', 'Silk', 'Silt', 'Skip', 'Sky', 'Slate', 
        'Sleek', 'Sleet', 'Slight', 'Sloe', 'Slope', 'Small', 'Snail', 'Snake', 'Snap', 'Sneeze', 'Snip', 'Snook', 'Soft', 'Song',
        'Sorrel', 'Spark', 'Sparrow', 'Speckle', 'Spider', 'Spike', 'Spire', 'Splash', 'Spot', 'Spotted', 'Spring', 'Spruce', 
        'Squirrel', 'Starling', 'Stem', 'Stoat', 'Stork', 'Stream', 'Strike', 
        'Stumpy', 'Sunny', 'Swallow', 'Swamp', 'Sweet', 'Swift', 'Sycamore', 'Tall', 'Talon', 'Tangle', 'Tansy', 'Tawny', 'Thistle', 'Thorn',
        'Thrift', 'Thrush', 'Thunder', 'Thyme', 'Tiger', 'Timber', 'Tiny', 'Tip', 'Toad', 'Torn', 'Trout', 'Tuft', 'Tulip', 
        'Tumble', 'Turtle', 'Vine', 'Vixen', 'Wasp', 'Weasel', 'Web', 'Weed', 'Wet', 'Wheat', 'Whirl', 'Whisker',
        'Whisper', 'Whispering', 'Whistle', 'Whorl', 'Wild', 'Willow', 'Wind', 'Wish', 'Wing', 'Wisteria', 'Wolf', 'Wood', 'Wren', 'Yarrow', 'Yew'
    ]

    colour_prefixes = {
        'WHITE': [
            'White', 'White', 'Pale', 'Snow', 'Cloud', 'Cloudy', 'Milk', 'Hail', 'Frost', 'Frozen', 'Freeze', 'Ice', 'Icy', 'Sheep',
            'Blizzard', 'Flurry', 'Moon', 'Light', 'Bone', 'Bright', 'Swan', 'Dove', 'Wooly', 'Cotton',
        ],
        'PALEGREY': [
            'Grey', 'Silver', 'Pale', 'Light', 'Cloud', 'Cloudy', 'Hail', 'Frost', 'Ice', 'Icy', 'Mouse', 'Bright', "Fog", 'Freeze',
            'Frozen', 'Stone', 'Pebble', 'Dove', 'Sky', 'Cotton', 'Heather', 'Ashen'
        ],
        'SILVER': [
            'Grey', 'Silver', 'Cinder', 'Ice', 'Icy', 'Frost', 'Frozen', 'Freeze', 'Rain', 'Blue',
            'River', 'Blizzard', 'Flurry', 'Bone', 'Bleak', 'Stone', 'Pebble', 'Heather'
        ],
        'GREY': [
            'Grey', 'Grey', 'Ash', 'Ashen', 'Cinder', 'Rock', 'Stone', 'Shade', 'Mouse', 'Smoke', 'Smoky', 'Shadow', "Fog", 'Bone', 
            'Bleak', 'Rain', 'Storm', 'Soot', 'Pebble', 'Mist', 'Misty', 'Heather'
        ],
        'DARKGREY': [
            'Grey', 'Shade', 'Raven', 'Crow', 'Stone', 'Dark', 'Night', 'Cinder', 'Ash', 'Ashen',
            'Smoke', 'Smokey', 'Shadow', 'Bleak', 'Rain', 'Storm', 'Pebble', 'Mist', 'Misty'
        ],
        'GHOST': [
            'Black', 'Black', 'Shade', 'Shaded', 'Crow', 'Raven', 'Ebony', 'Dark',
            'Night', 'Shadow', 'Scorch', 'Midnight', 'Bleak', 'Storm', 'Violet', 'Pepper', 'Bat', 'Fade'
        ],
        'PALEGINGER': [
            'Pale', 'Ginger', 'Sand', 'Sandy', 'Yellow', 'Sun', 'Sunny', 'Light', 'Lion', 'Bright',
            'Honey', 'Daisy', 'Warm', 'Robin'
        ],
        'GOLDEN': [
            'Gold', 'Golden', 'Yellow', 'Sun', 'Sunny', 'Light', 'Lightning', 'Thunder',
            'Honey', 'Tawny', 'Lion', 'Dandelion', 'Marigold', 'Warm'
        ],
        'GINGER': [
            'Ginger', 'Ginger', 'Red', 'Fire', 'Rust', 'Flame', 'Ember', 'Sun', 'Sunny', 'Light', 'Primrose', 'Rose',
            'Rowan', 'Fox', 'Tawny', "Plum", 'Orange', 'Warm', 'Burn', 'Burnt', 'Robin', 'Amber'
        ],
        'DARKGINGER': [
            'Ginger', 'Ginger', 'Red', 'Red', 'Fire', 'Flame', 'Ember', 'Oak', 'Shade', 'Russet',
            'Rowan', 'Fox', 'Orange', 'Copper', 'Cinnamon', 'Burn', 'Burnt', 'Robin'
        ],
        'CREAM': [
            'Sand', 'Sandy', 'Yellow', 'Pale', 'Cream', 'Light', 'Milk', 'Fawn',
            'Bone', 'Daisy', 'Branch', 'Warm', 'Robin', 'Almond', 'Acorn'
        ],
        'LIGHTBROWN': [
            'Brown', 'Pale', 'Light', 'Mouse', 'Dust', 'Dusty', 'Sand', 'Sandy', 'Bright', 'Mud',
            'Hazel', 'Vole', 'Branch', 'Warm', 'Robin', 'Almond', 'Acorn', 'Bark'
        ],
        'BROWN': [
            'Brown', 'Oak', 'Mouse', 'Dark', 'Shade', 'Russet', 'Dust', 'Dusty', 'Acorn', 'Mud', 'Deer', 'Fawn', 'Doe', 'Stag',
            'Twig', 'Owl', 'Otter', 'Log', 'Vole', 'Branch', 'Hazel', 'Robin', 'Acorn', 'Bark'
        ],
        'DARKBROWN': [
            'Brown', 'Dark', 'Shade', 'Night', 'Russet', 'Rowan', 'Mud', 'Oak', 'Stag', 'Elk', 'Twig',
            'Owl', 'Otter', 'Log', 'Hickory', 'Branch', 'Robin', 'Bark'
        ],
        'BLACK': [
            'Black', 'Black', 'Shade', 'Shaded', 'Crow', 'Raven', 'Ebony', 'Dark',
            'Night', 'Shadow', 'Scorch', 'Midnight', 'Pepper', 'Jet', 'Bat', 'Burnt'
        ]}

    eye_prefixes = {
        'YELLOW': ['Yellow', 'Moon', 'Daisy', 'Honey', 'Light'],
        'AMBER': ['Amber', 'Sun', 'Fire', 'Gold', 'Honey', 'Scorch'],
        'HAZEL': ['Hazel', 'Tawny', 'Hazel', 'Gold', 'Daisy', 'Sand'],
        'PALEGREEN': ['Pale', 'Green', 'Mint', 'Fern', 'Weed', 'Olive'],
        'GREEN': ['Green', 'Fern', 'Weed', 'Holly', 'Clover', 'Olive'],
        'BLUE': ['Blue', 'Blue', 'Ice', 'Sky', 'Lake', 'Frost', 'Water'],
        'DARKBLUE': ['Dark', 'Blue', 'Sky', 'Lake', 'Berry', 'Water', 'Deep'],
        'GREY': ['Grey', 'Stone', 'Silver', 'Ripple', 'Moon', 'Rain', 'Storm', 'Heather'],
        'CYAN': ['Sky', 'Blue', 'River', 'Rapid'],
        'EMERALD': ['Emerald', 'Green', 'Shine', 'Blue', 'Pine', 'Weed'],
        'PALEBLUE': ['Pale', 'Blue', 'Sky', 'River', 'Ripple', 'Day', 'Cloud'],
        'PALEYELLOW': ['Pale', 'Yellow', 'Sun', 'Gold'],
        'GOLD': ['Gold', 'Golden', 'Sun', 'Amber', 'Sap', 'Honey'],
        'HEATHERBLUE': ['Heather', 'Blue', 'Lilac', 'Rosemary', 'Lavender', 'Wisteria'],
        'COPPER': ['Copper', 'Red', 'Amber', 'Brown', 'Fire', 'Cinnamon'],
        'SAGE': ['Sage', 'Leaf', 'Olive', 'Bush', 'Clove', 'Green', 'Weed'],
        'BLUE2': ['Blue', 'Blue', 'Ice', 'Icy', 'Sky', 'Lake', 'Frost', 'Water'],
        'SUNLITICE': ['Sun', 'Ice', 'Icy', 'Frost', 'Sunrise', 'Dawn', 'Dusk', 'Odd', 'Glow'],
        'GREENYELLOW': ['Green', 'Yellow', 'Tawny', 'Hazel', 'Gold', 'Daisy', 'Sand', 'Sandy', 'Weed']
    }

    loner_names = [
        "Abyss", "Ace", "Adam", "Admiral", "Ah", "Agatha", "Alcina", "Alec", "Alfie", "Alice", "Alonzo", "Amber", "Amelia",
        "Amity", "Amy", "Angel", "Anita", "Anubis", "Armageddon", "Armin", "Apple Cider", "April", "Apu", "Ash", "Archie", "Aurora", "Azula",
        "Aries", "Aquarius", "Baba Yaga", "Bagel", "Bagheera", "Bailey", "Baisel", "Bandit", "Baphomet", "Bastet", "Bean",
        "Beanie Baby", "Beanie", "Beans", "Bebe", "Bede", "Belle", "Ben", "Benny", "Bently", "Bentley", "Beverly",
        "Bibelot", "Big Man", "Bigwig", "Bill Bailey", "Binx", "Birb", "Birdie", "Blinky Stubbins", "Blu",  "Bluebell", "Bologna", "Bolt",
        "Bonbon", "Bongo", "Bonnie", "Bonny", "Boo", "Booker", "Bombalurina", "Brandywine", "Bren", "Broccoli", "Buddy", "Bullwinkle",
        "Bumblebee", "Bunny", "Burger", "Burm", "Bustopher Jones", "Bub", "Cake", "Callie", "Calvin", "Cancer", "Cannelloni", "Capricorn",
        "Caramel", "Cardamom", "Carmen", "Carmin", "Carolina", "Caroline", "Carrie", "Cassandra", "Catie", "Catty", "Catrick",
        "Cayenne", "Cece", "Chance", "Chanel", "Chansey", "Chaos", "Captain", "Charles", "Charlie", "Charlotte", "Charm",
        "Chase", "Chip", "Cheese", "Cheesecake", "Cheeto", "Cheetoman", "Chef", "Cherry", "Chester", "Cheshire", "Chewie", "Chewy",
        "Chicco", "Chief", "Chinook", "Chip", "Chloe", "Chocolate", "Chocolate Chip", "Chris", "Chrissy", "Crumpet",
        "Chub", "Cinder", "Cinderblock", "Cloe", "Cloud", "Clover", "Cocoa", "Cocoa Puff", "Coffee", "Conan", "Cookie",
        "Coral", "Coricopat", "Cosmo", "Cowbell", "Cowboy", "Crab", "Cracker", "Cream", "Crispy", "Crow", "Crunchwrap", "Crunchy",
        "Cupcake", "Cutie", "Cooper", "Confetti", "Cyprus", "Dakota", "Dan", "Dandelion", "Danger Dave", "Daliah", "Dave", "Deli",
        "Delilah", "Della", "Demeter", "Dewey", "Digiorno", "Dinah", "Dirk", "Distinguished Gentleman", "Diona", "Dizzy", "Dolly", "Donald", "Donuts", "Dorian",
        "Dorothy", "Double Trouble", "Dova", "Dragonfly", "Dreamy", "Duchess", "Dune", "Dunnock", "Dust Bunny", "Dusty Cuddles",
        "Eclipse", "Daisy Mae", "Eda", "Eddie", "Eevee", "Egg", "Elden", "Elton", "Ember", "Emerald", "Emeline", "Emi", "Emma",
        "Emy", "Erica", "Esme", "Espresso", "Eve", "Evelyn", "Evie", "Evilface", "Erebus", "Fallow", "Fang", "Fawn",
        "Feather", "Felix", "Fern", "Ferret", "Ferry", "Figaro", "Finch", "Finnian", "Firefly", "Fishleg", "Fishtail", "Fiver",
        "Flabby", "Flamenco", "Flower", "Fluffy", "Flutie", "Fork", "Foxtrot", "Frank", "Frankie", "Frannie", "Fred",
        "Freddy", "Free", "French", "French Fry", "Frito", "Frumpkin", "Fry", "Frye", "Fuzziwig", "Galahad", "Gamble",
        "Gargoyle", "Garfield", "Garnet", "General Erasmus Dickinson", "Geode", "George", "Ghost", "Gibby",
        "Gilded Lily",  "Gingersnap", "Gir", "Gizmo", "Glass", "Glory", "Goose", "Good Sir", "Grace", "Grain",
        "Grasshopper", "Gravy", "Grizabella", "Guinness", "Gus", "Gust", "Gwendoline", "Gwynn", "Gemini", "Habanero", "Haiku", "Haku", "Harvey",
        "Havoc", "Hawkbit", "Hawkeye", "Hazel", "Henry", "Heathcliff", "Herbert", "Herc", "Hercules", "Hiccup", "Highness", "Hlao", "Hocus Pocus", "Hobbes", "Holly", "Hop",
        "Hot Sauce", "Hotdog", "Hubert", "Hughie", "Human", "Humphrey", "Hunter", "Harlequin", "Ice", "Icecube", "Ice Cube", "Icee", "Igor",
        "Ike", "Indi", "Insect", "Ipsy", "Isabel", "Itsy Bitsy", "Jack", "Jade", "Jaiden", "Jake", "James", "Jasper", "Jaxon", "Jay",
        "Jelly Jam", "Jellylorum", "Jenny", "Jennyanydots", "Jesse", "Jessica", "Jester", "Jethro", "Jewel", "Jewels", "Jimmy", "Jiminy Cricket",
        "Jinx", "John", "Johnny", "Joker", "Jolly", "Jolly Rancher", "Joob", "Jubie", "Judas", "Jude", "Judy", "Juliet",
        "June", "Jupiter", "KD", "Kate", "Katjie", "Katy", "Kelloggs", "Ken", "Kendra", "Kenny", "Kermit", "Kerry",
        "Ketchup", "Kettlingur", "Ketsl", "King", "Kingston", "Kip", "Kisha", "Kitty", "Kitty Cat", "Klondike", "Knox",
        "Kodiak", "Kong", "Kyle", "L", "Lacy", "Lady", "Lady Liberty", "Lady Figment", "Lakota", "Laku", "Lark",
        "Larch", "Lee", "Lemon", "Lemmy", "Leo", "Leon", "Lester", "Levon", "Lex", "Lil Baby", "Lilac", "Lilith",
        "Lily", "Linden", "Little Lady", "Little Nicky", "Little One", "Loaf", "Lobster", "Lola", "Lollipop", "Loona", "Lora",
        "Lorado", "Louie", "Louis", "Luchasaurus", "Lucky", "Lucy", "Luci-Purr", "Lugnut", "Luigi", "Luna", "Lupo",
        "Loyalty", "Libra", "Macavity", "Madi", "Maddy", "Makwa", "Maleficent", "Maggie", "Majesty", "Manda", "Mange", "Mango", "Marathon",
        "Marceline", "Mario", "Marny", "Matcha", "Matador", "Maverick", "Max", "May", "McChicken", "McFlurry", "Mick", "Meatlug",
        "Medusa", "Melody", "Meow-Meow", "Meowyman", "Mera", "Mew", "Midnight Goddess", "Miles", "Milhouse", "Millie",
        "Milo", "Milque", "Mimi", "Minette", "Mini", "Minna", "Minnie", "Mint", "Minty", "Missile Launcher", "Misty", "Mitzy Moo Moo",
        "Mitski", "Mittens", "Mochi", "Mocha", "Mojo", "Mollie", "Molly", "Molly Murder Mittens", "Monika", "Monster",
        "Monte", "Monzi", "Moon", "Mop", "Morel", "Moxie", "Mr. Kitty", "Mr. Kitty Whiskers", "Mr. Mistoffolees", "Mr. Whiskers", "Mr. Wigglebottom",
        "Mucha", "Munkustrap", "Mungojerrie", "Murder", "Mushroom", "Mitaine", "Myko", "Neel", "Nagi", "Nakeena", "Neil", "Nemo", "Nessie", "Nick",
        "Nightmare", "Nikki", "Niles", "Ninja", "Nintendo", "Nisha", "Nitro", "Noodle", "Nottingham", "Norman", "Nova",
        "Nugget", "Nuggets", "Nuka", "Nutella", "O'Leary", "Oakley", "Oapie", "Obi Wan", "Odetta", "Old Deuteronomy", "Old Man Sam",
        "Oleander", "Olga", "Oliver", "Oliva", "Ollie", "Omelet", "Onyx", "Oops", "Oopsy Dazey", "Ophelia", "Oreo",
        "Orion", "Oscar", "Otto", "Owen", "Pangur", "Patience", "Paulina", "Peach", "Peanut", "Peanut Wigglebutt", "Pear", "Pearl",
        "Pecan", "Penny", "Peony", "Pepper", "Pepita", "Pichi", "Pickles", "Pierre", "Pikachu", "Ping", "Ping Pong", "Pip",
        "Piper", "Pipsqueak", "Pipkin", "Pixel", "Plato", "Pocket", "Pochito", "Poki", "Polly", "Pong", "Ponyboy", "Poopy", "Porsche",
        "Potato", "Pouncival", "President", "Prickle", "Princess", "Private Eye", "Pudding", "Pumpernickel", "Punk", "Purdy",
        "Purry", "Pisces", "Pushee", "Quagmire", "Quake", "Queen", "Queenie", "Queeny", "Queso", "Queso Ruby", "Quest",
        "Quickie", "Quimby", "Quinn", "Quino", "Quinzee", "Quesadilla", "Radar", "Ramble", "Randy", "Rapunzel",
        "Raptor", "Rarity", "Rat", "Ray", "Reese", "Reeses Puff", "Ren", "Rio", "Riot", "River", "Riya", "Rocket", "Rodeo",
        "Rolo", "Roman", "Roomba", "Rooster", "Rory", "Rose", "Roselie", "Ruby", "Rudolph", "Rufus", "Rue", "Ruffnut", "Rum", "Rumpleteazer", "Rum Tum Tugger", "Russel",
        "Sadie", "Sagwa", "Sailor", "Saki", "Salmon", "Salt", "Sam", "Samantha", "Sandwich", "Sandy", "Sarge", "Sassy", "Sashimi", "Sausage", "Schmidt",
        "Scotch", "Scrooge", "Seamus", "Sekhmet", "Sega", "Seri", "Shamash", "Shampoo", "Shamwow", "Shay", "Sherman",
        "Shimmer", "Shiver", "Sillabub", "Silva", "Silver", "Slinky", "Skimbleshanks", "Skrunkly", "Sloane", "Slug", "Slushie", "Smarty Pants",
        "Smoothie", "Smores", "Sneakers", "Snek", "Snotlout", "Snoots", "Socks",  "Sofa", "Sol", "Sonata", "Sonic",
        "Sophie", "Sorbet", "Sox", "Spam", "Sparky", "Speedwell", "Spots", "Stan", "Star", "Starfish", "Stella",
        "Steve", "Steven", "Stinky", "Stripes", "Stolas", "Strawberry", "Stripes", "Sundae", "Sunny", "Sunset", "Sweet",
        "Sweet Marmalade", "Sweet Leon", "Sweet Creature", "Sweetie", "Scorpio", "Sagittarius", "Sylvester", "Tabatha", "Tabby",
        "Tabbytha", "Taco", "Taco Bell", "Tasha", "Tantomile", "Tamagotchi", "Tay", "Teacup", "Teddie", "Tempest", "Tetris",
        "Tesora", "Teufel", "Theo", "Thumbelina", "Tiana", "Tiny", "Tin Man", "Tigger", "Tikka", "Timmy", "Toast",
        "Toffee", "Tom", "Tomato", "Tomato Soup", "Toni", "Toothless", "Top Hat", "Torque", "Tortilla", "Treasure",
        "Trinket", "Trip", "Triscuit", "Trixie", "Trouble", "Trouble Nuggets", "Troublemaker", "Tucker", "Tuffnut",
        "Tumble", "Tumblebrutus", "Turbo", "Twilight", "Twinkle Lights", "Twister", "Twix", "Toastee", "Taurus", "Ula", "Ulyssa", "Victoria",
        "Union", "Uriel", "Vanilla", "Van Pelt", "Vaxx", "Venture", "Via", "Victor", "Vida", "Viktor", "Vinnie", "Vinyl",
        "Velociraptor", "Violet", "Vivienne", "Void", "Voltage", "Vox", "Virgo", "Wanda", "Warren Peace", "Webby", "Wendy", "Whiskers",
        "Whisper", "Wigglebutt", "Wiggity Wacks", "Windy", "Wishbone", "Wisp", "Wisteria", "Whiz Kid", "Worm", "X'ek",
        "Xelle", "Yaoyao", "Yen", "Yeza", "Yoshi", "Zelda", "Zim", "Zoe", "Zorro",
        ]
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
            if eyes in self.eye_prefixes:
                possible_prefix_categories.append(self.eye_prefixes[eyes])
            if colour in self.colour_prefixes:
                possible_prefix_categories.append(self.colour_prefixes[colour])
            # Choose appearance-based prefix if possible and named_after_appearance because True.
            if named_after_appearance and possible_prefix_categories:
                prefix_category = random.choice(possible_prefix_categories)
                self.prefix = random.choice(prefix_category)
            else:
                self.prefix = random.choice(self.normal_prefixes)
                    
        # Set suffix
        while self.suffix is None or self.suffix == self.prefix.casefold() or\
         str(self.suffix) in self.prefix.casefold() and not str(self.suffix) == '':
            if pelt is None or pelt == 'SingleColour':
                self.suffix = random.choice(self.normal_suffixes)
            else:
                named_after_pelt = not random.getrandbits(3) # Chance for True is '1/8'.
                # Pelt name only gets used if there's an associated suffix.
                if (named_after_pelt
                    and pelt in ["Tortie", "Calico"]
                    and tortiepattern in self.tortie_pelt_suffixes):
                    self.suffix = random.choice(self.tortie_pelt_suffixes[tortiepattern])
                elif named_after_pelt and pelt in self.pelt_suffixes:
                    self.suffix = random.choice(self.pelt_suffixes[pelt])
                else:
                    self.suffix = random.choice(self.normal_suffixes)

    def __repr__(self):
        if self.status in ["deputy", "warrior", "medicine cat", "elder", "mediator"]:
            return self.prefix + self.suffix
        elif self.status in ["kittypet", "loner", "rogue"]:
            return self.prefix
        else:
            return self.prefix + self.special_suffixes[self.status]



names = Name()
