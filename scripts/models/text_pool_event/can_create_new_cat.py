from typing import Union

from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import MISSING


class CanCreateNewCat(BaseModel):
    model_config = ConfigDict(extra="forbid")
    become_litter: Union[bool, MISSING] = Field(
        MISSING,
        description="True will generate a 2-5 litter of kittens rather than a single cat. This means the abbreviation for this litter should not be used within the text of the event, since they have no singular name or pronoun",
    )
    assign_blood_parent: Union[list[str], MISSING] = Field(
        MISSING,
        description="List of designations for cats who will become this cat's blood parents. These cats must have already been specified prior in involved_cats",
    )
    assign_adoptive_parent: Union[list[str], MISSING] = Field(
        MISSING,
        description="List of designations for cats who will become this cat's adoptive parents. These cats must have already been specified prior in involved_cats",
    )
    assign_mate: Union[list[str], MISSING] = Field(
        MISSING,
        description="List of designations for cats who will become this cat's mates. These cats must have already been specified prior in involved_cats",
    )
