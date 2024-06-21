from scripts.game_structure.extended_strenum import ExtendedStrEnum


class Status(ExtendedStrEnum):
    """
    Roles that a cat may hold. Check ExtendedStrEnum for more things!
    """
    # These are in this order for food priority filtering
    NEWBORN = "newborn"
    KITTEN = "kitten"
    ELDER = "elder"
    WARRIORAPP = "apprentice"
    WARRIOR = "warrior"
    MEDIATORAPP = "mediator apprentice"
    MEDIATOR = "mediator"
    MEDCATAPP = "medicine cat apprentice"
    MEDCAT = "medicine cat"
    DEPUTY = "deputy"
    LEADER = "leader"

    NONE = "NONE"
    EXCLAN = "former Clancat"
    EXILED = "exiled"
    KITTYPET = "kittypet"
    LONER = "loner"
    ROGUE = "rogue"

    def is_working_any(self):
        """True if cat is a working role (warrior + app, medcat + app, mediator + app, deputy and leader)"""
        return not (self.is_kit_any()
                    or self.is_elder()) \
            and self.is_inside_clan()

    def can_patrol_any(self):
        """True if able to go on patrol (warrior + app, medcat + app, deputy and leader)"""
        return (self.is_warrior_any()
                or self.is_medcat_any()
                or self.is_deputy_or_leader())

    def can_patrol_app(self):
        """True if apprentice who can go on patrol (warrior app and medcat app)"""
        return self in [Status.WARRIORAPP, Status.MEDCATAPP]

    def is_kit_any(self):
        """True if cat is newborn or kitten."""
        return self in [Status.NEWBORN, Status.KITTEN]

    def is_app_any(self):
        """True if cat is apprentice,
        medicine cat apprentice or mediator apprentice."""
        return self in [Status.WARRIORAPP,
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
        return self in [Status.WARRIOR, Status.WARRIORAPP]

    def is_deputy_or_leader(self):
        """True if cat is deputy or leader."""
        return self in [Status.DEPUTY, Status.LEADER]

    def is_warrior_medcat_or_mediator(self):
        """True if cat is warrior, medcat or mediator"""
        return self in [Status.WARRIOR, Status.MEDCAT, Status.MEDIATOR]

    def is_deputy_leader_or_warrior(self):
        """True if cat is warrior, deputy or leader"""
        return self.is_deputy_or_leader() or self.is_warrior()

    def is_outside_clan(self):
        """True if cat is former Clancat, exiled, kittypet, loner or rogue"""
        return self in [
            Status.EXCLAN, Status.EXILED, Status.KITTYPET,
            Status.LONER, Status.ROGUE]

    def is_inside_clan(self):
        """True if cat is a member of the Clan.

        (newborn, kitten, elder, warrior + app, medcat + app, mediator + app, deputy & leader)"""
        return not self.is_outside_clan() and not self.is_none()

    def is_newborn(self):
        """True if newborn."""
        return self == Status.NEWBORN

    def is_kitten(self):
        """True if kitten."""
        return self == Status.KITTEN

    def is_elder(self):
        """True if elder."""
        return self == Status.ELDER

    def is_warrior_app(self):
        """True if (warrior) apprentice."""
        return self == Status.WARRIORAPP

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

    def is_none(self):
        """True if debug/default empty value"""
        return self == Status.NONE
