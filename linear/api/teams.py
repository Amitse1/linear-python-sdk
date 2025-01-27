"""
Linear Teams API resource.
"""
from typing import Optional, List, Dict, Any, Iterator

from linear.models.team import Team
from linear.errors import LinearError


class TeamOperationError(LinearError):
    """Raised when a team operation fails."""
    def __init__(self, message: str, operation: str, data: Optional[Dict] = None):
        super().__init__(message)
        self.operation = operation
        self.data = data or {}


class TeamsResource:
    """
    Resource for interacting with Linear teams.
    """

    def __init__(self, client):
        self.client = client

    def get(self, id: str) -> Team:
        """
        Get a team by ID.

        Args:
            id: The team ID or key

        Returns:
            The team object

        Raises:
            TeamOperationError: If the team doesn't exist or can't be retrieved
        """
        query = """
        query Team($id: String!) {
            team(id: $id) {
                id
                name
                key
                description
                organization {
                    id
                }
                private
                defaultIssueState {
                    id
                    name
                    type
                    color
                    position
                    description
                    team {
                        id
                    }
                    createdAt
                    updatedAt
                    archivedAt
                }
                autoArchivePeriod
                autoClosePeriod
                cyclesEnabled
                cycleDuration
                cycleCooldownTime
                triageEnabled
                createdAt
                updatedAt
                archivedAt
            }
        }
        """
        result = self.client.query(query, variables={"id": id})
        if not result.get("team"):
            raise TeamOperationError(
                f"Team {id} not found",
                operation="get",
                data={"team_id": id}
            )
        return Team(**result["team"])

    def list(
        self,
        include_archived: bool = False,
        first: int = 50,
        after: Optional[str] = None,
    ) -> Iterator[Team]:
        """
        List teams.

        Args:
            include_archived: Include archived teams
            first: Number of teams to fetch per page
            after: Cursor for pagination

        Returns:
            Iterator of teams
        """
        query = """
        query Teams($first: Int!, $after: String, $includeArchived: Boolean) {
            teams(
                first: $first,
                after: $after,
                includeArchived: $includeArchived
            ) {
                nodes {
                    id
                    name
                    key
                    description
                    organization {
                        id
                    }
                    private
                    defaultIssueState {
                        id
                        name
                        type
                        color
                        position
                        description
                        team {
                            id
                        }
                        createdAt
                        updatedAt
                        archivedAt
                    }
                    autoArchivePeriod
                    autoClosePeriod
                    cyclesEnabled
                    cycleDuration
                    cycleCooldownTime
                    triageEnabled
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
            "includeArchived": include_archived
        }

        while True:
            result = self.client.query(query, variables=variables)
            teams = result["teams"]
            
            for node in teams["nodes"]:
                yield Team(**node)

            if not teams["pageInfo"]["hasNextPage"]:
                break

            variables["after"] = teams["pageInfo"]["endCursor"] 