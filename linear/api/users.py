"""
Linear Users API resource.
"""
from typing import Optional, List, Dict, Any, Iterator

from linear.models.user import User
from linear.errors import LinearError


class UserOperationError(LinearError):
    """Raised when a user operation fails."""
    def __init__(self, message: str, operation: str, data: Optional[Dict] = None):
        super().__init__(message)
        self.operation = operation
        self.data = data or {}


class UsersResource:
    """
    Resource for interacting with Linear users.
    """

    def __init__(self, client):
        self.client = client

    def get(self, id: str) -> User:
        """
        Get a user by ID.

        Args:
            id: The user ID

        Returns:
            The user object

        Raises:
            UserOperationError: If the user doesn't exist or can't be retrieved
        """
        query = """
        query User($id: ID!) {
            user(id: $id) {
                id
                name
                displayName
                email
                avatarUrl
                organization {
                    id
                }
                active
                lastSeen
                timezone
                isMe
                teams {
                    nodes {
                        id
                    }
                }
                createdAt
                updatedAt
                archivedAt
            }
        }
        """
        result = self.client.query(query, variables={"id": id})
        if not result.get("user"):
            raise UserOperationError(
                f"User {id} not found",
                operation="get",
                data={"user_id": id}
            )
        return User(**result["user"])

    def list(
        self,
        team_id: Optional[str] = None,
        include_archived: bool = False,
        include_disabled: bool = False,
        first: int = 50,
        after: Optional[str] = None,
    ) -> Iterator[User]:
        """
        List users.

        Args:
            team_id: Filter by team
            include_archived: Include archived users
            include_disabled: Include disabled users
            first: Number of users to fetch per page
            after: Cursor for pagination

        Returns:
            Iterator of users
        """
        query = """
        query Users(
            $first: Int!,
            $after: String,
            $includeArchived: Boolean,
            $includeDisabled: Boolean
        ) {
            users(
                first: $first,
                after: $after,
                includeArchived: $includeArchived,
                includeDisabled: $includeDisabled
            ) {
                nodes {
                    id
                    name
                    displayName
                    email
                    avatarUrl
                    organization {
                        id
                    }
                    active
                    lastSeen
                    timezone
                    isMe
                    teams {
                        nodes {
                            id
                        }
                    }
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
        """
        variables = {
            "first": first,
            "after": after,
            "includeArchived": include_archived,
            "includeDisabled": include_disabled
        }

        while True:
            result = self.client.query(query, variables=variables)
            users = result["users"]
            
            for node in users["nodes"]:
                user = User(**node)
                # Filter by team if specified
                if team_id and team_id not in user.team_ids:
                    continue
                yield user

            if not users["pageInfo"]["hasNextPage"]:
                break

            variables["after"] = users["pageInfo"]["endCursor"]

    def me(self) -> User:
        """
        Get the authenticated user.

        Returns:
            The authenticated user object

        Raises:
            UserOperationError: If the user can't be retrieved
        """
        query = """
        query Me {
            viewer {
                id
                name
                displayName
                email
                avatarUrl
                organization {
                    id
                }
                active
                lastSeen
                timezone
                isMe
                teams {
                    nodes {
                        id
                    }
                }
                createdAt
                updatedAt
                archivedAt
            }
        }
        """
        result = self.client.query(query)
        if not result.get("viewer"):
            raise UserOperationError(
                "Failed to get authenticated user",
                operation="me"
            )
        return User(**result["viewer"]) 