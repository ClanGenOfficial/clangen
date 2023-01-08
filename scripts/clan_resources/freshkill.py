from scripts.utility import get_queens
from scripts.cat.cats import Cat

PREY_REQUIREMENT = {
	"leader": 3,
	"deputy": 3,
	"medicine cat": 2,
	"medicine cat apprentice": 1.5,
	"warrior": 3,
	"apprentice": 1.5,
	"elder": 1.5,
	"queen": 4,
	"kitten": 0.5,
}

CONDITION_INCREASE = 0.5

FEEDING_ORDER = [
	"kitten",
	"queen",
	"elder",
	"medicine cat",
	"medicine cat apprentice",
	"apprentice",
	"warrior",
	"deputy",
	"leader"
]


class Nutrition():
	"""All the information about nutrition from one cat."""

	def __init__(self) -> None:
		"""Initialize the class."""
		self.max_score = 0
		self.current_score = 0
		self.percentage = 0


class Freshkill_Pile():
	"""Handle everything related to the freshkill pile of the clan."""

	def __init__(self, living_cats) -> None:
		"""Initialize the class."""
		# the pile could be handled as a list but this makes it more readable
		self.pile = {
			"expires_in_4": 0,
			"expires_in_3": 0,
			"expires_in_2": 0,
			"expires_in_1": 0,
		}
		self.total_amount = 0

		# the cat info stores the values of the nutrition scores
		# it will be checked and updated every time the feeding is happening
		# with this only living cats are in the list

		self.nutrition_info = {}
		for cat in living_cats:
			self.add_cat_to_nutrition(cat)

	def add_cat_to_nutrition(self, cat):
		"""Add a cat to the nutrition info"""
		nutrition = Nutrition()
		factor = 3
		if str(cat.status) in ["kitten", "elder"]:
			factor = 2

		max_score = PREY_REQUIREMENT[str(cat.status)] * factor
		nutrition.max_score = max_score
		nutrition.current_score = max_score
		nutrition.percentage = 100

		self.nutrition_info[cat.id] = nutrition

	def add_freshkill(self, amount):
		"""Add new fresh kill to the pile."""
		self.pile["expires_in_4"] += amount

	def time_skip(self, living_cats):
		"""Handle the time skip for the freshkill pile."""
		previous_amount = 0
		# update the freshkill pile
		for key, value in self.pile.items():
			self.pile[key] = previous_amount
			previous_amount = value
		self.total_amount = sum(self.pile.values())

		self.feed_cats(living_cats)
		
	def feed_cats(self, living_cats):
		"""Handles to feed all living cats."""
		self.update_nutrition(living_cats)

		relevant_group = []
		queens = get_queens(living_cats, Cat.all_cats)
		relevant_queens = []
		for queen in queens:
			kits = queen.get_children()
			young_kits = [kit for kit in kits if kit.moons < 3]
			if len(young_kits) > 0:
				relevant_queens.append(queen)

		for status_ in FEEDING_ORDER:
			if status_ == "queen":
				relevant_group = relevant_queens
			elif status_ == "kitten":
				relevant_group = [cat for cat in living_cats if str(cat.status) == status_ and cat.moons > 3]
			else:
				relevant_group = [cat for cat in living_cats if str(cat.status) == status_]
				# remove all cats, which are also queens
				relevant_group = [cat for cat in relevant_group if cat not in relevant_queens]
			
			self.feed_group(relevant_group, status_)

	def update_nutrition(self, living_cats):
		"""Update the nutrition information."""
		old_nutrition_info = self.nutrition_info
		self.nutrition_info = {}

		# TODO: check nutrition information from dead cats are removed
		for cat in living_cats:
			# update the nutrition_info
			if cat.id in old_nutrition_info:
				self.nutrition_info[cat.id] = old_nutrition_info[cat.id] 
				# check if the max_amount is correct, otherwise update
				if cat.moons == 6:
					self.nutrition_info[cat.id].max_amount = PREY_REQUIREMENT[str(cat.status)] * 3
				# TODO: maybe find a better way to handle this
				if cat.moons >= 120 and str(cat.status) == "elder":
					self.nutrition_info[cat.id].max_amount = PREY_REQUIREMENT[str(cat.status)] * 2
			else:
				self.add_cat_to_nutrition(cat)

	def feed_group(self, group, status_):
		"""Handle the feeding of a specific group of cats."""
		# check if there is enough prey for this group
		# TODO: CARE! Sick cats are not included in the calculation
		needed_prey = len(group) * PREY_REQUIREMENT[status_]
		enough_prey = needed_prey <= self.total_amount

		if not enough_prey:
			self.handle_not_enough_food(group, status_)
			return

		for cat in group:
			needed_prey = PREY_REQUIREMENT[status_]
			if cat.is_ill() or cat.is_injured():
				needed_prey += CONDITION_INCREASE
			self.feed_cat(cat, needed_prey)

	def handle_not_enough_food(self, group, status_):
		"""Handle the situation where there is not enough food for this group."""
		# TODO: sort and check which cats of this group can be feed and which can not
		# 		this should be depend on the tactic, which is chosen

	def feed_cat(self, cat, amount):
		"""Handle the feeding process."""
		remaining_amount = amount
		order = ["expires_in_1", "expires_in_2", "expires_in_3", "expires_in_4"]
		for key in order:
			remaining_amount = self.take_from_pile(key, remaining_amount)

		if remaining_amount > 0:
			self.nutrition_info[cat.id].current_score -= remaining_amount

			max_score = self.nutrition_info[cat.id].max_score
			percentage = self.nutrition_info[cat.id].current_score / max_score
			self.nutrition_info[cat.id].percentage = percentage

	def take_from_pile(self, pile_group, needed_amount):
		"""Take the amount from the pile group. Returns the rest of the original needed amount."""
		if needed_amount == 0:
			return needed_amount

		remaining_amount = needed_amount
		if self.pile[pile_group] >= needed_amount:
			self.pile[pile_group] -= needed_amount
			self.total_amount -= needed_amount
			remaining_amount = 0
		elif self.pile[pile_group] > 0:
			remaining_amount = needed_amount - self.pile[pile_group]
			self.total_amount -= self.pile[pile_group]
			self.pile[pile_group] = 0

		return remaining_amount

	def load_freshkill_pile(self):
		"""Load the freshkill pile."""

	def save_freshkill_pile(self):
		"""Save the freshkill pile."""

	def load_nutrition_info(self):
		"""Load the nutritional information."""

	def save_nutrition_info(self):
		"""Save the nutritional information."""