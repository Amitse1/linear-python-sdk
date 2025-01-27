# Linear Python (Unofficial) SDK

A Python client for the [Linear](https://linear.app) API. This SDK provides a convenient interface to interact with Linear's GraphQL API.

## Installation

```bash
pip install linear-sdk
```

## Quick Start

```python
from linear import LinearClient

# Initialize the client
client = LinearClient("your_api_key")

# Get all issues assigned to me
my_issues = client.issues.list(assignee=client.me)

# Create a new issue
new_issue = client.issues.create(
    title="Bug: Something is broken",
    description="This needs to be fixed",
    team_id="TEAM_ID"
)

# Get a specific issue
issue = client.issues.get("ISS-123")
```

## Features

- Full Linear API coverage
- Type hints for better IDE support
- Intuitive Pythonic interface
- Comprehensive test suite
- Rich documentation

## Authentication

You can get your API key from Linear by going to Settings > API > Personal API keys.

## License

MIT License 