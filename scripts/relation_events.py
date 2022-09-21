from .cats import *


class Relation_Events(object):
    """All relationship events."""

    def create_interaction(self, cat):
        # if the cat has no relationships, skip
        if len(cat.relationships) < 1 or cat.relationships is None:
            return

        cats_to_choose = list(
            filter(lambda iter_cat_id: iter_cat_id != cat.ID,
                   cat_class.all_cats.copy()))
        # increase chance of cats, which are already befriended
        like_threshold = 50
        relevant_relationships = list(
            filter(lambda relation: relation.platonic_like >= like_threshold,
                   cat.relationships))
        for relationship in relevant_relationships:
            cats_to_choose.append(relationship.cat_to)
            if relationship.platonic_like >= like_threshold * 2:
                cats_to_choose.append(relationship.cat_to)

        # increase chance of cats, which are already may be in love
        love_threshold = 40
        relevant_relationships = list(
            filter(lambda relation: relation.romantic_love >= love_threshold,
                   cat.relationships))
        for relationship in relevant_relationships:
            cats_to_choose.append(relationship.cat_to)
            if relationship.romantic_love >= love_threshold * 2:
                cats_to_choose.append(relationship.cat_to)

        # increase the chance a kitten interact with other kittens
        if cat.age == "kitten":
            kittens = list(
                filter(
                    lambda cat_id: cat.all_cats.get(cat_id).age == "kitten" and
                    cat_id != cat.ID, cat_class.all_cats.copy()))
            cats_to_choose = cats_to_choose + kittens

        # increase the chance a apprentice interact with otherapprentices
        if cat.age == "adolescent":
            apprentices = list(
                filter(
                    lambda cat_id: cat.all_cats.get(cat_id).age == "adolescent"
                    and cat_id != cat.ID, cat_class.all_cats.copy()))
            cats_to_choose = cats_to_choose + apprentices

        # choose cat and start
        random_id = random.choice(list(cat.all_cats.keys()))
        relevant_relationship_list = list(
            filter(
                lambda relation: str(relation.cat_to) == str(random_id) and
                not relation.cat_to.dead, cat.relationships))
        while len(relevant_relationship_list) < 1 or random_id == cat.ID:
            random_id = random.choice(list(cat.all_cats.keys()))
            relevant_relationship_list = list(
                filter(
                    lambda relation: str(relation.cat_to) == str(random_id) and
                    not relation.cat_to.dead, cat.relationships))
        relevant_relationship = relevant_relationship_list[0]
        relevant_relationship.start_action()

        self.relationship_outcome(relationship=relevant_relationship)

    def relationship_outcome(self, relationship):
        """Things that can happen, after relationship changes."""
        cat_from = relationship.cat_from
        cat_from_mate = None
        if cat_from.mate != None or cat_from.mate != '':
            cat_from_mate = cat_class.all_cats.get(cat_from.mate)

        cat_to = relationship.cat_to
        cat_to_mate = None
        if cat_to.mate != None or cat_to.mate != '':
            cat_to_mate = cat_class.all_cats.get(cat_to.mate)

        if relationship.opposit_relationship == None:
            relationship.link_relationship()

        # overcome dead mates
        if cat_from_mate != None and cat_from_mate.dead and randint(1, 20):
            game.cur_events_list.append(
                f'{str(cat_from.name)} will always love {str(cat_from_mate.name)} but has decided to move on'
            )
            cat_from.mate = None
            cat_from_mate.mate = None
        if cat_to_mate != None and cat_to_mate.dead and randint(1, 20):
            game.cur_events_list.append(
                f'{str(cat_to.name)} will always love {str(cat_to_mate.name)} but has decided to move on'
            )
            cat_to.mate = None
            cat_to_mate.mate = None

        # new mates
        both_no_mates = cat_to_mate == None and cat_from_mate == None
        # check ages of cats
        age_group1 = ['adolescent', 'young adult', 'adult']
        age_group2 = ['adult', 'senior adult', 'elder']
        both_in_same_age_group = (cat_from.age in age_group1 and cat_to.age in age_group1) or\
            (cat_from.age in age_group2 and cat_to.age in age_group2)
        random_mates = randint(1, 200)
        if (relationship.romantic_love > 20 and relationship.opposit_relationship.romantic_love > 20 and both_no_mates)\
            or (random_mates == 1 and both_in_same_age_group):
            self.new_mates(cat_from, cat_to)

        # breakup and new mate
        if game.settings[
                'affair'] and not relationship.mates and cat_from_mate != None:
            love_over_30 = relationship.romantic_love > 30 and relationship.opposit_relationship.romantic_love > 30
            normal_chance = randint(1, 10)
            # compare love value of current mates
            bigger_than_current = False
            bigger_love_chance = randint(1, 3)
            mate_relationship = list(
                filter(lambda r: r.cat_to.ID == cat_from.mate,
                       cat_from.relationships))

            # check cat from value
            if mate_relationship is not None and len(mate_relationship) > 0:
                bigger_than_current = relationship.romantic_love > mate_relationship[
                    0].romantic_love
            else:
                if cat_from_mate != None:
                    cat_from_mate.relationships.append(
                        Relationship(cat_from, cat_from_mate, True))
                bigger_than_current = True

            # check cat to value
            if cat_to_mate != None:
                opposite_mate_relationship = list(
                    filter(lambda r: r.cat_to.ID == cat_from.ID,
                           cat_to.relationships))
                if opposite_mate_relationship is not None and len(
                        opposite_mate_relationship) > 0:
                    bigger_than_current = bigger_than_current and relationship.romantic_love > opposite_mate_relationship[
                        0].romantic_love
                else:
                    cat_to_mate.relationships.append(
                        Relationship(cat_to, cat_to_mate, True))
                    bigger_than_current = bigger_than_current and True

            if (love_over_30
                    and normal_chance == 1) or (bigger_than_current
                                                and bigger_love_chance == 1):
                # break up the old relationships
                cat_from_mate = cat_class.all_cats.get(cat_from.mate)
                self.breakup(cat_from, cat_from_mate)

                if cat_to_mate != None:
                    self.breakup(cat_to, cat_to_mate)

                # new relationship
                game.cur_events_list.append(
                    f'{str(cat_from.name)} and {str(cat_to.name)} can\'t ignore their feelings for each other'
                )
                self.new_mates(cat_from, cat_to)

        # breakup
        if relationship.mates and 'negative' in relationship.effect:
            chance_number = 30
            if 'fight' in relationship.current_action_str:
                chance_number = 20
            chance = randint(0, chance_number)
            if chance == 1 or relationship.dislike > 20:
                self.breakup(cat_from, cat_to)

    def new_mates(self, cat1, cat2):
        # change cat 1
        cat1_relation = list(
            filter(lambda r: r.cat_to.ID == cat2.ID, cat1.relationships))
        cat1.mate = cat2.ID
        if cat1_relation is not None and len(cat1_relation) > 0:
            cat1_relation = cat1_relation[0]
            cat1_relation.mates = True
            cat1_relation.romantic_love += 15
            cat1_relation.comfortable += 10
            cat1_relation.trust += 10
        else:
            cat1.relationships.append(Relationship(cat1, cat2, True))

        # change cat 2
        cat2_relation = list(
            filter(lambda r: r.cat_to.ID == cat1.ID, cat2.relationships))
        cat2.mate = cat1.ID
        if cat2_relation is not None and len(cat2_relation) > 0:
            cat2_relation = cat2_relation[0]
            cat2_relation.mates = True
            cat2_relation.romantic_love += 15
            cat2_relation.comfortable += 10
            cat2_relation.trust += 10
        else:
            cat1.relationships.append(Relationship(cat1, cat2, True))

        game.cur_events_list.append(
            f'{str(cat1.name)} and {str(cat2.name)} have become mates')

    def breakup(self, cat1, cat2):
        # change cat 1
        cat1_relation = list(
            filter(lambda r: r.cat_to.ID == cat2.ID, cat1.relationships))
        cat1.mate = None
        if cat1_relation is not None and len(cat1_relation) > 0:
            cat1_relation = cat1_relation[0]
            cat1_relation.mates = False
            cat1_relation.romantic_love = 5
            cat1_relation.comfortable -= 20
            cat1_relation.trust -= 10
        else:
            cat1.relationships.append(Relationship(cat1, cat2))

        # change cat 2
        cat2_relation = list(
            filter(lambda r: r.cat_to.ID == cat1.ID, cat2.relationships))
        cat2.mate = None
        if cat2_relation is not None and len(cat2_relation) > 0:
            cat2_relation = cat2_relation[0]
            cat2_relation.mates = False
            cat2_relation.romantic_love = 5
            cat2_relation.comfortable -= 20
            cat2_relation.trust -= 10
        else:
            cat1.relationships.append(Relationship(cat1, cat2))

        game.cur_events_list.append(
            f'{str(cat1.name)} and {str(cat2.name)} broke up')


relation_events_class = Relation_Events()