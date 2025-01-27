"""
Example script to delete test issues with a specific title.
"""
from linear import LinearClient

def main():
    # Initialize client
    client = LinearClient()

    # Get authenticated user info
    me = client.me
    print(f"Authenticated as: {me.name}")

    # Find and delete issues with the specified title
    all_issues = client.issues.list()
    issues = [issue for issue in all_issues if issue.title == "Test issue with comments and attachments" or issue.title == "Test issue from SDK"]
    
    if not issues:
        print("No matching issues found")
        return

    deleted_count = 0
    for issue in issues:
        client.issues.delete(issue.id)
        deleted_count += 1
        print(f"Deleted issue: {issue.identifier}")

    print(f"\nDeleted {deleted_count} issue(s)")

if __name__ == "__main__":
    main()
