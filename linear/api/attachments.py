"""
Linear Attachments API resource.
"""
from typing import Optional, List, Dict, Any, Iterator, Union
from pathlib import Path

from linear.models.attachment import Attachment, AttachmentSource, AttachmentMetadata
from linear.errors import LinearError


class AttachmentOperationError(LinearError):
    """Raised when an attachment operation fails."""
    def __init__(self, message: str, operation: str, data: Optional[Dict] = None):
        super().__init__(message)
        self.operation = operation
        self.data = data or {}


class AttachmentsResource:
    """
    Resource for interacting with Linear attachments.
    """

    def __init__(self, client):
        self.client = client

    def get(self, id: str) -> Attachment:
        """
        Get an attachment by ID.

        Args:
            id: The attachment ID

        Returns:
            The attachment object

        Raises:
            AttachmentOperationError: If the attachment doesn't exist or can't be retrieved
        """
        query = """
        query Attachment($id: String!) {
            attachment(id: $id) {
                id
                title
                subtitle
                source
                sourceType
                url
                issue {
                    id
                }
                creator {
                    id
                }
                metadata
                groupBySource
                createdAt
                updatedAt
                archivedAt
            }
        }
        """
        result = self.client.query(query, variables={"id": id})
        if not result.get("attachment"):
            raise AttachmentOperationError(
                f"Attachment {id} not found",
                operation="get",
                data={"attachment_id": id}
            )
        return Attachment(**result["attachment"])

    def create_url(
        self,
        url: str,
        issue_id: str,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Attachment:
        """
        Create a URL attachment.

        Args:
            url: URL to attach
            issue_id: ID of the issue to attach to
            title: Optional title (defaults to URL)
            subtitle: Optional subtitle
            metadata: Optional metadata

        Returns:
            The created attachment

        Raises:
            AttachmentOperationError: If the attachment creation fails
        """
        # Include source in metadata for URL attachments
        metadata = metadata or {}
        metadata["source"] = AttachmentSource.URL.value

        variables = {
            "input": {
                "url": url,
                "issueId": issue_id,
                "title": title or url,
                "subtitle": subtitle,
                "metadata": metadata,
            }
        }

        return self._create_attachment(variables)

    def create_from_source(
        self,
        source: AttachmentSource,
        url: str,
        issue_id: str,
        title: str,
        subtitle: Optional[str] = None,
        source_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Attachment:
        """
        Create an attachment from an external source.

        Args:
            source: Source type (e.g., GDRIVE, FIGMA)
            url: URL to the source
            issue_id: ID of the issue to attach to
            title: Attachment title
            subtitle: Optional subtitle
            source_type: Optional specific type within the source
            metadata: Optional source-specific metadata

        Returns:
            The created attachment

        Raises:
            AttachmentOperationError: If the attachment creation fails
        """
        if source == AttachmentSource.URL:
            return self.create_url(url, issue_id, title, subtitle, metadata)

        # For non-URL attachments, include the source in metadata
        metadata = metadata or {}
        metadata["source"] = source.value
        if source_type:
            metadata["sourceType"] = source_type

        variables = {
            "input": {
                "url": url,
                "issueId": issue_id,
                "title": title,
                "subtitle": subtitle,
                "metadata": metadata,
            }
        }

        return self._create_attachment(variables)

    def _create_attachment(self, variables: Dict[str, Any]) -> Attachment:
        """Internal method to create attachments."""
        query = """
        mutation CreateAttachment($input: AttachmentCreateInput!) {
            attachmentCreate(input: $input) {
                success
                attachment {
                    id
                    title
                    subtitle
                    source
                    sourceType
                    url
                    issue {
                        id
                    }
                    creator {
                        id
                    }
                    metadata
                    groupBySource
                    createdAt
                    updatedAt
                    archivedAt
                }
            }
        }
        """
        result = self.client.query(query, variables=variables)
        create_result = result.get("attachmentCreate", {})
        
        if not create_result.get("success"):
            raise AttachmentOperationError(
                "Failed to create attachment",
                operation="create",
                data={"input": variables["input"]}
            )
        
        return Attachment(**create_result["attachment"])

    def delete(self, id: str) -> bool:
        """
        Delete an attachment.

        Args:
            id: Attachment ID

        Returns:
            True if the attachment was deleted successfully

        Raises:
            AttachmentOperationError: If the deletion fails
        """
        query = """
        mutation DeleteAttachment($id: ID!) {
            attachmentDelete(id: $id) {
                success
                _destroyedId
            }
        }
        """
        result = self.client.query(query, variables={"id": id})
        delete_result = result.get("attachmentDelete", {})
        
        if not delete_result.get("success"):
            raise AttachmentOperationError(
                f"Failed to delete attachment {id}",
                operation="delete",
                data={"attachment_id": id}
            )
        
        return True

    def list_for_issue(
        self,
        issue_id: str,
        first: int = 50,
        after: Optional[str] = None,
    ) -> Iterator[Attachment]:
        """
        List attachments for an issue.

        Args:
            issue_id: Issue ID to get attachments for
            first: Number of attachments to fetch per page
            after: Cursor for pagination

        Returns:
            Iterator of attachments
        """
        query = """
        query IssueAttachments($issueId: String!, $first: Int!, $after: String) {
            issue(id: $issueId) {
                attachments(first: $first, after: $after) {
                    nodes {
                        id
                        title
                        subtitle
                        source
                        sourceType
                        url
                        issue {
                            id
                        }
                        creator {
                            id
                        }
                        metadata
                        groupBySource
                        createdAt
                        updatedAt
                        archivedAt
                    }
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                }
            }
        }
        """
        variables = {
            "issueId": issue_id,
            "first": first,
            "after": after,
        }

        while True:
            result = self.client.query(query, variables=variables)
            issue = result.get("issue")
            if not issue:
                raise AttachmentOperationError(
                    f"Issue {issue_id} not found",
                    operation="list",
                    data={"issue_id": issue_id}
                )
            
            attachments = issue["attachments"]
            for node in attachments["nodes"]:
                yield Attachment(**node)

            if not attachments["pageInfo"]["hasNextPage"]:
                break

            variables["after"] = attachments["pageInfo"]["endCursor"] 