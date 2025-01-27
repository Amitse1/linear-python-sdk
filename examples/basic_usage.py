"""
Basic example of using the Linear SDK.
"""
import os
from datetime import datetime, timedelta
import logging

from linear import LinearClient
from linear.models.issue import WorkflowStateType, IssuePriority

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def main():
    # Initialize client (will use LINEAR_API_KEY environment variable)
    client = LinearClient()

    # Print authenticated user info
    me = client.me
    print(f"Authenticated as: {me.name} ({me.email})")

    # List my active issues
    print("\nMy active issues:")
    my_issues = client.issues.list(assignee_id=me.id)
    for issue in my_issues:
        if issue.is_active:
            print(f"- [{issue.identifier}] {issue.title}")

    # Create a new issue
    new_issue = client.issues.create(
        title="Test issue from SDK",
        description="This is a test issue created using the Linear Python SDK",
        team_id=client.me.default_team_id,  # Replace with your team ID
        state=WorkflowStateType.BACKLOG,
        priority=IssuePriority.MEDIUM,
    )
    print(f"\nCreated new issue: {new_issue.url}")

    # Update the issue
    updated_issue = client.issues.update(
        new_issue.id,
        description="Updated description",
        state=WorkflowStateType.STARTED,
    )
    print(f"Updated issue state to: {updated_issue.state}")

    # List all high priority issues created in the last week
    week_ago = datetime.now() - timedelta(days=7)
    print("\nHigh priority issues from last week:")
    high_priority_issues = client.issues.list(priority=IssuePriority.HIGH)
    print(high_priority_issues)
    for issue in high_priority_issues:
        if issue.created_at >= week_ago:
            print(f"- [{issue.identifier}] {issue.title}")


if __name__ == "__main__":
    main() 