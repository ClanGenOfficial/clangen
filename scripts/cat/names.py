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
        "catcher", "cloud", "clouds", "clover", "coral", "crawl", "creek", "cry", "dapple", "daisy", "dawn", "drift", "drop", "dusk", "dust",
        "ear", "ears", "eater", "eye", "eyes", "face", "fall", "fang", "fawn", "feather", "fern", "fin", "fire", "fish", "flake",
        "flame", "flight", "flick", "flood", "flower", "fox", "frost", "gaze", "goose", "gorse", "grass", "hail", "hare", "hawk", "haze",
        "heather", "hollow", "holly", "horse", "ice", "ivy", "jaw", "jay", "jump", "kite", "lake", "larch", "leaf", "leap", 
        "leaves", "leg", "light", "lightning", "lilac", "lily", "lotus", "mask", "mark", "minnow", "mist", "moth", "moon", "moss", "mouse",
        "muzzle", "needle", "nettle", "night", "noise", "nose", "nut", "pad", "patch", "path", "peak", "petal", "plume", "pond",
        "pool", "poppy", "pounce", "puddle", "rain", "rapid", "ripple", "river", "roar", "rose", "rump", "run", "runner", "scar",
        "scratch", "seed", "shade", "shadow", "shell", "shine", "sight", "skip", "sky", "slip", "snout", "snow", "song", "spark",
        "speck", "speckle", "spirit", "splash", "spot", "spots", "spring", "stalk", "stem", "step", "stone", "storm", "streak",
        "stream", "strike", "stripe", "sun", "swipe", "swoop", "talon", "teeth", "thistle", "thorn", "throat", "toe", "tree", 
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
        'Acacia', 'Adder', 'Alder', 'Algae', 'Aloe', 'Ant', 'Antler', 'Apple', 'Apricot', 'Arc', 'Arch', 'Aspen', 'Aster', 'Autumn',
        'Badger', 'Barley', 'Basil', 'Bass', 'Bay', 'Bayou', 'Beam', 'Bear', 'Beaver', 'Bee', 'Beech', 'Beetle', 'Berry',
        'Big', 'Birch', 'Bird', 'Bite', 'Bitter', 'Bittern', 'Bleak', 'Blight', 'Blink', 'Bliss', 'Blizzard', 'Bloom',
        'Blossom', 'Blotch', 'Bluebell', 'Bluff', 'Bog', 'Bold', 'Borage', 'Bough', 'Boulder', 'Bounce', 'Bracken', 'Bramble', 
        'Brave', 'Breeze', 'Briar', 'Bright', 'Brindle', 'Bristle', 'Broken', 'Brook', 'Broom', 'Brush', 'Bubble', 'Bubbling', 'Buck',
        'Bug', 'Bumble', 'Burdock', 'Burr', 'Bush', 'Buzzard', 'Carp', 'Cave', 'Cedar', 'Chaffinch', 'Char', 'Chasing', 'Cheetah', 'Cherry',
        'Chestnut', 'Chive', 'Cicada', 'Claw', 'Clay', 'Clear', 'Cliff', 'Clover', 'Coast', 'Cobra', 'Cod', 'Cold', 'Condor', 
        'Cone', 'Conifer', 'Cougar', 'Cow', 'Coyote', 'Crab', 'Crag', 'Crane', 'Creek', 'Cress', 'Crested', 'Cricket', 'Crooked',
        'Crouch', 'Curl', 'Curlew', 'Curly', 'Cypress', 'Dahlia', 'Daisy', 'Damp', 'Dancing', 'Dandelion', 'Dangling', 'Dapple',
        'Dappled', 'Dapples', 'Dawn', 'Day', 'Dead', 'Deer', 'Dew', 'Dewy', 'Doe', 'Dog', 'Down', 'Downy', 'Drake', 'Drift', 
        'Drizzle', 'Drought', 'Dry', 'Duck', 'Dull', 'Dune', 'Dusk', 'Eagle', 'Echo', 'Eel', 'Egret', 'Elder', 'Elm', 
        'Ermine', 'Faded', 'Faded', 'Fading', 'Falcon', 'Fallen', 'Falling', 'Fallow', 'Fawn', 'Feather', 'Fennel', 'Fern', 
        'Ferret', 'Fidget', 'Fierce', 'Fin', 'Finch', 'Fir', 'Fish', 'Flail', 'Flash', 'Flax', 'Fleck', 'Fleet', 'Flicker', 
        'Flight', 'Flint', 'Flip', 'Flood', 'Flower', 'Flutter', 'Fluttering', 'Fly', 'Foam', 'Fog', 'Forest', 'Freckle', 'Fringe',
        'Frog', 'Frond', 'Furled', 'Furze', 'Fuzzy', 'Gale', 'Gander', 'Gannet', 'Garlic', 'Gem', 'Giant', 'Gill', 'Gleam', 'Glow', 'Goose',
        'Gorge', 'Gorse', 'Grass', 'Gravel', 'Grouse', 'Gull', 'Gust', 'Hail', 'Half', 'Hare', 'Harvest',
        'Hatch', 'Haven', 'Hawk', 'Hay', 'Haze', 'Heath', 'Heavy', 'Hedge', 'Hen', 'Heron', 'Hill', 'Hoarse', 'Hollow', 'Holly',
        'Honey', 'Hoot', 'Hop', 'Hope', 'Hornet', 'Hound', 'Iris', 'Ivy', 'Jackdaw', 'Jagged', 'Jay', 'Jump', 'Juniper', 'Kestrel',
        'Kink', 'Kite', 'Lake', 'Lapping', 'Larch', 'Lark', 'Laurel', 'Lavender', 'Leaf', 'Leap', 'Leopard', 'Lichen', 'Light',
        'Lightning', 'Lilac', 'Lily', 'Lion', 'Little', 'Lizard', 'Locust', 'Long', 'Lost', 'Lotus', 'Loud', 'Low', 'Lynx', 
        'Maggot', 'Mallow', 'Mantis', 'Maple', 'Marigold', 'Marsh', 'Marten', 'Meadow', 'Mellow', 'Melting', 'Merry', 'Midge', 
        'Milk', 'Milkweed', 'Mink', 'Minnow', 'Mistle', 'Mite', 'Mock', 'Mole', 'Monkey', 'Moon', 'Moor', 'Morning', 'Moss', 
        'Mossy', 'Moth', 'Mottle', 'Mottled', 'Mouse', 'Mumble', 'Murk', 'Myrtle', 'Nacre', 'Narrow', 'Nectar', 'Needle', 'Nettle',
        'Newt', 'Nut', 'Oat', 'Odd', 'One', 'Orange', 'Osprey', 'Pansy', 'Panther', 'Parsley', 'Partridge', 'Patch', 'Peak', 
        'Pear', 'Peat', 'Perch', 'Petal', 'Pheasant', 'Pigeon', 'Pike', 'Pine', 'Pink', 'Piper', 'Plover', 'Plum', 'Pod',
        'Pond', 'Pool', 'Poppy', 'Posy', 'Pounce', 'Prance', 'Prickle', 'Prim', 'Primrose', 'Puddle', 'Python', 'Quail', 'Quick',
        'Pop', 'Quiet', 'Quill', 'Rabbit', 'Raccoon', 'Ragged', 'Rain', 'Rainswept', 'Rambling', 'Rat', 'Rattle', 'Raven', 'Reed',
        'Ridge', 'Rift', 'Ripple', 'Rising', 'River', 'Roach', 'Rook', 'Root', 'Rose', 'Rosy', 'Rot', 'Rowan', 'Rubble',
        'Running', 'Rush', 'Rye', 'Sage', 'Scar', 'Scorch', 'Sea', 'Sedge', 'Seed', 'Shard', 'Sharp', 'Shattered', 'Sheep', 
        'Shell', 'Shimmer', 'Shining', 'Shivering', 'Short', 'Shred', 'Shrew', 'Shy', 'Silk', 'Silt', 'Skip', 'Sky', 'Slate', 
        'Sleek', 'Sleet', 'Slight', 'Sloe', 'Slope', 'Small', 'Snail', 'Snake', 'Snap', 'Sneeze', 'Snip', 'Snook', 'Soft', 'Song',
        'Sorrel', 'Spark', 'Sparrow', 'Speckle', 'Spider', 'Spike', 'Spire', 'Splash', 'Spot', 'Spotted', 'Spring', 'Spruce', 
        'Squirrel', 'Starling', 'Steam', 'Stem', 'Stoat', 'Stork', 'Stream', 'Strike', 'Stripe', 'Strong', 'Stump', 
        'Stumpy', 'Sunny', 'Swallow', 'Swamp', 'Sweet', 'Swift', 'Sycamore', 'Tall', 'Talon', 'Tangle', 'Tansy', 'Tawny', 'Thistle', 'Thorn',
        'Thrift', 'Thrush', 'Thunder', 'Thyme', 'Tiger', 'Timber', 'Tiny', 'Tip', 'Toad', 'Torn', 'Trout', 'Tuft', 'Tulip', 
        'Tumble', 'Turtle', 'Twisted', 'Vine', 'Vixen', 'Warm', 'Wasp', 'Wave', 'Weasel', 'Web', 'Weed', 'Wet', 'Wheat', 'Whirl', 'Whisker',
        'Whisper', 'Whispering', 'Whistle', 'Whorl', 'Wild', 'Willow', 'Wind', 'Wish', 'Wing', 'Wisteria', 'Wolf', 'Wood', 'Wren', 'Yarrow', 'Yew'
    ]

    colour_prefixes = {
        'WHITE': [
            'White', 'White', 'Pale', 'Snow', 'Cloud', 'Cloudy', 'Milk', 'Hail', 'Frost', 'Frozen', 'Freeze', 'Ice', 'Icy', 'Sheep',
            'Blizzard', 'Flurry', 'Moon', 'Star', 'Light', 'Bone', 'Bright', 'Swan', 'Dove', 'Wooly', 'Wool', 'Cotton', 'Warm', 'Arctic'
        ],
        'PALEGREY': [
            'Grey', 'Silver', 'Pale', 'Light', 'Cloud', 'Cloudy', 'Hail', 'Frost', 'Ice', 'Icy', 'Mouse', 'Bright', "Fog", 'Freeze',
            'Frozen', 'Stone', 'Pebble', 'Dove', 'Sky', 'Cotton', 'Heather', 'Warm', 'Arctic', 'Ashen'
        ],
        'SILVER': [
            'Grey', 'Silver', 'Cinder', 'Ice', 'Icy', 'Frost', 'Frozen', 'Freeze', 'Rain', 'Blue',
            'River', 'Blizzard', 'Flurry', 'Bone', 'Bleak', 'Stone', 'Pebble', 'Heather', 'Warm', 'Arctic'
        ],
        'GREY': [
            'Grey', 'Grey', 'Ash', 'Ashen', 'Cinder', 'Rock', 'Stone', 'Shade', 'Mouse', 'Smoke', 'Smoky', 'Shadow', "Fog", 'Bone', 
            'Bleak', 'Rain', 'Storm', 'Soot', 'Pebble', 'Mist', 'Misty', 'Heather',
        ],
        'DARKGREY': [
            'Grey', 'Shade', 'Raven', 'Crow', 'Stone', 'Dark', 'Night', 'Cinder', 'Ash', 'Ashen',
            'Smoke', 'Smokey', 'Shadow', 'Bleak', 'Rain', 'Storm', 'Pebble', 'Mist', 'Misty'
        ],
        'GHOST': [
            'Black', 'Black', 'Shade', 'Shaded', 'Crow', 'Raven', 'Ebony', 'Dark',
            'Night', 'Shadow', 'Scorch', 'Midnight', 'Bleak', 'Storm', 'Violet', 'Pepper', 'Bat'
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
            'Ginger', 'Ginger', 'Red', 'Red', 'Fire', 'Rust', 'Flame', 'Ember', 'Oak', 'Shade', 'Russet',
            'Rowan', 'Fox', 'Orange', 'Copper', 'Cinnamon', 'Burn', 'Burnt', 'Jasper', 'Robin'
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
        'BLUE': ['Blue', 'Blue', 'Ice', 'Sky', 'Lake', 'Frost', 'Water', 'Sea'],
        'DARKBLUE': ['Dark', 'Blue', 'Sky', 'Lake', 'Berry', 'Water', 'Deep'],
        'GREY': ['Grey', 'Stone', 'Silver', 'Ripple', 'Moon', 'Rain', 'Storm', 'Heather'],
        'CYAN': ['Sky', 'Blue', 'River', 'Rapid', 'Sea'],
        'EMERALD': ['Emerald', 'Green', 'Shine', 'Blue', 'Pine', 'Weed'],
        'PALEBLUE': ['Pale', 'Blue', 'Sky', 'River', 'Ripple', 'Day', 'Cloud', 'Sea'],
        'PALEYELLOW': ['Pale', 'Yellow', 'Sun', 'Gold', 'Ray'],
        'GOLD': ['Gold', 'Golden', 'Sun', 'Amber', 'Sap', 'Honey'],
        'HEATHERBLUE': ['Heather', 'Blue', 'Lilac', 'Rosemary', 'Lavender', 'Wisteria'],
        'COPPER': ['Copper', 'Red', 'Amber', 'Brown', 'Fire', 'Cinnamon', 'Jasper'],
        'SAGE': ['Sage', 'Leaf', 'Olive', 'Bush', 'Clove', 'Green', 'Weed'],
        'BLUE2': ['Blue', 'Blue', 'Ice', 'Icy', 'Sky', 'Lake', 'Frost', 'Water'],
        'SUNLITICE': ['Sun', 'Ice', 'Icy', 'Frost', 'Sunrise', 'Dawn', 'Dusk', 'Odd', 'Glow'],
        'GREENYELLOW': ['Green', 'Yellow', 'Tawny', 'Hazel', 'Gold', 'Daisy', 'Sand', 'Sandy', 'Weed']
    }

    loner_names = [
        "Abyss", "Ace", "Ah" ,"Alcina", "Alec", "Alice", "Amber", "Amity", "Amy", "Angel", "Anita", "Ankh", "Anubis", "Armin", "April", "Ash",
        "Aurora", "Azula", "Aries", "Aquarius", "Bagel", "Bailey", "Bandit", "Baphomet", "Bastet", "Bean", "Beanie Baby", "Beans", "Bede",
        "Belle", "Benny", "Bently", "Bentley", "Beverly", "Big Man", "Birb", "Blu",  "Bluebell", "Bologna", "Bolt", "Bonbon", "Bongo", "Bonnie",
        "Bonny", "Boo", "Broccoli", "Buddy", "Bumblebee", "Bunny", "Burger", "Burm", "Bub", "Cake", "Callie", "Calvin", "Caramel", "Carmen", 
        "Carmin", "Carolina", "Caroline", "Carrie", "Catie", "Cat", "Catty", "Chance", "Chanel", "Chansey", "Chaos", "Charles", "Charlie", "Charlotte",
        "Charm", "Chase", "Cheese", "Cheesecake", "Cheeto", "Cheetoman", "Chef", "Cherry", "Chester", "Chewie", "Chewy", "Chicco", "Chief", "Chinook",
        "Chip", "Chloe", "Chocolate", "Chocolate Chip", "Chris", "Chrissy", "Cinder", "Cinderblock", "Cloe", "Cloud", "Cocoa", "Cocoa Puff", "Coffee",
        "Conan", "Cookie", "Coral", "Cosmo", "Cowbell", "Cowboy", "Crab", "Cracker", "Cream", "Crispy", "Crow", "Crunchwrap", "Crunchy", "Cupcake", "Cooper",
        "Cancer", "Capricorn", "Dakota", "Dan", "Dave", "Deli", "Delilah", "Della", "Delta", "Dewey", "Dirk", "Dog", "Doggo", "Dolly", "Donald", "Dragonfly", "Dreamy", "Duchess", "Dune",
        "Dunnock" "Eclipse", "Daisy Mae",  "Eda", "Eddie", "Eevee", "Egg", "Ember", "Emerald", "Emi", "Emma", "Emy", "Erica", "Espresso", "Eve", "Evelyn", "Evie",
        "Evilface", "Erebus", "Fallow", "Fang", "Fawn", "Feather", "Felix", "Fern", "Ferret", "Ferry", "Finch", "Firefly", "Fishleg", "Fishtail", "Fiver", "Flabby",
        "Flower", "Fluffy", "Flutie", "Fork", "Frank", "Frankie", "Frannie", "Fred", "Freddy", "Free", "French", "French Fry", "Frito", "Fry", "Frye", "Gamble", 
        "Gargoyle", "Garnet", "Geode", "George", "Ghost", "Gibby", "Gir", "Gizmo", "Glass", "Glory", "Goose", "Grace", "Grain", "Grasshopper", "Gravy", "Guinness",
        "Gust", "Gwendoline", "Gwynn", "Gemini", "Habanero", "Hamilton", "Haku", "Harvey", "Havoc", "Herc", "Hercules", "Hiccup", "Holly", "Hop", "Hot Sauce", "Hotdog",
        "Hughie", "Human", "Hunter", "Harlequin", "Ice", "Icecube", "Ice Cube", "Icee", "Igor", "Ike", "Indi", "Insect", "Isabel", "Jack", "Jade", "Jaiden",
        "Jake", "James", "Jasper", "Jaxon", "Jay", "Jenny", "Jesse", "Jessica", "Jester", "Jethro", "Jewel", "Jewels", "Jimmy", "Jinx", "John", "Johnny",
        "Jellybean", "Joker", "Jolly", "Jolly Rancher", "Joob", "Jubie", "Judas", "Jude", "Judy", "Juliet", "June", "Jupiter", "KD", "Kate", "Katy", "Kelloggs", "Ken",
        "Kendra", "Kenny", "Kermit", "Kerry", "Ketchup", "King", "Kingston", "Kip", "Kisha", "Kitty", "Kitty Cat", "Klondike", "Knox", "Kodiak", "Kong", "L", "Lacy",
        "Lakota", "Laku", "Lee", "Lemon", "Leo", "Leon", "Lester", "Lex", "Lilith", "Lily", "Lily", "Loaf", "Lobster", "Lola", "Loona", "Lora", "Louie", "Louis", "Lucky",
        "Lucy", "Lugnut", "Luigi", "Luke", "Luna", "Lupo", "Loyalty", "Libra", "Madi", "Makwa", "Maleficent", "Manda", "Mange", "Mango", "Marceline", "Matcha",
        "Maverick", "Max", "May", "McChicken", "McFlurry", "Meatlug", "Melody", "Menopause", "Meow-Meow", "Meowyman", "Mera", "Mew", "Miles", "Millie", "Milo",
        "Milque", "Mimi", "Minette", "Mini", "Minna", "Minnie", "Mint", "Minty", "Missile Launcher", "Mitski", "Mittens", "Mocha", "Mocha", "Mojo", "Mollie",
        "Molly", "Molly Murder Mittens", "Monika", "Monster", "Monte", "Monzi", "Moon", "Mop", "Moxie", "Mr. Kitty", "Mr. Kitty Whiskers", "Mr. Whiskers",
        "Mr. Wigglebottom", "Mucha", "Murder", "Mushroom", "Mitaine", "Myko", "Neel", "Nagi", "Nakeena", "Neil", "Nemo", "Nessie", "Nick", "Nightmare", "Nikki",
        "Niles", "Ninja", "Nintendo", "Nisha", "Nitro", "Noodle", "Norman" "Nova", "Nugget", "Nuggets", "Nuka", "Nutella", "O'Leary", "Oakley", "Oapie", "Obi Wan",
        "Old Man Sam", "Oleander", "Olga", "Oliver", "Oliva", "Ollie", "Omelet", "Onyx", "Oops", "Ophelia", "Oreo", "Orion", "Oscar", "Owen", "Peach", "Peanut",
        "Peanut Wigglebutt", "Pear", "Pearl", "Pecan", "Penny", "Peony", "Pepper", "Pichi", "Pickles", "Pikachu", "Ping", "Ping Pong",
        "Pip", "Piper", "Pipsqueak", "Pocket", "Poki", "Polly", "Pong", "Poopy", "Porsche", "Potato", "Prickle", "Princess", "Pumpernickel", "Punk", "Purdy",
        "Purry", "Pisces", "Pushee", "Quagmire", "Quake", "Queen", "Queenie", "Queeny", "Queso", "Queso Ruby", "Quest", "Quickie", "Quimby",
        "Quinn", "Quino", "Quinzee", "Quesadilla", "Ramble", "Randy", "Rarity", "Rat", "Ray", "Reese", "Reeses Puff", "Ren", "Rio", "Riot", "River",
        "Riya", "Rocket", "Rolo", "Roman", "Roomba", "Rooster", "Rory", "Rose", "Roselie", "Ruby", "Rudolph", "Rue", "Ruffnut", "Rum", "Sadie", "Saki",
        "Salmon", "Salt", "Sam", "Samantha", "Sandwich", "Sandy", "Sausage", "Schmidt", "Scotch", "Scrooge", "Seamus", "Sekhmet", "Seri", "Shampoo", "Shay",
        "Shimmer", "Shiver", "Silva", "Silver", "Skrunkly", "Sloane", "Slug", "Slushie", "Smoothie", "Smores", "Smudge", "Sneakers", "Snek", "Snotlout", "Socks", "Soda",
        "Sofa", "Sol", "Sonic", "Sophie", "Sorbet", "Sox", "Spam", "Sparky", "Spots", "Stan", "Star", "Starfish", "Stella", "Steve", "Steven", "Stinky",
        "Stolas", "Stripes", "Sundae", "Sunny", "Sunset", "Sweet", "Sweetie", "Scorpio", "Sagittarius", "Tabatha", "Tabby", "Tabbytha", "Taco", "Taco Bell",
        "Tasha", "Tempest", "Tetris", "Teufel", "Tiny", "Toast", "Toffee", "Tom", "Tomato", "Tomato Soup", "Toni", "Toothless", "Torque", "Tortilla", 
        "Treasure", "Triscuit", "Trixie", "Trouble", "Tucker", "Tuffnut", "Tumble", "Turbo", "Twilight", "Twister", "Twix", "Toastee", "Taurus", "Ula", "Union",
        "Uriel", "Vanilla", "Vaxx", "Velociraptor", "Venture", "Via", "Vida", "Viktor", "Vinnie", "Vinyl", "Violet", "Vivienne", "Void", "Voltage", "Vox", "Virgo", "Wanda", "Washington", "Webby",
        "Wendy", "Whiskers", "Whisper", "Wigglebutt", "Windy", "Wishbone", "Whiskey", "Wisp", "Wisteria", "Worm", "X'ek", "Zelda", "Zim", "Zoe"
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
        while self.suffix is None or self.suffix == self.prefix.casefold() or str(self.suffix) in self.prefix.casefold() and not str(self.suffix) == '':
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
        if self.status in self.special_suffixes:
            return self.prefix + self.special_suffixes[self.status]
        else:
            return self.prefix + self.suffix



names = Name()
