from typing import Annotated

from pydantic import StringConstraints, RootModel


class Skill(RootModel):
    root: Annotated[str, StringConstraints(pattern=r"^[A-Z]+,\s*[0-4]$")]
