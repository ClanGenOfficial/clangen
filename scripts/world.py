import pygame
import math
from noise import snoise2
import numpy as np
import pandas as pd

class World:
    def __init__(self, shape, seed):
        self.shape = shape
        self.seed = seed
        self.main_noisemap = self.generate_noisemap(self.seed, 5)
        self.heightmap = self.generate_noisemap(self.seed + self.seed, 15)

    def generate_noisemap(self, seed, scale):
        noisetile = np.zeros(self.shape)
        for y in range(self.shape[0]):
            for x in range(self.shape[1]):
                noisetile[x][y] = snoise2(x/scale, y/scale, octaves=6, persistence = 0.5, lacunarity = 2.0, base=seed, repeatx=40,repeaty=44)
        return noisetile

    def check_noisetile(self, x, y):
        return self.main_noisemap[x][y]
    
    def check_heighttile(self, x, y):
        return self.heightmap[x][y]
    
def save_map(mapinfo, clanname):
    mapinfo = pd.DataFrame.from_dict(mapinfo, orient='index')
    mapinfo.to_csv(f'saves/{clanname}map.csv', index = False, header=False)

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
