from strenum import StrEnum


class ExtendedStrEnum(StrEnum):
    @classmethod
    def list(cls):
        """Get a list of all the possible values in this class (strings, not Enum objects)"""
        return list(map(lambda c: c.value, cls))

    @classmethod
    def index(cls, val: str, **kwargs):
        """Get the index of the requested value in the list of enums
        :param str val: The value to find in the list of enums"""
        return cls.list().index(val)
