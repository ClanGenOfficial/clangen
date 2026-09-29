from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel
from pydantic_core import MISSING

type LayerOrder = str | list[LayerOrder]


class NormalLayer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    group_name: str = Field(..., description="Specifies which pelt-part will be used.")
    color: str | MISSING = Field(
        MISSING,
        description="Color name as defined in the color palettes. This group will be recolored to this color.",
    )
    blend_mode: Literal["normal", "multiply", "mask"] | MISSING = Field(
        MISSING, description="Refers to the blending mode in which the flat is applied"
    )
    opacity: int | MISSING = Field(
        100, description="Defines opacity of the layer. 0-100."
    )
    spritesheet: str | MISSING = Field(
        MISSING,
        description='This is the spritesheet to look for group_name in. Most helpful for tortie patches, which are in "patches_tortie".',
    )


class ReferenceLayer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pelt_name: str | MISSING = Field(
        MISSING, description="Refers to another pelt recipe."
    )
    palette: str | MISSING = Field(
        MISSING, description="Refers to a colour in another pelt recipe"
    )


class Layer(RootModel):
    root: NormalLayer | ReferenceLayer


class RecipeException(BaseModel):
    model_config = ConfigDict(extra="forbid")

    poses: list[str] | str | MISSING = Field(
        MISSING, description="Poses that this exception applies to."
    )
    colors: list[str] | str | MISSING = Field(
        MISSING, description="Colours that this exception applies to."
    )

    layer_order: list[LayerOrder] | MISSING = Field(
        MISSING, description="Layer order of this exception."
    )
    layers: dict[str, Layer] | MISSING = Field(
        MISSING, description="Layer data of this exception."
    )


class PeltRecipe(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        ..., description="Name of the recipe. Should be unique for each recipe."
    )
    layer_order: list[LayerOrder] = Field(
        ...,
        description="Order the layers of the pelt will be built. The first entry is the bottom layer, and it builds up from there.  You can also have compound layers.  They will be constructed first, then layered.",
    )
    layers: dict[str, Layer] = Field(..., description="Layers for the recipe.")
    exceptions: list[RecipeException]
