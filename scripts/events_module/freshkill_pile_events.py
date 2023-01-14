from scripts.events_module.generate_events import GenerateEvents

class Freshkill_Events():
    """All events with a connection to freshkill pile or the nutrition of cats."""

    def __init__(self) -> None:
        self.generate_events = GenerateEvents()


    def handle_low_nutrient(self, cat, nutrition_info):
        """
        Handles gaining conditions or death for cats with low nutrient.
        Game-mode: 'expanded' & 'cruel season'
        """
        if cat.ID not in nutrition_info.keys():
            print(f"WARNING: Could not find cat with ID {cat.ID}({cat.name}) in the nutrition information.")
            return

        nutr = nutrition_info[cat.ID]

        if nutr.percentage > 50:
            # nothing is happening if the percentage is above 50
            return
        elif nutr.percentage <= 0:
            # if percentage is 0 or lower, the cat will die
            print("TODO - dead")
        elif nutr.percentage <= 50:
            # if percentage is 50 or lower, the cat will gain illnesses
            # the elif statement above will prevent, that a dead cat will get an illness
            print("TODO - injury")


    def handle_amount_freshkill_pile(self, freshkill_pile, living_cats):
        """
        Handles events (eg. a fox is attacking the camp), which are related to the freshkill pile.
        Game-mode: 'expanded' & 'cruel season'
        """
        print("TODO - events if the amount of prey is too much")
