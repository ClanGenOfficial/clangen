from enum import IntEnum

class Status(IntEnum):
    """
    Roles that a cat may hold.
    """
    NONE = 0
    NEWBORN = 1
    KITTEN = 2
    ELDER = 3
    APP = 4
    WARRIOR = 5
    MEDIATORAPP = 6
    MEDIATOR = 7
    MEDCATAPP = 8
    MEDCAT = 9
    DEPUTY = 10
    LEADER = 11

    EXILED = -1




    @staticmethod
    def str_to_status(input_string: str):
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
        return self in [Status.NEWBORN, Status.KITTEN]

    def is_apprentice_any(self):
        return self in [Status.APP,
                        Status.MEDCATAPP,
                        Status.MEDIATORAPP]
    
    def is_mediator_any(self):
        return self in [Status.MEDIATOR, Status.MEDIATORAPP]
    
    def is_medcat_any(self):
        return self in [Status.MEDCAT, Status.MEDCATAPP]
    
    def is_warrior_any(self):
        return self in [Status.WARRIOR, Status.APP]
    
    def is_deputy_or_leader(self):
        return self in [Status.DEPUTY, Status.LEADER]