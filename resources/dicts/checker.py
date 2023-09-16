# import os
# import ujson

# their_trait_list = ['troublesome', 'fierce', 'bold', 'daring', 'confident', 'adventurous', 'arrogant', 'competitive', 'rebellious', 'bloodthirsty', 'cold', 'strict', 'vengeful', 'grumpy', 'charismatic', 'sneaky', 'cunning', 'arrogant', 'righteous', 'ambitious', 'strict', 'competitive', 'responsible', 'lonesome', 'righteous', 'calm', 'gloomy', 'wise', 'thoughtful', 'nervous', 'insecure', 'lonesome', 'troublesome', 'childish', 'playful', 'strange', 'loyal', 'responsible', 'wise', 'faithful', 'compassionate', 'faithful', 'loving', 'oblivious', 'sincere', 'childish', 'confident', 'bold', 'shameless', 'strange', 'oblivious', 'flamboyant', 'troublesome', 'bloodthirsty', 'sneaky', 'rebellious']
# you_trait_list = ['you_troublesome', 'you_fierce', 'you_bold', 'you_daring', 'you_confident', 'you_adventurous', 'you_arrogant', 'you_competitive', 'you_rebellious', 'you_bloodthirsty', 'you_cold', 'you_strict', 'you_vengeful', 'you_grumpy', 'you_charismatic', 'you_sneaky', 'you_cunning', 'you_arrogant', 'you_righteous', 'you_ambitious', 'you_strict', 'you_competitive', 'you_responsible', 'you_lonesome', 'you_righteous', 'you_calm', 'you_gloomy', 'you_wise', 'you_thoughtful', 'you_nervous', 'you_insecure', 'you_lonesome', 'you_troublesome', 'you_childish', 'you_playful', 'you_strange', 'you_loyal', 'you_responsible', 'you_wise', 'you_faithful', 'you_compassionate', 'you_faithful', 'you_loving', 'you_oblivious', 'you_sincere', 'you_childish', 'you_confident', 'you_bold', 'you_shameless', 'you_strange', 'you_oblivious', 'you_flamboyant', 'you_troublesome', 'you_bloodthirsty', 'you_sneaky', 'you_rebellious']
# you_backstory_list = [
#     "you_clanfounder",
#     "you_clanborn",
#     "you_outsiderroots",
#     "you_half-Clan",
#     "you_formerlyloner",
#     "you_formerlyrogue",
#     "you_formerlykittypet",
#     "you_formerlyoutsider",
#     "you_originallyanotherclan",
#     "you_orphaned",
#     "you_abandoned"
# ]
# they_backstory_list = ["they_clanfounder",
#     "they_clanborn",
#     "they_outsiderroots",
#     "they_half-Clan",
#     "they_formerlyloner",
#     "they_formerlyrogue",
#     "they_formerlykittypet",
#     "they_formerlyoutsider",
#     "they_originallyanotherclan",
#     "they_orphaned",
#     "they_abandoned"
# ]
# skill_list = ['teacher', 'hunter', 'fighter', 'runner', 'climber', 'swimmer', 'speaker', 'mediator', 'clever', 'insightful', 'sense', 'kit', 'story', 'lore', 'camp', 'healer', 'star', 'omen', 'dream', 'clairvoyant', 'prophet', 'ghost', 'explorer', 'tracker', 'artistan', 'guardian', 'tunneler', 'navigator', 'song', 'grace', 'clean', 'innovator', 'comforter', 'matchmaker', 'thinker', 'cooperative', 'scholar', 'time', 'treasure', 'fisher', 'language', 'sleeper']
# you_skill_list = ['you_teacher', 'you_hunter', 'you_fighter', 'you_runner', 'you_climber', 'you_swimmer', 'you_speaker', 'you_mediator', 'you_clever', 'you_insightful', 'you_sense', 'you_kit', 'you_story', 'you_lore', 'you_camp', 'you_healer', 'you_star', 'you_omen', 'you_dream', 'you_clairvoyant', 'you_prophet', 'you_ghost', 'you_explorer', 'you_tracker', 'you_artistan', 'you_guardian', 'you_tunneler', 'you_navigator', 'you_song', 'you_grace', 'you_clean', 'you_innovator', 'you_comforter', 'you_matchmaker', 'you_thinker', 'you_cooperative', 'you_scholar', 'you_time', 'you_treasure', 'you_fisher', 'you_language', 'you_sleeper']
# roles = ["Any", "any", "young elder", "newborn", "kitten", "apprentice", "medicine cat apprentice", "mediator apprentice", "no_kit","queen's apprentice", "warrior", "medicine cat", "mediator", "queen", "deputy", "leader", "elder"]
# cluster_list = ["assertive", "brooding", "cool", "upstanding", "introspective", "neurotic", "silly", "stable", "sweet", "unabashed", "unlawful"]
# you_cluster_list = ["you_assertive", "you_brooding", "you_cool", "you_upstanding", "you_introspective", "you_neurotic", "you_silly", "you_stable", "you_sweet", "you_unabashed", "you_unlawful"]

# def process_json_data(data):
#     list_of_tags = ["has_mate","reject","accept","heartbroken","from_parent","siblings_mate","non-related","murder","war","dead_close","talk_dead","hate","romantic_like","platonic_like","jealousy","dislike","comfort","respect","trust","random_cat","neutral","insult", "flirt", "leafbare", "newleaf", "greenleaf", "leaffall", 'beach', 'forest', 'plains', 'mountainous', 'wetlands', 'desert', "you_ill", "you_injured", "they_ill","you_grieving", "they_injured", "they_grieving","adopted_parent","from_mentor","from_your_apprentice","from_kit","from_mate","from_adopted_kit",
# "from_kit","sibling", "half sibling", "adopted_sibling", "parents_siblings", "cousin", "you_pregnant","they_pregnant"]
#     list_of_tags.extend(cluster_list + you_cluster_list + roles + their_trait_list + you_trait_list + you_backstory_list + they_backstory_list + skill_list + you_skill_list)
#     no_tags = set()
#     for key, value in data.items():
#         l = value[0]
#         for i in range(len(l)):
#             l[i] = l[i].lower()
#         for i in l:
#             if i not in list_of_tags:
#                 no_tags.add(i)
                
#     return no_tags
        

# def read_json_files_in_folder(folder_path):
#     nono_tags = set()
#     for filename in os.listdir(folder_path):
#         if filename.endswith('.json'):
#             with open(os.path.join(folder_path, filename), 'r') as json_file:
#                 try:
#                     data = ujson.load(json_file)
#                     nono_tags.update(process_json_data(data))
#                 except ValueError:
#                     print(f"Error reading JSON data from {filename}")
#     print(nono_tags)
# if __name__ == "__main__":
#     folder_path = "resources\dicts\lifegen_talk"
#     read_json_files_in_folder(folder_path)

import os
import ujson
import json

def handle_duplicate_keys(pairs):
    """
    Rename duplicate keys by appending a number.
    """
    seen = {}
    result = {}
    
    for key, value in pairs:
        while key in seen:
            seen[key] += 1
            key = f"{key}_{seen[key]}"
        else:
            seen[key] = 1

        result[key] = value

    return result

def process_json_file(filepath):
    with open(filepath, 'r') as json_file:
        data_str = json_file.read()

    # Load JSON with duplicate key handling
    data = json.loads(data_str, object_pairs_hook=handle_duplicate_keys)

    with open(filepath, 'w') as json_file:
        ujson.dump(data, json_file, indent=4)

def read_json_files_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            process_json_file(os.path.join(folder_path, filename))

if __name__ == "__main__":
    folder_path = "resources\dicts\lifegen_talk"
    read_json_files_in_folder(folder_path)