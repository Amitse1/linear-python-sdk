"""
Models for Linear comments.
"""
from typing import Optional, List, Dict
from pydantic import Field, BaseModel

from linear.models.base import Node


class CommentConnection(BaseModel):
    """Connection of comments."""
    nodes: List['Comment'] = Field(default_factory=list, description="List of comments")


class Comment(Node):
    """A Linear comment."""
    body: str = Field(..., description="Comment body/content")
    
    # Relations
    issue: Dict[str, str] = Field(..., description="Issue this comment belongs to")
    user: Dict[str, str] = Field(..., description="User who created this comment")
    parent: Optional[Dict[str, str]] = Field(
        default=None,
        description="Parent comment if this is a reply"
    )
    children: Optional[CommentConnection] = Field(
        default_factory=CommentConnection,
        description="Child comments/replies"
    )
    
    # Timestamps
    created_at: str = Field(
        ...,
        alias="createdAt",
        description="When the comment was created"
    )
    updated_at: str = Field(
        ...,
        alias="updatedAt",
        description="When the comment was last updated"
    )

    class Config:
        populate_by_name = True

    @property
    def issue_id(self) -> str:
        """Get the ID of the parent issue."""
        return self.issue.get('id')

    @property
    def user_id(self) -> str:
        """Get the ID of the comment author."""
        return self.user.get('id')

    @property
    def parent_id(self) -> Optional[str]:
        """Get the ID of the parent comment if this is a reply."""
        return self.parent.get('id') if self.parent else None

    @property
    def child_ids(self) -> List[str]:
        """Get the IDs of any child comments."""
        return [node.id for node in self.children.nodes] 