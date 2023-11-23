from random import choice, randint
import json
from operator import xor


class Genotype:
    def __init__(self, spec=None):
        self.furLength = ""
        self.eumelanin = ["", ""]
        self.sexgene = ["", ""]
        self.tortiepattern = None
        self.brindledbi = False
        if spec:
            self.chimera = False
            self.chimerapattern = None
        else:
            a = randint(1, 250)
            if a == 1:
                self.chimera = True
            else:
                self.chimera = False
            self.chimerapattern = None
        if self.chimera:
            self.chimerageno = Genotype('chimera')
        else:
            self.chimerageno = None
        self.gender = ""
        self.dilute = ""
        self.white = ["", ""]
        self.whitegrade = randint(1, 5)
        self.vitiligo = False
        self.deaf = False
        self.pointgene = ["", ""]
        self.silver = ""
        self.agouti = ["", ""]
        self.mack = ""
        self.ticked = ""
        self.breakthrough = False

        self.york = ["yuc", "yuc"]
        self.wirehair = ["wh", "wh"]
        self.laperm = ["lp", "lp"]
        self.cornish = ["R", "R"]
        self.urals = ["Ru", "Ru"]
        self.tenn = ["Tr", "Tr"]
        self.fleece = ["Fc", "Fc"]
        self.sedesp = ["Hr", "Hr"]
        self.ruhr = ["hrbd", "hrbd"]
        self.ruhrmod = ""
        self.lykoi = ["Ly", "Ly"]

        self.pinkdilute = ["Dp", "Dp"]
        self.dilutemd = ["dm", "dm"]
        self.ext = ["E", "E"]
        self.sunshine = ["G", "G"]
        self.karp = ["k", "k"]
        self.bleach = ["Lb", "Lb"]
        self.ghosting = ["gh", "gh"]
        self.satin = ["St", "St"]
        self.glitter = ["Gl", "Gl"]

        self.curl = ["cu", "cu"]
        self.fold = ["fd", "fd"]
        self.manx = ["ab", "ab"]
        self.manxtype = choice(["long", "most", "most", "stubby", "stubby", "stubby", "stubby", "stubby", "stubby", "stumpy", "stumpy", "stumpy", "stumpy", "stumpy", "stumpy", "stumpy", "stumpy", "riser", "riser", "riser", "riser", "riser", "riser", "riser", "riser", "riser", "rumpy", "rumpy", "rumpy", "rumpy", "rumpy", "rumpy", "rumpy", "rumpy", "rumpy", "rumpy"])
        self.kab = ["Kab", "Kab"]
        self.toybob = ["tb", "tb"]
        self.jbob = ["Jb", "Jb"]
        self.kub = ["kub", "kub"]
        self.ring = ["Rt", "Rt"]
        self.munch = ["mk", "mk"]
        self.poly = ["pd", "pd"]
        self.altai = ["al", "al"]

        self.wideband = ""
        self.wbtype = ""
        self.wbsum = 0

        self.rufousing = ""
        self.ruftype = ""
        self.rufsum = 0

        self.bengal = ""
        self.bengtype = ""
        self.bengsum = 0

        self.sokoke = ""
        self.soktype = ""
        self.soksum = 0

        self.spotted = ""
        self.spottype = ""
        self.spotsum = 0

        self.tickgenes = ""
        self.ticktype = ""
        self.ticksum = 0

        self.refraction = ""
        self.refgrade = ""
        self.refsum = 0

        self.pigmentation = ""
        self.piggrade = ""
        self.pigsum = 0

        self.lefteye = ""
        self.righteye = ""
        self.lefteyetype = "Error"
        self.righteyetype = "Error"

        self.extraeye = None
        self.extraeyetype = ""
        self.extraeyecolour = ""

    def fromJSON(self, jsonstring):
        #jsonstring = json.loads(jsonstring)

        self.furLength = jsonstring["furLength"]
        self.eumelanin = jsonstring["eumelanin"]
        self.sexgene = jsonstring["sexgene"]
        self.tortiepattern = jsonstring["tortiepattern"]
        self.brindledbi = jsonstring["brindledbi"]

        try:
            self.chimera = jsonstring['chimera']
            self.chimerapattern = jsonstring['chimerapattern']
            if(jsonstring["chimerageno"]):
                self.chimerageno = Genotype('chimera')
                self.chimerageno.fromJSON(jsonstring["chimerageno"])
            else:
                self.chimerageno = None    
            self.deaf = jsonstring['deaf']
        except:
            self.chimera = False
            self.chimerapattern = None
            self.chimerageno = None
            self.deaf = False

        self.gender = jsonstring["gender"]
        self.dilute = jsonstring["dilute"]
        self.white = jsonstring["white"]
        self.whitegrade = jsonstring["whitegrade"]
        self.vitiligo = jsonstring["vitiligo"]
        self.pointgene = jsonstring["pointgene"]
        self.silver = jsonstring["silver"]
        self.agouti = jsonstring["agouti"]
        self.mack = jsonstring["mack"]
        self.ticked = jsonstring["ticked"]
        self.breakthrough = jsonstring["breakthrough"]

        self.york = jsonstring["york"]
        self.wirehair = jsonstring["wirehair"]
        self.laperm = jsonstring["laperm"]
        self.cornish = jsonstring["cornish"]
        self.urals = jsonstring["urals"]
        self.tenn = jsonstring["tenn"]
        self.fleece = jsonstring["fleece"]
        self.sedesp = jsonstring["sedesp"]
        self.ruhr = jsonstring["ruhr"]
        self.ruhrmod = jsonstring["ruhrmod"]
        self.lykoi = jsonstring["lykoi"]
    
        self.pinkdilute = jsonstring["pinkdilute"]
        self.dilutemd = jsonstring["dilutemd"]
        self.ext = jsonstring["ext"]
        self.sunshine = jsonstring["sunshine"]
        self.karp = jsonstring["karp"]
        self.bleach = jsonstring["bleach"]
        self.ghosting = jsonstring["ghosting"]
        self.satin = jsonstring["satin"]
        self.glitter = jsonstring["glitter"]
    
        self.curl = jsonstring["curl"]
        self.fold = jsonstring["fold"]
        self.manx = jsonstring["manx"]
        self.manxtype = jsonstring["manxtype"]
        self.kab = jsonstring["kab"]
        self.toybob = jsonstring["toybob"]
        self.jbob = jsonstring["jbob"]
        self.kub = jsonstring["kub"]
        self.ring = jsonstring["ring"]
        self.munch = jsonstring["munch"]
        self.poly = jsonstring["poly"]
        self.altai = jsonstring["altai"]

        self.wideband = jsonstring["wideband"]
        #self.wbtype = jsonstring["wbtype"]
        #self.wbsum = jsonstring["wbsum"]

        self.rufousing = jsonstring["rufousing"]
        #self.ruftype = jsonstring["ruftype"]
        #self.rufsum = jsonstring["rufsum"]

        self.bengal = jsonstring["bengal"]
        #self.bengtype = jsonstring["bengtype"]
        #self.bengsum = jsonstring["bengsum"]

        self.sokoke = jsonstring["sokoke"]
        #self.soktype = jsonstring["soktype"]
        #self.soksum = jsonstring["soksum"]

        self.spotted = jsonstring["spotted"]
        #self.spottype = jsonstring["spottype"]
        #self.spotsum = jsonstring["spotsum"]

        self.tickgenes = jsonstring["tickgenes"]
        #self.ticktype = jsonstring["ticktype"]
        #self.ticksum = jsonstring["ticksum"]

        self.refraction = jsonstring["refraction"]
        #self.refgrade = jsonstring["refgrade"]
        #self.refsum = jsonstring["refsum"]

        self.pigmentation = jsonstring["pigmentation"]
        #self.piggrade = jsonstring["piggrade"]
        #self.pigsum = jsonstring["pigsum"]

        self.lefteye = jsonstring["lefteye"]
        self.righteye = jsonstring["righteye"]
        self.lefteyetype = jsonstring["lefteyetype"]
        self.righteyetype = jsonstring["righteyetype"]
        
        self.extraeye = jsonstring["extraeye"]
        self.extraeyetype = jsonstring["extraeyetype"]
        self.extraeyecolour = jsonstring["extraeyecolour"]

        self.PolyEval()

    def toJSON(self):
        chimgen = None

        if self.chimerageno:
            chimgen = self.chimerageno.toJSON()

        return {
            "furLength": self.furLength,
            "eumelanin": self.eumelanin,
            "sexgene" : self.sexgene,
            "tortiepattern" : self.tortiepattern,
            "brindledbi" : self.brindledbi,

            "chimera" : self.chimera,
            "chimerapattern" : self.chimerapattern,
            "chimerageno" : chimgen,

            "gender": self.gender,
            "dilute": self.dilute,
            "white" : self.white,
            "whitegrade" : self.whitegrade,
            "vitiligo" : self.vitiligo,
            "deaf" : self.deaf,
            "pointgene" : self.pointgene,
            "silver" : self.silver,
            "agouti" : self.agouti,
            "mack" : self.mack,
            "ticked" : self.ticked,
            "breakthrough" : self.breakthrough,

            "york" : self.york,
            "wirehair" : self.wirehair,
            "laperm" : self.laperm,
            "cornish" : self.cornish,
            "urals" : self.urals,
            "tenn" : self.tenn,
            "fleece" : self.fleece,
            "sedesp" : self.sedesp,
            "ruhr" : self.ruhr,
            "ruhrmod" : self.ruhrmod,
            "lykoi" : self.lykoi,

            "pinkdilute" : self.pinkdilute,
            "dilutemd" : self.dilutemd,
            "ext" : self.ext,
            "sunshine" : self.sunshine,
            "karp" : self.karp,
            "bleach" : self.bleach,
            "ghosting" : self.ghosting,
            "satin" : self.satin,
            "glitter" : self.glitter,

            "curl" : self.curl,
            "fold" : self.fold,
            "manx" : self.manx,
            "manxtype" : self.manxtype,
            "kab" : self.kab,
            "toybob" : self.toybob,
            "jbob" : self.jbob,
            "kub" : self.kub,
            "ring" : self.ring,
            "munch" : self.munch,
            "poly" : self.poly,
            "altai" : self.altai,

            "wideband" : self.wideband,
            "rufousing" : self.rufousing,
            "bengal" : self.bengal,
            "sokoke" : self.sokoke,
            "spotted" : self.spotted,
            "tickgenes" : self.tickgenes,
            "refraction" :self.refraction,
            "pigmentation" : self.pigmentation,
            
            "lefteye" : self.lefteye,
            "righteye" : self.righteye,
            "lefteyetype" :self.lefteyetype,
            "righteyetype" : self.righteyetype,
            
            "extraeye" : self.extraeye,
            "extraeyetype" :self.extraeyetype,
            "extraeyecolour" : self.extraeyecolour
        }

    def Generator(self, special=None):
        if self.chimera:
            self.chimerageno.Generator()
        
        a = randint(1, 100)
        if a == 1:
            self.vitiligo = True

        # FUR LENGTH
        
        a = randint(1, 4)

        if a == 1:
            self.furLength = ["L", "L"]
        elif a == 4:
            self.furLength = ["l", "l"]
        else:
            self.furLength = ["L", "l"]

        # EUMELANIN

        for i in range(2):
            if randint(1, 10) == 1:
                self.eumelanin[i] = "bl"
            elif randint(1, 5) == 1:
                self.eumelanin[i] = "b"
            else:
                self.eumelanin[i] = "B"

        # RED GENE

        if (randint(1, 2) == 1 and special != "fem") or special == "masc":
            self.sexgene = ["", "Y"]
            if randint(1, 1000) == 1:
                self.sexgene = ["", "", "Y"]
            
                for i in range(2):
                    if randint(1, 2) == 1:
                        self.sexgene[i] = "O"
                    else:
                        self.sexgene[i] = "o"
            else:
                if randint(1, 2) == 1:
                    self.sexgene[0] = "O"
                else:
                    self.sexgene[0] = "o"
            self.gender = "tom"
        else:
            if randint(1, 1000) == 1:
                self.sexgene = ["", "", ""]
                for i in range(3):
                    if randint(1, 2) == 1:
                        self.sexgene[i] = "O"
                    else:
                        self.sexgene[i] = "o"
            else:
                for i in range(2):
                    if randint(1, 2) == 1:
                        self.sexgene[i] = "O"
                    else:
                        self.sexgene[i] = "o"
            self.gender = "molly"
        if 'o' in self.sexgene and 'O' in self.sexgene and randint(1, 250)==1:
            self.brindledbi = True 

        # DILUTE

        a = randint(1, 4)

        if a == 1:
            self.dilute = ["D", "D"]
        elif a == 4:
            self.dilute = ["d", "d"]
        else:
            self.dilute = ["D", "d"]

        # WHITE

        for i in range(2):

            if randint(1, 100) == 1:
                self.white[i] = "wg"
            elif randint(1, 100) == 1:
                self.white[i] = "wt"
            elif randint(1, 20) == 1:
                self.white[i] = "W"
            elif randint(1, 2) == 1:
                self.white[i] = "ws"
            else:
                self.white[i] = "w"

        # ALBINO

        for i in range(2):
            a = randint(1, 100)
            b = randint(1, 100)
            c = randint(1, 10)
            d = randint(1, 5)

            if a == 1:
                self.pointgene[i] = "c"
            elif b == 1:
                self.pointgene[i] = "cm"
            elif c == 1:
                self.pointgene[i] = "cb"
            elif d == 1:
                self.pointgene[i] = "cs"
            else:
                self.pointgene[i] = "C"

        # SILVER

        a = randint(1, 100)

        if a == 1:
            self.silver = ["I", "I"]
        elif a < 12:
            self.silver = ["I", "i"]
        else:
            self.silver = ["i", "i"]

        # AGOUTI

        for i in range(2):
            a = randint(1, 100)
            b = randint(1, 2)
            if a == 1:
                self.agouti[i] = "Apb"
            elif b == 1:
                self.agouti[i] = "A"
            else:
                self.agouti[i] = "a"

        #print(self.agouti)
        # MACKEREL

        a = randint(1, 4)

        if a == 1:
            self.mack = ["Mc", "Mc"]
        elif a == 4:
            self.mack = ["mc", "mc"]
        else:
            self.mack = ["Mc", "mc"]

        # TICKED

        a = randint(1, 25)

        if a == 1:
            self.ticked = ["Ta", "Ta"]
        elif a <= 6:
            self.ticked = ["Ta", "ta"]
            if randint(1, 25) == 1:
                self.breakthrough = True
        else:
            self.ticked = ["ta", "ta"]

        # YORK, WIREHAIR, LAPERM, CORNISH, URAL, TENN, FLEECE

        A = [0, 0, 0, 0, 0, 0, 0]
        
        for i in range(7):
            a = randint(1, 1600)
            A[i] = a

        if A[0] == 1:
            self.york = ["Yuc", "Yuc"]
        elif A[0] <= 41:
            self.york = ["Yuc", "yuc"]
        
        if A[1] == 1:
            self.wirehair = ["Wh", "Wh"]
        elif A[1] <= 41:
            self.wirehair = ["Wh", "wh"]
        
        if A[2] == 1:
            self.laperm = ["Lp", "Lp"]
        elif A[2] <= 41:
            self.laperm = ["Lp", "lp"]
        
        if A[3] == 1:
            self.cornish = ["r", "r"]
        elif A[3] <= 41:
            self.cornish = ["R", "r"]
        
        if A[4] == 1:
            self.urals = ["ru", "ru"]
        elif A[4] <= 41:
            self.urals = ["Ru", "ru"]
        
        if A[5] == 1:
            self.tenn = ["tr", "tr"]
        elif A[5] <= 41:
            self.tenn = ["Tr", "tr"]
        
        if A[6] == 1:
            self.fleece = ["fc", "fc"]
        elif A[6] <= 41:
            self.fleece = ["Fc", "fc"]
            
        
        #SELKIRK/DEVON/HAIRLESS
    
        for i in range(2):
            a = randint(1, 100)
            b = randint(1, 40)
            c = randint(1, 40)

            if a == 1:
                self.sedesp[i] = "hr"
            elif b == 1:
                self.sedesp[i] = "re"
            elif c == 1:
                self.sedesp[i] = "Se"


        #ruhr + ruhrmod + lykoi

        a = randint(1, 10000)

        if a == 1:
            self.ruhr = ["Hrbd", "Hrbd"]
        elif a <= 101:
            self.ruhr = ["Hrbd", "hrbd"]
        
        a = randint(1, 4)

        if a == 1:
            self.ruhrmod = ["hi", "hi"]
        elif a == 4:
            self.ruhrmod = ["ha", "ha"]
        else:
            self.ruhrmod = ["hi", "ha"]

        a = randint(1, 10000)

        if a == 1:
            self.lykoi = ["ly", "ly"]
        elif a <= 101:
            self.lykoi = ["Ly", "ly"]

        # pinkdilute + dilutemd

        a = randint(1, 2500)

        if a == 1:
            self.pinkdilute = ["dp", "dp"]
        elif a <= 51:
            self.pinkdilute[1] = "dp"
        
        a = randint(1, 2500)

        if a == 1:
            self.dilutemd = ["Dm", "Dm"]
        elif a <= 51:
            self.dilutemd[0] = "Dm"

        # ext

        for i in range(2):
            a = randint(1, 50)
            b = randint(1, 40)
            c = randint(1, 40)
            d = randint(1, 40)

            if a == 1:
                self.ext[i] = "Eg"
            elif b == 1:
                self.ext[i] = "ec"
            elif c == 1:
                self.ext[i] = "er"
            elif d == 1:
                self.ext[i] = "ea"

        #sunshine

        for i in range(2):
            a = randint(1, 40)
            b = randint(1, 40)
            c = randint(1, 40)

            if a == 1:
                self.sunshine[i] = "sh" #sunSHine
            elif b == 1:
                self.sunshine[i] = "sg" #Siberian Gold / extreme sunshine
            elif c == 1:
                self.sunshine[i] = "fg" #Flaxen Gold
            else:
                self.sunshine[i] = "N" #No

        # karp + bleach + ghosting + satin + glitter

        for i in range(5):
            a = randint(1, 10000)
            A[i] = a

        if A[0] == 1:
            self.karp = ["K", "K"]
        elif A[0] <= 101:
            self.karp[0] = "K"

        if A[1] == 1:
            self.bleach = ["lb", "lb"]
        elif A[1] <= 101:
            self.bleach[1] = "lb"
        
        if A[2] == 1:
            self.ghosting = ["Gh", "Gh"]
        elif A[2] <= 101:
            self.ghosting[0] = "Gh"
        
        if A[3] == 1:
            self.satin = ["st", "st"]
        elif A[3] <= 101:
            self.satin[1] = "st"
        
        if A[4] == 1:
            self.glitter = ["gl", "gl"]
        elif A[4] <= 101:
            self.glitter[1] = "gl"

        # curl + fold

        a = randint(1, 2500)

        if a == 1:
            self.curl = ["Cu", "Cu"]
        elif a <= 51:
            self.curl[0] = "Cu"
        
        a = randint(1, 50)

        if a == 1:
            self.fold[0] = "Fd"


        #  manx + kab + toybob + jbob + kub + ring

        a = randint(1, 40)
        b = randint(1, 40)

        if a == 1:
            self.manx = ["Ab", "ab"]
        elif b == 1:
            self.manx = ["M", "m"]
        
        for i in range(5):
            a = randint(1, 1600)
            A[i] = a

        if A[0] == 1:
            self.kab = ["kab", "kab"]
        elif A[0] <= 41:
            self.kab[1] = "kab"
        
        if A[1] == 1:
            self.toybob = ["Tb", "Tb"]
        elif A[1] <= 41:
            self.toybob[0] = "Tb"

        if A[2] == 1:
            self.jbob = ["jb", "jb"]
        elif A[2] <= 41:
            self.jbob[1] = "jb"
        
        if A[3] == 1:
            self.kub = ["Kub", "Kub"]
        elif A[3] <= 41:
            self.kub[0] = "Kub"

        if A[4] == 1:
            self.ring = ["rt", "rt"]
        elif A[4] <= 41:
            self.ring[1] = "rt"
        
        # munch + poly + altai

        a = randint(1, 50)

        if a == 1:
            self.munch[0] = "Mk"
        
        a = randint(1, 100)

        if a == 1:
            self.poly = ["Pd", "Pd"]
        elif a <= 11:
            self.poly[0] = "Pd"
        
        a = randint(1, 2500)

        if a == 1:
            self.altai = ["Al", "Al"]
        elif a <= 51:
            self.altai[0] = "Al"

        genes = ["2", "2", "1", "1", "1", "1", "1", "1", "0", "0"]
        
        wbtypes = ["low", "medium", "high", "shaded", "chinchilla"]
        ruftypes = ["low", "medium", "rufoused"]

        self.wideband = ''
        self.rufousing = ''
        self.spotted = ''
        self.tickgenes = ''
        self.bengal = ''
        self.sokoke = ''
        self.refraction = ''
        self.pigmentation = ''
        
        for i in range(0, 8):
            self.wideband += choice(genes)
            self.wbsum += int(self.wideband[i])

        if self.wbsum < 7:
            self.wbtype = wbtypes[0]
        elif self.wbsum < 10:
            self.wbtype = wbtypes[1]
        elif self.wbsum < 12: 
            self.wbtype = wbtypes[2]
        elif self.wbsum < 14: 
            self.wbtype = wbtypes[3]
        else: 
            self.wbtype = wbtypes[4]

        for i in range(0, 4):
            self.rufousing += choice(genes)
            self.rufsum += int(self.rufousing[i])

        if self.rufsum < 3: 
            self.ruftype = ruftypes[0]
        elif self.rufsum < 6: 
            self.ruftype = ruftypes[1]
        else:
            self.ruftype = ruftypes[2]

        spottypes = ["fully striped", "slightly broken stripes", "broken stripes", "mostly broken stripes", "spotted"]
        genesspot = ["2", "1", "0"]

        for i in range(0, 4):
            self.spotted += choice(genesspot)
            self.spotsum += int(self.spotted[i])

        if self.spotsum < 1: 
            self.spottype = spottypes[0]
        elif self.spotsum < 3:
            self.spottype = spottypes[1]
        elif self.spotsum < 6:
            self.spottype = spottypes[2]
        elif self.spotsum < 8: 
            self.spottype = spottypes[3]
        else:
            self.spottype = spottypes[4]
        
        ticktypes = ["full barring", "reduced barring", "agouti"]
        genesmild = ["2", "2", "1", "1", "1", "1", "1", "0", "0", "0", "0", "0", "0"]

        for i in range(0, 4):
            self.tickgenes += choice(genesmild)
            self.ticksum += int(self.tickgenes[i])

        if self.ticksum < 4: 
            self.ticktype = ticktypes[0]
        elif self.ticksum < 6:
            self.ticktype = ticktypes[1]
        else:
            self.ticktype = ticktypes[2]

        bengtypes = ["normal markings", "mild bengal", "full bengal"]

        for i in range(0, 4):
            self.bengal += choice(genesmild)
            self.bengsum += int(self.bengal[i])

        if self.bengsum < 4: 
            self.bengtype = bengtypes[0]
        elif self.bengsum < 6:
            self.bengtype = bengtypes[1]
        else:
            self.bengtype = bengtypes[2]

        soktypes = ["normal markings", "mild fading", "full sokoke"]

        eyegenes = ["2", "2", "1", "1", "1", "1", "0", "0", "0"]

        for i in range(0, 4):
            self.sokoke += choice(eyegenes)
            self.soksum += int(self.sokoke[i])

        if self.soksum < 4: 
            self.soktype = soktypes[0]
        elif self.soksum < 6:
            self.soktype = soktypes[1]
        else:
            self.soktype = soktypes[2]

        for i in range(0, 9):
            self.refraction += choice(eyegenes)
            self.refsum += int(self.refraction[i])
            self.pigmentation += choice(eyegenes)
            self.pigsum += int(self.pigmentation[i])

        if self.refsum == 0:
            self.refgrade = 1
        elif self.refsum <= 1:
            self.refgrade = 2
        elif self.refsum <= 3:
            self.refgrade = 3
        elif self.refsum <= 5:
            self.refgrade = 4
        elif self.refsum <= 7:
            self.refgrade = 5
        elif self.refsum <= 10:
            self.refgrade = 6
        elif self.refsum <= 12:
            self.refgrade = 7
        elif self.refsum <= 14:
            self.refgrade = 8
        elif self.refsum <= 16:
            self.refgrade = 9
        elif self.refsum < 18:
            self.refgrade = 10
        else:
            self.refgrade = 11

        if self.pigsum == 0:
            self.piggrade = 1
        elif self.pigsum <= 1:
            self.piggrade = 2
        elif self.pigsum <= 3:
            self.piggrade = 3
        elif self.pigsum <= 5:
            self.piggrade = 4
        elif self.pigsum <= 7:
            self.piggrade = 5
        elif self.pigsum <= 10:
            self.piggrade = 6
        elif self.pigsum <= 12:
            self.piggrade = 7
        elif self.pigsum <= 14:
            self.piggrade = 8
        elif self.pigsum <= 16:
            self.piggrade = 9
        elif self.pigsum < 18:
            self.piggrade = 10
        else:
            self.piggrade = 11

        self.GeneSort()

        self.EyeColourFinder()

        self.refgrade = "R" + str(self.refgrade)
        self.piggrade = "P" + str(self.piggrade)

    def AltGenerator(self, special=None):
        if self.chimera:
            self.chimerageno.AltGenerator()
        a = randint(1, 100)
        if a == 1:
            self.vitiligo = True
        # FUR LENGTH

        a = randint(1, 4)

        if a == 1:
            self.furLength = ["L", "L"]
        elif a == 4:
            self.furLength = ["l", "l"]
        else:
            self.furLength = ["L", "l"]

        # EUMELANIN

        for i in range(2):
            if randint(1, 3) == 1:
                self.eumelanin[i] = "bl"
            elif randint(1, 2) == 1:
                self.eumelanin[i] = "b"
            else:
                self.eumelanin[i] = "B"

        # RED GENE

        if (randint(1, 2) == 1 and special != "fem") or special == "masc":
            self.sexgene = ["", "Y"]
            if randint(1, 1000) == 1:
                self.sexgene = ["", "", "Y"]
            
                for i in range(2):
                    if randint(1, 2) == 1:
                        self.sexgene[i] = "O"
                    else:
                        self.sexgene[i] = "o"
            elif randint(1, 2) == 1:
                self.sexgene[0] = "O"
            else:
                self.sexgene[0] = "o"
            self.gender = "tom"
        else:
            if randint(1, 1000) == 1:
                self.sexgene = ["", "", ""]
                for i in range(3):
                    if randint(1, 2) == 1:
                        self.sexgene[i] = "O"
                    else:
                        self.sexgene[i] = "o"
            else:
                for i in range(2):
                    if randint(1, 3) == 1:
                        self.sexgene[i] = "O"
                    else:
                        self.sexgene[i] = "o"
            self.gender = "molly"
        if 'o' in self.sexgene and 'O' in self.sexgene and randint(1, 250)==1:
            self.brindledbi = True 

        # DILUTE

        a = randint(1, 4)

        if a == 1:
            self.dilute = ["D", "D"]
        elif a == 4:
            self.dilute = ["d", "d"]
        else:
            self.dilute = ["D", "d"]

        # WHITE

        for i in range(2):

            if randint(1, 25) == 1:
                self.white[i] = "wg"
            elif randint(1, 25) == 1:
                self.white[i] = "wt"
            elif randint(1, 20) == 1:
                self.white[i] = "W"
            elif randint(1, 2) == 1:
                self.white[i] = "ws"
            else:
                self.white[i] = "w"

        # ALBINO

        for i in range(2):
            a = randint(1, 25)
            b = randint(1, 25)
            c = randint(1, 10)
            d = randint(1, 5)

            if a == 1:
                self.pointgene[i] = "c"
            elif b == 1:
                self.pointgene[i] = "cm"
            elif c == 1:
                self.pointgene[i] = "cb"
            elif d == 1:
                self.pointgene[i] = "cs"
            else:
                self.pointgene[i] = "C"

        # SILVER

        a = randint(1, 25)

        if a == 1:
            self.silver = ["I", "I"]
        elif a < 7:
            self.silver = ["I", "i"]
        else:
            self.silver = ["i", "i"]

        # AGOUTI
    
        for i in range(2):
            a = randint(1, 20)
            b = randint(1, 2)
            if a == 1:
                self.agouti[i] = "Apb"
            elif b == 1:
                self.agouti[i] = "A"
            else:
                self.agouti[i] = "a"

        

        # MACKEREL

        a = randint(1, 4)

        if a == 1:
            self.mack = ["Mc", "Mc"]
        elif a == 4:
            self.mack = ["mc", "mc"]
        else:
            self.mack = ["Mc", "mc"]

        # TICKED

        a = randint(1, 25)

        if a == 1:
            self.ticked = ["Ta", "Ta"]
        elif a <= 6:
            self.ticked = ["Ta", "ta"]
            if randint(1, 25) == 1:
                self.breakthrough = True
        else:
            self.ticked = ["ta", "ta"]

        # YORK, WIREHAIR, LAPERM, CORNISH, URAL, TENN, FLEECE

        A = [0, 0, 0, 0, 0, 0, 0]
        
        for i in range(7):
            a = randint(1, 100)
            A[i] = a

        if A[0] == 1:
            self.york = ["Yuc", "Yuc"]
        elif A[0] <= 21:
            self.york = ["Yuc", "yuc"]
        
        if A[1] == 1:
            self.wirehair = ["Wh", "Wh"]
        elif A[1] <= 21:
            self.wirehair = ["Wh", "wh"]
        
        if A[2] == 1:
            self.laperm = ["Lp", "Lp"]
        elif A[2] <= 21:
            self.laperm = ["Lp", "lp"]
        
        if A[3] == 1:
            self.cornish = ["r", "r"]
        elif A[3] <= 21:
            self.cornish = ["R", "r"]
        
        if A[4] == 1:
            self.urals = ["ru", "ru"]
        elif A[4] <= 21:
            self.urals = ["Ru", "ru"]
        
        if A[5] == 1:
            self.tenn = ["tr", "tr"]
        elif A[5] <= 21:
            self.tenn = ["Tr", "tr"]
        
        if A[6] == 1:
            self.fleece = ["fc", "fc"]
        elif A[6] <= 21:
            self.fleece = ["Fc", "fc"]
            
        
        #SELKIRK/DEVON/HAIRLESS
    
        for i in range(2):
            a = randint(1, 25)
            b = randint(1, 10)
            c = randint(1, 10)

            if a == 1:
                self.sedesp[i] = "hr"
            elif b == 1:
                self.sedesp[i] = "re"
            elif c == 1:
                self.sedesp[i] = "Se"


        #ruhr + ruhrmod + lykoi

        a = randint(1, 100)

        if a == 1:
            self.ruhr = ["Hrbd", "Hrbd"]
        elif a <= 21:
            self.ruhr = ["Hrbd", "hrbd"]
        
        a = randint(1, 4)

        if a == 1:
            self.ruhrmod = ["hi", "hi"]
        elif a == 4:
            self.ruhrmod = ["ha", "ha"]
        else:
            self.ruhrmod = ["hi", "ha"]

        a = randint(1, 100)

        if a == 1:
            self.lykoi = ["ly", "ly"]
        elif a <= 21:
            self.lykoi = ["Ly", "ly"]

        a = randint(1, 200)

        # pinkdilute + dilutemd

        a = randint(1, 125)

        if a == 1:
            self.pinkdilute = ["dp", "dp"]
        elif a <= 26:
            self.pinkdilute[1] = "dp"
        
        a = randint(1, 125)

        if a == 1:
            self.dilutemd = ["Dm", "Dm"]
        elif a <= 26:
            self.dilutemd[0] = "Dm"

        # ext

        for i in range(2):
            a = randint(1, 25)
            b = randint(1, 20)
            c = randint(1, 20)
            d = randint(1, 20)

            if a == 1:
                self.ext[i] = "Eg"
            elif b == 1:
                self.ext[i] = "ec"
            elif c == 1:
                self.ext[i] = "er"
            elif d == 1:
                self.ext[i] = "ea"

        #sunshine

        for i in range(2):
            a = randint(1, 20)
            b = randint(1, 20)
            c = randint(1, 20)

            if a == 1:
                self.sunshine[i] = "sh" #sunSHine
            elif b == 1:
                self.sunshine[i] = "sg" #Siberian Gold / extreme sunshine
            elif c == 1:
                self.sunshine[i] = "fg" #Flaxen Gold
            else:
                self.sunshine[i] = "N" #No

        # karp + bleach + ghosting + satin + glitter

        for i in range(5):
            a = randint(1, 250)
            A[i] = a

        if A[0] == 1:
            self.karp = ["K", "K"]
        elif A[0] <= 51:
            self.karp[0] = "K"

        if A[1] == 1:
            self.bleach = ["lb", "lb"]
        elif A[1] <= 51:
            self.bleach[1] = "lb"
        
        if A[2] == 1:
            self.ghosting = ["Gh", "Gh"]
        elif A[2] <= 51:
            self.ghosting[0] = "Gh"
        
        if A[3] == 1:
            self.satin = ["st", "st"]
        elif A[3] <= 51:
            self.satin[1] = "st"
        
        if A[4] == 1:
            self.glitter = ["gl", "gl"]
        elif A[4] <= 51:
            self.glitter[1] = "gl"

        # curl + fold

        a = randint(1, 625)

        if a == 1:
            self.curl = ["Cu", "Cu"]
        elif a <= 26:
            self.curl[0] = "Cu"
        
        a = randint(1, 25)

        if a == 1:
            self.fold[0] = "Fd"


        #  manx + kab + toybob + jbob + kub + ring

        a = randint(1, 40)
        b = randint(1, 40)

        if a == 1:
            self.manx = ["Ab", "ab"]
        elif b == 1:
            self.manx = ["M", "m"]
        
        for i in range(5):
            a = randint(1, 100)
            A[i] = a

        if A[0] == 1:
            self.kab = ["kab", "kab"]
        elif A[0] <= 21:
            self.kab[1] = "kab"
        
        if A[1] == 1:
            self.toybob = ["Tb", "Tb"]
        elif A[1] <= 21:
            self.toybob[0] = "Tb"

        if A[2] == 1:
            self.jbob = ["jb", "jb"]
        elif A[2] <= 21:
            self.jbob[1] = "jb"
        
        if A[3] == 1:
            self.kub = ["Kub", "Kub"]
        elif A[3] <= 21:
            self.kub[0] = "Kub"

        if A[4] == 1:
            self.ring = ["rt", "rt"]
        elif A[4] <= 21:
            self.ring[1] = "rt"
        
        # munch + poly + altai

        a = randint(1, 20)

        if a == 1:
            self.munch[0] = "Mk"
        
        a = randint(1, 25)

        if a == 1:
            self.poly = ["Pd", "Pd"]
        elif a <= 6:
            self.poly[0] = "Pd"
        
        a = randint(1, 125)

        if a == 1:
            self.altai = ["Al", "Al"]
        elif a <= 26:
            self.altai[0] = "Al"

        self.wideband = ''
        self.rufousing = ''
        self.spotted = ''
        self.tickgenes = ''
        self.bengal = ''
        self.sokoke = ''
        self.refraction = ''
        self.pigmentation = ''
        
        genes = ["2", "2", "1", "1", "1", "1", "0", "0"]
        
        wbtypes = ["low", "medium", "high", "shaded", "chinchilla"]
        ruftypes = ["low", "medium", "rufoused"]

        for i in range(0, 8):
            self.wideband += choice(genes)
            self.wbsum += int(self.wideband[i])

        if self.wbsum < 7:
            self.wbtype = wbtypes[0]
        elif self.wbsum < 10:
            self.wbtype = wbtypes[1]
        elif self.wbsum < 12: 
            self.wbtype = wbtypes[2]
        elif self.wbsum < 14: 
            self.wbtype = wbtypes[3]
        else: 
            self.wbtype = wbtypes[4]

        for i in range(0, 4):
            self.rufousing += choice(genes)
            self.rufsum += int(self.rufousing[i])

        if self.rufsum < 3: 
            self.ruftype = ruftypes[0]
        elif self.rufsum < 6: 
            self.ruftype = ruftypes[1]
        else:
            self.ruftype = ruftypes[2]

        spottypes = ["fully striped", "slightly broken stripes", "broken stripes", "mostly broken stripes", "spotted"]
        genesspot = ["2", "1", "0"]

        for i in range(0, 4):
            self.spotted += choice(genesspot)
            self.spotsum += int(self.spotted[i])

        if self.spotsum < 1: 
            self.spottype = spottypes[0]
        elif self.spotsum < 3:
            self.spottype = spottypes[1]
        elif self.spotsum < 6:
            self.spottype = spottypes[2]
        elif self.spotsum < 8: 
            self.spottype = spottypes[3]
        else:
            self.spottype = spottypes[4]
        
        ticktypes = ["full barring", "reduced barring", "agouti"]
        genesmild = ["2", "2", "1", "1", "1", "1", "1", "0", "0", "0", "0", "0", "0"]

        for i in range(0, 4):
            self.tickgenes += choice(genesmild)
            self.ticksum += int(self.tickgenes[i])

        if self.ticksum < 6: 
            self.ticktype = ticktypes[0]
        elif self.ticksum < 8:
            self.ticktype = ticktypes[1]
        else:
            self.ticktype = ticktypes[2]

        bengtypes = ["normal markings", "mild bengal", "full bengal"]

        for i in range(0, 4):
            self.bengal += choice(genesmild)
            self.bengsum += int(self.bengal[i])

        if self.bengsum < 4: 
            self.bengtype = bengtypes[0]
        elif self.bengsum < 6:
            self.bengtype = bengtypes[1]
        else:
            self.bengtype = bengtypes[2]

        soktypes = ["normal markings", "mild fading", "full sokoke"]

        eyegenes = ["2", "2", "2", "2", "1", "1", "1", "1", "0", "0", "0"]

        for i in range(0, 4):
            self.sokoke += choice(eyegenes)
            self.soksum += int(self.sokoke[i])

        if self.soksum < 4: 
            self.soktype = soktypes[0]
        elif self.soksum < 6:
            self.soktype = soktypes[1]
        else:
            self.soktype = soktypes[2]

        for i in range(0, 9):
            self.refraction += choice(eyegenes)
            self.refsum += int(self.refraction[i])
            self.pigmentation += choice(eyegenes)
            self.pigsum += int(self.pigmentation[i])

        if self.refsum == 0:
            self.refgrade = 1
        elif self.refsum <= 1:
            self.refgrade = 2
        elif self.refsum <= 3:
            self.refgrade = 3
        elif self.refsum <= 5:
            self.refgrade = 4
        elif self.refsum <= 7:
            self.refgrade = 5
        elif self.refsum <= 10:
            self.refgrade = 6
        elif self.refsum <= 12:
            self.refgrade = 7
        elif self.refsum <= 14:
            self.refgrade = 8
        elif self.refsum <= 16:
            self.refgrade = 9
        elif self.refsum < 18:
            self.refgrade = 10
        else:
            self.refgrade = 11

        if self.pigsum == 0:
            self.piggrade = 1
        elif self.pigsum <= 1:
            self.piggrade = 2
        elif self.pigsum <= 3:
            self.piggrade = 3
        elif self.pigsum <= 5:
            self.piggrade = 4
        elif self.pigsum <= 7:
            self.piggrade = 5
        elif self.pigsum <= 10:
            self.piggrade = 6
        elif self.pigsum <= 12:
            self.piggrade = 7
        elif self.pigsum <= 14:
            self.piggrade = 8
        elif self.pigsum <= 16:
            self.piggrade = 9
        elif self.pigsum < 18:
            self.piggrade = 10
        else:
            self.piggrade = 11

        self.GeneSort()

        self.EyeColourFinder()

        self.refgrade = "R" + str(self.refgrade)
        self.piggrade = "P" + str(self.piggrade)

    def KitGenerator(self, par1, par2=None):
        try:
            if par2 == None:
                par2 = Genotype()
                if('Y' in par1.sexgene):
                    par2.Generator("fem")
                else:
                    par2.Generator("masc")
            else:
                par2 = par2.genotype
        except:
            par2 = par2
            

        if self.chimera:
            self.chimerageno.KitGenerator(par1, par2)
    
        if randint(1, 5) == 1:
            self.whitegrade = par1.whitegrade
        elif randint(1, 5) == 1:
            self.whitegrade = par2.whitegrade

        if (par1.vitiligo and par2.vitiligo):
            a = randint(1, 25)
        elif(par1.vitiligo or par2.vitiligo):
            a = randint(1, 50)
        else:
            a = randint(1, 100)

        if(a == 1):
            self.vitiligo = True    
        
        
        self.furLength = [choice(par1.furLength), choice(par2.furLength)]

        if self.furLength[0] == "l":
            x = self.furLength[1]
            self.furLength[1] = self.furLength[0]
            self.furLength[0] = x
        
        self.eumelanin = [choice(par1.eumelanin), choice(par2.eumelanin)]

        if xor('Y' in par1.sexgene, 'Y' in par2.sexgene):
            if('Y' in par1.sexgene):
                if(randint(1, 2) == 1):
                    par1.sexgene[1] = par1.sexgene[0]
                else:
                    par2.sexgene[1] = par2.sexgene[0]
            else:
                if len(par1.sexgene) > 2:
                    par2.sexgene[1] = 'Y'
                elif len(par2.sexgene) > 2:
                    par1.sexgene[1] = 'Y'
                else:
                    if('O' in par1.sexgene and 'o' in par1.sexgene):
                        par2.sexgene[1] = 'Y'
                    elif ('O' in par2.sexgene and 'o' in par2.sexgene):
                        par1.sexgene[1] = 'Y'
                    else:
                        if(randint(1, 2) == 1):
                            par1.sexgene[1] = 'Y'
                        else:
                            par2.sexgene[1] = 'Y'

        if('Y' in par1.sexgene):
            mum = par2.sexgene
            pap = par1.sexgene
        else:
            mum = par1.sexgene
            pap = par2.sexgene

        if randint(1, 1000) == 1:
            self.sexgene = ["", "", ""]
            if randint(1, 2) == 1:
                self.gender = 'tom'
                if randint(1, 2) == 1:
                    self.sexgene[0] = choice(mum)
                    self.sexgene[1] = pap[0]
                    self.sexgene[2] = 'Y'
                else:
                    self.sexgene[2] = 'Y'
                    if len(mum) < 3:
                        self.sexgene[0] = mum[0]
                        self.sexgene[1] = mum[1]
                    else:
                        a = randint(0, 2)
                        b = randint(0, 2)
                        while b == a:
                            b = randint(0, 2)
                        
                        self.sexgene[0] = mum[a]
                        self.sexgene[1] = mum[b]
            else:
                self.gender = 'molly'
                if len(mum) < 3:
                    self.sexgene[0] = mum[0]
                    self.sexgene[1] = mum[1]
                else:
                    a = randint(0, 2)
                    b = randint(0, 2)
                    while b == a:
                        b = randint(0, 2)
                    
                    self.sexgene[0] = mum[a]
                    self.sexgene[1] = mum[b]
                self.sexgene[2] = pap[0]

        else:
            if(randint(1, 2) == 1):
                self.sexgene[1] = "Y"
                if(par1.sexgene[1] == "Y"):
                    self.sexgene[0] = choice(par2.sexgene)
                else:
                    self.sexgene[0] = choice(par1.sexgene)
                self.gender = "tom"
            else:
                if(par1.sexgene[1] == "Y"):
                    self.sexgene = [choice(par2.sexgene), par1.sexgene[0]]
                else:
                    self.sexgene = [choice(par1.sexgene), par2.sexgene[0]]
                self.gender = "molly"
        
        
        if 'o' in self.sexgene and 'O' in self.sexgene and randint(1, 250)==1:
            self.brindledbi = True 
        
        self.dilute = [choice(par1.dilute), choice(par2.dilute)]

        if(self.dilute[0] == "d"):
            x = self.dilute[1]
            self.dilute[1] = self.dilute[0]
            self.dilute[0] = x
        
        self.white = [choice(par1.white), choice(par2.white)]

        self.pointgene = [choice(par1.pointgene), choice(par2.pointgene)]

        self.silver = [choice(par1.silver), choice(par2.silver)]

        if(self.silver[0] == "i"):
            x = self.silver[1]
            self.silver[1] = self.silver[0]
            self.silver[0] = x

        self.agouti = [choice(par1.agouti), choice(par2.agouti)]

        self.mack = [choice(par1.mack), choice(par2.mack)]

        if(self.mack[0] == "mc"):
            x = self.mack[1]
            self.mack[1] = self.mack[0]
            self.mack[0] = x

        self.ticked = [choice(par1.ticked), choice(par2.ticked)]

        if self.ticked[0] != self.ticked[1] and randint(1, 25) == 1:
            self.breakthrough = True

        if(self.ticked[0] == "ta"):
            x = self.ticked[1]
            self.ticked[1] = self.ticked[0]
            self.ticked[0] = x

        self.york = [choice(par1.york), choice(par2.york)]

        if(self.york[0] == "yuc"):
            x = self.york[1]
            self.york[1] = self.york[0]
            self.york[0] = x

        self.wirehair = [choice(par1.wirehair), choice(par2.wirehair)]

        if(self.wirehair[0] == "wh"):
            x = self.wirehair[1]
            self.wirehair[1] = self.wirehair[0]
            self.wirehair[0] = x

        self.laperm = [choice(par1.laperm), choice(par2.laperm)]

        if(self.laperm[0] == "lp"):
            x = self.laperm[1]
            self.laperm[1] = self.laperm[0]
            self.laperm[0] = x

        self.cornish = [choice(par1.cornish), choice(par2.cornish)]

        if(self.cornish[0] == "r"):
            x = self.cornish[1]
            self.cornish[1] = self.cornish[0]
            self.cornish[0] = x

        self.urals = [choice(par1.urals), choice(par2.urals)]

        if(self.urals[0] == "ru"):
            x = self.urals[1]
            self.urals[1] = self.urals[0]
            self.urals[0] = x

        self.tenn = [choice(par1.tenn), choice(par2.tenn)]

        if(self.tenn[0] == "tr"):
            x = self.tenn[1]
            self.tenn[1] = self.tenn[0]
            self.tenn[0] = x

        self.fleece = [choice(par1.fleece), choice(par2.fleece)]

        if(self.fleece[0] == "fc"):
            x = self.fleece[1]
            self.fleece[1] = self.fleece[0]
            self.fleece[0] = x

        self.sedesp = [choice(par1.sedesp), choice(par2.sedesp)]

        self.ruhr = [choice(par1.ruhr), choice(par2.ruhr)]

        if(self.ruhr[0] == "hrbd"):
            x = self.ruhr[1]
            self.ruhr[1] = self.ruhr[0]
            self.ruhr[0] = x

        self.ruhrmod = [choice(par1.ruhrmod), choice(par2.ruhrmod)]

        if(self.ruhrmod[0] == "ha"):
            x = self.ruhrmod[1]
            self.ruhrmod[1] = self.ruhrmod[0]
            self.ruhrmod[0] = x

        self.lykoi = [choice(par1.lykoi), choice(par2.lykoi)]

        if(self.lykoi[0] == "ly"):
            x = self.lykoi[1]
            self.lykoi[1] = self.lykoi[0]
            self.lykoi[0] = x

        self.pinkdilute = [choice(par1.pinkdilute), choice(par2.pinkdilute)]

        if(self.pinkdilute[0] == "dp"):
            x = self.pinkdilute[1]
            self.pinkdilute[1] = self.pinkdilute[0]
            self.pinkdilute[0] = x

        self.dilutemd = [choice(par1.dilutemd), choice(par2.dilutemd)]

        if(self.dilutemd[0] == "dm"):
            x = self.dilutemd[1]
            self.dilutemd[1] = self.dilutemd[0]
            self.dilutemd[0] = x

        self.ext = [choice(par1.ext), choice(par2.ext)]
        self.sunshine = [choice(par1.sunshine), choice(par2.sunshine)]

        self.karp = [choice(par1.karp), choice(par2.karp)]

        if(self.karp[0] == "k"):
            x = self.karp[1]
            self.karp[1] = self.karp[0]
            self.karp[0] = x

        self.bleach = [choice(par1.bleach), choice(par2.bleach)]

        if(self.bleach[0] == "lb"):
            x = self.bleach[1]
            self.bleach[1] = self.bleach[0]
            self.bleach[0] = x

        self.ghosting = [choice(par1.ghosting), choice(par2.ghosting)]

        if(self.ghosting[0] == "gh"):
            x = self.ghosting[1]
            self.ghosting[1] = self.ghosting[0]
            self.ghosting[0] = x

        self.satin = [choice(par1.satin), choice(par2.satin)]

        if(self.satin[0] == "st"):
            x = self.satin[1]
            self.satin[1] = self.satin[0]
            self.satin[0] = x

        self.glitter = [choice(par1.glitter), choice(par2.glitter)]

        if(self.glitter[0] == "gl"):
            x = self.glitter[1]
            self.glitter[1] = self.glitter[0]
            self.glitter[0] = x

        self.curl = [choice(par1.curl), choice(par2.curl)]

        if(self.curl[0] == "cu"):
            self.curl[0] = self.curl[1]
            self.curl[1] = "cu"

        self.fold = [choice(par1.fold), choice(par2.fold)]

        if(self.fold[0] == "fd"):
            self.fold[0] = self.fold[1]
            self.fold[1] = "fd"
        
        self.manx = [choice(par1.manx), choice(par2.manx)]

        self.kab = [choice(par1.kab), choice(par2.kab)]

        if(self.kab[0] == "kab"):
            self.kab[0] = self.kab[1]
            self.kab[1] = "kab"

        self.toybob = [choice(par1.toybob), choice(par2.toybob)]

        if(self.toybob[0] == "tb"):
            self.toybob[0] = self.toybob[1]
            self.toybob[1] = "tb"

        self.jbob = [choice(par1.jbob), choice(par2.jbob)]

        if(self.jbob[0] == "jb"):
            self.jbob[0] = self.jbob[1]
            self.jbob[1] = "jb"

        self.kub = [choice(par1.kub), choice(par2.kub)]

        if(self.kub[0] == "kub"):
            self.kub[0] = self.kub[1]
            self.kub[1] = "kub"

        self.ring = [choice(par1.ring), choice(par2.ring)]

        if(self.ring[0] == "rt"):
            self.ring[0] = self.ring[1]
            self.ring[1] = "rt"

        self.munch = [choice(par1.munch), choice(par2.munch)]

        if(self.munch[0] == "mk"):
            self.munch[0] = self.munch[1]
            self.munch[1] = "mk"

        self.munch = [choice(par1.munch), choice(par2.munch)]

        if(self.munch[0] == "mk"):
            self.munch[0] = self.munch[1]
            self.munch[1] = "mk"

        self.poly = [choice(par1.poly), choice(par2.poly)]

        if(self.poly[0] == "pd"):
            self.poly[0] = self.poly[1]
            self.poly[1] = "pd"

        self.altai = [choice(par1.altai), choice(par2.altai)]

        if(self.altai[0] == "al"):
            self.altai[0] = self.altai[1]
            self.altai[1] = "al"

        self.wideband = ""
        for i in range(8):
            tempwb = 0
            if par1.wideband[i] == "2" or (par1.wideband[i] == "1" and randint(1, 2) == 1):
                tempwb = tempwb+1
                self.wbsum +=1
            if par2.wideband[i] == "2" or (par2.wideband[i] == "1" and randint(1, 2) == 1):
                tempwb = tempwb+1
                self.wbsum +=1
            self.wideband += str(tempwb)
        
        self.rufousing = ""
        for i in range(4):
            tempruf = 0
            if par1.rufousing[i] == "2" or (par1.rufousing[i] == "1" and randint(1, 2) == 1):
                tempruf = tempruf+1
                self.rufsum +=1
            if par2.rufousing[i] == "2" or (par2.rufousing[i] == "1" and randint(1, 2) == 1):
                tempruf = tempruf+1
                self.rufsum +=1
            self.rufousing += str(tempruf)
        
        self.bengal = ""
        for i in range(4):
            tempbeng = 0
            if par1.bengal[i] == "2" or (par1.bengal[i] == "1" and randint(1, 2) == 1):
                tempbeng = tempbeng+1
                self.bengsum +=1
            if par2.bengal[i] == "2" or (par2.bengal[i] == "1" and randint(1, 2) == 1):
                tempbeng = tempbeng+1
                self.bengsum +=1
            self.bengal += str(tempbeng)
        
        self.sokoke = ""
        for i in range(4):
            tempsok = 0
            if par1.sokoke[i] == "2" or (par1.sokoke[i] == "1" and randint(1, 2) == 1):
                tempsok = tempsok+1
                self.soksum +=1
            if par2.sokoke[i] == "2" or (par2.sokoke[i] == "1" and randint(1, 2) == 1):
                tempsok = tempsok+1
                self.soksum +=1
            self.sokoke += str(tempsok)
        
        self.spotted = ""
        for i in range(4):
            tempspot = 0
            if par1.spotted[i] == "2" or (par1.spotted[i] == "1" and randint(1, 2) == 1):
                tempspot = tempspot+1
                self.spotsum +=1
            if par2.spotted[i] == "2" or (par2.spotted[i] == "1" and randint(1, 2) == 1):
                tempspot = tempspot+1
                self.spotsum +=1
            self.spotted += str(tempspot)
        
        self.tickgenes = ""
        for i in range(4):
            temptick = 0
            if par1.tickgenes[i] == "2" or (par1.tickgenes[i] == "1" and randint(1, 2) == 1):
                temptick = temptick+1
                self.ticksum +=1
            if par2.tickgenes[i] == "2" or (par2.tickgenes[i] == "1" and randint(1, 2) == 1):
                temptick = temptick+1
                self.ticksum +=1
            self.tickgenes += str(temptick)

        self.refraction = ""
        for i in range(9):
            tempref = 0
            if par1.refraction[i] == "2" or (par1.refraction[i] == "1" and randint(1, 2) == 1):
                tempref = tempref+1
                self.refsum +=1
            if par2.refraction[i] == "2" or (par2.refraction[i] == "1" and randint(1, 2) == 1):
                tempref = tempref+1
                self.refsum +=1
            self.refraction += str(tempref)

        self.pigmentation = ""
        for i in range(9):
            temppig = 0
            if par1.pigmentation[i] == "2" or (par1.pigmentation[i] == "1" and randint(1, 2) == 1):
                temppig = temppig+1
                self.pigsum +=1
            if par2.pigmentation[i] == "2" or (par2.pigmentation[i] == "1" and randint(1, 2) == 1):
                temppig = temppig+1
                self.pigsum +=1
            self.pigmentation += str(temppig)

        self.GeneSort()
        self.PolyEval()
        self.EyeColourFinder()

        self.refgrade = "R" + str(self.refgrade)
        self.piggrade = "P" + str(self.piggrade)
    
    def PolyEval(self):
        wbtypes = ["low", "medium", "high", "shaded", "chinchilla"]
        ruftypes = ["low", "medium", "rufoused"]

        self.wbsum = 0
        self.rufsum = 0
        self.bengsum = 0
        self.soksum = 0
        self.spotsum = 0
        self.ticksum = 0
        self.refsum = 0
        self.pigsum = 0
        
        for i in self.wideband:
            self.wbsum += int(i)
        for i in self.rufousing:
            self.rufsum += int(i)
        for i in self.bengal:
            self.bengsum += int(i)
        for i in self.spotted:
            self.spotsum += int(i)
        for i in self.tickgenes:
            self.ticksum += int(i)
        for i in self.refraction:
            self.refsum += int(i)
        for i in self.pigmentation:
            self.pigsum += int(i)
        
        if self.wbsum < 7:
            self.wbtype = wbtypes[0]
        elif self.wbsum < 10:
            self.wbtype = wbtypes[1]
        elif self.wbsum < 12: 
            self.wbtype = wbtypes[2]
        elif self.wbsum < 14: 
            self.wbtype = wbtypes[3]
        else: 
            self.wbtype = wbtypes[4]

        if self.rufsum < 3: 
            self.ruftype = ruftypes[0]
        elif self.rufsum < 6: 
            self.ruftype = ruftypes[1]
        else:
            self.ruftype = ruftypes[2]

        spottypes = ["fully striped", "slightly broken", "broken stripes", "mostly broken", "spotted"]

        if self.spotsum < 1: 
            self.spottype = spottypes[0]
        elif self.spotsum < 3:
            self.spottype = spottypes[1]
        elif self.spotsum < 6:
            self.spottype = spottypes[2]
        elif self.spotsum < 8: 
            self.spottype = spottypes[3]
        else:
            self.spottype = spottypes[4]
        
        ticktypes = ["full barring", "reduced barring", "agouti"]

        if self.ticksum < 4: 
            self.ticktype = ticktypes[0]
        elif self.ticksum < 6:
            self.ticktype = ticktypes[1]
        else:
            self.ticktype = ticktypes[2]

        bengtypes = ["normal markings", "mild bengal", "full bengal"]

        if self.bengsum < 4: 
            self.bengtype = bengtypes[0]
        elif self.bengsum < 6:
            self.bengtype = bengtypes[1]
        else:
            self.bengtype = bengtypes[2]

        soktypes = ["normal markings", "mild fading", "full sokoke"]

        if self.soksum < 4: 
            self.soktype = soktypes[0]
        elif self.soksum < 6:
            self.soktype = soktypes[1]
        else:
            self.soktype = soktypes[2]

        if self.refsum == 0:
            self.refgrade = 1
        elif self.refsum <= 1:
            self.refgrade = 2
        elif self.refsum <= 3:
            self.refgrade = 3
        elif self.refsum <= 5:
            self.refgrade = 4
        elif self.refsum <= 7:
            self.refgrade = 5
        elif self.refsum <= 10:
            self.refgrade = 6
        elif self.refsum <= 12:
            self.refgrade = 7
        elif self.refsum <= 14:
            self.refgrade = 8
        elif self.refsum <= 16:
            self.refgrade = 9
        elif self.refsum < 18:
            self.refgrade = 10
        else:
            self.refgrade = 11

        if self.pigsum == 0:
            self.piggrade = 1
        elif self.pigsum <= 1:
            self.piggrade = 2
        elif self.pigsum <= 3:
            self.piggrade = 3
        elif self.pigsum <= 5:
            self.piggrade = 4
        elif self.pigsum <= 7:
            self.piggrade = 5
        elif self.pigsum <= 10:
            self.piggrade = 6
        elif self.pigsum <= 12:
            self.piggrade = 7
        elif self.pigsum <= 14:
            self.piggrade = 8
        elif self.pigsum <= 16:
            self.piggrade = 9
        elif self.pigsum < 18:
            self.piggrade = 10
        else:
            self.piggrade = 11
    
    def GeneSort(self):
        if self.eumelanin[0] == "bl":
            self.eumelanin[0] = self.eumelanin[1]
            self.eumelanin[1] = "bl"
        elif self.eumelanin[0] == "b" and self.eumelanin[1] != "bl":
            self.eumelanin[0] = self.eumelanin[1]
            self.eumelanin[1] = "b"

        if len(self.sexgene) > 2 and self.sexgene[2] == "O" and self.sexgene[0] == "o":
            self.sexgene[2] = self.sexgene[0]
            self.sexgene[0] = "O"
        elif len(self.sexgene) > 2 and self.sexgene[2] == "O":
            self.sexgene[2] = self.sexgene[1]
            self.sexgene[1] = "O"
        elif self.sexgene[1] == "O":
            self.sexgene[1] = self.sexgene[0]
            self.sexgene[0] = "O"

        if self.white[0] == "wg":
            self.white[0] = self.white[1]
            self.white[1] = "wg"
        elif self.white[0] == "w" and self.white[1] != "wg":
            self.white[0] = self.white[1]
            self.white[1] = "w"
        elif self.white[0] == "wt" and self.white[1] != "wg" and self.white[1] != "w":
            self.white[0] = self.white[1]
            self.white[1] = "wt"
        elif self.white[1] == "W":
            self.white[1] = self.white[0]
            self.white[0] = "W"

        if self.pointgene[0] == "c":
            self.pointgene[0] = self.pointgene[1]
            self.pointgene[1] = "c"
        elif self.pointgene[0] == "cm" and self.pointgene[1] != "c":
            self.pointgene[0] = self.pointgene[1]
            self.pointgene[1] = "cm"
        elif self.pointgene[0] == "cs" and self.pointgene[1] != "c" and self.pointgene[1] != "cm":
            self.pointgene[0] = self.pointgene[1]
            self.pointgene[1] = "cs"
        elif self.pointgene[1] == "C":
            self.pointgene[1] = self.pointgene[0]
            self.pointgene[0] = "C"

        if self.agouti[0] == "a":
            self.agouti[0] = self.agouti[1]
            self.agouti[1] = "a"
        elif self.agouti[0] == "Apb" and self.agouti[1] != "a":
            self.agouti[0] = self.agouti[1]
            self.agouti[1] = "Apb"

        if self.sedesp[0] == "re":
            self.sedesp[0] = self.sedesp[1]
            self.sedesp[1] = "re"
        elif self.sedesp[0] == "hr" and self.sedesp[1] != "re":
            self.sedesp[0] = self.sedesp[1]
            self.sedesp[1] = "hr"
        elif self.sedesp[1] == "Se":
            self.sedesp[1] = self.sedesp[0]
            self.sedesp[0] = "Se"

        if self.ext[0] == "ec":
            self.ext[0] = self.ext[1]
            self.ext[1] = "ec"
        elif self.ext[0] == "er" and self.ext[1] != "ec":
            self.ext[0] = self.ext[1]
            self.ext[1] = "er"
        elif self.ext[1] == "Eg":
            self.ext[1] = self.ext[0]
            self.ext[0] = "Eg"
        elif self.ext[1] == "E" and self.ext[0] != "Eg":
            self.ext[1] = self.ext[0]
            self.ext[0] = "E"

        if self.sunshine[0] == "sh":
            self.sunshine[0] = self.sunshine[1]
            self.sunshine[1] = "sh"
        elif self.sunshine[0] == "fg":
            self.sunshine[0] = self.sunshine[1]
            self.sunshine[1] = "fg"
        elif self.sunshine[0] == "sg":
            self.sunshine[0] = self.sunshine[1]
            self.sunshine[1] = "sg"

        if self.manx[1] == "M":
            self.manx[1] = self.manx[0]
            self.manx[0] = "M"
        elif self.manx[1] == "Ab":
            self.manx[1] = self.manx[0]
            self.manx[0] = "Ab"

    def EyeColourFinder(self):
        Ref1 = ["Citrine", "Golden Beryl", "Yellow", "Pale Golden", "Golden", "Amber", "Light Orange", "Orange", "Cinnabar", "Auburn", "Copper", "Ice Blue", "Albino Pink"]
        Ref2 = ["Pale Citrine", "Pale Yellow", "Lemon", "Deep Yellow", "Dull Golden", "Honey", "Pale Orange", "Burnt Orange", "Dark Orange", "Russet", "Dark Topaz", "Aquamarine", "Albino Rose"]
        Ref3 = ["Lemonade Yellow", "Straw Yellow", "Dandelion Yellow", "Banana Yellow", "Sunglow Yellow", "Copal", "Dull Orange", "Rust Orange", "Topaz", "Chocolate", "Burgundy", "Sky Blue", "Albino Magenta"]
        Ref4 = ["Light Celadon", "Pale Chartreuse", "Pear Green", "Brass Yellow", "Golden Green", "Butterscotch", "Dusty Orange", "Tawny", "Jasper", "Light Brown", "Earth", "Cyan", "Albino Periwinkle"]
        Ref5 = ["Light Jade", "Pale Lime", "Spring Bud", "Chartreuse", "Pale Hazel", "Yellow Hazel", "Golden Flourite", "Beaver Brown", "Sienna", "Chestnut", "Umber", "Baby Blue", "Albino Violet"]
        Ref6 = ["Light Flourite", "Mantis Green", "Spring Green", "Lime", "Green Tea", "Hazel", "Golden Brown", "Dark Copal", "Cinnamon", "Raw Umber", "Sepia", "Aqua", "Albino Glass"]
        Ref7 = ["Pale Emerald", "Apple Green", "Shamrock", "Lemon-Lime", "Peridot", "Antique Brass", "Dark Hazel", "Brown-Green", "Hazel Brown", "Bronze", "Bistre Brown", "Cerulean", "Moonstone"]
        Ref8 = ["Malachite", "Olivine", "Pastel Green", "Bright Green", "Pistachio", "Dull Olive", "Murky Green", "Jungle Green", "Hemlock Green", "Thatch Green", "Muddy", "Ocean Blue", "Albino Ice Blue"]
        Ref9 = ["Pale Turquoise", "Mint", "Snake Green", "Dark Lime", "Fern Green", "Dull Green", "Dark Fern Green", "Olive", "Tumbleweed Green", "Bronze Olive", "Deep Bronze", "Teal", "Albino Aquamarine"]
        Ref10 = ["Turquoise", "Viridian", "Green Onion", "Leaf Green", "Green", "Sap Green", "Dark Leaf Green", "Forest Green", "Dark Peridot", "Seaweed Green", "Dark Olive", "Sapphire", "Albino Sky Blue"]
        Ref11 = ["Deep Turquoise", "Amazonite", "Pine Green", "Deep Leaf Green", "Jade", "Emerald", "Deep Green", "Deep Forest Green", "Dark Green", "Dark Moss Green", "Black Olive", "Azure", "Albino Azure"]

        sectoralindex = randint(0, 74)
        het2index = randint(0, 99)
        blueindex = 1
        hetindex = 1

        if self.dilute[0] == "d" or self.pointgene == ["cb", "cb"] or self.pointgene == ["cb", "c"] or self.pointgene == ["cb", "cm"]:
            if randint(1, 5) == 1:
                self.piggrade = self.piggrade - 1
        
        if self.pointgene == ["cb", "cs"] or self.piggrade == 0 or ((self.pointgene == ["cb", "cm"] or self.pointgene == ["cm", "cm"] or self.pointgene == ["cm", "c"]) and randint(1, 5) == 1):
            self.piggrade = 1

        def RefTypeFind(x, piggrade):
            y = ""
                    
            if x == 1:
                y = Ref1[piggrade-1]
            elif x == 2:
                y = Ref2[piggrade-1]
            elif x == 3:
                y = Ref3[piggrade-1]
            elif x == 4:
                y = Ref4[piggrade-1]
            elif x == 5:
                y = Ref5[piggrade-1]
            elif x == 6:
                y = Ref6[piggrade-1]
            elif x == 7:
                y = Ref7[piggrade-1]
            elif x == 8:
                y = Ref8[piggrade-1]
            elif x == 9:
                y = Ref9[piggrade-1]
            elif x == 10:
                y = Ref10[piggrade-1]
            elif x == 11:
                y = Ref11[piggrade-1]

            return y
        
        def SecondaryRefTypeFind(x, piggrade):
            y = ""

            piggrade = "P" + str(piggrade)
            if piggrade == "P12":
                piggrade = "blue"
            elif piggrade == "P13":
                piggrade = "albino"
                    
            y += "R" + str(x) + " ; " + str(piggrade) + ""
            return y
        
        


        if self.white == ["w","w"] or self.white == ["w", "wg"] or self.white == ["wg", "wg"]:
            blueindex = randint(0, 99)
        elif self.white == ["ws","w"] or self.white == ["ws","wg"] or self.white == ["wt", "w"] or self.white == ["wt", "wg"]:
            blueindex = randint(0, 74)
        elif self.white == ["ws","ws"] or self.white == ["wt", "wt"] or self.white == ["ws", "wt"]:
            blueindex = randint(0, 24)
        elif self.pointgene == ["cb","cs"]:
            blueindex = randint(0, 7)
        elif self.white[0] == "W":
            blueindex = randint(0, 14)
            if randint(1, 4) == 1 and blueindex == 0:
                self.deaf = True
        if self.white == ["W","W"]:
            blueindex = randint(0, 2)
            if randint(1, 4) < 4 and blueindex == 0:
                self.deaf = True
        
        if self.pointgene[0] == "cs" or ((self.pointgene == ["cb","cm"] or self.pointgene == ["cm","cm"] or self.pointgene == ["cm","c"]) and randint(0, 4)==0) or (self.altai != ["al", "al"] and randint(0, 4) == 0):
            blueindex = 0
        if self.altai[1] == 'Al':
            if randint(0, 1) == 0:
                blueindex = 0
                if randint(0, 1) == 0:
                    self.deaf = True
        

        if 'ws' not in self.white and 'wt' not in self.white:
            hetindex = randint(0, 74)
        elif self.white[0] in ['ws', 'wt'] and self.white[1] not in ['ws', 'wt']:
            hetindex = randint(0, 24)
        elif self.white[0] in ['ws', 'wt'] and self.white[1] in ['ws', 'wt']:
            hetindex = randint(0, 14)
        elif self.white[0] == "W":
            hetindex = randint(0, 9)
            if randint(1, 10) == 1 and hetindex == 0:
                self.deaf = True
        if self.white == ["W","W"]:
            hetindex = randint(0, 2)
            if randint(1, 8) == 1 and hetindex == 0:
                self.deaf = True
        if self.altai != ["al","al"] and randint(0, 4)!= 0:
            hetindex = 0

        if het2index == 0 and not (self.pinkdilute[0] == "dp" or ("c" in self.pointgene and self.pointgene[0] != "C")) and blueindex != 0:
            tempref = randint(1, 11)
            temppig = randint(1, 12)
            if randint(1, 2)==1:
                self.lefteye = RefTypeFind(tempref, temppig)
                self.righteye = RefTypeFind(self.refgrade, self.piggrade)

                self.lefteyetype = SecondaryRefTypeFind(tempref, temppig)
                self.righteyetype = SecondaryRefTypeFind(self.refgrade, self.piggrade)
            else:
                self.righteye = RefTypeFind(tempref, temppig)
                self.lefteye = RefTypeFind(self.refgrade, self.piggrade)

                self.lefteyetype = SecondaryRefTypeFind(self.refgrade, self.piggrade)
                self.righteyetype = SecondaryRefTypeFind(tempref, temppig)
        else:
            self.righteye = RefTypeFind(self.refgrade, self.piggrade)
            self.lefteye = RefTypeFind(self.refgrade, self.piggrade)

            self.lefteyetype = SecondaryRefTypeFind(self.refgrade, self.piggrade)
            self.righteyetype = SecondaryRefTypeFind(self.refgrade, self.piggrade)

            if(sectoralindex == 0):
                self.extraeye = 'sectoral' + str(randint(1, 6))
            a = [randint(1, 11), randint(1, 12)]
            self.extraeyecolour = RefTypeFind(a[0], a[1])
            self.extraeyetype = SecondaryRefTypeFind(a[0], a[1])
                
                
            if self.pinkdilute[0] == "dp" or ("c" in self.pointgene and self.pointgene[0] != "C"):
                self.lefteye = RefTypeFind(self.refgrade, 13)
                self.righteye = RefTypeFind(self.refgrade, 13)

                self.lefteyetype = SecondaryRefTypeFind(self.refgrade, 13)
                self.righteyetype = SecondaryRefTypeFind(self.refgrade, 13)

                if het2index == 0:
                    tempref = randint(1, 11)
                    if randint(0, 1)==0:
                        self.lefteye = RefTypeFind(tempref, 13)
                        self.lefteyetype = SecondaryRefTypeFind(tempref, 13)
                    else:
                        self.righteye = RefTypeFind(tempref, 13)
                        self.righteyetype = SecondaryRefTypeFind(tempref, 13)
                elif self.extraeye:
                    self.extraeyecolour = RefTypeFind(a[0], 13)
                    self.extraeyetype = SecondaryRefTypeFind(a[0], 13)
            elif(blueindex == 0):
                self.lefteye = RefTypeFind(self.refgrade, 12)
                self.righteye = RefTypeFind(self.refgrade, 12)

                self.lefteyetype = SecondaryRefTypeFind(self.refgrade, 12)
                self.righteyetype = SecondaryRefTypeFind(self.refgrade, 12)

                if het2index == 0:
                    tempref = randint(1, 11)
                    if(randint(0,1)==0):
                        self.lefteye = RefTypeFind(tempref, 12)
                        self.lefteyetype = SecondaryRefTypeFind(tempref, 12)
                    else:
                        self.righteye = RefTypeFind(tempref, 12)
                        self.righteyetype = SecondaryRefTypeFind(tempref, 12)
                elif self.extraeye:
                    self.extraeyecolour = RefTypeFind(a[0], 12)
                    self.extraeyetype = SecondaryRefTypeFind(a[0], 12)
            elif hetindex == 0:
                if(randint(0,1)==0):
                    self.lefteye = RefTypeFind(self.refgrade, 12)
                    self.lefteyetype = SecondaryRefTypeFind(self.refgrade, 12)
                else:
                    self.righteye = RefTypeFind(self.refgrade, 12)
                    self.righteyetype = SecondaryRefTypeFind(self.refgrade, 12)

    def ShowGenes(self):
        self.PolyEval()
        self.Cat_Genes = [self.furLength, self.eumelanin, self.sexgene, self.dilute, self.white, self.pointgene, self.silver,
                     self.agouti, self.mack, self.ticked]
        self.Fur_Genes = [self.york, self.wirehair, self.laperm, self.cornish, self.urals, self.tenn, self.fleece, self.sedesp, self.ruhr, self.ruhrmod, self.lykoi]
        self.Other_Colour = [self.pinkdilute, self.dilutemd, self.ext, self.sunshine, self.karp, self.bleach, self.ghosting, self.satin, self.glitter]
        self.Body_Genes = [self.curl, self.fold, self.manx, self.kab, self.toybob, self.jbob, self.kub, self.ring, self.munch, self.poly, self.altai]
        self.Polygenes = ["Rufousing:", self.rufousing, self.ruftype, "Bengal:", self.bengal, self.bengtype, "Sokoke:", self.sokoke, self.soktype, "Spotted:", self.spotted, self.spottype, "Ticked:", self.tickgenes, self.ticktype]
        self.Polygenes2 = ["Wideband:", self.wideband, self.wbtype, "Refraction:", self.refraction, self.refgrade, "Pigmentation:", self.pigmentation, self.piggrade]

        return self.Cat_Genes, "Other Fur Genes: ", self.Fur_Genes, "Other Colour Genes: ", self.Other_Colour, "Body Mutations: ", self.Body_Genes, "Polygenes: ", self.Polygenes, self.Polygenes2
    
    