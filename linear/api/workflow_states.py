"""
Linear Workflow States API resource.
"""
from typing import Optional, List, Dict, Any, Iterator

from linear.models.issue import WorkflowState
from linear.errors import LinearError


class WorkflowStateOperationError(LinearError):
    """Raised when a workflow state operation fails."""
    def __init__(self, message: str, operation: str, data: Optional[Dict] = None):
        super().__init__(message)
        self.operation = operation
        self.data = data or {}


class WorkflowStatesResource:
    """
    Resource for interacting with Linear workflow states.
    """

    def __init__(self, client):
        self.client = client

    def get(self, id: str) -> WorkflowState:
        """
        Get a workflow state by ID.

        Args:
            id: The workflow state ID

        Returns:
            The workflow state object

        Raises:
            WorkflowStateOperationError: If the state doesn't exist or can't be retrieved
        """
        query = """
        query WorkflowState($id: ID!) {
            workflowState(id: $id) {
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
        }
        """
        result = self.client.query(query, variables={"id": id})
        if not result.get("workflowState"):
            raise WorkflowStateOperationError(
                f"Workflow state {id} not found",
                operation="get",
                data={"state_id": id}
            )
        return WorkflowState(**result["workflowState"])

    def list(
        self,
        team_id: str,
        include_archived: bool = False,
    ) -> Iterator[WorkflowState]:
        """
        List workflow states for a team.

        Args:
            team_id: Team ID to get states for
            include_archived: Include archived states

        Returns:
            Iterator of workflow states
        """
        query = """
        query TeamWorkflowStates($teamId: ID!, $includeArchived: Boolean) {
            team(id: $teamId) {
                states(includeArchived: $includeArchived) {
                    nodes {
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
                }
            }
        }
        """
        variables = {
            "teamId": team_id,
            "includeArchived": include_archived,
        }

        result = self.client.query(query, variables=variables)
        team = result.get("team")
        if not team:
            raise WorkflowStateOperationError(
                f"Team {team_id} not found",
                operation="list",
                data={"team_id": team_id}
            )

        states = team["states"]
        for node in states["nodes"]:
            yield WorkflowState(**node) 