from scripts.game_structure.game_essentials import game


# ---------------------------------------------------------------------------- #
#                            !IMPORTANT INFORMATION!                           #
#              currently not integrated, this are just the base classes        #
#    me (Lixxis) will integrate them after tests are written and completed     #
# ---------------------------------------------------------------------------- #


def medical_cats_condition_fulfilled():
    fulfilled = False

    medicine_apprentices = list(filter(
        lambda c: c.status =='medicine apprentices' and not c.dead and not c.exiled, game.cat_class.all_cats.values()
        ))
    medicine_cats = list(filter(
        lambda c: c.status == 'medicine cat' and not c.dead and not c.exiled, game.cat_class.all_cats.values()
        ))
    needed_meds = int(len(list(filter(
        lambda c: not c.dead and not c.exiled, game.cat_class.all_cats.values())
        )) % 15)

    amount_of_cats = len(medicine_cats) >= needed_meds or len(medicine_apprentices) >= needed_meds * 2
     
    if amount_of_cats:
        fulfilled = True

    return fulfilled


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
            risks):
        self.name = name
        self.mortality = int(mortality)
        self.infectiousness = int(infectiousness)
        self.duration = int(duration)
        self.medicine_duration = int(medicine_duration)
        self.medicine_mortality = int(medicine_mortality)
        self.risks = risks

        self.current_duration = duration
        self.current_mortality = mortality
        if medical_cats_condition_fulfilled():
            self.current_duration = medicine_duration
            self.current_mortality = medicine_mortality

    @property
    def current_duration(self):
        return self._current_duration

    @current_duration.setter
    def current_duration(self, value):
        if medical_cats_condition_fulfilled():
            if value > self.medicine_duration:
                value = self.medicine_duration
        
        self._current_duration = value

    @property
    def current_mortality(self):
        return self._current_mortality

    @current_mortality.setter
    def current_mortality(self, value):
        if medical_cats_condition_fulfilled():
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
            illness_infectiousness):
        self.name = name
        self.duration = duration
        self.medicine_duration = medicine_duration
        self.mortality = mortality
        self.risks = risks
        self.illness_infectiousness = illness_infectiousness

        self.current_duration = duration
        self.current_mortality = mortality
        if medical_cats_condition_fulfilled():
            self.current_duration = medicine_duration

    @property
    def current_duration(self):
        return self._current_duration

    @current_duration.setter
    def current_duration(self, value):
        if medical_cats_condition_fulfilled():
            if value > self.medicine_duration:
                value = self.medicine_duration
        
        self._current_duration = value

    @property
    def current_mortality(self):
        return self._current_mortality

    @current_mortality.setter
    def current_mortality(self, value):        
        self._current_mortality = value
