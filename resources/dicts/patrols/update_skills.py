import ujson
import collections
import os
from os.path import exists as file_exists
from enum import Enum

""" This script exists to count and catalogue all patrols.   """
class SkillPath(Enum):
    TEACHER = (
        "quick to help",
        "good teacher",
        "great teacher",
        "excellent teacher"
    )
    HUNTER =  (
        "moss-ball hunter",
        "great hunter",
        "renowned hunter"
    )
    FIGHTER = (
        "avid play-fighter",
        "good fighter",
        "formidable fighter",
        "unusually strong fighter"
    )
    RUNNER = (
        "never sits still",
        "fast runner",
        "incredible runner",
        "fast as the wind"
    )
    CLIMBER = (
        "constantly climbing",
        "good climber",
        "great climber",
        "impressive climber"
    )
    SWIMMER = (
        "splashes in puddles",
        "good swimmer",
        "talented swimmer",
        "fish-like swimmer"
    )
    SPEAKER = (
        "confident with words",
        "good speaker",
        "great speaker",
        "eloquent speaker"
    )
    MEDIATOR = (
        "quick to make peace",
        "good mediator",
        "great mediator",
        "skilled mediator"
    )
    CLEVER = (
        "quick witted",
        "clever",
        "very clever",
        "incredibly clever"
    )
    INSIGHTFUL = (
        "careful listener",
        "helpful insight",
        "valuable insight",
        "trusted advisor"
    )
    SENSE = (
        "oddly observant",
        "natural intuition",
        "keen eye",
        "unnatural senses"
    )
    KIT = (
        "active imagination",
        "good kitsitter",
        "great kitsitter",
        "beloved kitsitter"
    )
    STORY = (
        "lover of stories",
        "good storyteller",
        "great storyteller",
        "masterful storyteller"
    )
    LORE = (
        "interested in Clan history",
        "learner of lore",
        "lore keeper",
        "lore master"
    )
    CAMP = (
        "picky nest builder",
        "steady paws",
        "den builder",
        "camp keeper"
    )
    HEALER = (
        "interested in herbs",
        "good healer",
        "great healer",
        "fantastic healer"
    )
    STAR = (
        "curious about StarClan",
        "innate connection to StarClan",
        "strong connection to StarClan",
        "unbreakable connection to StarClan"
    )
    OMEN = (
        "interested in oddities",
        "omen seeker",
        "omen sense",
        "omen sight"
    )
    DREAM = (
        "restless sleeper",
        "strange dreamer",
        "dream walker",
        "dream shaper"
    )
    CLAIRVOYANT = (
        "oddly insightful",
        "somewhat clairvoyant",
        "fairly clairvoyant",
        "incredibly clairvoyant"
    )
    PROPHET = (
        "fascinated by prophecies",
        "prophecy seeker",
        "prophecy interpreter",
        "prophet"
    )
    GHOST = (
        "morbid curiosity",
        "ghost sense",
        "ghost sight",
        "ghost speaker"
    )


conversion = {
            "strong connection to StarClan": (SkillPath.STAR, 2), 
            "good healer": (SkillPath.HEALER, 1),
            "great healer": (SkillPath.HEALER, 2),
            "fantastic healer": (SkillPath.HEALER, 3),
            "good teacher": (SkillPath.TEACHER, 1),
            "great teacher": (SkillPath.TEACHER, 2),
            "fantastic teacher": (SkillPath.TEACHER, 3),
            "good mediator": (SkillPath.MEDIATOR, 1),
            "great mediator": (SkillPath.MEDIATOR, 2),
            "excellent mediator": (SkillPath.MEDIATOR, 3),
            "smart": (SkillPath.CLEVER, 1),
            "very smart": (SkillPath.CLEVER, 2),
            "extremely smart": (SkillPath.CLEVER, 3),
            "good hunter": (SkillPath.HUNTER, 1),
            "great hunter": (SkillPath.HUNTER, 2),
            "fantastic hunter": (SkillPath.HUNTER, 3),
            "good fighter": (SkillPath.FIGHTER, 1),
            "great fighter": (SkillPath.FIGHTER, 2),
            "excellent fighter": (SkillPath.FIGHTER, 3),
            "good speaker": (SkillPath.SPEAKER, 1),
            "great speaker": (SkillPath.SPEAKER, 2),
            "excellent speaker": (SkillPath.SPEAKER, 3),
            "good storyteller": (SkillPath.STORY, 1),
            "great storyteller": (SkillPath.STORY, 2),
            "fantastic storyteller": (SkillPath.STORY, 3),
            "smart tactician": (SkillPath.INSIGHTFUL, 1),
            "valuable tactician": (SkillPath.INSIGHTFUL, 2),
            "valuable insight": (SkillPath.INSIGHTFUL, 3),
            "good kitsitter": (SkillPath.KIT, 1),
            "great kitsitter": (SkillPath.KIT, 2),
            "beloved kitsitter": (SkillPath.KIT, 3),
            "camp keeper": (SkillPath.CAMP, 3),
            "den builder": (SkillPath.CAMP, 2),
            "omen sight": (SkillPath.OMEN, 3),
            "dream walker": (SkillPath.DREAM, 2),
            "clairvoyant": (SkillPath.CLAIRVOYANT, 2),
            "prophet": (SkillPath.PROPHET, 3),
            "lore keeper": (SkillPath.LORE, 2),
            "keen eye": (SkillPath.SENSE, 2)
        }

def change_skill(pa):
    global conversion
    
    with open(pa, 'r') as read_file:
        patrol_data = ujson.loads(read_file.read())
    
    if len(patrol_data) < 1:
        return
    
    if not isinstance(patrol_data[0], dict):
        return
    
    for _p in patrol_data:
        if "win_skills" in _p:
            converted_skills = []
            if _p["win_skills"] is None:
                _p["win_skills"] = []
            for _skill in _p["win_skills"]:
                if _skill in conversion:
                    converted_skills.append([conversion[_skill][0].name, conversion[_skill][1]])
            
            #Remove duplicates:
            lowest = {}
            for x in converted_skills:
                if x[0] not in lowest:
                    lowest[x[0]] = x[1]
                else:
                    lowest[x[0]] = min(x[1], lowest[x[0]])
            
            final_skills = []
            for x in lowest:
                final_skills.append(f"{x},{lowest[x]}")
            
            _p["win_skills"] = final_skills
        
        if "fail_skills" in _p:
            converted_skills = []
            if _p["fail_skills"] is None:
                _p["fail_skills"] = []
            for _skill in _p["fail_skills"]:
                #print(_skill)
                if _skill in conversion:
                    converted_skills.append([conversion[_skill][0].name, conversion[_skill][1]])
            
            #Remove duplicates:
            lowest = {}
            for x in converted_skills:
                if x[0] not in lowest:
                    lowest[x[0]] = x[1]
                else:
                    lowest[x[0]] = min(x[1], lowest[x[0]])
            
            final_skills = []
            for x in lowest:
                final_skills.append(f"{x},{lowest[x]}")
            
            _p["fail_skills"] = final_skills
    
    with open(pa, 'w') as write_file:
        write_file.write(ujson.dumps(patrol_data, indent=4).replace("\/", "/"))

root_dir = "../patrols"
file_set = set()

for dir_, _, files in os.walk(root_dir):
    for file_name in files:
        rel_dir = os.path.relpath(dir_, root_dir)
        rel_file = os.path.join(rel_dir, file_name)
        if os.path.splitext(rel_file)[-1].lower() == ".json":
            file_set.add(rel_file)

for pa in file_set:
    change_skill(pa)

