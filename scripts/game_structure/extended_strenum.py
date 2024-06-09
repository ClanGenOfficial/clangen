from strenum import StrEnum


class ExtendedStrEnum(StrEnum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

    @classmethod
    def index(cls, val: str, **kwargs):
        return cls.list().index(val)
