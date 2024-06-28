import random
from typing import Dict, List, Any, Union

from scripts.constraintbooster.constrainttypes import (
    SimpleConstraint,
    NestedConstraint,
    SplitConstraint,
)


class ConstraintBooster:
    def __init__(self, proc_chance=5, number_of_groups=3, min_group_size=2):
        """
        Create a constraint booster.
        :param proc_chance: The chance each group has of being selected (1/x). Default 5.
        :param number_of_groups: Number of groups to make, default 3
        :param min_group_size: Minimum number of items permitted per group, default 2
        """
        self._constraints = []
        self.proc_chance = proc_chance
        self.number_of_groups = number_of_groups
        self.min_group_size = min_group_size

    def add_simple_constraint(
        self, name: str, blacklist: Union[List[str], None] = None
    ):
        """A basic constraint awards 1 constraint point if its name is in the
        highest-level of the passed object at analysis time
        :param str name: The name of the constraint group
        :param blacklist: Values to exclude
        """
        self._constraints.append(SimpleConstraint(name, blacklist))

    def add_nested_constraint(
        self, name: str, blacklist: Union[List[str], None] = None
    ):
        """
        Awards 1 point per value nested within "name" on the passed object at analysis time.
        :param name: The name of the parent group to count from
        :param blacklist: Any values to ignore within the group
        :return: None
        """
        self._constraints.append(NestedConstraint(name, blacklist))

    def add_split_constraint(
        self,
        name: str,
        separator: str,
        field: int,
        point_array: Dict[str, int],
        blacklist: Union[Dict[str, int], None] = None,
    ):
        """
        Awards points corresponding to the values in point_array for the field requested
        :param name: The name of the group to check within
        :param separator: The string to split the nested input by
        :param field: Which of the split pieces to score
        :param point_array: A lookup table of the scores to award
        :param blacklist: Dictionary of keys to not split & the desired constraint value for them, default None
        """
        self._constraints.append(
            SplitConstraint(name, separator, field, point_array, blacklist)
        )

    def get_choice(self, options: List, debug_force_flat=False) -> Any:
        """
        Use to get a constraint-weighted choice from the provided options
        :param List options: The values to use
        :param debug_force_flat: Debug value, used to force failure on the random rolls. For testing only!
        :return: One of the objects from the options list
        """
        option_dict = self._get_constraint_points(options)
        groups = self._make_groups(option_dict)

        selected_group = None
        if not debug_force_flat:
            for group in groups:
                if random.randint(1, self.proc_chance):
                    selected_group = group
                    break
        if selected_group is None:
            # if nothing succeeded, we return to a flat chance
            selected_group = options

        if not isinstance(selected_group, list):
            # there is only one value, return it as the selection
            return selected_group

        final_choice = random.choices(
            selected_group,
            weights=[x.weight for x in selected_group],
        )[0]

        return final_choice

    def _get_constraint_points(self, options: List) -> Dict[int, Any]:
        """
        Get a list of constraint points corresponding to the degree of constraint of the input options
        :param options: The options to compare
        :return: A dictionary mapping constraint level to the input options
        """
        all_constraint_points = []
        for option in options:
            constraint_points = 0

            for constraint in self._constraints:
                constraint_points += constraint.compute(option)

            all_constraint_points.append(constraint_points)

        return zip(all_constraint_points, options)

    def _make_groups(self, options: Dict[int, Any]) -> List[List]:
        """
        Create the buckets of options to prioritise
        :param options: The dictionary of options to split
        :return: the input options, split into 3 buckets of mostly equal size
        """
        sorted_by_constraint = [
            val for (_, val) in sorted(options, key=lambda x: x[0], reverse=False)
        ]

        if len(sorted_by_constraint) < self.number_of_groups * self.min_group_size:
            return sorted_by_constraint

        # we reverse afterward to ensure that the largest group is always the end group
        # in case we have an unevenly split offering
        groups = self.split(sorted_by_constraint, self.number_of_groups)
        groups.reverse()
        return groups

    @staticmethod
    def split(a, n):  # abducted from StackOverflow
        """Splits `a` evenly into `n` groups"""
        k, m = divmod(len(a), n)
        return [a[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)] for i in range(n)]
