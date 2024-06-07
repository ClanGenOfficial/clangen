from strenum import StrEnum

class Status(StrEnum):
    """
    Roles that a cat may hold.
    """
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

    EXILED = "exiled"


    @staticmethod
    def str_to_status(input_string: str):
        """Returns the Status corresponding to the input string."""
        if input_string == 'newborn':
            return Status.NEWBORN
        elif input_string == 'kitten':
            return Status.KITTEN
        elif input_string == 'elder':
            return Status.ELDER
        elif input_string == 'apprentice':
            return Status.APP
        elif input_string == 'warrior':
            return Status.WARRIOR
        elif input_string == 'mediator apprentice':
            return Status.MEDIATORAPP
        elif input_string == 'mediator':
            return Status.MEDIATOR
        elif input_string == 'medicine cat apprentice':
            return Status.MEDCATAPP
        elif input_string == 'medicine cat':
            return Status.MEDCAT
        elif input_string == 'deputy':
            return Status.DEPUTY
        elif input_string == 'leader':
            return Status.LEADER
    def is_kit_any(self):
        """True if cat is newborn or kitten."""
        return self in [Status.NEWBORN, Status.KITTEN]

    def is_apprentice_any(self):
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
    
    def is_deputy_or_leader(self):
        """True if cat is deputy or leader."""
        return self in [Status.DEPUTY, Status.LEADER]

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