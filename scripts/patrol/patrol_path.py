#!/usr/bin/env python3
# -*- coding: ascii -*-
import random
from random import choice, randint, choices
from typing import List, Dict, Union, TYPE_CHECKING
import re
import pygame
from os.path import exists as path_exists
from scripts.patrol.patrol_outcome import PatrolOutcome

if TYPE_CHECKING:
    from scripts.patrol.patrol import Patrol

from scripts.cat.history import History
from scripts.clan import HERBS
from scripts.utility import (
    change_clan_relations,
    change_clan_reputation,
    change_relationship_values, create_new_cat,
)
from scripts.game_structure.game_essentials import game
from scripts.cat.skills import SkillPath
from scripts.cat.cats import Cat, ILLNESSES, INJURIES, PERMANENT, BACKSTORIES
from scripts.cat.pelts import Pelt
from scripts.cat_relations.relationship import Relationship
from scripts.clan_resources.freshkill import ADDITIONAL_PREY, PREY_REQUIREMENT, HUNTER_EXP_BONUS, HUNTER_BONUS, \
    FRESHKILL_ACTIVE


class PatrolPath():

    def __init__(
            self,
            button_text: str,
            success_outcomes: List[PatrolOutcome],
            fail_outcomes: List[PatrolOutcome] ):
        
        
        
        self.button_text = button_text
        self.success_outcomes = success_outcomes
        self.fail_outcomes = fail_outcomes
        