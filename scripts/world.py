from noise import snoise2
from numpy import zeros
import csv

class World:
    def __init__(self, shape, seed):
        self.shape = shape
        self.seed = seed
        self.main_noise_map = self.generate_noise_map(self.seed, 5)
        self.height_map = self.generate_noise_map(self.seed + self.seed, 15)

    def generate_noise_map(self, seed, scale):
        noise_tile = zeros(self.shape)
        for y in range(self.shape[0]):
            for x in range(self.shape[1]):
                noise_tile[x][y] = snoise2(x/scale, y/scale, octaves=6, persistence = 0.5, lacunarity = 2.0, base=seed, repeatx=40,repeaty=44)
        return noise_tile

    def check_noise_tile(self, x, y):
        return self.main_noise_map[x][y]
    
    def check_heighttile(self, x, y):
        return self.height_map[x][y]
    
def save_map(mapinfo, clanname):
    with open(f'saves/{clanname}map.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        for key in mapinfo:
            writer.writerow(mapinfo[key])

def load_map(clanname):
    dict_from_csv = {}
    with open(f'{clanname}map.csv', 'r') as read_file:
            clan_data = read_file.read()
    sections = clan_data.split('\n')
    for tileinfo in sections:
        if tileinfo == "":
            continue
        tileinfo = tileinfo.split(',')
        for trait in tileinfo:
            if tileinfo[0] == "":
                continue
            else:
                x = int(tileinfo[0])
                y = int(tileinfo[1])
                tile_biome = tileinfo[2]
                tile_claim = tileinfo[3]
                tile_twolegs = tileinfo[4]
                tile_thunderpath = tileinfo[5]
                tile_prey = tileinfo[6]
                tile_plants = tileinfo[7]
                dict_from_csv[(x,y)] = [x,y,tile_biome,tile_claim,tile_twolegs,tile_thunderpath,tile_prey,tile_plants]
    return dict_from_csv
