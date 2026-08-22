import logging
import random
from math import floor

from scripts.cat.cats import cat_class, Cat
from scripts.cat.enums import CatRank, CatAge
from scripts.cat.skills import SkillPath
from scripts.clan_package.settings import get_clan_setting
from scripts.conditions import (
    medicine_cats_can_cover_clan,
    get_amount_cat_for_one_medic,
)
from scripts.events_module.ceremony.generate_normal_ceremony import create_ceremony
from scripts.game_structure import game, constants

logger = logging.getLogger(__name__)


def check_for_ceremony(main_cat: Cat):
    """
    Checks if a cat needs to undergo a ceremony, then handles everything pertaining to that ceremony.
    :param main_cat: The cat object that must be checked for a potential ceremony
    """

    # Protection check, to ensure "None" cats won't cause a crash.
    if not main_cat or main_cat.dead:
        return

    # TODO: set ceremony_accessory somehow? perhaps as switch or a cat attr?

    # game.clan.rank check
    if main_cat.status.rank == CatRank.DEPUTY and game.clan.deputy is None:
        game.clan.deputy = main_cat
    if main_cat.status.rank == CatRank.MEDICINE_CAT and game.clan.medicine_cat is None:
        game.clan.medicine_cat = main_cat

    # PROMOTE DEPUTY TO LEADER
    if main_cat.status.rank == CatRank.DEPUTY:
        # If a Clan deputy exists, and the leader is dead, outside, or doesn't exist, make the deputy leader.
        if not game.clan.leader or not game.clan.leader.status.alive_in_player_clan:
            _handle_leader_ceremony(main_cat)
            return

    # OLD CAT RETIRE
    if (
        not main_cat.no_retire
        and main_cat.status.rank in (CatRank.WARRIOR, CatRank.DEPUTY)
        and not main_cat.apprentice
        and main_cat.moons > 114
    ):
        # There is some variation in the age.
        if main_cat.moons > 140 or not int(
            random.random() * (-0.7 * main_cat.moons + 100)
        ):
            if main_cat.status.rank == CatRank.DEPUTY:  # unset the deputy
                game.clan.deputy = None

            trigger_ceremony(main_cat, CatRank.ELDER)
            return

    # BECOME APPRENTICE
    if main_cat.moons == cat_class.age_moons[CatAge.ADOLESCENT][0]:
        if main_cat.status.rank == CatRank.KITTEN:
            # BECOME MEDICINE APPRENTICE
            if _is_suitable_medcat_app(main_cat):
                trigger_ceremony(main_cat, CatRank.MEDICINE_APPRENTICE)
                ceremony_accessory = True
                return
            elif _is_suitable_mediator_app(main_cat):
                trigger_ceremony(main_cat, CatRank.MEDIATOR_APPRENTICE)
                ceremony_accessory = True
                return
            else:
                trigger_ceremony(main_cat, CatRank.APPRENTICE)
                ceremony_accessory = True
                return

    # graduate
    if main_cat.status.rank.is_any_apprentice_rank():
        if get_clan_setting("12_moon_graduation"):
            _ready = main_cat.moons >= 12
        else:
            _ready = (
                main_cat.experience_level not in ["untrained", "learning"]
                and main_cat.moons
                >= constants.CONFIG["graduation"]["min_graduating_age"]
            ) or main_cat.moons >= constants.CONFIG["graduation"]["max_apprentice_age"][
                main_cat.status.rank
            ]

        if _ready:
            if main_cat.status.rank == CatRank.APPRENTICE:
                trigger_ceremony(main_cat, CatRank.WARRIOR)
                ceremony_accessory = True

            # promote to med cat
            elif main_cat.status.rank == CatRank.MEDICINE_APPRENTICE:
                trigger_ceremony(main_cat, CatRank.MEDICINE_CAT)
                ceremony_accessory = True

            elif main_cat.status.rank == CatRank.MEDIATOR_APPRENTICE:
                trigger_ceremony(main_cat, CatRank.MEDIATOR)
                ceremony_accessory = True


def _handle_leader_ceremony(main_cat):
    """
    Handles everything pertaining to a leader ceremony.
    """
    game.clan.leader_lives = 9
    trigger_ceremony(main_cat, CatRank.LEADER)
    main_cat.generate_lead_ceremony()
    game.clan.deputy = None
    game.clan.leader = main_cat


def trigger_ceremony(main_cat: Cat, new_rank: CatRank):
    """
    Actually triggers the ceremony to occur and initiates the cat's rank change.
    :param main_cat: The cat object receiving the ceremony
    :param new_rank: The CatRank that main_cat is becoming
    """
    old_name = str(main_cat.name)

    current_mentor = Cat.fetch_cat(main_cat.mentor) if main_cat.mentor else None

    main_cat.rank_change(new_rank)
    main_cat.rank_change_traits_skill(current_mentor)

    create_ceremony(main_cat=main_cat, old_name=old_name)


def _is_suitable_mediator_app(main_cat: Cat) -> bool:
    """
    Determines whether this cat will become a mediator
    :param main_cat: A kitten preparing for apprenticeship ceremony
    :return: True if the kitten should be a mediator, False otherwise
    """
    # Chance for mediator apprentice
    mediator_list = list(
        filter(
            lambda x: x.status.rank == CatRank.MEDIATOR
            and x.status.alive_in_player_clan,
            Cat.all_cats_list,
        )
    )
    # This checks if at least one mediator already has an apprentice.
    has_mediator_apprentice = False
    for c in mediator_list:
        if c.apprentice:
            has_mediator_apprentice = True
            break
    chance = constants.CONFIG["roles"]["mediator_app_chance"]
    if main_cat.personality.trait in [
        "charismatic",
        "loving",
        "responsible",
        "wise",
        "thoughtful",
    ]:
        chance = int(chance / 1.5)
    if main_cat.is_disabled():
        chance = int(chance / 2)
    if chance == 0:
        chance = 1
    # Only become a mediator if there is already one in the clan.
    if (
        mediator_list
        and not has_mediator_apprentice
        and not int(random.random() * chance)
    ):
        return True
    return False


def _is_suitable_medcat_app(cat) -> bool:
    """
    Determines whether this cat will become a medicine cat
    :param cat: A kitten preparing for apprenticeship ceremony
    :return: True if the kitten should be a medcat, False otherwise
    """
    # assign chance to become med app depending on current med cat and traits
    chance = constants.CONFIG["roles"]["base_medicine_app_chance"]  # 41
    logger.info("Medcat app %s starting chance: %d", str(cat.name), chance)

    med_cat_list = [
        i
        for i in Cat.all_cats_list
        if i.status.rank.is_any_medicine_rank() and i.status.alive_in_player_clan
    ]

    num_medcats = len(med_cat_list)

    # get number of medcat apps
    num_med_apps = len(
        [cat.status.rank == CatRank.MEDICINE_APPRENTICE for cat in med_cat_list]
    )
    logger.debug("Current number of medcats: %d", num_medcats - num_med_apps)
    logger.debug("Current number of medcat apps: %d", num_med_apps)

    # check if the Clan has sufficient med cats
    enough_working_meds = medicine_cats_can_cover_clan(
        Cat.all_cats.values(),
        amount_per_med=get_amount_cat_for_one_medic(game.clan),
    )

    if (
        floor(num_med_apps / max(1, (len(med_cat_list) - num_med_apps)))
        > constants.CONFIG["roles"]["medicine cat apprentice"]["max_medcats_to_apps"]
    ):
        if enough_working_meds:
            # early return if the ratio of apps would be too high
            logger.info("Too many apprentices for medcat population. Aborting.")
            return False
        logger.debug(
            "Too many apprentices for medcat population, but not enough medicine cats for Clan! Continuing."
        )

    # check if the medicine cats are old
    senior_meds = [
        c
        for c in med_cat_list
        if c.age == "senior" and c.status.rank == CatRank.MEDICINE_CAT
    ]

    ancient_meds = [
        c
        for c in senior_meds
        if c.moons
        >= constants.CONFIG["roles"]["medicine cat apprentice"][
            "threshold_moons_ancient"
        ]
    ]

    senior_med_ratio = (len(senior_meds) / num_medcats) if num_medcats != 0 else 0

    ancient_med_ratio = (len(ancient_meds) / num_medcats) if num_medcats != 0 else 0

    if (
        ancient_med_ratio
        > constants.CONFIG["roles"]["medicine cat apprentice"][
            "threshold_percentage_ancient"
        ]
        / 100
    ):
        # These chances apply if enough medicine cats are very old.
        if enough_working_meds:
            chance = chance / 3
        else:
            logger.info("Not enough healthy medicine cats")
            chance = chance / 14

        logger.info("Ancient medicine cats, chance updated to %d", round(chance))
    elif (
        senior_med_ratio
        > constants.CONFIG["roles"]["medicine cat apprentice"][
            "threshold_percentage_seniors"
        ]
        / 100
    ):
        # These chances apply if enough medicine cats are elders.
        if enough_working_meds:
            chance = chance / 2.22
        else:
            logger.info("Not enough healthy medicine cats")
            chance = chance / 14

        logger.info("Senior medicine cats, chance updated to %d", round(chance))
    else:
        # These chances will only be reached if the
        # Clan has at least one non-elder medicine cat.
        if not enough_working_meds:
            chance = chance / 7.125
            logger.info(
                "Not enough healthy medicine cats, chance updated to %d", chance
            )
        else:
            chance = chance * 2.22
            logger.info(
                "Enough healthy young medicine cats, chance updated to %d", chance
            )

    if cat.personality.trait in [
        "careful",
        "compassionate",
        "loving",
        "wise",
        "faithful",
    ]:
        chance = chance / 1.3
        logger.info("Suitable trait, chance updated to %d", round(chance))

    elif cat.personality.trait in [
        "adventurous",
        "arrogant",
        "bold",
        "bloodthirsty",
        "cold",
        "fierce",
        "rebellious",
        "troublesome",
        "vengeful",
    ]:
        chance = chance * 2
        logger.info("Unsuitable trait, chance updated to %d", round(chance))

    beneficial_skills = [
        SkillPath.OMEN,
        SkillPath.PROPHET,
        SkillPath.HEALER,
        SkillPath.STAR,
        SkillPath.DREAM,
        SkillPath.CLAIRVOYANT,
        SkillPath.GHOST,
        SkillPath.CAMP,
    ]

    if cat.skills.primary.path in beneficial_skills:
        chance = chance / 2
        logger.info("beneficial primary skill, chance updated to %d", round(chance))

    if cat.skills.secondary and cat.skills.secondary.path in beneficial_skills:
        chance = chance / 4
        logger.info("beneficial secondary skill, chance updated to %d", round(chance))

    if cat.is_disabled():
        chance = chance / 2

    if num_med_apps == 0:
        # if there are no apprentices at all, make it slightly easier to get one
        logger.info("No apprentices at all")
        chance = chance / 1.8
        logger.info("No medcat apprentices at all, chance updated to %d", chance)
    if num_med_apps > 1:
        # if there's already at least one medcat app, make it harder to get another
        chance = chance * (1 + (0.2 * (num_med_apps - 1)))
        logger.info("%d medcat apps, chance updated to %d", num_med_apps, chance)

    chance = max(1, int(chance))

    success = not int(random.random() * chance)
    logger.info("%s final chance: %d | SUCCESS: %s", cat.name, chance, success)
    return success
