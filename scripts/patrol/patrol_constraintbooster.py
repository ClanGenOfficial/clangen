from scripts.constraintbooster import ConstraintBooster

patrol_constraint_booster = ConstraintBooster()
patrol_constraint_booster.add_simple_constraint("biome", ["any"])
patrol_constraint_booster.add_simple_constraint("camp", ["any"])
patrol_constraint_booster.add_simple_constraint("season", ["any"])
patrol_constraint_booster.add_nested_constraint("tags")
patrol_constraint_booster.add_nested_constraint("min_max_status")


point_array = {
    "5": 1,
    "10": 1,
    "15": 1,
    "20": 2,
    "25": 2,
    "30": 3,
    "35": 3,
    "40": 4,
    "45": 4,
    "50": 5,
    "55": 5,
    "60": 6,
    "65": 6,
    "70": 7,
    "75": 7,
    "80": 8,
    "85": 8,
    "90": 9,
    "95": 9,
}
patrol_constraint_booster.add_split_constraint(
    "relationship_constraint",
    "_",
    field=1,
    point_array=point_array,
    blacklist={
        "siblings": 5,
        "mates": 5,
        "mates_with_pl": 5,
        "parent/child": 5,
        "child/parent": 5,
    },
)
