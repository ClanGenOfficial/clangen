from itertools import combinations

import ujson

"""
This tool is meant to help us check if every possible facet combo is covered! Simply run this script. 
If any holes are detected, a warning will be printed. 
Normal traits and kit traits are checked and warned for separately. 
When the script is done running, it will print a "Finished!" message.
"""


with open(
    "../resources/dicts/traits/trait_ranges.json", "r", encoding="utf-8"
) as read_file:
    FACET_RANGES = ujson.loads(read_file.read())

# range of 0-16, we repeat each number 4 times since there are 4 facets that can be from 0-16
facet_range = list(range(0, 17)) * 4


def check_validity(range_dict, combination) -> bool:
    for trait in range_dict:
        if combination[0] not in range(
            trait["lawfulness"][0], trait["lawfulness"][1] + 1
        ):
            continue
        if combination[1] not in range(
            trait["sociability"][0], trait["sociability"][1] + 1
        ):
            continue
        if combination[2] not in range(
            trait["aggression"][0], trait["aggression"][1] + 1
        ):
            continue
        if combination[3] not in range(
            trait["stability"][0], trait["stability"][1] + 1
        ):
            continue

        return True

    return False


# now we check every possible combo of those numbers
for combo in combinations(facet_range, 4):
    # check normal traits
    fit_trait = check_validity(FACET_RANGES["normal_traits"].values(), combo)

    if not fit_trait:
        print(f"WARNING: {combo} was not valid for any normal trait")

    # check kit traits
    fit_trait = check_validity(FACET_RANGES["kit_traits"].values(), combo)
    if not fit_trait:
        print(f"WARNING: {combo} was not valid for any kit trait")

print("Finished. If no warning printed, then all facet combos are valid.")
