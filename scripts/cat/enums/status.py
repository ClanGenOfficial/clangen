from strenum import StrEnum


class Status(StrEnum):
    """
    Roles that a cat may hold.
    """
    # These are in this order for food priority filtering
    NONE = "ERROR"
    NEWBORN = "newborn"
    KITTEN = "kitten"
    ELDER = "elder"
    APP = "apprentice"
    WARRIOR = "warrior"
    MEDIATORAPP = "mediator apprentice"
    MEDIATOR = "mediator"
    MEDCATAPP = "medicine cat apprentice"
    MEDCAT = "medicine cat"
    DEPUTY = "deputy"
    LEADER = "leader"

    EXCLAN = "former Clancat"
    EXILED = "exiled"
    KITTYPET = "kittypet"
    LONER = "loner"
    ROGUE = "rogue"

    def is_working_any(self):
        """Return true if in clan and NOT newborn, kitten or elder."""
        return not (self.is_kit_any()
                    and self.is_elder()) \
            and not self.is_outside_clan()

    def is_patrol_any(self):
        """True if able to go on patrol (working cats minus mediator & mediator app)"""
        return (self.is_warrior_any()
                or self.is_medcat_any()
                or self.is_leadership())

    def is_patrol_app(self):
        """True if apprentice who can go on patrol (warrior app or medcat app)"""
        return self in [Status.APP, Status.MEDCATAPP]

    def is_kit_any(self):
        """True if cat is newborn or kitten."""
        return self in [Status.NEWBORN, Status.KITTEN]

    def is_app_any(self):
        """True if cat is apprentice,
        medicine cat apprentice or mediator apprentice."""
        return self in [Status.APP,
                        Status.MEDCATAPP,
                        Status.MEDIATORAPP]

    def is_mediator_any(self):
        """True if cat is mediator or mediator apprentice."""
        return self in [Status.MEDIATOR, Status.MEDIATORAPP]

    def is_medcat_any(self):
        """True if cat is medicine cat or medicine cat apprentice."""
        return self in [Status.MEDCAT, Status.MEDCATAPP]

    def is_warrior_any(self):
        """True if cat is warrior or apprentice."""
        return self in [Status.WARRIOR, Status.APP]

    def is_leadership(self):
        """True if cat is deputy or leader."""
        return self in [Status.DEPUTY, Status.LEADER]

    def is_normal_adult(self):
        """True if cat is deputy, leader or warrior"""
        return self.is_leadership() or self.is_warrior()

    def is_outside_clan(self):
        """True if cat does not hold a Clan role"""
        return self in [
            Status.EXCLAN, Status.EXILED, Status.KITTYPET,
            Status.LONER, Status.ROGUE]

    def is_newborn(self):
        """True if newborn."""
        return self == Status.NEWBORN

    def is_kitten(self):
        """True if kitten."""
        return self == Status.KITTEN

    def is_elder(self):
        """True if elder."""
        return self == Status.ELDER

    def is_app(self):
        """True if (warrior) apprentice."""
        return self == Status.APP

    def is_warrior(self):
        """True if warrior."""
        return self == Status.WARRIOR

    def is_mediator_app(self):
        """True if mediator apprentice."""
        return self == Status.MEDIATORAPP

    def is_mediator(self):
        """True if mediator."""
        return self == Status.MEDIATOR

    def is_medcat_app(self):
        """True if medicine cat apprentice."""
        return self == Status.MEDCATAPP

    def is_medcat(self):
        """True if medicine cat."""
        return self == Status.MEDCAT

    def is_deputy(self):
        """True if deputy."""
        return self == Status.DEPUTY

    def is_leader(self):
        """True if leader."""
        return self == Status.LEADER

    def is_ex_clan(self):
        """True if status is former Clancat"""
        return self == Status.EXCLAN

    def is_exiled(self):
        """True if exiled"""
        return self == Status.EXILED

    def is_kittypet(self):
        """True if kittypet"""
        return self == Status.KITTYPET

    def is_loner(self):
        """True if loner"""
        return self == Status.LONER

    def is_rogue(self):
        """True if rogue"""
        return self == Status.ROGUE
