"""
GraphQL utilities for the Linear SDK.
"""
from typing import Optional, Dict, Any

import requests
from graphql import parse, print_ast

from linear.errors import GraphQLError, NetworkError, AuthenticationError, RateLimitError


def validate_query(query: str) -> str:
    """
    Validate and format a GraphQL query.

    Args:
        query: The GraphQL query string

    Returns:
        The formatted query string

    Raises:
        GraphQLError: If the query is invalid
    """
    try:
        ast = parse(query)
        return print_ast(ast)
    except Exception as e:
        raise GraphQLError(f"Invalid GraphQL query: {str(e)}")


def execute_query(
    session: requests.Session,
    url: str,
    query: str,
    variables: Optional[Dict[str, Any]] = None,
    timeout: int = 30,
) -> dict:
    """
    Execute a GraphQL query against the Linear API.

    Args:
        session: The requests session to use
        url: The API endpoint URL
        query: The GraphQL query string
        variables: Optional variables for the query
        timeout: Request timeout in seconds

    Returns:
        The query response data

    Raises:
        NetworkError: If the request fails
        AuthenticationError: If authentication fails
        RateLimitError: If rate limit is exceeded
        GraphQLError: If the query execution fails
    """
    try:
        formatted_query = validate_query(query)
        payload = {"query": formatted_query}
        if variables:
            payload["variables"] = variables

        response = session.post(url, json=payload, timeout=timeout)

        if response.status_code == 401:
            raise AuthenticationError("Invalid API key")
        elif response.status_code == 429:
            raise RateLimitError("API rate limit exceeded")
        elif response.status_code != 200:
            raise NetworkError(f"Request failed with status {response.status_code}")

        result = response.json()
        if "errors" in result:
            raise GraphQLError(
                "GraphQL query failed",
                errors=result.get("errors", [])
            )

        return result["data"]

    except requests.exceptions.RequestException as e:
        raise NetworkError(f"Network error: {str(e)}")
    except ValueError as e:
        raise NetworkError(f"Invalid JSON response: {str(e)}") 