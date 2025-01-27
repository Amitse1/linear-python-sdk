"""
Example of team and user management with the Linear SDK.
"""
import os
from datetime import datetime, timedelta

from linear import LinearClient
from linear.models.issue import WorkflowStateType, IssuePriority


def main():
    # Initialize client
    client = LinearClient()

    # Get authenticated user info
    me = client.me
    print(f"Authenticated as: {me.name} ({me.email})")
    
    # List teams
    print("\nMy teams:")
    for team in client.teams.list():
        if team.id in me.team_ids:
            print(f"- [{team.key}] {team.name}")
            
            # List team members
            print("  Members:")
            for user in client.users.list(team_id=team.id):
                print(f"  - {user.name}")
            
            # List active issues in the team
            active_issues = [
                issue for issue in client.issues.list(team_id=team.id)
                if issue.is_active
            ]
            print(f"  Active issues: {len(active_issues)}")

    # Get my default team
    if me.default_team_id:
        default_team = client.teams.get(me.default_team_id)
        print(f"\nDefault team: {default_team.name}")
        
        # Create an issue in my default team
        new_issue = client.issues.create(
            title="Test issue from SDK",
            description="This is a test issue created using the Linear Python SDK",
            team_id=default_team.id,
            state=WorkflowStateType.BACKLOG,
            priority=IssuePriority.MEDIUM,
        )
        print(f"\nCreated new issue: {new_issue.url}")


if __name__ == "__main__":
    main() 