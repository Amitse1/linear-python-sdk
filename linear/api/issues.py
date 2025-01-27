"""
Linear Issues API resource.
"""
from typing import Optional, List, Dict, Any, Iterator

from linear.models.issue import Issue, WorkflowStateType, IssuePriority
from linear.errors import LinearError


class IssueOperationError(LinearError):
    """Raised when an issue operation fails."""
    def __init__(self, message: str, operation: str, data: Optional[Dict] = None):
        super().__init__(message)
        self.operation = operation
        self.data = data or {}


class IssuesResource:
    """
    Resource for interacting with Linear issues.
    """

    def __init__(self, client):
        self.client = client

    def get(self, id: str) -> Issue:
        """
        Get an issue by ID.

        Args:
            id: The issue ID or key (e.g. "ISS-123")

        Returns:
            The issue object

        Raises:
            IssueOperationError: If the issue doesn't exist or can't be retrieved
        """
        query = """
        query Issue($id: String!) {
            issue(id: $id) {
                id
                title
                description
                state {
                    id
                    name
                    type
                    color
                    position
                    description
                    team {
                        id
                        name
                        key
                        description
                        organization {
                            id
                        }
                        createdAt
                        updatedAt
                        archivedAt
                    }
                    createdAt
                    updatedAt
                    archivedAt
                }
                priority
                number
                identifier
                team {
                    id
                    name
                    key
                    description
                    organization {
                        id
                    }
                    createdAt
                    updatedAt
                    archivedAt
                }
                assignee {
                    id
                    name
                    displayName
                    email
                    avatarUrl
                    organization {
                        id
                    }
                    createdAt
                    updatedAt
                    archivedAt
                }
                creator {
                    id
                    name
                    displayName
                    email
                    avatarUrl
                    organization {
                        id
                    }
                    createdAt
                    updatedAt
                    archivedAt
                }
                dueDate
                startedAt
                completedAt
                canceledAt
                labelIds
                parent {
                    id
                }
                children {
                    nodes {
                        id
                    }
                }
                url
                branchName
                estimate
                createdAt
                updatedAt
                archivedAt
            }
        }
        """
        result = self.client.query(query, variables={"id": id})
        if not result.get("issue"):
            raise IssueOperationError(
                f"Issue {id} not found",
                operation="get",
                data={"issue_id": id}
            )
        return Issue(**result["issue"])

    def create(
        self,
        title: str,
        team_id: str,
        description: Optional[str] = None,
        state_id: Optional[str] = None,
        priority: Optional[IssuePriority] = None,
        assignee_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        **kwargs
    ) -> Issue:
        """
        Create a new issue.

        Args:
            title: Issue title
            team_id: Team ID
            description: Issue description in markdown
            state_id: ID of the workflow state
            priority: Issue priority
            assignee_id: ID of user to assign to
            parent_id: Parent issue ID
            **kwargs: Additional fields to set (must be valid IssueCreateInput fields)

        Returns:
            The created issue

        Raises:
            IssueOperationError: If the issue creation fails
        """
        # Define valid input fields for IssueCreateInput
        valid_input_fields = {
            "title", "teamId", "description", "stateId", "priority",
            "assigneeId", "parentId", "estimate", "dueDate", "labelIds"
        }

        # Filter out any invalid fields from kwargs
        filtered_kwargs = {
            k: v for k, v in kwargs.items() 
            if k in valid_input_fields
        }

        variables = {
            "input": {
                "title": title,
                "teamId": team_id,
                "description": description,
                "stateId": state_id,
                "priority": priority.value if priority else None,
                "assigneeId": assignee_id,
                "parentId": parent_id,
                **filtered_kwargs
            }
        }

        # Remove None values from input
        variables["input"] = {
            k: v for k, v in variables["input"].items()
            if v is not None
        }

        query = """
        mutation CreateIssue($input: IssueCreateInput!) {
            issueCreate(input: $input) {
                success
                issue {
                    id
                    title
                    description
                    state {
                        id
                        name
                        type
                        color
                        position
                        description
                        team {
                            id
                            name
                            key
                            description
                            organization {
                                id
                            }
                            createdAt
                            updatedAt
                            archivedAt
                        }
                        createdAt
                        updatedAt
                        archivedAt
                    }
                    priority
                    number
                    identifier
                    team {
                        id
                        name
                        key
                        description
                        organization {
                            id
                        }
                        createdAt
                        updatedAt
                        archivedAt
                    }
                    assignee {
                        id
                        name
                        displayName
                        email
                        avatarUrl
                        organization {
                            id
                        }
                        createdAt
                        updatedAt
                        archivedAt
                    }
                    creator {
                        id
                        name
                        displayName
                        email
                        avatarUrl
                        organization {
                            id
                        }
                        createdAt
                        updatedAt
                        archivedAt
                    }
                    dueDate
                    startedAt
                    completedAt
                    canceledAt
                    labelIds
                    parent {
                        id
                    }
                    children {
                        nodes {
                            id
                        }
                    }
                    url
                    branchName
                    estimate
                    createdAt
                    updatedAt
                    archivedAt
                }
            }
        }
        """
        result = self.client.query(query, variables=variables)
        create_result = result.get("issueCreate", {})
        
        if not create_result.get("success"):
            raise IssueOperationError(
                "Failed to create issue",
                operation="create",
                data={"input": variables["input"], "errors": create_result.get("errors")}
            )
        
        return Issue(**create_result["issue"])

    def delete(self, id: str) -> bool:
        """
        Delete an issue.

        Args:
            id: Issue ID or key

        Returns:
            True if the issue was deleted successfully

        Raises:
            IssueOperationError: If the deletion fails
        """
        query = """
        mutation DeleteIssue($id: String!) {
            issueDelete(id: $id) {
                success
            }
        }
        """
        result = self.client.query(query, variables={"id": id})
        delete_result = result.get("issueDelete", {})
        
        if not delete_result.get("success"):
            raise IssueOperationError(
                f"Failed to delete issue {id}",
                operation="delete",
                data={"issue_id": id}
            )
        
        return True

    def update(self, id: str, **fields) -> Issue:
        """
        Update an issue.

        Args:
            id: Issue ID
            **fields: Fields to update

        Returns:
            The updated issue

        Raises:
            IssueOperationError: If the update fails
        """
        # Define valid input fields for IssueUpdateInput
        valid_input_fields = {
            "title", "description", "stateId", "priority",
            "assigneeId", "parentId", "estimate", "dueDate", "labelIds"
        }

        # Filter out any invalid fields and handle enums
        filtered_fields = {
            k: v.value if isinstance(v, (WorkflowStateType, IssuePriority)) else v
            for k, v in fields.items()
            if k in valid_input_fields
        }

        variables = {
            "id": id,
            "input": filtered_fields
        }

        query = """
        mutation UpdateIssue($id: String!, $input: IssueUpdateInput!) {
            issueUpdate(id: $id, input: $input) {
                success
                issue {
                    id
                    title
                    description
                    state {
                        id
                        name
                        type
                        color
                        position
                        description
                        team {
                            id
                            name
                            key
                            description
                            organization {
                                id
                            }
                            createdAt
                            updatedAt
                            archivedAt
                        }
                        createdAt
                        updatedAt
                        archivedAt
                    }
                    priority
                    number
                    identifier
                    team {
                        id
                        name
                        key
                        description
                        organization {
                            id
                        }
                        createdAt
                        updatedAt
                        archivedAt
                    }
                    assignee {
                        id
                        name
                        displayName
                        email
                        avatarUrl
                        organization {
                            id
                        }
                        createdAt
                        updatedAt
                        archivedAt
                    }
                    creator {
                        id
                        name
                        displayName
                        email
                        avatarUrl
                        organization {
                            id
                        }
                        createdAt
                        updatedAt
                        archivedAt
                    }
                    dueDate
                    startedAt
                    completedAt
                    canceledAt
                    labelIds
                    parent {
                        id
                    }
                    children {
                        nodes {
                            id
                        }
                    }
                    url
                    branchName
                    estimate
                    createdAt
                    updatedAt
                    archivedAt
                }
            }
        }
        """
        result = self.client.query(query, variables=variables)
        update_result = result.get("issueUpdate", {})
        
        if not update_result.get("success"):
            raise IssueOperationError(
                f"Failed to update issue {id}",
                operation="update",
                data={"issue_id": id, "input": variables["input"]}
            )
        
        return Issue(**update_result["issue"])

    def list(
        self,
        team_id: Optional[str] = None,
        assignee_id: Optional[str] = None,
        creator_id: Optional[str] = None,
        state: Optional[WorkflowStateType] = None,
        priority: Optional[IssuePriority] = None,
        include_archived: bool = False,
        first: int = 50,
        after: Optional[str] = None,
    ) -> Iterator[Issue]:
        """
        List issues matching the given filters.

        Args:
            team_id: Filter by team
            assignee_id: Filter by assignee
            creator_id: Filter by creator
            state: Filter by state
            priority: Filter by priority
            include_archived: Include archived issues
            first: Number of issues to fetch per page
            after: Cursor for pagination

        Returns:
            Iterator of issues
        """
        filter_dict = {}
        
        if team_id:
            filter_dict["team"] = {"id": {"eq": team_id}}
        if assignee_id:
            filter_dict["assignee"] = {"id": {"eq": assignee_id}}
        if creator_id:
            filter_dict["creator"] = {"id": {"eq": creator_id}}
        if state:
            filter_dict["state"] = {"type": {"eq": state.value}}
        if priority:
            filter_dict["priority"] = {"eq": priority.value}
        if not include_archived:
            filter_dict["archivedAt"] = {"null": True}

        variables = {
            "first": first,
            "after": after,
            "filter": filter_dict if filter_dict else None,
            "includeCreator": True
        }

        query = """
        query Issues($first: Int!, $after: String, $filter: IssueFilter, $includeCreator: Boolean!) {
            issues(first: $first, after: $after, filter: $filter) {
                nodes {
                    id
                    title
                    description
                    state {
                        id
                        name
                        type
                        color
                        position
                        description
                        team {
                            id
                            name
                            key
                            description
                            organization {
                                id
                            }
                            createdAt
                            updatedAt
                            archivedAt
                        }
                        createdAt
                        updatedAt
                        archivedAt
                    }
                    priority
                    number
                    identifier
                    team {
                        id
                        name
                        key
                        description
                        organization {
                            id
                        }
                        createdAt
                        updatedAt
                        archivedAt
                    }
                    assignee {
                        id
                        name
                        displayName
                        email
                        avatarUrl
                        organization {
                            id
                        }
                        createdAt
                        updatedAt
                        archivedAt
                    }
                    creator @include(if: $includeCreator) {
                        id
                        name
                        displayName
                        email
                        avatarUrl
                        organization {
                            id
                        }
                        createdAt
                        updatedAt
                        archivedAt
                    }
                    dueDate
                    startedAt
                    completedAt
                    canceledAt
                    labelIds
                    parent {
                        id
                    }
                    children {
                        nodes {
                            id
                        }
                    }
                    url
                    branchName
                    estimate
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

        while True:
            result = self.client.query(query, variables=variables)
            issues = result["issues"]
            
            for node in issues["nodes"]:
                yield Issue(**node)

            if not issues["pageInfo"]["hasNextPage"]:
                break

            variables["after"] = issues["pageInfo"]["endCursor"] 