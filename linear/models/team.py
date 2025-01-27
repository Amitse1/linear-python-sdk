"""
Models for Linear teams.
"""
from typing import Optional, List

from pydantic import Field, BaseModel

from linear.models.base import Node
from linear.models.user import Organization
from linear.models.workflow_state import WorkflowState


class Team(Node):
    """A Linear team."""
    name: str = Field(..., description="Team name")
    key: str = Field(..., description="Team key (e.g. 'ENG')")
    description: Optional[str] = Field(
        default=None,
        description="Team description"
    )
    
    # Organization
    organization: Organization = Field(..., description="Team's organization")
    private: bool = Field(
        default=False,
        description="Whether the team is private"
    )
    
    # Timestamps
    created_at: str = Field(
        ...,
        alias="createdAt",
        description="When the team was created"
    )
    updated_at: str = Field(
        ...,
        alias="updatedAt",
        description="When the team was last updated"
    )
    archived_at: Optional[str] = Field(
        default=None,
        alias="archivedAt",
        description="When the team was archived, if applicable"
    )
    
    # Settings
    default_issue_state: Optional[WorkflowState] = Field(
        default=None,
        alias="defaultIssueState",
        description="Default state for new issues"
    )
    auto_archive_period: int = Field(
        default=0,
        description="Days after which completed issues are archived (0 = never)"
    )
    auto_close_period: int = Field(
        default=0,
        description="Days after which issues are automatically closed (0 = never)"
    )
    
    # Cycles
    cycles_enabled: bool = Field(
        default=True,
        description="Whether cycles are enabled"
    )
    cycle_duration: int = Field(
        default=14,
        description="Default cycle duration in days"
    )
    cycle_cooldown_time: int = Field(
        default=0,
        alias="cycleCooldownTime",
        description="Days between cycles"
    )
    
    # Triage
    triage_enabled: bool = Field(
        default=False,
        description="Whether triage mode is enabled"
    )

    class Config:
        populate_by_name = True

    @property
    def issue_key_prefix(self) -> str:
        """Get the prefix used for issue identifiers."""
        return self.key.upper() 