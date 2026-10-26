# Patrol Outcomes

## Minimum Required
>The smallest amount of information you're required to include in this format. 

```json
{
    "frequency": 4,
    "strings": [
        "m_c spent time chatting with r_c."
    ],
    "exp_gained": 0
}
```

### Full Format

This event type uses the [TextPoolEvent Format](../textpoolevents/textpoolevent-format.md)

Any parameters with patrol-specific notes are explained below.

### Disallowed Parameters

The following parameters from the TextPoolFormat are not used for Patrol Outcome Events:

- [event_id](../textpoolevents/textpoolevent-format.md#event_id-str)

***

### poi: Dict
[Main poi Notes](../textpoolevents/textpoolevent-format.md#poi-dict)

If the top level of the patrol already has a POI constraint, then that POI will be used for all the outcomes as well. You cannot specify a second, different POI to use for an outcome.  

If you're looking to utilize the top level POI in the outcome, then no extra constraints are necessary on the outcome level. You can simply refer to the POI in the text and it will use the same POI as the top level.

***

### required_cat_types: Dict[str, List[int]]
[Main required_cat_types Notes](../textpoolevents/textpoolevent-format.md#required_cat_types-dictstr-listint)

!!! caution
    Remember that the greater patrol parameter will have already been applied, so adding an outcome-specific `required_cat_types` will require even *more* specific patrol compositions.

***

### involved_cats: dict[str: dict]
[Main involved_cats Notes](../textpoolevents/textpoolevent-format.md#involved_cats-dictstr-dict)

You can either specify further constraints for cats already specified in the greater patrol `involved_cats`, or you can specify new involved cats for this outcome.

It's possible to "reuse" a cat under a new designation, but with tighter constraints. You can utilize the `s_c` designations for this use. You will need to add the `prior_abbreviation` parameter to the dictionary for the `s_c` cat:

For example:
```json
"s_c0":{
    "prior_abbreviation": ["p_l", "r_c1"],
    "status": ["warrior"]
}
```
In this example, `s_c` can be either `p_l` or `r_c1`, but only if those cats are also `warrior` rank.

You can utilize any prior declared cat designation *or* to allow any cat in the patrol to be s_c, you can use `any`.

These can also be exclusionary tags such as: `-p_l` to allow any cat *except* `p_l` to take this role.

!!! tip
    `s_c` used to be used only for trait and skill constrained cats. Now it's for *any* sort of constraint. This could be a health constraint, group constraint, literally any constraint.

***

### patrol_temperament: list[str]
[Main patrol_temperament Notes](../textpoolevents/textpoolevent-format.md#patrol_temperament-liststr)

!!! tip
    Constraining temperament on an outcome rather than on the patrol keeps the patrol available for everyone. A wary patrol and a mellow one can walk into the same border skirmish and come away with different stories.

***

### other_clan_temperament: list[str]
[Main other_clan_temperament Notes](../textpoolevents/textpoolevent-format.md#other_clan_temperament-liststr)

!!! caution
    An outcome using this will never be chosen if no other Clan is involved in the patrol, so make sure every outcome list has at least one option without it.

***

### reputation_changes: dict
[Main reputation_changes Notes](../textpoolevents/textpoolevent-format.md#reputation_changes-dict)

> Defaults:
>
> | Outcome type          | Change                  |
> |-----------------------|-------------------------|
> | Success               | 2                       |
> | Failure               | 0 or -1                 |
> | Antagonize success    | -2                      |
> | Antagonize failure    | -1 or 0                 |

***

### lost: list[dict]
[Main lost Notes](../textpoolevents/textpoolevent-format.md#lost-listdict)

`patrol_cats` can be used to lose the entire patrol.

***

