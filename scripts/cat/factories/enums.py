from enum import Enum


class CatType(Enum):
    NEW = 0
    LOAD_JSON = 1
    LOAD_CSV = 2
    FADED = 3
    TEST = 999
