#!/usr/bin/env python3
# -*- coding: ascii -*-
from typing import List, Union
from scripts.patrol.patrol_outcome import PatrolOutcome
from scripts.patrol.patrol_path import PatrolPath


class PatrolEvent:

    def __init__(self,
                patrol_id,
                biome: List[str] = None,
                season: List[str] = None,
                types: List[str] = None,
                tags: List[str] = None,
                weight: int = 20,
                patrol_art: Union[str, None] = None,
                patrol_art_clean: Union[str, None] = None,
                intro_text: str = "",
                decline_text: str = "",
                chance_of_success=0,
                patrol_paths: List[PatrolPath]= None,
                min_cats=1,
                max_cats=6,
                min_max_status: dict = None,
                relationship_constraints: List[str] = None,
                pl_skill_constraints: List[str] = None,
                pl_trait_constraints: List[str] = None):
        
        self.patrol_id = patrol_id
        self.weight = weight
        self.types = types if types is not None else []
        
        self.patrol_art = patrol_art
        self.patrol_art_clean = patrol_art_clean
        self.biome = biome if biome is not None else ["Any"]
        self.season = season if season is not None else ["Any"]
        self.tags = tags if tags is not None else []
        self.intro_text = intro_text
        
        self.patrol_paths = patrol_paths if patrol_paths is not None else []
        self.relationship_constraints = relationship_constraints if relationship_constraints \
                                              is not None else []
        self.pl_skill_constraints = pl_skill_constraints if pl_skill_constraints is not None else []
        self.pl_trait_constraints = pl_trait_constraints if pl_trait_constraints is not None else []
        self.min_max_status = min_max_status if min_max_status is not None else {}

    @property
    def new_cat(self) -> bool:
        """Returns boolian if there are any outcomes that results in 
            a new cat joining (not just meeting)"""
        
        for out in self.success_outcomes + self.fail_outcomes + \
             self.antag_fail_outcomes + self.antag_success_outcomes:
            for sublist in out.new_cat:
                if "join" in sublist:
                    return True
                
        return False
    
    @property
    def other_clan(self) -> bool:
        """Return boolian indicating if any outcome has any reputation effect"""
        for out in self.success_outcomes + self.fail_outcomes + \
             self.antag_fail_outcomes + self.antag_success_outcomes:
            if out.other_clan_rep is not None:
                return True
            
        return False
        