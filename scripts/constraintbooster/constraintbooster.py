from copy import copy
from typing import Dict, List, Tuple


class ConstraintBooster:
    _constraints = {"basic": set(), "nested": set(), "split": {}, "complex": {}}

    def add_basic_constraint(self, name: str):
        """A basic constraint awards 1 constraint point if its name is in the
        highest-level of the passed object at analysis time.
        :param str name: The name of the constraint group"""
        self._constraints["basic"].add(name)

    def add_nested_constraint(self, name: str):
        """
        Awards 1 point per value nested within "name" on the passed object at analysis time.
        :param name: The name of the parent group to count from
        :return: None
        """
        self._constraints["nested"].add(name)

    def add_split_constraint(
        self,
        name: str,
        separator: str,
        field: int,
        point_array: Dict[str, int],
        blacklist: list = None,
        blacklist_value: int = 0,
    ):
        """
        Awards points corresponding to the values in lookup point_array for the field requested
        :param name: The name of the group to check within
        :param separator: The string to split the nested input by
        :param field: Which of the split pieces to score
        :param point_array: A lookup table of the scores to award
        :param blacklist: Values to not split, default None
        :param blacklist_value: Value to award per blacklisted item, default 0
        :return: None
        """
        if name in self._constraints["split"].keys():
            raise Exception("Key already exists in constraints!")
        self._constraints["split"][name] = {
            "separator": separator,
            "field": field,
            "point_array": point_array,
            "blacklist": blacklist,
            "blacklist_value": blacklist_value,
        }

    def add_complex_constraint(self, name: str):
        pass

    def _get_constraint_points(self, options: list):
        """
        Get a list of constraint points corresponding to the degree of constraint of the input options
        :param options: The options to compare
        :return: A list of integers corresponding to the degree of constraint
        """
        all_constraint_points = []
        for option in options:
            constraint_points = 0

            for constraint in self._constraints["basic"]:
                if constraint in option:
                    constraint_points += 1

            for constraint in self._constraints["nested"]:
                if constraint in option:
                    constraint_points += len(option.constraint.values())

            for key, constraint_block in self._constraints["split"]:
                if key in option:
                    for record in option.key:
                        if option.key in constraint_block.blacklist:
                            constraint_points += constraint_block.blacklist_value
                            continue
                        split = record.split(constraint_block.separator)
                        # if the selected field's value is found in the point_array,
                        # award that many points. otherwise, skip.
                        if (
                            split[constraint_block.field]
                            in constraint_block.point_array
                        ):
                            constraint_points += constraint_block.point_array[
                                split[constraint_block.field]
                            ]

            all_constraint_points.append(constraint_points)

        return all_constraint_points

    def _make_groups(
        self, options: List, all_constraint_points: List[int]
    ) -> Tuple[List[int], List[int], List[int]]:

        sorted_weights = copy(all_constraint_points)
        sorted_weights.sort(reverse=True)
        sorted_weights = list(dict.fromkeys(sorted_weights))
        # count = [all_constraint_points.count(x) for x in sorted_weights]

        buckets = self.split(options, 3)

    @staticmethod
    def split(a, n):  # abducted from StackOverflow
        k, m = divmod(len(a), n)
        return (a[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)] for i in range(n))
