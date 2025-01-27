"""
Base models for Linear objects.
"""
from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field, ConfigDict


class LinearObject(BaseModel):
    """Base class for all Linear objects."""
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda s: s.replace("_", ""),
    )

    id: str = Field(..., description="Unique identifier of the object")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    raw_data: Dict[str, Any] = Field(
        default_factory=dict,
        exclude=True,
        description="Raw data from the API"
    )

    def __init__(self, **data):
        super().__init__(**data)
        self.raw_data = data


class Node(LinearObject):
    """Base class for objects that can be archived."""
    archived_at: Optional[datetime] = Field(
        default=None,
        description="Archived timestamp"
    )

    @property
    def is_archived(self) -> bool:
        """Whether the object is archived."""
        return self.archived_at is not None


class Actor(Node):
    """Base class for objects that can perform actions."""
    name: str = Field(..., description="Name of the actor")
    email: Optional[str] = Field(
        default=None,
        description="Email of the actor"
    ) 