from scripts.game_structure.game_essentials import game


# ---------------------------------------------------------------------------- #
#                            !IMPORTANT INFORMATION!                           #
#              currently not integrated, this are just the base classes        #
#    me (Lixxis) will integrate them after tests are written and completed     #
# ---------------------------------------------------------------------------- #


def medical_cats_condition_fulfilled(number_medicine_cats, number_medicine_apprentices):
    fulfilled = False

    medicine_apprentices = list(filter(lambda c: c.status =='medicine apprentices', game.cat_class.all_cats.values()))
    medicine_cats = list(filter(lambda c: c.status == 'medicine cat', game.cat_class.all_cats.values()))
    if len(medicine_cats) >= number_medicine_cats or\
        len(medicine_apprentices) >= number_medicine_apprentices:
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
            risks,
            number_medicine_cats = 1,
            number_medicine_apprentices = 2):
        self.name = name
        self.mortality = int(mortality)
        self.infectiousness = int(infectiousness)
        self.duration = int(duration)
        self.medicine_duration = int(medicine_duration)
        self.medicine_mortality = int(medicine_mortality)
        self.risks = risks
        self.number_medicine_cats = number_medicine_cats
        self.number_medicine_apprentices = number_medicine_apprentices

        self.current_duration = duration
        self.current_mortality = mortality
        if medical_cats_condition_fulfilled(self.number_medicine_cats, self.number_medicine_apprentices):
            self.current_duration = medicine_duration
            self.current_mortality = medicine_mortality

    @property
    def current_duration(self):
        return self._current_duration

    @current_duration.setter
    def current_duration(self, value):
        if medical_cats_condition_fulfilled(self.number_medicine_cats,self.number_medicine_apprentices):
            if value > self.medicine_duration:
                value = self.medicine_duration
        
        self._current_duration = value

    @property
    def current_mortality(self):
        return self._current_mortality

    @current_mortality.setter
    def current_mortality(self, value):
        if medical_cats_condition_fulfilled(self.number_medicine_cats, self.number_medicine_apprentices):
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
            medicine_mortality,
            risks,
            illness_infectiousness,
            number_medicine_cats = 1,
            number_medicine_apprentices = 2):
        self.name = name
        self.duration = duration
        self.medicine_duration = medicine_duration
        self.mortality = mortality
        self.medicine_mortality = medicine_mortality
        self.risks = risks
        self.illness_infectiousness = illness_infectiousness
        self.number_medicine_cats = number_medicine_cats
        self.number_medicine_apprentices = number_medicine_apprentices

        self.current_duration = duration
        self.current_mortality = mortality
        if medical_cats_condition_fulfilled(self.number_medicine_cats, self.number_medicine_apprentices):
            self.current_duration = medicine_duration
            self.current_mortality = medicine_mortality

    @property
    def current_duration(self):
        return self._current_duration

    @current_duration.setter
    def current_duration(self, value):
        if medical_cats_condition_fulfilled(self.number_medicine_cats,self.number_medicine_apprentices):
            if value > self.medicine_duration:
                value = self.medicine_duration
        
        self._current_duration = value

    @property
    def current_mortality(self):
        return self._current_mortality

    @current_mortality.setter
    def current_mortality(self, value):
        if medical_cats_condition_fulfilled(self.number_medicine_cats, self.number_medicine_apprentices):
            if value < self.medicine_mortality:
                value = self.medicine_mortality
        
        self._current_mortality = value
