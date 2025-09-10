# Cat Status

Cat status is primarily composed of four properties and their associated enums:

| Property   | Enum/Type   | Use                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|------------|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `social`   | `CatSocial` | This is the cat's current social caste. For example, if a cat is part of a Clan, they are a `CLANCAT`. If a cat is owned by Twolegs, they are a `KITTYPET`.                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `group`    | `CatGroup`  | This is the group *type* for the group that a cat is currently affiliated with. If they have no group, this will be `CatGroup.NONE`, which does function as a `NoneType` value. Note that each afterlife has its own `CatGroup` and that all other Clans are considered `CatGroup.OTHER_CLAN` as opposed to the player's `CatGroup.PLAYER_CLAN`. This info isn't saved within the cat's save file, but is retrieved during runtime based off of the `group_ID`.                                                                                                                     |
| `group_ID` | `str`       | This is the group_ID for the group that a cat is currently affiliated with. If they have no group, this will be `None`. Note that each afterlife has its own ID. The "default" groups: `PLAYER_CLAN`, `STARCLAN`, `DARK_FOREST`, and `UNKNOWN_RESIDENCE` each have static IDs that will always be the same across every save file. These can be easily accessed via `CatGroup.PLAYER_CLAN_ID`, `CatGroup.STARCLAN_ID`, `CatGroup.DARK_FOREST_ID'`, and `CatGroup.UNKNOWN_RESIDENCE_ID`. Other groups will have IDs assigned when they are created and saved within their save info. |
| `rank`     | `CatRank`   | This is the rank a cat currently holds, typically within a group. For now, only `CLANCAT`s have ranks. Cats that are part of a `CatSocial` that has no ranks will take a `CatRank` matching their `CatSocial`. For example, a `CatSocial.LONER` will also be a `CatRank.LONER`.                                                                                                                                                                                                                                                                                                     |

We also utilize one more enum: `CatStanding`. This is, essentially, what a group thinks of a cat. For example, a member of a group will have the standing `MEMBER`, while a cat who was exiled from the group would have the standing `EXILED`. You can use the func `get_standing_with_group()` to retrieve a cat's currently standing with a group. The functions `is_lost()` and `is_exiled()` can assist in quickly finding `standing` status.

!!! Important
    All of this information is stored within two attributes: `group_history` and `standing_history`. These preserve all past information as well as current information. We can retrieve the number of moons a cat has held a rank, we can pull a cat's entire `standing` history with a certain group, we can see all the `social`s a cat has held in their life. The majority of this information can be retrieved through properties and funcs already made in `status.py`.

## Common Status Changes

### Exiled or Lost
When cats are exiled or lost from a group, their `group` will change to `None` and their `standing` with their old group will change to `EXILED` or `LOST` respectively. Their `social` will change to one of the outsider socials: `ROGUE`, `KITTYPET`, `LONER`; and their `rank` will change to match this `social`.

!!! tip
    Note that you can always get their past information through `all_socials`, `all_groups`, `all_ranks` and `get_standing_with_group()`

### Dead
When cats die, their `group` becomes one of the three afterlives: `STARCLAN`, `UNKNOWN_RESIDENCE`, `DARK_FOREST`. This means that if you want to check what group they were in before dying, you would need to use `all_groups`. Their `rank` and `social` will stay the same as it was in life. If they were within a group during life, their `standing` with that group becomes `KNOWN`.

!!! tip
    As the afterlives are groups, they can also have associated `standing`s with cats! A member of an afterlife will have the `MEMBER` standing. If a cat's afterlife `group` changes, the prior group's standing will become `KNOWN`. 

### Joining the Player Clan
Cats of all social castes can join the player Clan. When they do, their `social` will change to `CLANCAT` and they'll gain a `rank` appropriate for their age. Their `standing` with the player Clan changes to `MEMBER`. Their `group` becomes `PLAYER_CLAN`. 

!!! tip
    Some cats who join the Clan may have already been a `CLANCAT`! Perhaps they are a prior member who was lost or exiled, or perhaps they're from a different Clan. When they join the player Clan, they will attempt to take their last held Clan rank. Note that `LEADER`s and `DEPUTY`s will become `WARRIOR`s. If this rank is incompatible with their current age, our current functions for handling this process will detect that discrepancy and correct it with an associated ceremony event.

### Near vs. Far
`standing_history` doesn't just track the cat's `standing` with a group, it also tracks their `near` attribute with that group. `near` is a bool. `True` means a cat is close enough with that group to interact with it. `False` means they are too far away from that group to interact with it.

For now, this value only changes when cats are driven away via the Leader's Den. This replaces the old `driven_out` cat attribute.