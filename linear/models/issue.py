"""
Models for Linear issues.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import Field, BaseModel

from linear.models.base import Node
from linear.models.team import Team
from linear.models.user import User
from linear.models.workflow_state import WorkflowState, WorkflowStateType


class IssuePriority(int, Enum):
    """Priority levels for an issue (0 is no priority, 1 is lowest, 4 is highest)."""
    NO_PRIORITY = 0
    URGENT = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class MinimalIssue(Node):
    """A minimal issue representation for relationships."""
    title: Optional[str] = Field(
        default=None,
        description="Issue title"
    )
    state: Optional[WorkflowState] = Field(
        default=None,
        description="Current workflow state"
    )
    number: Optional[int] = Field(
        default=None,
        description="Issue number"
    )
    identifier: Optional[str] = Field(
        default=None,
        description="Issue identifier (e.g. ENG-123)"
    )
    team: Optional[Team] = Field(
        default=None,
        description="Team this issue belongs to"
    )
    url: Optional[str] = Field(
        default=None,
        description="URL to the issue in Linear"
    )
    created_at: Optional[str] = Field(
        default=None,
        alias="createdAt",
        description="When the issue was created"
    )
    updated_at: Optional[str] = Field(
        default=None,
        alias="updatedAt",
        description="When the issue was last updated"
    )

    class Config:
        populate_by_name = True


class IssueConnection(BaseModel):
    """Connection of issues."""
    nodes: List[MinimalIssue] = Field(default_factory=list, description="List of issues")


class Issue(Node):
    """A Linear issue."""
    title: str = Field(..., description="Issue title")
    description: Optional[str] = Field(
        default=None,
        description="Issue description in markdown"
    )
    state: WorkflowState = Field(
        ...,
        description="Current workflow state"
    )
    priority: IssuePriority = Field(
        default=IssuePriority.NO_PRIORITY,
        description="Issue priority"
    )
    
    # Identifiers
    number: int = Field(..., description="Issue number")
    identifier: str = Field(..., description="Issue identifier (e.g. ENG-123)")
    team: Team = Field(..., description="Team this issue belongs to")
    
    # Assignments
    assignee: Optional[User] = Field(
        default=None,
        description="Assigned user"
    )
    creator: Optional[User] = Field(
        default=None,
        description="User who created this issue"
    )
    
    # Dates
    due_date: Optional[str] = Field(
        default=None,
        alias="dueDate",
        description="Due date"
    )
    started_at: Optional[str] = Field(
        default=None,
        alias="startedAt",
        description="When work was started"
    )
    completed_at: Optional[str] = Field(
        default=None,
        alias="completedAt",
        description="When the issue was completed"
    )
    canceled_at: Optional[str] = Field(
        default=None,
        alias="canceledAt",
        description="When the issue was canceled"
    )
    created_at: str = Field(
        ...,
        alias="createdAt",
        description="When the issue was created"
    )
    updated_at: str = Field(
        ...,
        alias="updatedAt",
        description="When the issue was last updated"
    )
    archived_at: Optional[str] = Field(
        default=None,
        alias="archivedAt",
        description="When the issue was archived"
    )
    
    # Labels and relationships
    label_ids: List[str] = Field(
        default_factory=list,
        alias="labelIds",
        description="IDs of labels attached to this issue"
    )
    parent: Optional[MinimalIssue] = Field(
        default=None,
        description="Parent issue"
    )
    children: Optional[IssueConnection] = Field(
        default_factory=IssueConnection,
        description="Child issues"
    )
    
    # Metadata
    url: str = Field(..., description="URL to the issue in Linear")
    branch_name: str = Field(
        default="",
        alias="branchName",
        description="Git branch name for the issue"
    )

    class Config:
        populate_by_name = True

    @property
    def is_completed(self) -> bool:
        """Whether the issue is completed."""
        return self.state.type == WorkflowStateType.COMPLETED

    @property
    def is_canceled(self) -> bool:
        """Whether the issue is canceled."""
        return self.state.type == WorkflowStateType.CANCELED

    @property
    def is_active(self) -> bool:
        """Whether the issue is active (not completed/canceled/archived)."""
        return not (self.is_completed or self.is_canceled or self.is_archived) 