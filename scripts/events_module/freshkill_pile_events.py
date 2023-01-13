from scripts.events_module.generate_events import GenerateEvents

class Freshkill_events():
	"""All events with a connection to freshkill pile or the nutrition of cats."""

	def __init__(self) -> None:
		self.generate_events = GenerateEvents()


	def handle_low_nutrient(self, cat):
		"""
		Handles gaining conditions or death for cats with low nutrient.
		Game-mode: 'expanded' & 'cruel season'
		"""
		# adding condition if the nutrition is below 50%

		# death


	def handle_amount_freshkill_pile(self, freshkill_pile):
		"""
		Handles events, which are related to the freshkill pile.
		Game-mode: 'expanded' & 'cruel season'
		"""
