import ujson
import collections
import os
from os.path import exists as file_exists

""" This script exists to count and catalogue all patrols.   """

HERBS = None
with open("C:/Users/maiak/Documents/GitHub/clangen/clangen/resources/dicts/herbs.json", 'r', encoding='utf-8') as read_file:
    HERBS = ujson.loads(read_file.read())
    
with open("C:/Users/maiak/Documents/GitHub/clangen/clangen/resources/dicts/conditions/illnesses.json", 'r') as read_file:
    ILLNESSES = ujson.loads(read_file.read())

with open("C:/Users/maiak/Documents/GitHub/clangen/clangen/resources/dicts/conditions/injuries.json", 'r') as read_file:
    INJURIES = ujson.loads(read_file.read())

with open("C:/Users/maiak/Documents/GitHub/clangen/clangen/resources/dicts/conditions/permanent_conditions.json", 'r') as read_file:
    PERMANENT = ujson.loads(read_file.read())

with open("C:/Users/maiak/Documents/GitHub/clangen/clangen/resources/dicts/backstories.json", 'r') as read_file:
    BACKSTORIES = ujson.loads(read_file.read())

    def get_patrol_art(patrol_id) -> tuple:
        """
        grabs art for the patrol based on the patrol_id
        -first checks for image file with exact patrol_id
        -then checks for image file with the patrol_id minus any numbers
        -then checks for image file with the patrol_id minus any numbers and with 'gen' replacing biome indicator
        -if none of those are available, then uses placeholder patrol type image
        if you are adding art and the art has gore or blood, add its exact patrol id to the explicit_patrol_art.json
        """
        path = "C:/Users/maiak/Documents/GitHub/clangen/clangen/resources/images/patrol_art/"

        # if gore isn't allowed then placeholder is shown instead
        explict = [
        "fst_hunt_fox_greenleafscavenge1",
        "fst_hunt_fox_greenleafscavenge2",
        "fst_hunt_fox_greenleafscavenge3",
        "fst_hunt_foxgray_greenleafscavenge1",
        "fst_hunt_foxgray_greenleafscavenge2",
        "fst_hunt_foxgray_greenleafscavenge3",
        "fst_hunt_foxgray_leaf-fallscavenge1",
        "fst_hunt_foxgray_leaf-fallscavenge2",
        "fst_hunt_foxgray_leaf-fallscavenge3",
        "bch_hunt_redfox_scavenge1",
        "bch_hunt_redfox_scavenge2",
        "bch_hunt_redfox_scavenge3",
        "bch_hunt_foxgray_scavenge1",
        "bch_hunt_foxgray_scavenge2",
        "bch_hunt_foxgray_scavenge3"
        ]

        
        generic = None
        if patrol_id.find('med') != -1:
            generic = 'med'
        elif patrol_id.find('hunt') != -1:
            generic = 'hunt'
        elif patrol_id.find('train') != -1:
            generic = 'train'
        elif patrol_id.find('bord') != -1:
            generic = 'bord'
            
        generic = f"{generic}_general_intro" if generic else None


        image_name = patrol_id
        specfic = None
        # looking for exact patrol ID
        if file_exists(f"{path}{image_name}.png"):
            specfic = image_name

        # looking for patrol ID without numbers
        image_name = ''.join([i for i in image_name if not i.isdigit()])
        if file_exists(f"{path}{image_name}.png"):
            specfic = image_name

        # looking for patrol ID with biome indicator replaced with 'gen'
        # if that isn't found then patrol type placeholder will be used
        image_name = ''.join([i for i in image_name if not i.isdigit()])
        image_name = image_name.replace("fst_", "gen_")
        image_name = image_name.replace("mtn_", "gen_")
        image_name = image_name.replace("pln_", "gen_")
        image_name = image_name.replace("bch_", "gen_")
        if file_exists(f"{path}{image_name}.png"):
            specfic = image_name
    
        if not specfic:
            specfic = generic
            
        return (specfic, generic if patrol_id in explict else None)


def reformat_patrol(path:str):
    """Reformat patrol"""


    with open(path, "r") as read_file:
        patrols = ujson.loads(read_file.read())

    if not patrols:
        return

    if type(patrols[0]) != dict:
        print(path, "is not in the correct patrol format. It may not be a patrol .json.")
        return

    outcomes_convert = {
            "unscathed_common": 0,
            "unscathed_rare": 1,
            "stat_skill": 2,
            "stat_trait": 3
        }

    
    all_new_patrols = []
    for p_ in patrols:
        new_patrol = {
            "patrol_id": p_["patrol_id"],
            "biome": [p_["biome"]],
            "season": [p_.get("season", "Any")],
            "types": [],
            "tags": [],
            "patrol_art": None,
            "patrol_art_clean": None,
            "min_cats": p_["min_cats"],
            "max_cats": p_["max_cats"],
            "min_max_status": {},
            "weight": 20, 
            "intro_text": p_["intro_text"],
            "decline_text": p_["decline_text"],
            "chance_of_success": p_["chance_of_success"],
            "pl_skill_constraint": None,
            "relationship_constraint": None,
            "success_outcomes": [],
            "fail_outcomes": [],
        }
        
        # Patrol Art
        patrol_art = get_patrol_art(p_["patrol_id"])
        new_patrol["patrol_art"] = patrol_art[0]
        if patrol_art[1]:
            new_patrol["patrol_art_clean"] = patrol_art[1]
        else:
            new_patrol.pop("patrol_art_clean")
        
        
        # First, type:
        tags = set(p_["tags"])
        
        if "reputation" in tags:
            tags.remove("reputation")
        if "fighting" in tags:
            tags.remove("fighting")
        
        # -----------------------------------------------------------------------------------
        
        
        for _ty in ("hunting", "border", "training", "herb_gathering"):
            if _ty in tags:
                tags.remove(_ty)
                new_patrol["types"].append(_ty)
        
        # ---------------------------------------------------------------------------------------------------------
        
        min_max_status = {
            "warrior": [0, 6],
            "deputy": [0, 6],
            "leader": [0, 6],
            "apprentice": [0, 6],
            "medicine cat": [0, 6],
            "medicine cat apprentice": [0, 6],
            "healer cats": [0, 6],
            "all apprentices": [0, 6],
            "normal adult": [0, 6]
        }
        
        if "herb_gathering" in new_patrol["types"]:
            min_max_status["healer cats"][0] = 1
        
        if "med_only" in tags:
            tags.remove("med_only")
            min_max_status["normal adult"] = [-1, -1]
            min_max_status["apprentice"] = [-1, -1]
        
        if "apprentice" in tags:
            tags.remove("apprentice")
            if "herb_gathering" in new_patrol["types"]:
                min_max_status["medicine cat apprentice"][0] = 1
            else:
                min_max_status["apprentice"][0] = 1
                
        if "warrior_app" in tags:
            tags.remove("warrior_app")
            min_max_status["apprentice"][0] = 1
            
        if "deputy" in tags:
            tags.remove("deputy")
            min_max_status["deputy"][0] = 1
            
        if "leader" in tags:
            tags.remove("leader")
            min_max_status["leader"][0] = 1
            
        if "warrior" in tags:
            tags.remove("warrior")
            min_max_status["normal adult"][0] = 1
            
        if "med_cat" in tags:
            tags.remove("med_cat")
            min_max_status["medicine cat"][0] = 1
        
        if "no_app" in tags:
            tags.remove("no_app")
            min_max_status["all apprentices"] = [-1, -1]
            
        if "no_leader" in tags:
            tags.remove("no_leader")
            min_max_status["leader"] = [-1, -1]
            
        if "no_deputy" in tags:
            tags.remove("no_deputy")
            min_max_status["deputy"] = [-1, -1]
            
        if "five_apprentices" in tags:
            tags.remove("five_apprentices")
            min_max_status["all apprentices"] = [5, 5]
            
        if "four_apprentices" in tags:
            tags.remove("four_apprentices")
            min_max_status["all apprentices"] = [4, 4]
            
        if "three_apprentices" in tags:
            tags.remove("three_apprentices")
            min_max_status["all apprentices"] = [3, 3]
        
        if "two_apprentices" in tags:
            tags.remove("two_apprentices")
            min_max_status["all apprentices"] = [2, 2]
            
        if "one_apprentice" in tags:
            tags.remove("one_apprentice")
            min_max_status["all apprentices"] = [1, 1]
            
        #Remove the unneeded ones
        for sta, num in min_max_status.copy().items():
            if num == [0, 6]:
                min_max_status.pop(sta)
                
        new_patrol["min_max_status"] = min_max_status
        
        
        #---------------------------------------------------------------------------------------
        
        # Possible stat cats:
        possible_stat_cats = []
        if "pl_has_stat" in tags:
            tags.remove("pl_has_stat")
            possible_stat_cats.append("p_l")
            
        if "rc_has_stat" in tags:
            tags.remove("rc_has_stat")
            possible_stat_cats.append("r_c")
            
        if "app1_has_stat" in tags:
            tags.remove("app1_has_stat")
            possible_stat_cats.append("app1")
            
        if "adult_stat" in tags:
            tags.remove("adult_stat")
            possible_stat_cats.append("adult")
        
        if "app_stat" in tags:
            tags.remove("app_stat")
            possible_stat_cats.append("app")
        
        # ---------------------------------------------------------------------------------------
        
        #OOF, there's min max status. Let's do outcomes
        prey_number_translation = {}
        idx = 0
        if not p_.get("success_text"):
            print(p_)
        
        for k in p_["success_text"].keys():
            prey_number_translation[k] = idx
            idx += 1
        
        # ---------------------------------------------------------------------------------------
        
        # Gather some relationship details
        relationship_amounts = {}
        n = 5
        if "big_change" in tags:
            tags.remove("big_change")
            n = 10
        
        
        for x in ("romantic", "platonic","respect", "comfort", "trust"):
            if x in tags:
                if x != "romantic":
                    tags.remove(x)
                if n in relationship_amounts:
                    relationship_amounts[n].append(x)
                else:
                    relationship_amounts[n] = [x]
        
        for x in ("dislike", "jealous"):
            if x in tags:
                tags.remove(x)
                if -n in relationship_amounts:
                    relationship_amounts[-n].append(x)
                else:
                    relationship_amounts[-n] = [x]
        
        for x, i in (("pos_jealous", "jealous"), ("pos_dislike", "dislike")):
            if x in tags:
                tags.remove(x)
                if n in relationship_amounts:
                    relationship_amounts[n].append(i)
                else:
                    relationship_amounts[n] = [i]
                
        if "sacrificial" in tags:
            tags.remove("sacrificial")
            if 15 in relationship_amounts:
                relationship_amounts[15].extend(["trust", "respect"])
            else:
                relationship_amounts[15] = ["trust", "respect"]
                   
        cats_to = []
        cats_from = []
        rel_mutual = False
        if "clan_to_p_l" in tags:
            tags.remove("clan_to_p_l")
            cats_to.append("p_l")
            cats_from.append("clan")
        
        if "clan_to_r_c" in tags:
            tags.remove("clan_to_r_c")
            cats_to.append("r_c_or_s_c")
            cats_from.append("clan")
        
        if "clan_to_patrol" in tags:
            tags.remove("clan_to_patrol")
            cats_to.append("patrol")
            cats_from.append("clan")
            
        if "patrol_to_r_c" in tags:
            tags.remove("patrol_to_r_c")
            cats_to.append("r_c_or_s_c")
            cats_from.append("patrol")
            
        if "patrol_to_p_l" in tags:
            tags.remove("patrol_to_p_l")
            cats_to.append("p_l")
            cats_from.append("patrol")
        
        if "rel_patrol" in tags:
            tags.remove("rel_patrol")
            cats_to.append("patrol")
            cats_from.append("patrol")
        
        if "rel_two_apps" in tags:
            tags.remove("rel_two_apps")
            if "romantic" in tags:
                tags.add("rom_two_apps")
            cats_to.append("app1")
            cats_from.append("app2")
            
        if "p_l_to_r_c" in tags:
            tags.remove("p_l_to_r_c")
            cats_to.append("p_l")
            cats_from.append("r_c")
            rel_mutual = True
        
        if "s_c_to_r_c" in tags:
            tags.remove("s_c_to_r_c")
            cats_to.append("s_c")
            cats_from.append("r_c")
            rel_mutual = True
        
        if not (cats_to and cats_from):
            cats_to = ["patrol"]
            cats_from = ["patrol"]
        
        #-----------------------------------------------------------------------------------------
        # NEW CAT STUFF
        new_cat_meeting = False
        if "meeting" in tags:
            tags.remove("meeting")
            new_cat_meeting = True
            
        new_cat_attributes = []
        for x in tags.copy():
            if "new_cat" in x:
                tags.remove(x)
                new_cat_attributes.extend(x.split("_"))
                
        new_cat_injury = None
        for x in tags.copy():
            if x.startswith("nc_"):
                tags.remove(x)
                if x[3:] in ("battle_injury", "minor_injury", "blunt_force_injury", "hot_injury", "cold_injury", "big_bite_injury", "small_bite_injury", "beak_bite", "rat_bite", "sickness"):
                    new_cat_injury = x[3:]
                else:
                    print(f"opps: {x}")

        if "new_cat_injury" in tags:
            tags.remove("new_cat_injury")
        
        if new_cat_attributes:
            tags.add("new_cat")
        
        
        # ----------------------------------------------------------------------------------------
        # SUCCESS OUTCOMES
        patrol_has_prey = False
        
        
        outcomes = []
        for key, text in p_["success_text"].items():
            out = {
                "text": text,
                "exp": p_["exp"],
            }
            
            if "rare" in key:
                out["weight"] = 5
            else:
                out["weight"] = 20
                
            if "stat_trait" in key and p_.get("win_trait"):
                if p_.get("win_trait"):
                    out["stat_trait"] = p_.get("win_trait")
                    
                if possible_stat_cats:
                    out["can_have_stat"] = possible_stat_cats
                    
            if "stat_skill" in key and p_.get("win_skills"):
                if p_.get("win_skills"):
                    out["stat_skill"] = p_.get("win_skills")
                    
                if possible_stat_cats:
                    out["can_have_stat"] = possible_stat_cats

            herb_details = []
            if "herb" in tags:
                tags.remove("herb")
            
            if f"no_herbs{outcomes_convert[key]}" in tags:
                tags.remove(f"no_herbs{outcomes_convert[key]}")
            else:
                if f"many_herbs{outcomes_convert[key]}" in tags:
                    tags.remove(f"many_herbs{outcomes_convert[key]}")
                    herb_details.append("many_herbs")
                elif "random_herbs" in tags:
                    herb_details.append("random_herbs")
                
                for _tag in tags.copy():
                    if _tag in HERBS:
                        herb_details.append(_tag)
                        
                if herb_details:
                    out["herbs"] = herb_details
                
            # PREY PREY PREY
            prey_types = ("small_prey", "medium_prey", "large_prey", "huge_prey")
            prey_details = []
            for pre in prey_types:
                if pre in tags or pre + str(prey_number_translation[key]) in tags:
                    patrol_has_prey = True
                    if pre + str(prey_number_translation[key]) in tags:
                        tags.remove(pre + str(prey_number_translation[key]))
                    prey_details.append(pre.split("_")[0])
                    
            if prey_details:
                out["prey"] = prey_details
            
            
            # Relationships
            relation_details = []
            cats_to_adjust = []
            for x in cats_to:
                if x == "r_c_or_s_c":
                    x = "s_c" if (out.get("stat_trait") or out.get("stat_skill")) else "r_c"
                cats_to_adjust.append(x)
                
            cats_from_adjust = []
            for x in cats_from:
                if x == "r_c_or_s_c":
                    x = "s_c" if (out.get("stat_trait") or out.get("stat_skill")) else "r_c"
                cats_from_adjust.append(x)
            
            if "no_change_success" not in tags:
                for amount, values in relationship_amounts.items():
                    relation_details.append({
                        "cats_to": cats_to_adjust,
                        "cats_from": cats_from_adjust,
                        "mutual": rel_mutual,
                        "values": values,
                        "amount": amount,
                    })
                    
            if relation_details:
                out["relationships"] = relation_details
                
             # new cats
            new_cat_details = []
            litter_details = []
            is_kit = False
            if new_cat_attributes and f"no_new_cat{outcomes_convert[key]}" not in tags:
                backgrounds = ("kittypet", "clancat", "rogue", "loner")
                for x in new_cat_attributes:
                    if x in backgrounds:
                        new_cat_details.append(x)
                        continue
                    
                    if x == "medcat":
                        new_cat_details.append("status:medicine cat")
                        continue
                    
                    if x == "warrior":
                        new_cat_details.append("status:warrior")
                        continue
                    
                    if x == "dead":
                        new_cat_details.append("dead")
                        continue
                    
                    if x == "outside":
                        new_cat_details.append("meeting")
                        continue
                    
                    if x == "kitten":
                        new_cat_details.append("status:kitten")
                        possible_backstories = []
                        for back in BACKSTORIES["backstories"]:
                            if back in new_cat_attributes:
                                possible_backstories.append(back)
                        
                        if possible_backstories:
                            new_cat_details.append("backstory:" + ",".join(possible_backstories))
                        
                        continue
                    
                    if x == "tom":
                        new_cat_details.append("male")
                        continue
                    
                    if x == "female":
                        new_cat_details.append("female")
                        continue
                    
                    if x == "elder":
                        new_cat_details.extend(["status:elder", "age:senior"])
                        continue
                    
                    if x == "apprentice":
                        new_cat_details.append("status:apprentice")
                    
                    if x == f"litter{outcomes_convert[key]}" and not is_kit:
                        litter_details.extend(["litter", "parent:0"])
                        if "litternewborn" in new_cat_attributes:
                            litter_details.append("status:newborn")
                        else:
                            litter_details.append("status:kitten")
                        
                        possible_backstories = []
                        for back in BACKSTORIES["backstories"]:
                            if back in new_cat_attributes:
                                possible_backstories.append(back)
                        
                        if possible_backstories:
                            litter_details.append("backstory:" + ",".join(possible_backstories))
                                
                        continue
                
                    if x in ("injury", "new", "cat") or x in BACKSTORIES["backstories"]:
                        continue
                
                    print(f"unknown new_cat tags: {x}")
            
            if new_cat_details:
                out["new_cat"] = [
                    new_cat_details
                ]
                
                if litter_details:
                    out["new_cat"].append(litter_details)
                    
                relationship_block = {
                    "cats_from": ["n_c:0"],
                    "cats_to": ["patrol"],
                    "values": [
                        "platonic",
                        "trust",
                        "comfort"
                    ],
                    "amount": 10
                }
                if "relationships" in out:
                    out["relationships"].append(relationship_block)
                    print("APPEND APPEND  " + p_["patrol_id"])
                else:
                    out["relationships"] = [relationship_block]
                    
                out["outsider_rep"] = 1
                    
            if new_cat_injury:
                out["injury"] = [{
                    "cats": ["n_c:0"],
                    "injuries": [new_cat_injury],
                }]
            
                
            if "other_clan" in tags and "otherclan_nochangesuccess" not in tags:
                n = 2
                if f"success_reldown{outcomes_convert[key]}" in tags:
                    tags.remove(f"success_reldown{outcomes_convert[key]}")
                    n = -1
                out["other_clan_rep"] = n
            
                
            outcomes.append(out)
        
        new_patrol["success_outcomes"] = outcomes
        #-------------------------------------------------------------------------------------------

        # Remove
        prey_types = ("small_prey", "medium_prey", "large_prey", "huge_prey")
        for pre in prey_types:
            if pre in tags:
                tags.remove(pre)
                
        if "no_change_success" in tags:
            tags.remove("no_change_success")
        if "otherclan_nochangesuccess" in tags:
            tags.remove("otherclan_nochangesuccess")
        for x in tags:
            if "no_new_cat" in x:
                tags.remove(x)
                
        if "many_herbs" in tags:
            tags.remove("many_herbs")
        if "random_herbs" in tags:
            tags.remove("random_herbs")
        for x in HERBS:
            if x in tags:
                tags.remove(x)
        
        # --------------------------------------------------------------------------------------------
        # FAIL OUTCOMES
        outcomes = []
        body = True
        if "no_body" in tags:
            tags.remove("no_body")
            body = False
        
        all_lives = False
        if "all_lives" in tags:
            tags.remove("all_lives")
            all_lives = True
            
        some_lives = False
        if "some_lives" in tags:
            tags.remove("some_lives")
            some_lives = True
        
        possible_injuries = []
        condition_lists = (
                "battle_injury", "minor_injury", "blunt_force_injury", "hot_injury", "cold_injury", "big_bite_injury", "small_bite_injury", "beak_bite", "rat_bite"
            )
        for x in condition_lists:
            if x in tags:
                tags.remove(x)
                possible_injuries.append(x)
        for x in INJURIES:
            if x in tags:
                tags.remove(x)
                possible_injuries.append(x)
        for x in ILLNESSES:
            if x in tags:
                tags.remove(x)
                possible_injuries.append(x)
        for x in PERMANENT:
            if x in tags:
                tags.remove(x)
                possible_injuries.append(x)
        
        if "non_lethal" in tags:
            tags.remove("non_lethal")
            possible_injuries.append("non_lethal")
        
        possible_scars = []
        if "scar" in tags:
            tags.remove("scar")
        for x in ["ONE", "TWO", "THREE", "TAILSCAR", "SNOUT", "CHEEK", "SIDE", "THROAT", "TAILBASE", "BELLY",
                "LEGBITE", "NECKBITE", "FACE", "MANLEG", "BRIGHTHEART", "MANTAIL", "BRIDGE", "RIGHTBLIND", "LEFTBLIND",
                "BOTHBLIND", "BEAKCHEEK", "BEAKLOWER", "CATBITE", "RATBITE", "QUILLCHUNK", "QUILLSCRATCH",
                "LEFTEAR", "RIGHTEAR", "NOTAIL", "HALFTAIL", "NOPAW", "NOLEFTEAR", "NORIGHTEAR", "NOEAR",
                "SNAKE", "TOETRAP", "BURNPAWS", "BURNTAIL", "BURNBELLY", "BURNRUMP", "FROSTFACE", "FROSTTAIL", "FROSTMITT",
                "FROSTSOCK"]:
            if x in tags:
                possible_scars.append(x)
                tags.remove(x)
                
        for key, text in p_["fail_text"].items():
            # Gonna skip the leader death outcomes. Sorry not sorry
            if key == "leader_death":
                continue
            
            no_fail_prey = False
            if tags.intersection(set(["no_fail_prey", "poison_clan", "death", "disaster", "multi_deaths", "no_body",
                           "cruel_season", "gone", "multi_gone", "disaster_gone"])) or body == False :
                no_fail_prey = True
            
            out = {
                "text": text,
                "exp": 0,
                "weight": 20
            }
            
            if "rare" in key:
                out["weight"] = 5
            
            injury = False
            death = False
            if "injury" in key:
                out["weight"] = 10
                injury = True
            if "death" in key:
                out["weight"] = 10
                death = True
            
            if "stat" in key and (p_.get("fail_trait") or p_.get("fail_skills")):
                if p_.get("fail_trait"):
                    out["stat_trait"] = p_.get("fail_trait")
                    
                if p_.get("fail_skills"):
                    out["stat_skill"] = p_.get("fail_skills")
                    
                if possible_stat_cats:
                    out["can_have_stat"] = possible_stat_cats
            
            if death:
                dead_cats = []
                if out.get("stat_trait") or out.get("stat_skill"):
                    dead_cats.append("s_c")
                else:
                    dead_cats.append("r_c")
                
                if "gone" in tags or "disaster_gone" in tags or "multi_gone" in tags:
                    if "disaster_gone" in tags:
                        dead_cats = ["patrol"]
                    elif "multi_gone" in tags:
                        dead_cats = ["multi"]
                    
                    out["lost_cats"] = dead_cats
                else:
                    if "disaster" in tags:
                        dead_cats = ["patrol"]
                    elif "multi_deaths" in tags:
                        dead_cats = ["multi"]
                
                    if all_lives:
                        dead_cats.append("all_lives")
                    elif some_lives:
                        dead_cats.append("some_lives")
                        
                    out["dead_cats"] = dead_cats
                
            if injury:
                if not possible_injuries:
                    print(f"oh no injuries: {path}, {p_['patrol_id']}")
                    continue
                
                injured_details = [
                    {
                        "cats": [],
                        "injuries": possible_injuries,
                        "scars": possible_scars
                    }
                ]
                
                if "poison_clan" in tags:
                    injured_details[0]["cats"].append("some_clan")
                elif "injure_all" in tags:
                    injured_details[0]["cats"].append("patrol")
                elif out.get("stat_trait") or out.get("stat_skill"):
                    injured_details[0]["cats"].append("s_c")
                elif new_patrol["min_max_status"].get("apprentice", [0, 0])[0] >= 1 or \
                        new_patrol["min_max_status"].get("medicine cat apprentice", [0, 0])[0] >= 1:
                    injured_details[0]["cats"].append("app1")
                else:
                    injured_details[0]["cats"].append("r_c")
                
                out["injury"] = injured_details
            
            if out.get("dead_cats") or out.get("injury"):
                if p_.get("history_text"):
                    out["history_text"] = p_["history_text"]
                else:
                    print(f"death or injury without text: {p_['patrol_id']}, {path}")
            
            new_cat_details = []
            if new_cat_attributes and new_cat_meeting:
                backgrounds = ("kittypet", "clancat", "rogue", "loner")
                new_cat_details.append("meeting")
                for x in new_cat_attributes:
                    
                    if x in backgrounds:
                        new_cat_details.append(x)
                        continue
                            
                    if x == "kitten":
                        new_cat_details.append("status:kitten")                        
                        continue
                    
                    if x == "tom":
                        new_cat_details.append("male")
                        continue
                    
                    if x == "female":
                        new_cat_details.append("female")
                        continue
                    
                    if x == "elder":
                        new_cat_details.extend(["age:senior"])
                        
            if new_cat_attributes:
                if "no_change_fail_rep" in tags:
                    out["outsider_rep"] = 0
                else:
                    out["outsider_rep"] = -1
                        
            if new_cat_details:
                out["new_cat"] = [
                    new_cat_details
                ]
            
            
            relation_details = []
            cats_to_adjust = []
            for x in cats_to:
                if x == "r_c_or_s_c":
                    x = "s_c" if (out.get("stat_trait") or out.get("stat_skill")) else "r_c"
                cats_to_adjust.append(x)
                
            cats_from_adjust = []
            for x in cats_from:
                if x == "r_c_or_s_c":
                    x = "s_c" if (out.get("stat_trait") or out.get("stat_skill")) else "r_c"
                cats_from_adjust.append(x)
            
            if "no_change_fail" not in tags:
                for amount, values in relationship_amounts.items():
                    relation_details.append({
                        "cats_to": cats_to_adjust,
                        "cats_from": cats_from_adjust,
                        "mutual": rel_mutual,
                        "values": values,
                        "amount": -amount,
                    })
                    
            if relation_details:
                out["relationships"] = relation_details
            
            if not no_fail_prey and patrol_has_prey:
                out["prey"] = ["very_small"]
                
            if "other_clan" in tags and "otherclan_nochangefail" not in tags:
                out["other_clan_rep"] = -1
            
                
            outcomes.append(out)
        
        new_patrol["fail_outcomes"] = outcomes
        
                
                
        if "multi_deaths" in tags:
            tags.remove("multi_deaths")
        if "gone" in tags:
            tags.remove("gone")
        if "disaster_gone" in tags:
            tags.remove("disaster_gone")
            tags.add("disaster")
        if "multi_gone" in tags:
            tags.remove("multi_gone")
        if "injury" in tags:
            tags.remove("injury")
        if "death" in tags:
            tags.remove("death")
        if "poison_clan" in tags:
            tags.remove("poison_clan")
        if "no_fail_prey" in tags:
            tags.remove("no_fail_prey")
        if "injure_all" in tags:
            tags.remove("injure_all")
        if "no_change_fail" in tags:
            tags.remove("no_change_fail")
        if "otherclan_nochangefail" in tags:
            tags.remove("otherclan_nochangefail")
        if "no_change_fail_rep" in tags:
            tags.remove("no_change_fail_rep")
            
        if p_.get("antagonize_fail_text"):
            new_patrol["antag_fail_outcomes"] = [
                {
                    "text": p_.get("antagonize_fail_text"),
                    "exp": 0,
                    "weight": 20,
                }
            ]
            
            if "other_clan" in tags:
                new_patrol["antag_fail_outcomes"][0]["other_clan_rep"] = -1
            elif new_cat_attributes:
                new_patrol["antag_fail_outcomes"][0]["outsider_rep"] = -1
        
        if p_.get("antagonize_text"):
            new_patrol["antag_success_outcomes"] = [
                {
                    "text": p_.get("antagonize_text"),
                    "exp": p_["exp"],
                    "weight": 20,
                }
            ]
            
            if "other_clan" in tags:
                if "otherclan_antag_nochangefail" not in tags:
                    new_patrol["antag_success_outcomes"][0]["other_clan_rep"] = -2
            elif new_cat_attributes:
                new_patrol["antag_success_outcomes"][0]["outsider_rep"] = -2
            
        
        if "otherclan_antag_nochangefail" in tags:
            tags.remove("otherclan_antag_nochangefail")
        
        
        new_patrol["tags"] = list(tags)
        
        ## Constraints:
        skill_constraints = []
        relation_constraints = []
        for ty, dets in p_.get("constraints", {}).items():
            if ty == "skill":
                skill_constraints.extend(dets)
            if ty == "relationship":
                relation_constraints.extend(dets)
        
        if skill_constraints:
            new_patrol["pl_skill_constraint"] = skill_constraints
        else:
            new_patrol.pop("pl_skill_constraint")
        
        if relation_constraints:
            new_patrol["relationship_constraint"] = relation_constraints
        else:
            new_patrol.pop("relationship_constraint")
        
         
        all_new_patrols.append(new_patrol)
    
    with open(path, "w") as write_file:
        write = ujson.dumps(all_new_patrols, indent = 4)
        write = write.replace("\/", "/")
        write_file.write(write)


root_dir = "C:/Users/maiak/Documents/GitHub/clangen/clangen/resources/dicts/patrols"
file_set = set()

for dir_, _, files in os.walk(root_dir):
    for file_name in files:
        rel_dir = os.path.relpath(dir_, root_dir)
        #print(rel_dir)
        rel_file = os.path.join(rel_dir, file_name)
        #print(rel_file)
        if os.path.splitext(rel_file)[-1].lower() == ".json":
            file_set.add(rel_file)
            

for pa in file_set:
    try:
        reformat_patrol(pa)
    except:
        print(pa)
        raise
