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
        "acorn", "ash", "aster", "back", "beam", "bee", "belly", "berry", "bite", "bird", "blaze", "blink",
        "blossom", "bloom", "blotch", "bounce", "branch", "breeze", "briar", "bright", "brook", "burr", "bush",
        "call", "cloud", "clover", "coral", "creek", "cry", "dapple", "daisy", "dawn", "dragon", "drift", "drop",
        "dusk", "dust", "ear", "ears", "earth", "emperor", "eye", "eyes", "face", "fall", "fang", "feather", "fern", "fin", "fire",
        "fish", "flame", "flight", "flood", "flower", "frost", "gaze", "ghost", "god", "goose", "gorse", "grass", "ground", "guardian",
        "hail", "hare", "hawk", "haze", "heather", "holly", "hollow", "hunter", "ivy", "jaw", "jay", "jump", "king", "kite", "knight", 
        "lake", "larch", "leaf", "leap", "leg", "light", "lilac", "lily", "lotus", "magic", "mask", "mind", "mist", "moth",
        "moon", "mouse", "needle", "nettle", "night", "noise", "nose", "nut", "pad", "path", "patch",
        "petal", "pond", "pool", "poppy", "pounce", "puddle", "queen", "rapid", "rose", "rump", "run", "runner",
        "scar", "seed", "seeker", "shade", "shadow", "shell", "shine", "sight", "skip", "sky", "slip", "snow", "song", "soul", 
        "spark", "speck", "speckle", "spirit", "splash", "spot", "spots", "spring", "stalk", "stem", "step",
        "stone", "storm", "streak", "stream", "strike", "stripe", "sun", "swipe", "swoop",
        "tail", "tree", "throat", "tuft", "watcher", "water", "whisper", "willow", "wind", "wing", "wish"
        "bark", "bloom", "bracken", "burrow", "clouds", "crawl", "eater", "fawn", "flake", "fox", "horse", "ice",
        "leaves", "lightning", "minnow", "moss", "muzzle", "paws", "peak", "rain", "ripple", "river", "roar", "scratch", "snout", 
        "talon", "teeth", "thistle", "thorn", "toe", "wave", "whistle", 
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
        'Agouti': ['back', 'pelt', 'fur']
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
        'Acacia', 'Acorn', 'Adder', 'Alder', 'Algae', 'Almond', 'Aloe', 'Amber', 'Ant', 'Antler', 'Apple', 'Apricot', 'Arc', 'Arch', 'Arctic',
        'Ash', 'Ashen', 'Aspen', 'Aster', 'Autumn', 'Badger', 'Bark', 'Barley', 'Basil', 'Bass', 'Bat', 'Bay', 'Bayou', 'Beam',
        'Bear', 'Beaver', 'Bee', 'Beech', 'Beetle', 'Berry', 'Big', 'Birch', 'Bird', 'Bite', 'Bitter', 'Bittern', 'Blaze', 'Bleak', 'Blight',
        'Blink', 'Bliss', 'Bloom', 'Blossom', 'Blotch', 'Bluff', 'Bog','Bold', 'Borage', 'Bough', 'Boulder', 'Bounce', 'Bracken', 'Bramble',
        'Branch', 'Brave', 'Breeze', 'Briar', 'Bright', 'Brindle', 'Bristle', 'Broken', 'Brook', 'Brush', 'Bubble', 'Bubbling', 'Buck',
        'Bug', 'Bumble', 'Burdock', 'Burn', 'Burnt', 'Burr', 'Bush', 'Buzzard', 'Carp', 'Cedar', 'Chaffinch', 'Char', 'Cheetah', 'Cherry',
        'Chestnut', 'Chive', 'Cicada', 'Cinder', 'Cinnamon', 'Claw', 'Clay', 'Cliff', 'Cloud', 'Clover', 'Coast', 'Cobra', 'Cod', 'Cold',
        'Condor', 'Cone', 'Conifer', 'Copper', 'Cotton', 'Cougar', 'Cow', 'Coyote', 'Crab', 'Crag', 'Crane', 'Creek', 'Cress', 'Crested',
        'Cricket', 'Crooked', 'Crouch', 'Crow', 'Crow', 'Crystal', 'Curl', 'Curlew', 'Curly', 'Cypress', 'Dahlia', 'Daisy', 'Damp', 'Dapple', 'Dappled',
        'Dark', 'Dawn', 'Day', 'Dead', 'Deer', 'Desert' 'Dew', 'Doe', 'Dog', 'Dove', 'Down', 'Downy', 'Drake', 'Dragon', 'Drift', 'Drizzle', 'Drought',
        'Dry', 'Duck', 'Dull', 'Dune', 'Dusk', 'Dust', 'Eagle', 'Earth', 'Echo', 'Eel', 'Egret', 'Elk', 'Elm', 'Ember', 'Energy', 'Ermine', 'Eternal', 'Faded', 'Fading', 'Fae',
        'Falcon', 'Fallen', 'Fallow', 'Fawn', 'Feather', 'Fennel', 'Fern', 'Ferret', 'Fidget', 'Fierce', 'Fin', 'Finch', 'Fir', 'Fish',
        'Flail', 'Flame', 'Flash', 'Flax', 'Fleck', 'Fleet', 'Flicker', 'Flight', 'Flint', 'Flip', 'Flood', 'Flower', 'Flower',
        'Flurry', 'Flutter', 'Fly', 'Foam', 'Forest', 'Fox', 'Freckle', 'Freeze', 'Fringe', 'Frog', 'Frond', 'Frost', 'Frozen', 'Furled',
        'Fuzzy', 'Gander', 'Gannet', 'Gem', 'Ghost', 'Giant', 'Gill', 'Gleam', 'Glow', 'God', 'Goose', 'Gorge', 'Gorse', 'Grass', 'Gravel', 'Ground', 'Grouse', 'Gull', 'Gust',
        'Hail', 'Half', 'Hare', 'Harvest', 'Hatch', 'Hawk', 'Hay', 'Haze', 'Heath', 'Heather', 'Heavy', 'Hedge', 'Hen', 'Heron', 'Hickory',
        'Hill', 'Hoarse', 'Hollow', 'Holly', 'Hoot', 'Hop', 'Hope', 'Hornet', 'Hound', 'Ice', 'Icy', 'Iris', 'Ivy', 'Jagged', 'Jasper', 'Jay', 'Jet',
        'Jump', 'Juniper', 'Kestrel', 'Kink', 'Kite', 'Lake', 'Larch', 'Lark', 'Laurel', 'Lavender', 'Leaf', 'Leap', 'Leopard', 'Lichen', 'Light',
        'Lightning', 'Lilac', 'Lily', 'Little', 'Lizard', 'Locust', 'Log', 'Long', 'Lost', 'Lotus', 'Loud', 'Low', 'Lynx', 'Maggot', 'Magic',
        'Mallow', 'Mantis', 'Maple', 'Marigold', 'Marsh', 'Marten', 'Meadow', 'Mellow', 'Merry', 'Midge', 'Milk', 'Mind', 'Mink', 'Minnow', 'Mint', 'Mist',
        'Mistle', 'Misty', 'Mite', 'Mock', 'Mole', 'Moon', 'Moor', 'Morning', 'Moss', 'Mossy', 'Moth', 'Mottle', 'Mottled', 'Mountain',
        'Mouse', 'Mud', 'Mumble', 'Murk', 'Nacre', 'Narrow', 'Nectar', 'Needle', 'Nettle', 'Newt', 'Night', 'Nut', 'Oak', 'Oat', 'Odd', 'One',
        'Orange', 'Osprey', 'Otter', 'Owl', 'Pale', 'Pansy', 'Panther', 'Parsley', 'Partridge', 'Patch', 'Peak', 'Pear', 'Peat',
        'Pebble', 'Pepper', 'Perch', 'Petal', 'Pheasant', 'Pigeon', 'Pike', 'Pine', 'Piper', 'Plover', 'Pod', 'Pond', 'Pool', 'Poppy', 'Posy',
        'Pounce', 'Prance', 'Prickle', 'Prim', 'Puddle', 'Python', 'Quail', 'Quick', 'Quiet', 'Quill', 'Rabbit', 'Raccoon', 'Ragged', 'Rain',
        'Rambling', 'Rat', 'Rattle', 'Raven', 'Reed', 'Ridge', 'Rift', 'Ripple', 'River', 'Roach', 'Robin', 'Rock', 'Rook', 'Root', 'Rose',
        'Rosy', 'Rot', 'Rowan', 'Royal', 'Rubble', 'Running', 'Rush', 'Rust', 'Rye', 'Sage', 'Sandy', 'Scar', 'Scorch', 'Sea', 'Sedge', 'Seed', 'Shade',
        'Shard', 'Sharp', 'Shell', 'Shimmer', 'Short', 'Shrew', 'Shy', 'Silk', 'Silt', 'Skip', 'Sky', 'Slate', 'Sleek', 'Sleet', 'Slight', 'Sloe',
        'Slope', 'Small', 'Smoke', 'Smoky', 'Snail', 'Snake', 'Snap', 'Sneeze', 'Snip', 'Soft', 'Song', 'Soot', 'Sorrel', 'Spark', 'Sparrow',
        'Speckle', 'Spider', 'Spike', 'Spire', 'Spirit', 'Splash', 'Spotted', 'Spring', 'Spruce', 'Squirrel', 'Stag', 'Starling', 'Steam', 'Stoat', 'Stone',
        'Stork', 'Storm', 'Stream', 'Strike', 'Stump', 'Swallow', 'Swamp', 'Swan', 'Sweet', 'Swift', 'Tall', 'Talon', 'Thistle', 'Thorn',
        'Thrift', 'Thunder', 'Thyme', 'Tiger', 'Timber', 'Time', 'Tip', 'Toad', 'Torn', 'Trout', 'Tuft', 'Tulip', 'Tumble', 'Turtle', 'Twig', 'Vine', 'Violet', 'Vixen',
        'Vole', 'Warm', 'Wasp', 'Weasel', 'Web', 'Weed', 'Wet', 'Wheat', 'Whirl', 'Whisker', 'Wild', 'Willow', 'Wind', 'Wisteria', 'Wolf', 'Wood', 
        'Wren', 'Wyrm', 'Wyvern', 'Yarrow', 'Yew'
        'Blizzard', 'Bluebell', 'Chasing', 'Claw', 'Clear', 'Dancing', 'Dandelion', 'Dangling', 'Dapples', 'Dewy',
        'Elder', 'Falling',  'Fluttering', 'Fog', 'Furze', 'Gale', 'Haven', 'Honey', 'Jackdaw', 
        'Lapping', 'Lion', 'Melting', 'Milkweed', 'Monkey', 'Myrtle', 'Pink', 'Plum', 'Primrose', 'Rainswept', 'Rising', 
        'Shattered', 'Sheep', 'Shining', 'Shivering', 'Shred', 'Snook', 'Spot', 'Stem', 'Stripe', 'Strong', 'Stumpy', 'Sunny', 'Tangle', 'Tansy', 'Tawny', 
        'Thrush', 'Tiny', 'Twisted', 'Wave', 'Whisper', 'Whispering', 'Whistle', 'Whorl', 'Wish',
    ]

    colour_prefixes = {
        'WHITE': [
            'White', 'White', 'Pale', 'Snow', 'Cloud', 'Cloudy', 'Milk', 'Hail', 'Frost', 'Frozen', 'Freeze', 'Ice', 'Icy', 'Sheep',
            'Blizzard', 'Flurry', 'Moon', 'Star', 'Light', 'Bone', 'Bright', 'Swan', 'Dove', 'Wooly', 'Cotton', 'Warm', 'Arctic'
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
            'Brown', 'Oak', 'Mouse', 'Dark', 'Shade', 'Russet', 'Dust', 'Dusty' 'Acorn', 'Mud', 'Deer', 'Fawn', 'Doe', 'Stag',
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
        "Abyss", "Ace", "Ah" ,"Alcina", "Alec", "Alice", "Amber", "Amity", "Amy", "Angel", "Anita", "Anubis", "Armin", "April", "Ash", 
        "Aurora", "Azula", "Aries", "Aquarius", "Bagel", "Bailey", "Bandit", "Baphomet", "Bastet", "Bean", "Beanie Baby", "Beans", "Bede",
        "Belle", "Benny", "Bently", "Bentley", "Beverly", "Big Man", "Birb", "Blu",  "Bluebell", "Bologna", "Bolt", "Bonbon", "Bongo", "Bonnie",
        "Bonny", "Boo", "Broccoli", "Buddy", "Bumblebee", "Bunny", "Burger", "Burm", "Bub", "Cake", "Callie", "Calvin", "Caramel", "Carmen", 
        "Carmin", "Carolina", "Caroline", "Carrie", "Catie", "Catty", "Chance", "Chanel", "Chansey", "Chaos", "Charles", "Charlie", "Charlotte",
        "Charm", "Chase", "Cheese", "Cheesecake", "Cheeto", "Cheetoman", "Chef", "Cherry", "Chester", "Chewie", "Chewy", "Chicco", "Chief", "Chinook",
        "Chip", "Chloe", "Chocolate", "Chocolate Chip", "Chris", "Chrissy", "Cinder", "Cinderblock", "Cloe", "Cloud", "Cocoa", "Cocoa Puff", "Coffee",
        "Conan", "Cookie", "Coral", "Cosmo", "Cowbell", "Cowboy", "Crab", "Cracker", "Cream", "Crispy", "Crow", "Crunchwrap", "Crunchy", "Cupcake", "Cooper",
        "Cancer", "Capricorn", "Dakota", "Dan", "Dave", "Deli", "Delilah", "Della", "Dewey", "Dirk", "Dolly", "Donald", "Dragonfly", "Dreamy", "Duchess", "Dune",
        "Dunnock" "Eclipse", "Daisy Mae",  "Eda", "Eddie", "Eevee", "Egg", "Ember", "Emerald", "Emi", "Emma", "Emy", "Erica", "Espresso", "Eve", "Evelyn", "Evie",
        "Evilface", "Erebus", "Fallow", "Fang", "Fawn", "Feather", "Felix", "Fern", "Ferret", "Ferry", "Finch", "Firefly", "Fishleg", "Fishtail", "Fiver", "Flabby",
        "Flower", "Fluffy", "Flutie", "Fork", "Frank", "Frankie", "Frannie", "Fred", "Freddy", "Free", "French", "French Fry", "Frito", "Fry", "Frye", "Gamble", 
        "Gargoyle", "Garnet", "Geode", "George", "Ghost", "Gibby", "Gir", "Gizmo", "Glass", "Glory", "Goose", "Grace", "Grain", "Grasshopper", "Gravy", "Guinness",
        "Gust", "Gwendoline", "Gwynn", "Gemini", "Habanero", "Haku", "Harvey", "Havoc", "Herc", "Hercules", "Hiccup", "Holly", "Hop", "Hot Sauce", "Hotdog",
        "Hughie", "Human", "Hunter", "Harlequin", "Ice", "Icecube", "Ice Cube", "Icee", "Igor", "Ike", "Indi", "Insect", "Isabel", "Jack", "Jade", "Jaiden",
        "Jake", "James", "Jasper", "Jaxon", "Jay", "Jenny", "Jesse", "Jessica", "Jester", "Jethro", "Jewel","Jewels", "Jimmy", "Jinx", "John", "Johnny",
        "Joker", "Jolly", "Jolly Rancher", "Joob", "Jubie", "Judas", "Jude", "Judy", "Juliet", "June", "Jupiter", "KD", "Kate", "Katy", "Kelloggs", "Ken",
        "Kendra", "Kenny", "Kermit", "Kerry", "Ketchup", "King", "Kingston", "Kip", "Kisha", "Kitty", "Kitty Cat", "Klondike", "Knox", "Kodiak", "Kong", "L", "Lacy",
        "Lakota", "Laku", "Lee", "Leo", "Leon", "Lester", "Lex", "Lilith", "Lily", "Lily", "Loaf", "Lobster", "Lola", "Loona", "Lora", "Louie", "Louis", "Lucky",
        "Lucy", "Lugnut", "Luigi", "Luna", "Lupo", "Loyalty", "Libra", "Madi", "Makwa", "Maleficent", "Manda", "Mange", "Mango", "Marceline", "Matcha", 
        "Maverick", "Max", "May", "McChicken", "McFlurry", "Meatlug", "Melody", "Meow-Meow", "Meowyman", "Mera", "Mew", "Miles", "Millie", "Milo",
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
        "Shimmer", "Shiver", "Silva", "Silver", "Skrunkly", "Sloane", "Slug", "Slushie", "Smoothie", "Smores", "Sneakers", "Snek", "Snotlout", "Socks", 
        "Sofa", "Sol", "Sonic", "Sophie", "Sorbet", "Sox", "Spam", "Sparky", "Spots", "Stan", "Star", "Starfish", "Stella", "Steve", "Steven", "Stinky",
        "Stolas", "Stripes", "Sundae", "Sunny", "Sunset", "Sweet", "Sweetie", "Scorpio", "Sagittarius", "Tabatha", "Tabby", "Tabbytha", "Taco", "Taco Bell",
        "Tasha", "Tempest", "Tetris", "Teufel", "Tiny", "Toast", "Toffee", "Tom", "Tomato", "Tomato Soup", "Toni", "Toothless", "Torque", "Tortilla", 
        "Treasure", "Triscuit", "Trixie", "Trouble", "Tucker", "Tuffnut", "Tumble", "Turbo", "Twilight", "Twister", "Twix", "Toastee", "Taurus", "Ula", "Union",
        "Uriel", "Vanilla", "Vaxx", "Venture", "Via", "Vida", "Viktor", "Vinnie", "Vinyl", "Violet", "Vivienne", "Void", "Voltage", "Vox", "Virgo", "Wanda", "Webby",
        "Wendy", "Whiskers", "Whisper", "Wigglebottom", "Wigglebutt", "Windy", "Wishbone", "Wisp", "Wisteria", "Worm", "X'ek", "Zelda", "Zim", "Zoe",
        "Olivier", "Kaz", "Kira", "Shira", "Marina", "Nur", "Roy", "Gala", "Bilbo", "Geralt", "Witcher", "Homunculus", "Alchemist", "The Knight", "Inej", "Jesper",
        "Nina", "Matthias", "Wylan", "Dirtyhands", "Wraith", "Monomon", "Lurien", "Herrah", "Shabor", "Pharaoh", "Porki", "Dark"
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
        if self.status in ["deputy", "warrior", "medicine cat", "elder", "mediator"]:
            return self.prefix + self.suffix
        else:
            return self.prefix + self.special_suffixes[self.status]


names = Name()
