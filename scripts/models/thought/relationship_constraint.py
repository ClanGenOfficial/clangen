from __future__ import annotations

from pydantic import RootModel

from scripts.models.common.relationship_status import RelationshipStatus


class RelationshipConstraint(RootModel):
    root: RelationshipStatus
