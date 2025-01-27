"""
Models for Linear users.
"""
from typing import Optional, List, Dict

from pydantic import Field, BaseModel

from linear.models.base import Actor


class Organization(BaseModel):
    """Organization information."""
    id: str = Field(..., description="Organization ID")


class Team(BaseModel):
    """Team information."""
    id: str = Field(..., description="Team ID")


class TeamConnection(BaseModel):
    """Connection of teams."""
    nodes: List[Team] = Field(default_factory=list, description="List of teams")


class User(Actor):
    """A Linear user."""
    # Basic info
    name: str = Field(
        ...,
        description="User's full name"
    )
    display_name: Optional[str] = Field(
        default=None,
        alias="displayName",
        description="User's display name"
    )
    email: str = Field(
        ...,
        description="User's email address"
    )
    avatar_url: Optional[str] = Field(
        default=None,
        alias="avatarUrl", 
        description="URL of the user's avatar"
    )
    
    # Organization
    organization: Organization = Field(
        ...,
        description="User's organization"
    )
    
    # Status and timestamps
    active: bool = Field(
        default=True,
        description="Whether the user is active"
    )
    last_seen: Optional[str] = Field(
        default=None,
        alias="lastSeen",
        description="When the user was last seen"
    )
    created_at: str = Field(
        ...,
        alias="createdAt",
        description="When the user was created"
    )
    updated_at: str = Field(
        ...,
        alias="updatedAt", 
        description="When the user was last updated"
    )
    archived_at: Optional[str] = Field(
        default=None,
        alias="archivedAt",
        description="When the user was archived, if applicable"
    )
    
    # Settings
    timezone: Optional[str] = Field(
        default=None,
        description="User's timezone"
    )
    is_me: bool = Field(
        default=False,
        alias="isMe",
        description="Whether this user is the authenticated user"
    )
    
    # Teams
    teams: TeamConnection = Field(
        default_factory=TeamConnection,
        description="Teams the user belongs to"
    )

    class Config:
        populate_by_name = True

    @property
    def team_ids(self) -> List[str]:
        """Get list of team IDs for backwards compatibility."""
        return [team.id for team in self.teams.nodes]

    @property
    def default_team_id(self) -> Optional[str]:
        """Get first team ID for backwards compatibility."""
        return self.team_ids[0] if self.team_ids else None 