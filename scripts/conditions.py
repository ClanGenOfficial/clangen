import math

from scripts.game_structure.game_essentials import game


def medical_cats_condition_fulfilled(all_cats, amount_per_med):
    fulfilled = False

    allowed_injuries = [
        "bruises",
        "scrapes",
        "tickbites",
        "torn pelt",
        "torn ear",
        "splinter",
        "joint pain"
    ]
    allowed_illnesses = [
        "fleas",
        "running nose"
    ]
    medicine_apprentices = list(filter(
        lambda c: c.status =='medicine apprentices' and not c.dead and not c.exiled and\
            (not c.is_ill() or c.is_ill() and c.illness.name in allowed_illnesses) and\
            (not c.is_injured() or c.is_injured() and c.injury.name in allowed_injuries)
            , all_cats
    ))
    medicine_cats = list(filter(
        lambda c: c.status == 'medicine cat' and not c.dead and not c.exiled and\
            (not c.is_ill() or c.is_ill() and c.illness.name in allowed_illnesses) and\
            (not c.is_injured() or c.is_injured() and c.injury.name in allowed_injuries)
            , all_cats
    ))

    relevant_cats = list(filter(lambda c: not c.dead and not c.exiled, all_cats))
    number = len(relevant_cats) / (amount_per_med + 1)

    needed_meds = math.ceil(number)

    fulfilled = len(medicine_cats) >= needed_meds or len(medicine_apprentices) >= needed_meds * 2
    return fulfilled

def get_amount_cat_for_one_medic(clan):
    """Returns """
    amount = 15
    if clan and clan.game_mode == 'cruel season':
        amount = 10
    return amount


# ---------------------------------------------------------------------------- #
#                                    Illness                                   #
# ---------------------------------------------------------------------------- #

class Illness():
    def __init__(self, 
            name, 
            mortality, 
            infectiousness, 
            duration, 
            medicine_duration, 
            medicine_mortality,
            risks,
            event_triggered = False):
        self.name = name
        self.mortality = int(mortality)
        self.infectiousness = int(infectiousness)
        self.duration = int(duration)
        self.medicine_duration = int(medicine_duration)
        self.medicine_mortality = int(medicine_mortality)
        self.risks = risks
        self.new = event_triggered

        self.current_duration = duration
        self.current_mortality = mortality
        amount_per_med = get_amount_cat_for_one_medic(game.clan)
        if medical_cats_condition_fulfilled(game.cat_class.all_cats.values(), amount_per_med):
            self.current_duration = medicine_duration
            self.current_mortality = medicine_mortality

    @property
    def current_duration(self):
        return self._current_duration

    @current_duration.setter
    def current_duration(self, value):
        amount_per_med = get_amount_cat_for_one_medic(game.clan)
        if medical_cats_condition_fulfilled(game.cat_class.all_cats.values(), amount_per_med):
            if value > self.medicine_duration:
                value = self.medicine_duration
        
        self._current_duration = value

    @property
    def current_mortality(self):
        return self._current_mortality

    @current_mortality.setter
    def current_mortality(self, value):
        amount_per_med = get_amount_cat_for_one_medic(game.clan)
        if medical_cats_condition_fulfilled(game.cat_class.all_cats.values(), amount_per_med):
            if value < self.medicine_mortality:
                value = self.medicine_mortality
        
        self._current_mortality = value

# ---------------------------------------------------------------------------- #
#                                   Injuries                                   #
# ---------------------------------------------------------------------------- #

class Injury():
    def __init__(self, 
            name,
            duration,
            medicine_duration,
            mortality,
            risks,
            illness_infectiousness,
            event_triggered = False):
        self.name = name
        self.duration = duration
        self.medicine_duration = medicine_duration
        self.mortality = mortality
        self.risks = risks
        self.illness_infectiousness = illness_infectiousness
        self.new = event_triggered

        self.current_duration = duration
        self.current_mortality = mortality
        amount_per_med = get_amount_cat_for_one_medic(game.clan)
        if medical_cats_condition_fulfilled(game.cat_class.all_cats.values(), amount_per_med):
            self.current_duration = medicine_duration

    @property
    def current_duration(self):
        return self._current_duration

    @current_duration.setter
    def current_duration(self, value):
        amount_per_med = get_amount_cat_for_one_medic(game.clan)
        if medical_cats_condition_fulfilled(game.cat_class.all_cats.values(), amount_per_med):
            if value > self.medicine_duration:
                value = self.medicine_duration
        
        self._current_duration = value

    @property
    def current_mortality(self):
        return self._current_mortality

    @current_mortality.setter
    def current_mortality(self, value):        
        self._current_mortality = value
