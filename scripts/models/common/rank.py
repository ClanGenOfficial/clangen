from enum import Enum


class Rank(Enum):
    NEWBORN = "newborn"
    KITTEN = "kitten"
    APPRENTICE = "apprentice"
    MEDICINE_APPRENTICE = "medicine cat apprentice"
    MEDIATOR_APPRENTICE = "mediator apprentice"
    WARRIOR = "warrior"
    MEDICINE_CAT = "medicine cat"
    MEDIATOR = "mediator"
    DEPUTY = "deputy"
    LEADER = "leader"
    ELDER = "elder"

    # outsider ranks
    LONER = "loner"
    ROGUE = "rogue"
    KITTYPET = "kittypet"


def validate_clan_rank(value: str) -> str:
    ranks = [r.value for r in Rank]
    _, rank_str = value.split(":")
    if rank_str not in ranks:
        raise ValueError(f"Rank {rank_str} in {value} is not a valid rank!")
    return value
