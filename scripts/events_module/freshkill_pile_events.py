from scripts.events_module.generate_events import GenerateEvents
from scripts.game_structure.game_essentials import game

class Freshkill_Events():
    """All events with a connection to freshkill pile or the nutrition of cats."""

    def __init__(self) -> None:
        self.generate_events = GenerateEvents()


    def handle_nutrient(self, cat, nutrition_info):
        """
        Handles gaining conditions or death for cats with low nutrient.
        Game-mode: 'expanded' & 'cruel season'
        """
        if cat.ID not in nutrition_info.keys():
            print(f"WARNING: Could not find cat with ID {cat.ID}({cat.name}) in the nutrition information.")
            return

        nutr = nutrition_info[cat.ID]

        # first remove the illnesses of the cat, when nutrition are raised
        if nutr.percentage > 70 and cat.is_ill() and "malnourished" in cat.illnesses:
            print("TODO - heal")
        elif nutr.percentage > 30 and cat.is_ill() and "starving" in cat.illnesses:
            if nutr.percentage < 70:
                print("TODO - gain malnourished")
            else:
                print("TODO - heal")
        elif nutr.percentage <= 0:
            # this statement above will prevent, that a dead cat will get an illness
            # if percentage is 0 or lower, the cat will die
            print("TODO - dead")
            if cat.status == "leader":
                game.clan.leader_lives -= 1
            cat.die()
        elif nutr.percentage <= 70:
            # if percentage is 70 or lower, the cat will gain "malnourished" illness
            # (except kits, they will already get the illness "starving")
            print("TODO - gain malnourished")
        elif nutr.percentage <= 40:
            # if percentage is 40 or lower, the cat will gain "starving" status
            print("TODO - gain starving")


    def handle_amount_freshkill_pile(self, freshkill_pile, living_cats):
        """
        Handles events (eg. a fox is attacking the camp), which are related to the freshkill pile.
        Game-mode: 'expanded' & 'cruel season'
        """
        print("TODO - events if the amount of prey is too much")
