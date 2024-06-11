class CatConfig:
    no_kits = False
    no_mates = False
    no_retire = False
    prevent_fading = False
    favorite = False

    def __init__(self, no_kits=False, no_mates=False, no_retire=False, prevent_fading=False, favorite=False):
        self.no_kits = no_kits
        self.no_mates = no_mates
        self.no_retire = no_retire
        self.prevent_fading = prevent_fading
        self.favorite = favorite
