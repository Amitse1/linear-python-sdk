"""
Linear Comments API resource.
"""
from typing import List, Optional, Dict
from linear.models.comment import Comment
from linear.errors import LinearError


class CommentOperationError(LinearError):
    """Raised when a comment operation fails."""
    def __init__(self, message: str, operation: str, data: Optional[Dict] = None):
        super().__init__(message)
        self.operation = operation
        self.data = data or {}


class CommentsResource:
    """
    Handles operations related to Linear comments.
    """
    
    def __init__(self, client):
        self.client = client

    def get(self, comment_id: str) -> Comment:
        """
        Get a comment by ID.

        Args:
            comment_id: The comment ID

        Returns:
            The comment object

        Raises:
            CommentOperationError: If the comment doesn't exist or can't be retrieved
        """
        query = """
        query Comment($id: String!) {
            comment(id: $id) {
                id
                body
                issue { id }
                user { id }
                parent { id }
                children {
                    nodes {
                        id
                    }
                }
                createdAt
                updatedAt
            }
        }
        """
        result = self.client.query(query, {'id': comment_id})
        if not result.get("comment"):
            raise CommentOperationError(
                f"Comment {comment_id} not found",
                operation="get",
                data={"comment_id": comment_id}
            )
        return Comment(**result["comment"])

    def create(self, issue_id: str, body: str, parent_id: Optional[str] = None) -> Comment:
        """
        Create a new comment.

        Args:
            issue_id: ID of the issue to comment on
            body: Comment content in markdown
            parent_id: Optional parent comment ID for replies

        Returns:
            The created comment

        Raises:
            CommentOperationError: If the comment creation fails
        """
        query = """
        mutation CommentCreate($input: CommentCreateInput!) {
            commentCreate(input: $input) {
                success
                comment {
                    id
                    body
                    issue { id }
                    user { id }
                    parent { id }
                    children {
                        nodes {
                            id
                        }
                    }
                    createdAt
                    updatedAt
                }
            }
        }
        """
        variables = {
            'input': {
                'issueId': issue_id,
                'body': body,
                'parentId': parent_id
            }
        }
        result = self.client.query(query, variables)
        create_result = result.get("commentCreate", {})
        
        if not create_result.get("success"):
            raise CommentOperationError(
                "Failed to create comment",
                operation="create",
                data={"input": variables["input"]}
            )
        
        return Comment(**create_result["comment"])

    def update(self, comment_id: str, body: str) -> Comment:
        """
        Update an existing comment.

        Args:
            comment_id: ID of the comment to update
            body: New comment content in markdown

        Returns:
            The updated comment

        Raises:
            CommentOperationError: If the update fails
        """
        query = """
        mutation CommentUpdate($id: String!, $input: CommentUpdateInput!) {
            commentUpdate(id: $id, input: $input) {
                success
                comment {
                    id
                    body
                    issue { id }
                    user { id }
                    parent { id }
                    children {
                        nodes {
                            id
                        }
                    }
                    createdAt
                    updatedAt
                }
            }
        }
        """
        variables = {
            'id': comment_id,
            'input': {
                'body': body
            }
        }
        result = self.client.query(query, variables)
        update_result = result.get("commentUpdate", {})
        
        if not update_result.get("success"):
            raise CommentOperationError(
                f"Failed to update comment {comment_id}",
                operation="update",
                data={"comment_id": comment_id, "input": variables["input"]}
            )
        
        return Comment(**update_result["comment"])

    def delete(self, comment_id: str) -> bool:
        """
        Delete a comment.

        Args:
            comment_id: ID of the comment to delete

        Returns:
            True if the comment was deleted successfully

        Raises:
            CommentOperationError: If the deletion fails
        """
        query = """
        mutation CommentDelete($id: String!) {
            commentDelete(id: $id) {
                success
            }
        }
        """
        result = self.client.query(query, {'id': comment_id})
        delete_result = result.get("commentDelete", {})
        
        if not delete_result.get("success"):
            raise CommentOperationError(
                f"Failed to delete comment {comment_id}",
                operation="delete",
                data={"comment_id": comment_id}
            )
        
        return True

    def list_for_issue(
        self,
        issue_id: str,
        first: int = 50,
        after: Optional[str] = None,
    ) -> List[Comment]:
        """
        List all comments for an issue.

        Args:
            issue_id: ID of the issue to get comments for
            first: Number of comments to fetch per page
            after: Cursor for pagination

        Returns:
            List of comments

        Raises:
            CommentOperationError: If the issue doesn't exist or comments can't be retrieved
        """
        query = """
        query IssueComments($issueId: String!, $first: Int!, $after: String) {
            issue(id: $issueId) {
                comments(first: $first, after: $after) {
                    nodes {
                        id
                        body
                        issue { id }
                        user { id }
                        parent { id }
                        createdAt
                        updatedAt
                    }
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                }
            }
        }
        """
        all_comments = []
        variables = {
            "issueId": issue_id,
            "first": first,
            "after": after
        }

        while True:
            result = self.client.query(query, variables)
            issue = result.get("issue")
            if not issue:
                raise CommentOperationError(
                    f"Issue {issue_id} not found",
                    operation="list",
                    data={"issue_id": issue_id}
                )
            
            comments = issue["comments"]
            all_comments.extend([Comment(**node) for node in comments["nodes"]])

            if not comments["pageInfo"]["hasNextPage"]:
                break

            variables["after"] = comments["pageInfo"]["endCursor"]
        
        return all_comments 