"""
Example of issue collaboration using comments and attachments.
"""
from linear import LinearClient
from linear.models.attachment import AttachmentSource


def main():
    # Initialize client
    client = LinearClient()
    me = client.me

    # Get my default team
    if not me.default_team_id:
        print("No default team set")
        return

    # Create a test issue
    issue = client.issues.create(
        title="Test issue with comments and attachments",
        description="This is a test issue to demonstrate comments and attachments",
        team_id=me.default_team_id,
    )
    print(f"Created issue: {issue.url}")

    # Add a comment
    comment = client.comments.create(
        body="Here's a design document for review",
        issue_id=issue.id
    )
    print(f"Added comment: {comment.body}")

    # Add a reply to the comment
    reply = client.comments.create(
        body="Thanks for sharing! I'll take a look.",
        issue_id=issue.id,
        parent_id=comment.id
    )
    print(f"Added reply: {reply.body}")

    # Add attachments from different sources
    # 1. URL attachment
    url_attachment = client.attachments.create_url(
        url="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        issue_id=issue.id,
        title="Design Document",
        subtitle="Latest version of the design"
    )
    print(f"Added URL attachment: {url_attachment.title}")

    # 2. Figma attachment
    figma_attachment = client.attachments.create_from_source(
        source=AttachmentSource.FIGMA,
        url="<URL>",
        issue_id=issue.id,
        title="UI Design",
        subtitle="High-fidelity mockups",
        metadata={
            "fileKey": "xyz",
            "nodeId": "123",
            "type": "design"
        }
    )
    print(f"Added Figma attachment: {figma_attachment.title}")

    # List all comments
    print("\nComments:")
    comments = client.comments.list_for_issue(issue.id)
    for comment in comments:
        prefix = "  ↳ " if comment.parent_id else "- "
        print(f"{prefix}{comment.body}")
        if getattr(comment, 'edited_at', None):  # Check if comment was edited
            print("  (edited)")

    # List all attachments
    print("\nAttachments:")
    attachments = client.attachments.list_for_issue(issue.id)
    for attachment in attachments:
        print(f"- [{attachment.source}] {attachment.title}")  # Changed from source_name to source
        if attachment.subtitle:
            print(f"  {attachment.subtitle}")

    # Clean up - delete the test issue
    client.issues.delete(issue.id)
    print("\nDeleted test issue")


if __name__ == "__main__":
    main() 