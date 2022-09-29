# simple utility function which are not direkt related to a class


def get_highes_romantic_relation(relationships):
    """Returns the relationship with the hightes romantic value."""
    romantic_relation = list(filter(lambda rel: rel.romantic_love > 0, relationships))
    if romantic_relation is None or len(romantic_relation) == 0:
        return None

    relation = romantic_relation[0]
    max_love_value = relation.romantic_love
    # if there more love relations, pick the biggest one
    for inter_rel in romantic_relation:
        if max_love_value < inter_rel.romantic_love:
            max_love_value = inter_rel.romantic_love
            relation = inter_rel

    return relation
