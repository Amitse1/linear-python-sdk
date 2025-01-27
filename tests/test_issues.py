"""
Tests for the Issues API resource.
"""
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from linear import LinearClient
from linear.models.issue import Issue, IssueState, IssuePriority
from linear.api.issues import IssueOperationError


@pytest.fixture
def client():
    """Create a test client."""
    return LinearClient(api_key="test-key")


@pytest.fixture
def mock_issue_data():
    """Create mock issue data."""
    return {
        "id": "issue-id",
        "title": "Test Issue",
        "description": "Test description",
        "state": "backlog",
        "priority": 2,  # MEDIUM priority
        "number": 123,
        "identifier": "TEST-123",
        "teamId": "team-id",
        "assigneeId": "user-id",
        "creatorId": "creator-id",
        "url": "https://linear.app/test/issue/TEST-123",
        "createdAt": "2023-01-01T00:00:00Z",
        "updatedAt": "2023-01-01T00:00:00Z",
    }


def test_get_issue(client, mock_issue_data):
    """Test getting a single issue."""
    with patch.object(client, "query") as mock_query:
        mock_query.return_value = {"issue": mock_issue_data}
        
        issue = client.issues.get("TEST-123")
        
        assert isinstance(issue, Issue)
        assert issue.id == "issue-id"
        assert issue.title == "Test Issue"
        assert issue.state == IssueState.BACKLOG
        assert issue.priority == IssuePriority.MEDIUM


def test_get_nonexistent_issue(client):
    """Test getting an issue that doesn't exist."""
    with patch.object(client, "query") as mock_query:
        mock_query.return_value = {"issue": None}
        
        with pytest.raises(IssueOperationError) as exc_info:
            client.issues.get("NONEXISTENT-123")
        
        assert exc_info.value.operation == "get"
        assert "not found" in str(exc_info.value)


def test_create_issue(client, mock_issue_data):
    """Test creating an issue."""
    with patch.object(client, "query") as mock_query:
        mock_query.return_value = {"issueCreate": {"success": True, "issue": mock_issue_data}}
        
        issue = client.issues.create(
            title="Test Issue",
            team_id="team-id",
            description="Test description",
            state=IssueState.BACKLOG,
            priority=IssuePriority.MEDIUM,
        )
        
        assert isinstance(issue, Issue)
        assert issue.title == "Test Issue"
        assert issue.team_id == "team-id"
        mock_query.assert_called_once()


def test_create_issue_failure(client):
    """Test handling of issue creation failure."""
    with patch.object(client, "query") as mock_query:
        mock_query.return_value = {
            "issueCreate": {
                "success": False,
                "errors": [{"message": "Invalid team ID"}]
            }
        }
        
        with pytest.raises(IssueOperationError) as exc_info:
            client.issues.create(
                title="Test Issue",
                team_id="invalid-team",
            )
        
        assert exc_info.value.operation == "create"
        assert "Failed to create issue" in str(exc_info.value)
        assert "invalid-team" in str(exc_info.value.data)


def test_update_issue(client, mock_issue_data):
    """Test updating an issue."""
    with patch.object(client, "query") as mock_query:
        mock_query.return_value = {"issueUpdate": {"success": True, "issue": mock_issue_data}}
        
        issue = client.issues.update(
            "TEST-123",
            title="Updated Title",
            state=IssueState.STARTED,
        )
        
        assert isinstance(issue, Issue)
        mock_query.assert_called_once()


def test_update_issue_failure(client):
    """Test handling of issue update failure."""
    with patch.object(client, "query") as mock_query:
        mock_query.return_value = {
            "issueUpdate": {
                "success": False,
                "errors": [{"message": "Issue not found"}]
            }
        }
        
        with pytest.raises(IssueOperationError) as exc_info:
            client.issues.update(
                "NONEXISTENT-123",
                title="Updated Title"
            )
        
        assert exc_info.value.operation == "update"
        assert "Failed to update issue" in str(exc_info.value)


def test_delete_issue(client):
    """Test deleting an issue."""
    with patch.object(client, "query") as mock_query:
        mock_query.return_value = {
            "issueDelete": {
                "success": True,
                "_destroyedId": "issue-id"
            }
        }
        
        result = client.issues.delete("TEST-123")
        assert result is True
        mock_query.assert_called_once()


def test_delete_issue_failure(client):
    """Test handling of issue deletion failure."""
    with patch.object(client, "query") as mock_query:
        mock_query.return_value = {
            "issueDelete": {
                "success": False,
                "errors": [{"message": "Not authorized"}]
            }
        }
        
        with pytest.raises(IssueOperationError) as exc_info:
            client.issues.delete("TEST-123")
        
        assert exc_info.value.operation == "delete"
        assert "Failed to delete issue" in str(exc_info.value)


def test_list_issues(client, mock_issue_data):
    """Test listing issues."""
    mock_response = {
        "issues": {
            "nodes": [mock_issue_data],
            "pageInfo": {
                "hasNextPage": False,
                "endCursor": None
            }
        }
    }
    
    with patch.object(client, "query") as mock_query:
        mock_query.return_value = mock_response
        
        issues = list(client.issues.list(team_id="team-id"))
        
        assert len(issues) == 1
        assert isinstance(issues[0], Issue)
        assert issues[0].id == "issue-id"
        mock_query.assert_called_once()


def test_list_issues_pagination(client, mock_issue_data):
    """Test issue list pagination."""
    responses = [
        {
            "issues": {
                "nodes": [mock_issue_data],
                "pageInfo": {
                    "hasNextPage": True,
                    "endCursor": "cursor1"
                }
            }
        },
        {
            "issues": {
                "nodes": [mock_issue_data],
                "pageInfo": {
                    "hasNextPage": False,
                    "endCursor": None
                }
            }
        }
    ]
    
    with patch.object(client, "query") as mock_query:
        mock_query.side_effect = responses
        
        issues = list(client.issues.list())
        
        assert len(issues) == 2
        assert mock_query.call_count == 2


def test_issue_priority_order():
    """Test that issue priorities are ordered correctly."""
    assert IssuePriority.NO_PRIORITY.value == 0
    assert IssuePriority.LOW.value == 1
    assert IssuePriority.MEDIUM.value == 2
    assert IssuePriority.HIGH.value == 3
    assert IssuePriority.URGENT.value == 4
    
    # Test ordering
    assert IssuePriority.NO_PRIORITY < IssuePriority.LOW
    assert IssuePriority.LOW < IssuePriority.MEDIUM
    assert IssuePriority.MEDIUM < IssuePriority.HIGH
    assert IssuePriority.HIGH < IssuePriority.URGENT 