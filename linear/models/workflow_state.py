"""
Models for Linear workflow states.
"""
from enum import Enum
from typing import Optional, Dict

from pydantic import Field, BaseModel


class WorkflowStateType(str, Enum):
    """Types of workflow states."""
    TRIAGE = "triage"
    BACKLOG = "backlog"
    UNSTARTED = "unstarted"
    STARTED = "started"
    COMPLETED = "completed"
    CANCELED = "canceled"
    DUPLICATE = "duplicate"


class MinimalTeam(BaseModel):
    """A minimal team representation for relationships."""
    id: str = Field(..., description="Team ID")
    name: Optional[str] = Field(default=None, description="Team name")
    key: Optional[str] = Field(default=None, description="Team key")
    description: Optional[str] = Field(default=None, description="Team description")
    organization: Optional[Dict[str, str]] = Field(default=None, description="Organization this team belongs to")
    created_at: Optional[str] = Field(
        default=None,
        alias="createdAt",
        description="When the team was created"
    )
    updated_at: Optional[str] = Field(
        default=None,
        alias="updatedAt",
        description="When the team was last updated"
    )
    archived_at: Optional[str] = Field(
        default=None,
        alias="archivedAt",
        description="When the team was archived"
    )

    class Config:
        populate_by_name = True


class WorkflowState(BaseModel):
    """A workflow state in Linear."""
    id: str = Field(..., description="State ID")
    name: str = Field(..., description="State name")
    type: WorkflowStateType = Field(..., description="State type")
    color: str = Field(..., description="State color")
    position: Optional[float] = Field(
        default=None,
        description="Position in the workflow"
    )
    description: Optional[str] = Field(
        default=None,
        description="State description"
    )
    team: MinimalTeam = Field(
        ...,
        description="Team this state belongs to"
    )
    created_at: str = Field(
        ...,
        alias="createdAt",
        description="When the state was created"
    )
    updated_at: str = Field(
        ...,
        alias="updatedAt",
        description="When the state was last updated"
    )
    archived_at: Optional[str] = Field(
        default=None,
        alias="archivedAt",
        description="When the state was archived"
    )

    class Config:
        populate_by_name = True 