"""
Models for Linear attachments.
"""
from enum import Enum
from typing import Optional, Dict, Any

from pydantic import ConfigDict, Field, BaseModel

from linear.models.base import Node
from linear.models.issue import Issue
from linear.models.user import User


class AttachmentSource(str, Enum):
    """Source types for attachments."""
    GDRIVE = "gdrive"
    FIGMA = "figma"
    GITHUB = "github"
    GITLAB = "gitlab"
    URL = "url"
    GENERIC = "generic"


class AttachmentMetadata(BaseModel):
    """Metadata for attachments."""
    model_config = ConfigDict(extra="allow")
    
    # Common fields
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    
    # Source-specific fields will be stored in the extra fields


class Attachment(Node):
    """A Linear attachment."""
    title: str = Field(..., description="Attachment title")
    subtitle: Optional[str] = Field(
        default=None,
        description="Attachment subtitle"
    )
    
    # Source
    source: Optional[AttachmentSource] = Field(
        default=None,
        description="Source of the attachment"
    )
    source_type: Optional[str] = Field(
        default=None,
        alias="sourceType",
        description="Specific type within the source"
    )
    url: str = Field(..., description="URL to the attachment")
    
    # Relations
    issue: Dict[str, str] = Field(..., description="Issue this attachment belongs to")
    creator: Dict[str, str] = Field(..., description="User who created this attachment")
    
    # Metadata
    metadata: AttachmentMetadata = Field(
        default_factory=AttachmentMetadata,
        description="Source-specific metadata"
    )
    group_by_source: bool = Field(
        default=True,
        alias="groupBySource",
        description="Whether to group with other attachments from the same source"
    )
    
    # Timestamps
    created_at: str = Field(
        ...,
        alias="createdAt",
        description="When the attachment was created"
    )
    updated_at: str = Field(
        ...,
        alias="updatedAt",
        description="When the attachment was last updated"
    )
    archived_at: Optional[str] = Field(
        default=None,
        alias="archivedAt",
        description="When the attachment was archived"
    )

    class Config:
        populate_by_name = True

    def __init__(self, **data):
        # If source is not in response, try to get it from metadata
        if "source" not in data and "metadata" in data:
            metadata = data.get("metadata", {})
            if isinstance(metadata, str):
                try:
                    metadata = eval(metadata)  # Handle string metadata
                except:
                    metadata = {}
            source = metadata.get("source")
            if source:
                data["source"] = source
        super().__init__(**data)

    @property
    def issue_id(self) -> str:
        """Get the ID of the parent issue."""
        return self.issue.get('id')

    @property
    def creator_id(self) -> str:
        """Get the ID of the user who created this attachment."""
        return self.creator.get('id')

    @property
    def is_file(self) -> bool:
        """Whether this is a file attachment."""
        return self.source == AttachmentSource.GENERIC

    @property
    def is_url(self) -> bool:
        """Whether this is a URL attachment."""
        return self.source == AttachmentSource.URL

    @property
    def source_name(self) -> str:
        """Get a human-readable source name."""
        return self.source.value.title() if self.source else "Unknown" 