from strenum import StrEnum


class RelType(StrEnum):
    ROMANCE = "romance"
    LIKE = "like"
    RESPECT = "respect"
    TRUST = "trust"
    COMFORT = "comfort"


class RelTier(StrEnum):
    # like
    LOATHES = "loathes"
    HATES = "hates"
    DISLIKES = "dislikes"
    KNOWS_OF = "knows_of"
    LIKES = "likes"
    ENJOYS = "enjoys"
    CHERISHES = "cherishes"
    # respect
    RESENTS = "resents"
    ENVIES = "envies"
    BEGRUDGES = "begrudges"
    ACKNOWLEDGES = "acknowledges"
    PRAISES = "praises"
    RESPECTS = "respects"
    ADMIRES = "admires"
    # trust
    DISCREDITS = "discredits"
    DISTRUSTS = "distrusts"
    DOUBTS = "doubts"
    OBSERVES = "observes"
    LISTENS_TO = "listens_to"
    TRUSTS = "trusts"
    CONFIDES_IN = "confides_in"
    # comfort
    RUNS_FROM = "runs_from"
    FEARS = "fears"
    AVOIDS = "avoids"
    CONSIDERS = "considers"
    RELATES_TO = "relates_to"
    UNDERSTANDS = "understands"
    KNOWS_DEEPLY = "knows_deeply"
    # romance
    UNINTERESTED = "uninterested"
    FANCIES = "fancies"
    ADORES = "adores"
    LOVES = "loves"

    @property
    def is_like_level(self):
        return self in (
            self.LOATHES,
            self.HATES,
            self.DISLIKES,
            self.KNOWS_OF,
            self.LIKES,
            self.ENJOYS,
            self.CHERISHES,
        )

    @property
    def is_respect_level(self):
        return self in (
            self.RESENTS,
            self.ENVIES,
            self.BEGRUDGES,
            self.ACKNOWLEDGES,
            self.PRAISES,
            self.RESPECTS,
            self.ADMIRES,
        )

    @property
    def is_trust_level(self):
        return self in (
            self.DISCREDITS,
            self.DISTRUSTS,
            self.DOUBTS,
            self.OBSERVES,
            self.LISTENS_TO,
            self.TRUSTS,
            self.CONFIDES_IN,
        )

    @property
    def is_comfort_level(self):
        return self in (
            self.RUNS_FROM,
            self.FEARS,
            self.AVOIDS,
            self.CONSIDERS,
            self.RELATES_TO,
            self.UNDERSTANDS,
            self.KNOWS_DEEPLY,
        )

    @property
    def is_romance_level(self):
        return self in (self.UNINTERESTED, self.FANCIES, self.ADORES, self.LOVES)

    @property
    def is_any_neg(self):
        return self.is_extreme_neg or self.is_mid_neg or self.is_low_neg

    @property
    def is_any_pos(self):
        return self.is_extreme_pos or self.is_mid_pos or self.is_low_pos

    @property
    def is_extreme_neg(self):
        return self in (self.LOATHES, self.RESENTS, self.DISCREDITS, self.RUNS_FROM)

    @property
    def is_mid_neg(self):
        return self in (
            self.HATES,
            self.ENVIES,
            self.HATES,
            self.DISTRUSTS,
            self.FEARS,
        )

    @property
    def is_low_neg(self):
        return self in (self.DISLIKES, self.BEGRUDGES, self.DOUBTS, self.AVOIDS)

    @property
    def is_neutral(self):
        return self in (
            self.KNOWS_OF,
            self.ACKNOWLEDGES,
            self.OBSERVES,
            self.CONSIDERS,
            self.UNINTERESTED,
        )

    @property
    def is_low_pos(self):
        return self in (
            self.LIKES,
            self.PRAISES,
            self.LISTENS_TO,
            self.RELATES_TO,
            self.FANCIES,
        )

    @property
    def is_mid_pos(self):
        return self in (
            self.ENJOYS,
            self.RESPECTS,
            self.TRUSTS,
            self.UNDERSTANDS,
            self.ADORES,
        )

    @property
    def is_extreme_pos(self):
        return self in (
            self.CHERISHES,
            self.ADMIRES,
            self.CONFIDES_IN,
            self.KNOWS_DEEPLY,
            self.LOVES,
        )


rel_type_tiers: dict = {
    RelType.LIKE: [l for l in [*RelTier] if l.is_like_level],
    RelType.RESPECT: [l for l in [*RelTier] if l.is_respect_level],
    RelType.TRUST: [l for l in [*RelTier] if l.is_trust_level],
    RelType.COMFORT: [l for l in [*RelTier] if l.is_comfort_level],
    RelType.ROMANCE: [l for l in [*RelTier] if l.is_romance_level],
}
