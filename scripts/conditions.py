from scripts.game_structure.game_essentials import game


# ---------------------------------------------------------------------------- #
#                            !IMPORTANT INFORMATION!                           #
#              currently not integrated, this are just the base classes        #
#    me (Lixxis) will integrate them after tests are written and completed     #
# ---------------------------------------------------------------------------- #


def medical_cats_condition_fulfilled(number_medicine_cats, number_medicine_apprentices):
    fulfilled = False

    medicine_apprentices = filter(lambda c: c.status =='medicine apprentices', game.cat_class.all_cats)
    medicine_cats = filter(lambda c: c.status == 'medicine cat', game.cat_class.all_cats)
    if len(medicine_cats) >= number_medicine_cats or\
        len(medicine_apprentices) >= number_medicine_apprentices:
        fulfilled = True

    return fulfilled


# ---------------------------------------------------------------------------- #
#                                    Illness                                   #
# ---------------------------------------------------------------------------- #

class Illness():
    def _init_(self, 
            name, 
            mortality, 
            infectiousness, 
            duration, 
            medicine_duration, 
            medicine_mortality, 
            number_medicine_cats = 1,
            number_medicine_apprentices = 2):
        self.name = name
        self.mortality = mortality
        self.infectiousness = infectiousness
        self.duration = duration
        self.medicine_duration = medicine_duration
        self.medicine_mortality = medicine_mortality
        self.number_medicine_cats = number_medicine_cats
        self.number_medicine_apprentices = number_medicine_apprentices


    @property
    def duration(self):
        if medical_cats_condition_fulfilled(self.number_medicine_cats, self.number_medicine_apprentices):
            return self.medicine_duration

        return self._duration

    @property
    def medicine_duration(self):
        if medical_cats_condition_fulfilled(self.number_medicine_cats, self.number_medicine_apprentices):
            return self.medicine_duration

        return self._duration

    @property
    def mortality(self):
        if medical_cats_condition_fulfilled(self.number_medicine_cats, self.number_medicine_apprentices):
            return self.medicine_mortality

        return self._mortality

    @property
    def medicine_mortality(self):
        if medical_cats_condition_fulfilled(self.number_medicine_cats, self.number_medicine_apprentices):
            return self.medicine_mortality

        return self._mortality


# ---------------------------------------------------------------------------- #
#                                   Injuries                                   #
# ---------------------------------------------------------------------------- #

class Injury():
    def _init_(self, 
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

    @property
    def duration(self):
        if medical_cats_condition_fulfilled(self.number_medicine_cats, self.number_medicine_apprentices):
            return self.medicine_duration

        return self._duration

    @property
    def medicine_duration(self):
        if medical_cats_condition_fulfilled(self.number_medicine_cats, self.number_medicine_apprentices):
            return self.medicine_duration

        return self._duration

    @property
    def mortality(self):
        if medical_cats_condition_fulfilled(self.number_medicine_cats, self.number_medicine_apprentices):
            return self.medicine_mortality

        return self._mortality

    @property
    def medicine_mortality(self):
        if medical_cats_condition_fulfilled(self.number_medicine_cats, self.number_medicine_apprentices):
            return self.medicine_mortality

        return self._mortality
