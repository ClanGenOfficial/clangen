from strenum import StrEnum


class RelValue(StrEnum):
    ROMANCE = "romance"
    LIKE = "like"
    RESPECT = "respect"
    TRUST = "trust"
    COMFORT = "comfort"


class ValueLevel(StrEnum):
    # like
    HATES = "hates"
    DISLIKES = "dislikes"
    LIKES = "likes"
    LOVES = "loves"
    # respect
    RESENTS = "resents"
    ENVIES = "envies"
    RESPECTS = "respects"
    ADMIRES = "admires"
    # trust
    DISTRUSTS = "distrusts"
    DOUBTS = "doubts"
    FAVORS = "favors"
    TRUSTS = "trusts"
    # comfort
    FEARS = "fears"
    AVOIDS = "avoids"
    SEEKS = "seeks"
    RELIES_ON = "relies_on"
    # romance
    FANCIES = "fancies"
    ADORES = "adores"

    def is_like_level(self):
        return self in (self.HATES, self.DISLIKES, self.LIKES, self.LOVES)

    def is_respect_level(self):
        return self in (self.RESENTS, self.ENVIES, self.RESPECTS, self.ADMIRES)

    def is_trust_level(self):
        return self in (self.DISTRUSTS, self.DOUBTS, self.FAVORS, self.TRUSTS)

    def is_comfort_level(self):
        return self in (self.FEARS, self.AVOIDS, self.SEEKS, self.RELIES_ON)

    def is_romance_level(self):
        return self in (self.FANCIES, self.ADORES)

    def is_extreme_neg(self):
        return self in (self.HATES, self.RESENTS, self.DISTRUSTS, self.FEARS)

    def is_neg(self):
        return self in (self.DISLIKES, self.ENVIES, self.DOUBTS, self.AVOIDS)

    def is_pos(self):
        return self in (
            self.LIKES,
            self.RESPECTS,
            self.FAVORS,
            self.SEEKS,
            self.FANCIES,
        )

    def is_extreme_pos(self):
        return self in (
            self.LOVES,
            self.ADMIRES,
            self.TRUSTS,
            self.RELIES_ON,
            self.ADORES,
        )
