from .genotype import *

class Phenotype():

    def __init__(self, genotype):
        self.length = ""

        self.highwhite = ""
        self.fade = ""
        self.colour = ""
        self.silvergold = ""
        self.tabtype = ""
        self.tabby = ""
        self.tortie = ""
        self.point = ""
        self.lowwhite = ""
        self.karpati = ""
        self.specwhite = ""

        self.eartype = ""
        self.tailtype = ""
        self.bobtailnr = 0
        self.pawtype = ""
        self.furtype = []

        self.genotype = genotype

    def FurtypeFinder(self):
        furtype = []
        
        if self.genotype.lykoi[0] == "ly":
            furtype.append("sparse")
        
        if self.genotype.wirehair[0] == "Wh" and self.genotype.ruhr != ["Hrbd", "hrbd"]:
            if len(furtype)>0:
                furtype.append(", ")
            else:
                furtype.append("wiry")
        
        if self.genotype.laperm[0] == "Lp" or self.genotype.cornish[0] == "r" or self.genotype.urals[0] == "ru" or self.genotype.tenn[0] == "tr" or self.genotype.fleece[0] == "fc" or self.genotype.sedesp[0] == "Se" or self.genotype.sedesp[0] == "re" or self.genotype.ruhr == ["Hrbd", "hrbd"]:
            if len(furtype)>0:
                furtype.append(", ")

            if self.genotype.ruhr[0] == "Hrbd" and self.genotype.ruhrmod == ["hi", "ha"]:
                furtype.append("patchy ")
            
            if self.genotype.ruhr[0] != "Hrbd":
                furtype.append("rexed")
            else:
                furtype.append("brush-coated")
        
        if self.genotype.satin[0] == "st" or self.genotype.tenn[0] == "tr":
            furtype.append(" satin")
        elif self.genotype.glitter[0] == "gl" and self.genotype.agouti[0] != "a":
            furtype.append(" shiny")

        if len(furtype)>0:
            furtype.append(" fur")
        
        if self.genotype.york[0] == "Yuc" :
            if len(furtype)>0:
                furtype.append(" and ")
            furtype.append("no undercoat")

        if self.genotype.ruhr[1] == "Hrbd" or (self.genotype.ruhr == ["Hrbd", "hrbd"] and self.genotype.ruhrmod[0] == "ha") or self.genotype.sedesp[0] == "hr" or (self.genotype.york[0] == "Yuc" and self.genotype.cornish[0] == "r"):
            self.length = "hairless"
            furtype = []
        elif self.genotype.furLength[0] == "l":
            self.length = "longhaired"
        else:
            self.length = "shorthaired"

        if(len(furtype)==0):
            furtype.append("")
        self.furtype = furtype
    def MainColourFinder(self):
        colour = ""
        tortie = ""

        if(self.genotype.sexgene[0] == "O" and (self.genotype.sexgene[1] == "O" or self.genotype.sexgene[1] == "Y") and ((len(self.genotype.sexgene) > 2 and ((self.genotype.sexgene[2] == "O" or self.genotype.sexgene[2] == "Y"))) or len(self.genotype.sexgene)==2)):
            if(self.genotype.dilute[0] == "d"):
                if(self.genotype.pinkdilute[0] == "dp"):
                    colour += "ivory"
                else:
                    colour = "cream"

                if(self.genotype.dilutemd[0] == "Dm"):
                    colour += " apricot"
            else:
                if(self.genotype.pinkdilute[0] == "dp"):
                    colour = "honey"
                else:
                    colour = "red"
        else:
            if(self.genotype.dilute[0] == "d"):
                if(self.genotype.eumelanin[0] == "B"):
                    if(self.genotype.pinkdilute[0] == "dp"):
                        colour += "platinum"
                    else:
                        colour = "blue"
                elif(self.genotype.eumelanin[0] == "b"):
                    if(self.genotype.pinkdilute[0] == "dp"):
                        colour += "lavender"
                    else:
                        colour = "lilac"
                else:
                    if(self.genotype.pinkdilute[0] == "dp"):
                        colour += "beige"
                    else:
                        colour = "fawn"

                if(self.genotype.dilutemd[0] == "Dm"):
                    colour += " caramel"
            else:
                if(self.genotype.pinkdilute[0] == "dp"):
                    if(self.genotype.eumelanin[0] == "B"):
                        colour = "dove"
                    elif(self.genotype.eumelanin[0] == "b"):
                        colour = "champagne"
                    else:
                        colour = "buff"
                else:
                    if(self.genotype.eumelanin[0] == "B"):
                        colour = "black"
                    elif(self.genotype.eumelanin[0] == "b"):
                        colour = "chocolate"
                    else:
                        colour = "cinnamon"

        if(self.genotype.sexgene[0] == "O" and (self.genotype.sexgene[1] == "o" or (len(self.genotype.sexgene) > 2 and self.genotype.sexgene[2] == "o"))):
            tortie = "tortie "

        

        self.colour = colour
        if(tortie != "" and self.genotype.brindledbi):
            tortie = "brindled bicolour "
        self.tortie = tortie

    
    def WhiteFinder(self):
        if(self.genotype.white[1] in ["ws", 'wt']):
            if(self.tortie != "" and self.tortie != 'brindled bicolour '):
                self.tortie = "calico "
            elif (self.tortie == "" or self.genotype.whitegrade > 2):
                self.highwhite = "white and "
        
        elif(self.genotype.white[0] in ['ws', 'wt'] and self.genotype.whitegrade > 1):
            if(self.tortie != "" and self.tortie != 'brindled bicolour ' and self.genotype.whitegrade > 4):
                self.tortie = "calico "
            else:
                self.lowwhite = "and white "
            
        
        if(self.genotype.white[0] == "wg"):
            self.specwhite = "white gloves"
        elif("wt" in self.genotype.white):
            self.specwhite = "a white dorsal stripe"
            
    def PointFinder(self):
        self.point = ""

        if(self.genotype.pointgene[0] == 'cb'):
            if(self.genotype.pointgene[1] == 'cs'):
               self.point = "mink "
            elif(self.genotype.pointgene[1] == 'cm'):
                self.point = "burmocha "
            else:
                self.point = "sepia "
        elif(self.genotype.pointgene[0] == 'cs'):
            if(self.genotype.pointgene[1] == 'cm'):
                self.point = "siamocha "
            else:
                self.point = "point "
        elif(self.genotype.pointgene[0] == 'cm'):
            self.point = "mocha "

        if(self.point != ''):
            if(self.colour == 'red'):
                if(self.point != "sepia " and self.point != "burmocha " and self.point != "mocha "):
                    self.colour = 'flame'
            elif(self.colour == 'black'):
                if(self.point == "sepia " or self.point == "burmocha " or self.point == "mocha "):
                    self.colour = 'sable'
                    if(self.point == "sepia "):
                        self.point = ''
                else:
                    self.colour = 'seal'

        
    def ExtFinder(self):
        if('o' in self.genotype.sexgene):
            if(self.genotype.ext[0] == 'ec'):
                if(self.colour == ''):
                    self.tortie = " " + self.tortie
                self.colour = 'agouti carnelian'
                if(self.genotype.agouti[0] == 'a'):
                    self.colour = "non" + self.colour
                if(self.genotype.dilute[0] == 'd' or self.genotype.pinkdilute[0] == 'dp'):
                    self.colour = "light" + self.colour
            
            elif(self.genotype.ext[0] == 'er'):
                self.colour += ' russet'
            elif(self.genotype.ext[0] == 'ea'):
                if(self.genotype.dilute[0] == 'd' or self.genotype.pinkdilute[0] == 'dp'):
                    self.colour += " light"
                self.colour += ' amber'
    def KarpFadeFinder(self):
        self.karpati = ""
        self.fade = ""

        if(self.genotype.karp[0] == 'K'):
            self.karpati = "karpati "
        
        if(self.genotype.bleach[0] == "lb"):
            self.fade = "bleached "
        elif(self.genotype.ghosting[0] == "Gh"):
            self.fade = "faded "
    def SolidWhite(self, pattern=None):
        if(self.genotype.white[0] == "W" or self.genotype.pointgene[0] == "c" or pattern == ["full white"]):
            self.highwhite = ""
            self.fade = ""
            if(self.genotype.pointgene[0] == "c"):
                self.colour = "albino"
            else:
                self.colour = "white"
            self.silvergold = ""
            self.tabtype = ""
            self.tabby = ""
            self.tortie = ""
            self.point = ""
            self.lowwhite = ""
            self.karpati = ""
            self.specwhite = ""
    def SilverGoldFinder(self):
        self.silvergold = ""

        if(self.genotype.agouti[0] == 'a' and 'o' in self.genotype.sexgene):
            if(self.genotype.silver[0] == 'I'):
                if(self.genotype.wbsum > 13):
                    self.silvergold = 'masked silver '
                else:
                    if(self.genotype.wbsum > 9):
                        self.silvergold = 'light '
                    self.silvergold += 'smoke '
        else:
            if(self.genotype.silver[0] == 'I'):
                if(self.genotype.sunshine[0] in ['sg', 'sh']):
                    self.silvergold = 'bimetallic '
                elif(self.genotype.sunshine[0] == 'fg'):
                    self.silvergold = 'silver copper '
                elif ('o' not in self.genotype.sexgene):
                    self.silvergold = 'cameo '
                else:
                    self.silvergold = 'silver '
            elif(self.genotype.sunshine[0] == 'sg' or self.genotype.wbsum > 11):
                self.silvergold = 'golden '
            elif(self.genotype.sunshine[0] == 'sh'):
                self.silvergold = 'sunshine '
            elif(self.genotype.sunshine[0] == 'fg'):
                self.silvergold = 'flaxen gold '

    def TabbyFinder(self):
        self.tabby = ""
        self.tabtype = ""

        if (self.genotype.ext[0] == 'Eg' and 'o' in self.genotype.sexgene and self.genotype.agouti[0] != 'a'):
            self.tabtype += 'grizzled '
        if (self.genotype.agouti == ['Apb', 'Apb'] and 'o' in self.genotype.sexgene):
            self.tabtype += 'twilight '
        elif (self.genotype.agouti[0] == 'Apb' and 'o' in self.genotype.sexgene):
            self.tabtype += 'charcoal '

        if(self.tabtype == ' '):
            self.tabtype = ''

        def FindPattern():
            if(self.genotype.ticked[0] != 'ta'):
                if(self.genotype.wbsum > 13):
                    self.tabby = 'chinchilla'
                elif(self.genotype.ticked[1] == 'Ta' or not self.genotype.breakthrough):
                    if (self.genotype.wbsum > 11):
                        self.tabby = 'shaded'
                    elif(self.genotype.ticksum > 7):
                        self.tabby = 'agouti'
                    else:
                        self.tabby = 'ticked'
                else:
                    if(self.genotype.mack[0] == 'mc'):
                        self.tabby = 'ghost-patterned'
                    elif(self.genotype.spotsum > 5):
                        self.tabby = 'servaline'
                    else:
                        if(self.genotype.spotsum > 2):
                            self.tabby = 'broken '
                        self.tabby += 'pinstripe'
            elif(self.genotype.mack[0] == 'mc'):
                self.tabby = 'blotched'
            elif(self.genotype.spotsum > 5):
                self.tabby = 'spotted'
            else:
                if(self.genotype.spotsum > 2):
                    self.tabby = 'broken '
                self.tabby += 'mackerel'
            
            if(self.tabby != "" and (self.genotype.bengsum > 3 or self.genotype.soksum > 5)):
                if(self.genotype.bengsum > 3):
                    if(self.tabby == "spotted"):
                        self.tabby = "rosetted"
                    elif(self.tabby == "broken mackerel"):
                        self.tabby = "broken braided"
                    elif(self.tabby == "mackerel"):
                        self.tabby = "braided"
                    elif(self.tabby == "blotched"):
                        self.tabby = "marbled"

                    elif(self.tabby == "servaline"):
                        self.tabby += "-rosetted"
                    elif('pinstripe' in self.tabby):
                        self.tabby += "-braided"
                    elif(self.tabby == "ghost-patterned"):
                        self.tabby = "ghost marble"
                elif(self.tabby == 'blotched'):
                    self.tabby = 'sokoke'
            
        if('o' not in self.genotype.sexgene or self.genotype.agouti[0] != 'a' or self.tabtype != '' or ('smoke' in self.silvergold and self.length == 'shorthaired') or self.genotype.ext[0] not in ['Eg', 'E']):
            FindPattern()
        
        if(self.tortie != '' and self.tabby != '' and self.tortie != ' brindled bicolour '):
            if(self.tortie == 'calico '):
                self.tortie = ' caliby '
            else:
                self.tortie = ' torbie '
        elif(self.tabby != '' and self.point not in ['point ', 'mink ', 'siamocha ']):
            self.tabby += ' tabby '
        elif(self.tabby != ''  and self.point in ['point ', 'mink ', 'siamocha ']):
            if(self.colour == 'seal' or self.colour == 'chocolate'):
                self.tabby += ' lynx '
            elif('o' not in self.genotype.sexgene):
                self.tabby = ''
            else:
                self.tabby = ' lynx '

    def EarFinder(self):
        self.eartype = ""

        if(self.genotype.fold[0] == 'Fd'):
            self.eartype += 'folded'
            if(self.genotype.curl[0] == 'Cu'):
                self.eartype += ' back'
            self.eartype += ' ears'
        elif(self.genotype.curl[0] == 'Cu'):
            self.eartype = 'curled back ears'
    
    def LegFinder(self):
        self.pawtype = ""

        if(self.genotype.munch[0] == 'Mk'):
            self.pawtype = "short legs"
        
        if(self.genotype.poly[0] == 'Pd'):
            if(self.pawtype != ""):
                self.pawtype += ", "
            
            self.pawtype += 'extra toes'

    def TailFinder(self):
        self.tailtype = ""

        if(self.genotype.manx[0] != 'M' or (self.genotype.manxtype != 'rumpy' and self.genotype.manxtype != 'stumpy' and self.genotype.manxtype != 'riser')):
            if(self.genotype.kab[0] == 'kab' or self.genotype.toybob[1] == 'Tb' or self.genotype.kub[0] == 'Kub' or self.genotype.jbob[0] == 'jb'):
                self.tailtype = 'stubby, pom-pom '
                self.bobtailnr = 2
            else:
                if(self.genotype.jbob[1] == 'jb' or self.genotype.toybob[0] == 'Tb'):
                    self.tailtype = 'kinked, '
                if(self.genotype.manx[0] == 'Ab' or self.genotype.toybob[0] == 'Tb' or self.genotype.jbob[1] == 'jb' or (self.genotype.manx[0] == 'M' and self.genotype.manxtype == 'stubby')):
                    self.tailtype += "short "
                    self.bobtailnr = 3
                    if self.genotype.manx[0] == 'Ab' and (self.genotype.manxtype == 'rumpy' or self.genotype.manxtype == 'riser'):
                        self.bobtailnr = 2
                    elif not(self.genotype.toybob[0] == 'Tb' or self.genotype.jbob[1] == 'jb') and ((self.genotype.manx[0] == 'Ab' and (self.genotype.manxtype == 'long' or self.genotype.manxtype == 'most')) or (self.genotype.manx[0] == 'M' and self.genotype.manxtype == 'stubby')):
                        self.bobtailnr = 4
                elif(self.genotype.manx[0] == 'M' and self.genotype.manxtype == 'most'):
                    self.tailtype += 'somewhat shortened '
                    self.bobtailnr = 5
                
                if(self.genotype.ring[0] == 'rt'):
                    self.tailtype = 'curled ' + self.tailtype
        elif(self.genotype.manx[0] == 'M'):
            if(self.genotype.manxtype == 'stumpy'):
                self.tailtype = 'stubby '
                self.tailtype = 3
            elif(self.genotype.manxtype == 'riser'):
                self.tailtype = 'stubby, barely visible '
                self.tailtype = 1
            elif(self.genotype.manxtype == 'rumpy'):
                self.tailtype = 'no '
                self.tailtype = 1

        if(self.tailtype != ''):
            self.tailtype += "tail"

    def PhenotypeOutput(self, gender, pattern=None):
        self.FurtypeFinder()
        self.MainColourFinder()
        self.WhiteFinder()
        self.PointFinder()
        self.ExtFinder()
        self.KarpFadeFinder()

        self.SilverGoldFinder()
        self.TabbyFinder()

        self.SolidWhite(pattern=pattern)

        self.EarFinder()
        self.TailFinder()
        self.LegFinder()

        if(self.genotype.chimera and not self.genotype.chimerapattern):
            self.genotype.chimerapattern = self.ChooseTortiePattern('chim')

        eyes = ""

        furtype = ""
        for i in self.furtype:
            furtype += i

        if(self.genotype.lefteye == self.genotype.righteye):
            eyes = self.genotype.lefteye + " eyes"
        else:
            eyes = "one " + self.genotype.lefteye + " eye, one " + self.genotype.righteye + " eye"
        
        if(self.genotype.extraeye):
            eyes += " and sectoral heterochromia"

        withword = ""
        if (self.eartype !="" or self.tailtype!="" or self.pawtype!="" or furtype!=""):
            withword += ", " + self.specwhite + ", " + furtype + ", " + self.eartype + ", " + self.tailtype + ", " + self.pawtype
            while(withword[0] == ","):
                withword = withword[2:]
            while(withword[(len(withword)-2)] == ","):
                withword = withword[:(len(withword)-2)]
            nochange = False
            while(nochange == False):
                withword = withword.replace(", , ", ", ")
                if(withword == withword.replace(", , ", ", ")):
                    nochange = True

        if(withword != ""):
            withword += " and "    

        withword = " with " + withword + eyes.lower()

        if gender == "nonbinary":
            gendera = "cat"
        elif gender == "tom" or gender == "trans tom":
            gendera = "tom"
        else:
            gendera = "molly"

        if self.genotype.chimera:
            gendera = "chimera " + gendera
        
        return self.length + " " + self.highwhite + self.fade + self.colour + " " + self.silvergold + self.tabtype + self.tabby + self.tortie + self.point + self.lowwhite + self.karpati + gendera + withword
    
    def EyeColourRestore(self):
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

        def FindEye(Ref, Pig):
            eye = "Error"
            if Pig == "lue":
                Pig = 11
            elif Pig == "lbino":
                Pig = 12
            else:
                Pig = int(Pig)-1

            if Ref == "R1":
                eye = Ref1[Pig]
            elif Ref == "R2":
                eye = Ref2[Pig]
            elif Ref == "R3":
                eye = Ref3[Pig]
            elif Ref == "R4":
                eye = Ref4[Pig]
            elif Ref == "R5":
                eye = Ref5[Pig]
            elif Ref == "R6":
                eye = Ref6[Pig]
            elif Ref == "R7":
                eye = Ref7[Pig]
            elif Ref == "R8":
                eye = Ref8[Pig]
            elif Ref == "R9":
                eye = Ref9[Pig]
            elif Ref == "R10":
                eye = Ref10[Pig]
            elif Ref == "R11":
                eye = Ref11[Pig]
            
            return eye
        
        lefttemp = self.lefteyetype.split(" ; ")
        righttemp = self.righteyetype.split(" ; ")

        self.lefteye = FindEye(lefttemp[0], lefttemp[1][1:])
        self.righteye = FindEye(righttemp[0], righttemp[1][1:])


    def GetTabbySprite(self):
        pattern = ""

        if(self.genotype.ticked[1] == "Ta" or ((not self.genotype.breakthrough or self.genotype.mack[0] == "mc") and self.genotype.ticked[0] == "Ta")):
            if(self.genotype.ticktype == "agouti"):
                pattern = 'agouti'
            elif(self.genotype.ticktype == 'reduced barring'):
                if(self.genotype.mack[0] == "mc"):
                    pattern = 'redbarc'
                else:
                    pattern = 'redbar'
            else:
                if(self.genotype.mack[0] == "mc"):
                    pattern = 'fullbarc'
                else:
                    pattern = 'fullbar'
        elif(self.genotype.ticked[0] == "Ta"):
            if(self.genotype.bengtype == "normal markings"):
                if(self.genotype.spottype == "broken stripes"):
                    pattern = 'brokenpins'
                elif(self.genotype.spotsum < 6):
                    pattern = 'pinstripe'
                else:
                    pattern = 'servaline'
            else:
                if(self.genotype.spottype == "broken stripes"):
                    pattern = 'brokenpinsbraid'
                elif(self.genotype.spotsum < 6):
                    pattern = 'pinsbraided'
                else:
                    pattern = 'leopard'
        elif(self.genotype.mack[0] == "mc"):
            if(self.genotype.bengtype == "normal markings"):
                pattern = 'classic'
            else:
                pattern = 'marbled'
        else:
            if(self.genotype.bengtype == "normal markings"):
                if(self.genotype.spottype == "broken stripes"):
                    pattern = 'brokenmack'
                elif(self.genotype.spotsum < 6):
                    pattern = 'mackerel'
                else:
                    pattern = 'spotted'
            else:
                if(self.genotype.spottype == "broken stripes"):
                    pattern = 'brokenbraid'
                elif(self.genotype.spotsum < 6):
                    pattern = 'braided'
                else:
                    pattern = 'rosetted'
                

        return pattern
      
    def ChooseTortiePattern(self, spec = None):
        tortie_low_patterns = ['DELILAH', 'MOTTLED', 'EYEDOT', 'BANDANA', 'SMUDGED', 'EMBER', 'BRINDLE', 'SAFI', 'BELOVED', 'BODY', 
                               'SHILOH', 'FRECKLED']
        tortie_mid_patterns = ['ONE', 'TWO', 'SMOKE', 'MINIMALONE', 'MINIMALTWO', 'MINIMALTHREE', 'MINIMALFOUR', 'OREO', 'CHIMERA',
                                'CHEST', 'GRUMPYFACE', 'SIDEMASK', 'PACMAN', 'BRIE' ,'ORIOLE', 'ROBIN', 'PAIGE', 'HEARTBEAT']
        tortie_high_patterns = ['THREE', 'FOUR', 'REDTAIL', 'HALF', 'STREAK', 'MASK', 'SWOOP', 'ARMTAIL', 'STREAMSTRIKE', 'DAUB',
                                'ROSETAIL', 'DAPPLENIGHT', 'BLANKET']
        
        chosen = ""

        if spec:
            chosen = choice([choice(tortie_high_patterns), choice(tortie_high_patterns), choice(tortie_mid_patterns), choice(tortie_mid_patterns), choice(tortie_low_patterns)])

        elif(self.genotype.white[1] == "ws" or self.genotype.white[1] == "wt"):
            if self.genotype.whitegrade > 2:
                if(randint(1, 10) == 1):
                    chosen = choice(tortie_low_patterns)
                elif(randint(1, 5) == 1):
                    chosen = choice(tortie_mid_patterns)
                else:
                    chosen = choice(tortie_high_patterns)
            else:
                if(randint(1, 7) == 1):
                    chosen = choice(tortie_low_patterns)
                elif(randint(1, 3) == 1):
                    chosen = choice(tortie_mid_patterns)
                else:
                    chosen = choice(tortie_high_patterns)
        elif(self.genotype.white[0] == 'ws' or self.genotype.white[0] == 'wt'):
            if self.genotype.whitegrade > 3:
                if(randint(1, 7) == 1):
                    chosen = choice(tortie_high_patterns)
                elif(randint(1, 3) == 1):
                    chosen = choice(tortie_mid_patterns)
                else:
                    chosen = choice(tortie_low_patterns)
            else:
                if(randint(1, 10) == 1):
                    chosen = choice(tortie_high_patterns)
                elif(randint(1, 5) == 1):
                    chosen = choice(tortie_mid_patterns)
                else:
                    chosen = choice(tortie_low_patterns)
        else:
            if(randint(1, 15) == 1):
                chosen = choice(tortie_high_patterns)
            elif(randint(1, 7) == 1):
                chosen = choice(tortie_mid_patterns)
            else:
                chosen = choice(tortie_low_patterns)

        return chosen        

    
    def SpriteInfo(self, moons):
        self.maincolour = ""
        self.spritecolour = ""
        self.caramel = ""
        self.tortpattern = ""
        self.patchmain = ""
        self.patchcolour = ""

        if self.genotype.pointgene[0] == "c":
            self.spritecolour = "albino"
            self.caramel = ""
            self.maincolour = self.spritecolour
        elif self.genotype.white[0] == "W":
            self.spritecolour = "white"
            self.caramel = ""
            self.maincolour = self.spritecolour
        elif (self.genotype.sexgene[0] == "O" and self.genotype.sexgene[1] != "o") or (self.genotype.ext[0] == 'ea' and ((moons > 8 and self.genotype.agouti[0] != 'a') or (moons > 47))) or (self.genotype.ext[0] == 'er' and moons > 23) or (self.genotype.ext[0] == 'ec' and (self.genotype.agouti[0] != 'a' or moons > 5)):
            main = self.FindRed(self.genotype, moons)
            self.maincolour = main[0]
            self.spritecolour = main[1]
        elif(self.genotype.sexgene[0] == "o"):
            main = self.FindBlack(self.genotype, moons)
            self.maincolour = main[0]
            self.spritecolour = main[1]
        else:
            if self.genotype.tortiepattern is not None:
                self.tortpattern = self.genotype.tortiepattern
                if 'rev' in self.tortpattern:
                    if(self.genotype.brindledbi):
                        self.maincolour = "white"
                        self.spritecolour = "white"
                    else:
                        main = self.FindRed(self.genotype, moons)
                        self.maincolour = main[0]
                        self.spritecolour = main[1]
                    main = self.FindBlack(self.genotype, moons)
                    self.patchmain = main[0]
                    self.patchcolour = main[1]
                else:
                    main = self.FindBlack(self.genotype, moons)
                    self.maincolour = main[0]
                    self.spritecolour = main[1]
                    if(self.genotype.brindledbi):
                        self.maincolour = "white"
                        self.spritecolour = "white"
                    else:
                        main = self.FindRed(self.genotype, moons)
                        self.patchmain = main[0]
                        self.patchcolour = main[1]
            else:
                self.tortpattern = self.ChooseTortiePattern()
                if randint(1, 10) == 1:
                    self.pattern = 'rev'+self.tortpattern
                    main = self.FindRed(self.genotype, moons)
                    self.maincolour = main[0]
                    self.spritecolour = main[1]
                    main = self.FindBlack(self.genotype, moons)
                    self.patchmain = main[0]
                    self.patchcolour = main[1]
                else:
                    main = self.FindBlack(self.genotype, moons)
                    self.maincolour = main[0]
                    self.spritecolour = main[1]
                    main = self.FindRed(self.genotype, moons)
                    self.patchmain = main[0]
                    self.patchcolour = main[1]

                self.genotype.tortiepattern = self.tortpattern

    def FindBlack(self, genes, moons):
        if genes.eumelanin[0] == "bl" or (genes.eumelanin[0] == 'b' and genes.ext[0] == 'er'):
            if(genes.dilutemd[0] == 'Dm' or (genes.ext[0] == 'er' and moons < 12 and moons > 5)):
                self.caramel = 'caramel'
            
            if(genes.dilute[0] == "d" or (genes.ext[0] == 'er' and moons < 12)):
                if(genes.pinkdilute[0] == "dp"):
                    colour = "beige"
                else:
                    colour = "fawn"
            else:
                if(genes.pinkdilute[0] == "dp"):
                    colour = "buff"
                else:
                    colour = "cinnamon"
                    self.caramel = ""
        elif genes.eumelanin[0] == "b" or genes.ext[0] == 'er':
            if(genes.dilutemd[0] == 'Dm' or (genes.ext[0] == 'er' and moons < 12 and moons > 5)):
                self.caramel = 'caramel'
            
            if(genes.dilute[0] == "d" or (genes.ext[0] == 'er' and moons < 12)):
                if(genes.pinkdilute[0] == "dp"):
                    colour = "lavender"
                else:
                    colour = "lilac"
            else:
                if(genes.pinkdilute[0] == "dp"):
                    colour = "champagne"
                else:
                    colour = "chocolate"
                    self.caramel = ""
        else:
            if(genes.dilutemd[0] == 'Dm'):
                self.caramel = 'caramel'
            
            if(genes.dilute[0] == "d"):
                if(genes.pinkdilute[0] == "dp"):
                    colour = "platinum"
                else:
                    colour = "blue"
            else:
                if(genes.pinkdilute[0] == "dp"):
                    colour = "dove"
                else:
                    colour = "black"
                    self.caramel = ""
        
        maincolour = colour
        
        if (genes.agouti[0] != "a" and genes.ext[0] != "Eg") or (genes.ext[0] not in ['Eg', 'E'] and moons > 0):
            if genes.silver[0] == "I" or (moons < 3 and genes.karp[0] == "K"):
                if genes.sunshine[0] == "sg":
                    colour =  colour + "silver" + "chinchilla"
                elif genes.sunshine[0] == "sh" or genes.sunshine[0] == "fg" or (genes.ext[0] == 'ea' and moons > 3):
                    colour =  colour + "silver" + "shaded"
                else:
                    colour =  colour + "silver" + genes.wbtype
            elif genes.pointgene[0] != "C" or genes.agouti[0] == "Apb":
                if genes.sunshine[0] == "sg":
                    colour =  colour + "low" + "chinchilla"
                elif genes.sunshine[0] == "sh" or genes.sunshine[0] == "fg" or (genes.ext[0] == 'ea' and moons > 3):
                    colour =  colour + "low" + "shaded"
                else:
                    colour = colour + "low" + genes.wbtype
            else:
                if genes.sunshine[0] == "sg":
                    colour =  colour + genes.ruftype + "chinchilla"
                elif genes.sunshine[0] == "sh" or genes.sunshine[0] == "fg" or (genes.ext[0] == 'ea' and moons > 3):
                    colour =  colour + genes.ruftype + "shaded"
                else:
                    colour = colour + genes.ruftype + genes.wbtype
        
        return [maincolour, colour]

    def FindRed(self, genes, moons, special = None):
        maincolour = genes.ruftype
        if(genes.dilute[0] == "d"):
            if(genes.pinkdilute[0] == "dp"):
                if genes.dilutemd[0] == "Dm":
                    colour = "ivory-apricot"
                else:
                    colour = "ivory"
            else:
                if genes.dilutemd[0] == "Dm":
                    colour = "apricot"
                else:
                    colour = "cream"
        else:
            if(genes.pinkdilute[0] == "dp"):
                if genes.dilutemd[0] == "Dm":
                    colour = "honey-apricot"
                else:
                    colour = "honey"
            else:
                colour = "red"
        
        maincolour += colour
        
        if colour == "apricot":
            if genes.ruftype == "low" or special=='low':
                if genes.silver[0] == "I" and special != 'nosilver' or (moons < 3 and genes.karp[0] == "K"):
                    if genes.sunshine[0] == "sg":
                        colour =  "cream" + "silver" + "chinchilla"
                    elif genes.sunshine[0] == "sh" or genes.sunshine[0] == "fg":
                        colour =  "cream" + "silver" + "shaded"
                    else:
                        colour = "cream" + "silver" + genes.wbtype
                else:
                    if genes.sunshine[0] == "sg":
                        colour =  "cream" + "medium" + "chinchilla"
                    elif genes.sunshine[0] == "sh" or genes.sunshine[0] == "fg":
                        colour =  "cream" + "medium" + "shaded"
                    else:
                        colour = "cream" + "medium" + genes.wbtype
            elif genes.ruftype == "medium":
                if genes.silver[0] == "I" and special != 'nosilver' or (moons < 3 and genes.karp[0] == "K"):
                    if genes.sunshine[0] == "sg":
                        colour =  "cream" + "silver" + "chinchilla"
                    elif genes.sunshine[0] == "sh" or genes.sunshine[0] == "fg":
                        colour =  "cream" + "silver" + "shaded"
                    else:
                        colour = "cream" + "silver" + genes.wbtype
                else:
                    if genes.sunshine[0] == "sg":
                        colour =  "cream" + "rufoused" + "chinchilla"
                    elif genes.sunshine[0] == "sh" or genes.sunshine[0] == "fg":
                        colour =  "cream" + "rufoused" + "shaded"
                    else:
                        colour = "cream" + "rufoused" + genes.wbtype
            else:
                if genes.silver[0] == "I" and special != 'nosilver' or (moons < 3 and genes.karp[0] == "K"):
                    if genes.sunshine[0] == "sg":
                        colour =  "red" + "silver" + "chinchilla"
                    elif genes.sunshine[0] == "sh" or genes.sunshine[0] == "fg":
                        colour =  "red" + "silver" + "shaded"
                    else:
                        colour = "red" + "silver" + genes.wbtype
                else:
                    if genes.sunshine[0] == "sg":
                        colour =  "red" + "low" + "chinchilla"
                    elif genes.sunshine[0] == "sh" or genes.sunshine[0] == "fg":
                        colour =  "red" + "low" + "shaded"
                    else:
                        colour = "red" + "low" + genes.wbtype
        elif colour == "honey-apricot":
            if genes.ruftype == "low" or special=='low':
                if genes.silver[0] == "I" and special != 'nosilver' or (moons < 3 and genes.karp[0] == "K"):
                    if genes.sunshine[0] == "sg":
                        colour =  "honey" + "silver" + "chinchilla"
                    elif genes.sunshine[0] == "sh" or genes.sunshine[0] == "fg":
                        colour =  "honey" + "silver" + "shaded"
                    else:
                        colour = "honey" + "silver" + genes.wbtype
                else:
                    if genes.sunshine[0] == "sg":
                        colour =  "honey" + "medium" + "chinchilla"
                    elif genes.sunshine[0] == "sh" or genes.sunshine[0] == "fg":
                        colour =  "honey" + "medium" + "shaded"
                    else:
                        colour = "honey" + "medium" + genes.wbtype
            elif genes.ruftype == "medium":
                if genes.silver[0] == "I" and special != 'nosilver' or (moons < 3 and genes.karp[0] == "K"):
                    if genes.sunshine[0] == "sg":
                        colour =  "honey" + "silver" + "chinchilla"
                    elif genes.sunshine[0] == "sh" or genes.sunshine[0] == "fg":
                        colour =  "honey" + "silver" + "shaded"
                    else:
                        colour = "honey" + "silver" + genes.wbtype
                else:
                    if genes.sunshine[0] == "sg":
                        colour =  "honey" + "rufoused" + "chinchilla"
                    elif genes.sunshine[0] == "sh" or genes.sunshine[0] == "fg":
                        colour =  "honey" + "rufoused" + "shaded"
                    else:
                        colour = "honey" + "rufoused" + genes.wbtype
            else:
                if genes.silver[0] == "I" and special != 'nosilver' or (moons < 3 and genes.karp[0] == "K"):
                    if genes.sunshine[0] == "sg":
                        colour =  "red" + "silver" + "chinchilla"
                    elif genes.sunshine[0] == "sh" or genes.sunshine[0] == "fg":
                        colour =  "red" + "silver" + "shaded"
                    else:
                        colour = "red" + "silver" + genes.wbtype
                else:
                    if genes.sunshine[0] == "sg":
                        colour =  "red" + "low" + "chinchilla"
                    elif genes.sunshine[0] == "sh" or genes.sunshine[0] == "fg":
                        colour =  "red" + "low" + "shaded"
                    else:
                        colour = "red" + "low" + genes.wbtype
        elif colour == "ivory-apricot":
            if genes.ruftype == "low" or special=='low':
                if genes.silver[0] == "I" and special != 'nosilver' or (moons < 3 and genes.karp[0] == "K"):
                    if genes.sunshine[0] == "sg":
                        colour =  "ivory" + "silver" + "chinchilla"
                    elif genes.sunshine[0] == "sh" or genes.sunshine[0] == "fg":
                        colour =  "ivory" + "silver" + "shaded"
                    else:
                        colour = "ivory" + "silver" + genes.wbtype
                else:
                    if genes.sunshine[0] == "sg":
                        colour =  "ivory" + "medium" + "chinchilla"
                    elif genes.sunshine[0] == "sh" or genes.sunshine[0] == "fg":
                        colour =  "ivory" + "medium" + "shaded"
                    else:
                        colour = "ivory" + "medium" + genes.wbtype
            elif genes.ruftype == "medium":
                if genes.silver[0] == "I" and special != 'nosilver' or (moons < 3 and genes.karp[0] == "K"):
                    if genes.sunshine[0] == "sg":
                        colour =  "ivory" + "silver" + "chinchilla"
                    elif genes.sunshine[0] == "sh" or genes.sunshine[0] == "fg":
                        colour =  "ivory" + "silver" + "shaded"
                    else:
                        colour = "ivory" + "silver" + genes.wbtype
                else:
                    if genes.sunshine[0] == "sg":
                        colour =  "ivory" + "rufoused" + "chinchilla"
                    elif genes.sunshine[0] == "sh" or genes.sunshine[0] == "fg":
                        colour =  "ivory" + "rufoused" + "shaded"
                    else:
                        colour = "ivory" + "rufoused" + genes.wbtype
            else:
                if genes.silver[0] == "I" and special != 'nosilver' or (moons < 3 and genes.karp[0] == "K"):
                    if genes.sunshine[0] == "sg":
                        colour =  "honey" + "silver" + "chinchilla"
                    elif genes.sunshine[0] == "sh" or genes.sunshine[0] == "fg":
                        colour =  "honey" + "silver" + "shaded"
                    else:
                        colour = "honey" + "silver" + genes.wbtype
                else:
                    if genes.sunshine[0] == "sg":
                        colour =  "honey" + "low" + "chinchilla"
                    elif genes.sunshine[0] == "sh" or genes.sunshine[0] == "fg":
                        colour =  "honey" + "low" + "shaded"
                    else:
                        colour = "honey" + "low" + genes.wbtype
        elif genes.silver[0] == "I" and special != 'nosilver' or (moons < 3 and genes.karp[0] == "K"):
            if genes.sunshine[0] == "sg":
                colour =  colour + "silver" + "chinchilla"
            elif genes.sunshine[0] == "sh" or genes.sunshine[0] == "fg":
                colour =  colour + "silver" + "shaded"
            else:
                colour =  colour + "silver" + genes.wbtype
        elif genes.pointgene[0] not in ["C", "cm"] or special=='low':
            if genes.sunshine[0] == "sg":
                colour =  colour + "low" + "chinchilla"
            elif genes.sunshine[0] == "sh" or genes.sunshine[0] == "fg":
                colour =  colour + "low" + "shaded"
            else:
                colour = colour + "low" + genes.wbtype
        else:
            if genes.sunshine[0] == "sg":
                colour =  colour + genes.ruftype + "chinchilla"
            elif genes.sunshine[0] == "sh" or genes.sunshine[0] == "fg":
                colour =  colour + genes.ruftype + "shaded"
            else:
                colour = colour + genes.ruftype + genes.wbtype
        
        
        return [maincolour, colour]

        """class SingleColour(object):
    name = "Solid"
    sprites = {1: 'solidc'}

    def __init__(self, genes, moons, length):
        self.genes = genes
        self.length = length
        self.carnelian = ""
        self.caramel = " caramel"
        
        if genes.pointgene[0] == "c":
            self.colour = "albino"
            self.caramel = ""
        elif genes.white[0] == "W":
            self.colour = "white"
            self.caramel = ""
        elif genes.eumelanin[0] == "bl" or genes.pointgene[0] == "cm":
            if(genes.dilute[0] == "d"):
                if(genes.pinkdilute[0] == "dp"):
                    self.colour = "beige"
                else:
                    self.colour = "fawn"
            else:
                if(genes.pinkdilute[0] == "dp"):
                    self.colour = "buff"
                else:
                    self.colour = "cinnamon"
                    self.caramel = ""
        elif genes.eumelanin[0] == "b":
            if(genes.dilute[0] == "d"):
                if(genes.pinkdilute[0] == "dp"):
                    self.colour = "lavender"
                else:
                    self.colour = "lilac"
            else:
                if(genes.pinkdilute[0] == "dp"):
                    self.colour = "champagne"
                else:
                    self.colour = "chocolate"
                    self.caramel = ""
        else:
            if(genes.dilute[0] == "d"):
                if(genes.pinkdilute[0] == "dp"):
                    self.colour = "platinum"
                else:
                    self.colour = "blue"
            else:
                if(genes.pinkdilute[0] == "dp"):
                    self.colour = "dove"
                else:
                    self.colour = "black"
                    self.caramel = ""
        
        self.maincolour = self.colour

class Tabby(object):
    name = "NewTabby"
    sprites = {1: 'tabby'}

    def __init__(self, genes, moons, length):
        self.maincolour = ""
        self.carnelian = ""
        self.caramel = " caramel"
        if (genes.sexgene[0] == "O" and genes.sexgene[0] != "o") or genes.ext[0] not in ["Eg", "E"]:
            self.caramel = ""
            self.maincolour = genes.ruftype
            if(genes.dilute[0] == "d"):
                if(genes.pinkdilute[0] == "dp"):
                    if genes.dilutemd[0] == "Dm":
                        self.colour = "ivory-apricot"
                    else:
                        self.colour = "ivory"
                else:
                    if genes.dilutemd[0] == "Dm":
                        self.colour = "apricot"
                    else:
                        self.colour = "cream"
            else:
                if(genes.pinkdilute[0] == "dp"):
                    if genes.dilutemd[0] == "Dm":
                        self.colour = "honey-apricot"
                    else:
                        self.colour = "honey"
                else:
                    self.colour = "red"
        elif genes.eumelanin[0] == "bl" or genes.pointgene[0] == "cm":
            if(genes.dilute[0] == "d"):
                if(genes.pinkdilute[0] == "dp"):
                    self.colour = "beige"
                else:
                    self.colour = "fawn"
            else:
                if(genes.pinkdilute[0] == "dp"):
                    self.colour = "buff"
                else:
                    self.colour = "cinnamon"
                    self.caramel = ""
        elif genes.eumelanin[0] == "b":
            if(genes.dilute[0] == "d"):
                if(genes.pinkdilute[0] == "dp"):
                    self.colour = "lavender"
                else:
                    self.colour = "lilac"
            else:
                if(genes.pinkdilute[0] == "dp"):
                    self.colour = "champagne"
                else:
                    self.colour = "chocolate"
                    self.caramel = ""
        else:
            if(genes.dilute[0] == "d"):
                if(genes.pinkdilute[0] == "dp"):
                    self.colour = "platinum"
                else:
                    self.colour = "blue"
            else:
                if(genes.pinkdilute[0] == "dp"):
                    self.colour = "dove"
                else:
                    self.colour = "black"
                    self.caramel = ""
        
        
        self.maincolour += self.colour

        
        if genes.ext[0] == "Ec" and genes.agouti[0] == "a" and (genes.sexgene[0] == "o" or genes.sexgene[1] == "o"):
            self.carnelian = " carnelian"
        
        if self.colour == "apricot":
            if genes.ruftype == "low":
                if genes.silver[0] == "I" or (moons < 3 and genes.karp[0] == "K"):
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        self.colour =  "cream" + "silver" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        self.colour =  "cream" + "silver" + "shaded"
                    else:
                        self.colour = "cream" + "silver" + genes.wbtype
                else:
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        self.colour =  "cream" + "rufoused" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        self.colour =  "cream" + "rufoused" + "shaded"
                    else:
                        self.colour = "cream" + "rufoused" + genes.wbtype
            elif genes.ruftype == "medium":
                if genes.silver[0] == "I" or (moons < 3 and genes.karp[0] == "K"):
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        self.colour =  "red" + "silver" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        self.colour =  "red" + "silver" + "shaded"
                    else:
                        self.colour = "red" + "silver" + genes.wbtype
                else:
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        self.colour =  "red" + "low" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        self.colour =  "red" + "low" + "shaded"
                    else:
                        self.colour = "red" + "low" + genes.wbtype
            else:
                if genes.silver[0] == "I" or (moons < 3 and genes.karp[0] == "K"):
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        self.colour =  "red" + "silver" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        self.colour =  "red" + "silver" + "shaded"
                    else:
                        self.colour = "red" + "silver" + genes.wbtype
                else:
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        self.colour =  "red" + "medium" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        self.colour =  "red" + "medium" + "shaded"
                    else:
                        self.colour = "red" + "medium" + genes.wbtype
        elif self.colour == "honey-apricot":
            if genes.ruftype == "low":
                if genes.silver[0] == "I" or (moons < 3 and genes.karp[0] == "K"):
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        self.colour =  "honey" + "silver" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        self.colour =  "honey" + "silver" + "shaded"
                    else:
                        self.colour = "honey" + "silver" + genes.wbtype
                else:
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        self.colour =  "honey" + "medium" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        self.colour =  "honey" + "medium" + "shaded"
                    else:
                        self.colour = "honey" + "medium" + genes.wbtype
            elif genes.ruftype == "medium":
                if genes.silver[0] == "I" or (moons < 3 and genes.karp[0] == "K"):
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        self.colour =  "honey" + "silver" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        self.colour =  "honey" + "silver" + "shaded"
                    else:
                        self.colour = "honey" + "silver" + genes.wbtype
                else:
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        self.colour =  "honey" + "rufoused" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        self.colour =  "honey" + "rufoused" + "shaded"
                    else:
                        self.colour = "honey" + "rufoused" + genes.wbtype
            else:
                if genes.silver[0] == "I" or (moons < 3 and genes.karp[0] == "K"):
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        self.colour =  "red" + "silver" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        self.colour =  "red" + "silver" + "shaded"
                    else:
                        self.colour = "red" + "silver" + genes.wbtype
                else:
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        self.colour =  "red" + "low" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        self.colour =  "red" + "low" + "shaded"
                    else:
                        self.colour = "red" + "low" + genes.wbtype
        elif self.colour == "ivory-apricot":
            if genes.ruftype == "low":
                if genes.silver[0] == "I" or (moons < 3 and genes.karp[0] == "K"):
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        self.colour =  "ivory" + "silver" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        self.colour =  "ivory" + "silver" + "shaded"
                    else:
                        self.colour = "ivory" + "silver" + genes.wbtype
                else:
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        self.colour =  "ivory" + "rufoused" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        self.colour =  "ivory" + "rufoused" + "shaded"
                    else:
                        self.colour = "ivory" + "rufoused" + genes.wbtype
            elif genes.ruftype == "medium":
                if genes.silver[0] == "I" or (moons < 3 and genes.karp[0] == "K"):
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        self.colour =  "honey" + "silver" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        self.colour =  "honey" + "silver" + "shaded"
                    else:
                        self.colour = "honey" + "silver" + genes.wbtype
                else:
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        self.colour =  "honey" + "low" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        self.colour =  "honey" + "low" + "shaded"
                    else:
                        self.colour = "honey" + "low" + genes.wbtype
            else:
                if genes.silver[0] == "I" or (moons < 3 and genes.karp[0] == "K"):
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        self.colour =  "honey" + "silver" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        self.colour =  "honey" + "silver" + "shaded"
                    else:
                        self.colour = "honey" + "silver" + genes.wbtype
                else:
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        self.colour =  "honey" + "medium" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        self.colour =  "honey" + "medium" + "shaded"
                    else:
                        self.colour = "honey" + "medium" + genes.wbtype
        elif genes.silver[0] == "I" or (moons < 3 and genes.karp[0] == "K"):
            if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                self.colour =  self.colour + "silver" + "chinchilla"
            elif genes.sunshine[0] == "sh":
                self.colour =  self.colour + "silver" + "shaded"
            else:
                self.colour =  self.colour + "silver" + genes.wbtype
        elif genes.pointgene[0] not in ["C", "cm"] or genes.agouti[0] == "Apb":
            if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                self.colour =  self.colour + "low" + "chinchilla"
            elif genes.sunshine[0] == "sh":
                self.colour =  self.colour + "low" + "shaded"
            else:
                self.colour = self.colour + "low" + genes.wbtype
        else:
            if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                self.colour =  self.colour + genes.ruftype + "chinchilla"
            elif genes.sunshine[0] == "sh":
                self.colour =  self.colour + genes.ruftype + "shaded"
            else:
                self.colour = self.colour + genes.ruftype + genes.wbtype
        
        self.length = length

class Tortie(object):
    name = "Tortie"
    sprites = {1: 'tortie', 2: 'tortie'}
    tortie_patterns = ['brindled1', 'patched1', 'patched2']

    def __init__(self, genes, moons, length, pattern):
        self.length = length
        self.colour = ""
        self.maincolour = ""
        self.carnelian = ""
        self.caramel = ""

        if pattern is not None:
            self.pattern = pattern
            if 'rev' in pattern:
                main = self.FindRed(genes, moons, 1)
                self.maincolour = main[0]
                self.colour = main[1]
                main = self.FindBlack(genes, moons, 2)
                self.patchmaincolour = main[0]
                self.patchcolour = main[1]
            else:
                main = self.FindBlack(genes, moons, 1)
                self.maincolour = main[0]
                self.colour = main[1]
                main = self.FindRed(genes, moons, 2)
                self.patchmaincolour = main[0]
                self.patchcolour = main[1]
        else:
            self.pattern = choice(self.tortie_patterns)
            if randint(1, 10) == 1:
                self.pattern = 'rev'+self.pattern
                main = self.FindRed(genes, moons, 1)
                self.maincolour = main[0]
                self.colour = main[1]
                main = self.FindBlack(genes, moons, 2)
                self.patchmaincolour = main[0]
                self.patchcolour = main[1]
            else:
                main = self.FindBlack(genes, moons, 1)
                self.maincolour = main[0]
                self.colour = main[1]
                main = self.FindRed(genes, moons, 2)
                self.patchmaincolour = main[0]
                self.patchcolour = main[1]

    def FindBlack(self, genes, moons, which):
        if genes.eumelanin[0] == "bl" or genes.pointgene[0] == "cm":
            if(genes.dilute[0] == "d"):
                if(genes.pinkdilute[0] == "dp"):
                    colour = "beige"
                else:
                    colour = "fawn"
            else:
                if(genes.pinkdilute[0] == "dp"):
                    colour = "buff"
                else:
                    colour = "cinnamon"
                    self.caramel = ""
        elif genes.eumelanin[0] == "b":
            if(genes.dilute[0] == "d"):
                if(genes.pinkdilute[0] == "dp"):
                    colour = "lavender"
                else:
                    colour = "lilac"
            else:
                if(genes.pinkdilute[0] == "dp"):
                    colour = "champagne"
                else:
                    colour = "chocolate"
                    self.caramel = ""
        else:
            if(genes.dilute[0] == "d"):
                if(genes.pinkdilute[0] == "dp"):
                    colour = "platinum"
                else:
                    colour = "blue"
            else:
                if(genes.pinkdilute[0] == "dp"):
                    colour = "dove"
                else:
                    colour = "black"
                    self.caramel = ""
        
        maincolour = colour
        
        if genes.agouti[0] != "a" and genes.ext[0] != "Eg":
            self.sprites[which] = 'tabby'
            if genes.silver[0] == "I" or (moons < 3 and genes.karp[0] == "K"):
                if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                    colour =  colour + "silver" + "chinchilla"
                elif genes.sunshine[0] == "sh":
                    colour =  colour + "silver" + "shaded"
                else:
                    colour =  colour + "silver" + genes.wbtype
            elif genes.pointgene[0] != "C" or genes.agouti[0] == "Apb":
                if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                    colour =  colour + "low" + "chinchilla"
                elif genes.sunshine[0] == "sh":
                    colour =  colour + "low" + "shaded"
                else:
                    colour = colour + "low" + genes.wbtype
            else:
                if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                    colour =  colour + genes.ruftype + "chinchilla"
                elif genes.sunshine[0] == "sh":
                    colour =  colour + genes.ruftype + "shaded"
                else:
                    colour = colour + genes.ruftype + genes.wbtype
        else:
            self.sprites[which] = 'solidc'

        return [maincolour, colour]

    def FindRed(self, genes, moons, which):
        maincolour = genes.ruftype
        if(genes.dilute[0] == "d"):
            if(genes.pinkdilute[0] == "dp"):
                if genes.dilutemd[0] == "Dm":
                    colour = "ivory-apricot"
                else:
                    colour = "ivory"
            else:
                if genes.dilutemd[0] == "Dm":
                    colour = "apricot"
                else:
                    colour = "cream"
        else:
            if(genes.pinkdilute[0] == "dp"):
                if genes.dilutemd[0] == "Dm":
                    colour = "honey-apricot"
                else:
                    colour = "honey"
            else:
                colour = "red"
        
        maincolour += colour
        
        if colour == "apricot":
            if genes.ruftype == "low":
                if genes.silver[0] == "I" or (moons < 3 and genes.karp[0] == "K"):
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        colour =  "cream" + "silver" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        colour =  "cream" + "silver" + "shaded"
                    else:
                        colour = "cream" + "silver" + genes.wbtype
                else:
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        colour =  "cream" + "rufoused" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        colour =  "cream" + "rufoused" + "shaded"
                    else:
                        colour = "cream" + "rufoused" + genes.wbtype
            elif genes.ruftype == "medium":
                if genes.silver[0] == "I" or (moons < 3 and genes.karp[0] == "K"):
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        colour =  "red" + "silver" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        colour =  "red" + "silver" + "shaded"
                    else:
                        colour = "red" + "silver" + genes.wbtype
                else:
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        colour =  "red" + "low" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        colour =  "red" + "low" + "shaded"
                    else:
                        colour = "red" + "low" + genes.wbtype
            else:
                if genes.silver[0] == "I" or (moons < 3 and genes.karp[0] == "K"):
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        colour =  "red" + "silver" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        colour =  "red" + "silver" + "shaded"
                    else:
                        colour = "red" + "silver" + genes.wbtype
                else:
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        colour =  "red" + "medium" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        colour =  "red" + "medium" + "shaded"
                    else:
                        colour = "red" + "medium" + genes.wbtype
        elif colour == "honey-apricot":
            if genes.ruftype == "low":
                if genes.silver[0] == "I" or (moons < 3 and genes.karp[0] == "K"):
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        colour =  "honey" + "silver" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        colour =  "honey" + "silver" + "shaded"
                    else:
                        colour = "honey" + "silver" + genes.wbtype
                else:
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        colour =  "honey" + "medium" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        colour =  "honey" + "medium" + "shaded"
                    else:
                        colour = "honey" + "medium" + genes.wbtype
            elif genes.ruftype == "medium":
                if genes.silver[0] == "I" or (moons < 3 and genes.karp[0] == "K"):
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        colour =  "honey" + "silver" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        colour =  "honey" + "silver" + "shaded"
                    else:
                        colour = "honey" + "silver" + genes.wbtype
                else:
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        colour =  "honey" + "rufoused" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        colour =  "honey" + "rufoused" + "shaded"
                    else:
                        colour = "honey" + "rufoused" + genes.wbtype
            else:
                if genes.silver[0] == "I" or (moons < 3 and genes.karp[0] == "K"):
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        colour =  "red" + "silver" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        colour =  "red" + "silver" + "shaded"
                    else:
                        colour = "red" + "silver" + genes.wbtype
                else:
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        colour =  "red" + "low" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        colour =  "red" + "low" + "shaded"
                    else:
                        colour = "red" + "low" + genes.wbtype
        elif colour == "ivory-apricot":
            if genes.ruftype == "low":
                if genes.silver[0] == "I" or (moons < 3 and genes.karp[0] == "K"):
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        colour =  "ivory" + "silver" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        colour =  "ivory" + "silver" + "shaded"
                    else:
                        colour = "ivory" + "silver" + genes.wbtype
                else:
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        colour =  "ivory" + "rufoused" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        colour =  "ivory" + "rufoused" + "shaded"
                    else:
                        colour = "ivory" + "rufoused" + genes.wbtype
            elif genes.ruftype == "medium":
                if genes.silver[0] == "I" or (moons < 3 and genes.karp[0] == "K"):
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        colour =  "honey" + "silver" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        colour =  "honey" + "silver" + "shaded"
                    else:
                        colour = "honey" + "silver" + genes.wbtype
                else:
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        colour =  "honey" + "low" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        colour =  "honey" + "low" + "shaded"
                    else:
                        colour = "honey" + "low" + genes.wbtype
            else:
                if genes.silver[0] == "I" or (moons < 3 and genes.karp[0] == "K"):
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        colour =  "honey" + "silver" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        colour =  "honey" + "silver" + "shaded"
                    else:
                        colour = "honey" + "silver" + genes.wbtype
                else:
                    if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                        colour =  "honey" + "medium" + "chinchilla"
                    elif genes.sunshine[0] == "sh":
                        colour =  "honey" + "medium" + "shaded"
                    else:
                        colour = "honey" + "medium" + genes.wbtype
        elif genes.silver[0] == "I" or (moons < 3 and genes.karp[0] == "K"):
            if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                colour =  colour + "silver" + "chinchilla"
            elif genes.sunshine[0] == "sh":
                colour =  colour + "silver" + "shaded"
            else:
                colour =  colour + "silver" + genes.wbtype
        elif genes.pointgene[0] not in ["C", "cm"] or genes.agouti[0] == "Apb":
            if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                colour =  colour + "low" + "chinchilla"
            elif genes.sunshine[0] == "sh":
                colour =  colour + "low" + "shaded"
            else:
                colour = colour + "low" + genes.wbtype
        else:
            if genes.sunshine[0] == "sb" or genes.sunshine[0] == "fg":
                colour =  colour + genes.ruftype + "chinchilla"
            elif genes.sunshine[0] == "sh":
                colour =  colour + genes.ruftype + "shaded"
            else:
                colour = colour + genes.ruftype + genes.wbtype
        
        self.sprites[which] = 'tabby'
        
        return [maincolour, colour]"""