from typing import Union

from pydantic import RootModel

from scripts.models.common.kit_trait import KitTrait
from scripts.models.common.trait import Trait


class AllTrait(RootModel):
    root: Union[Trait, KitTrait]
