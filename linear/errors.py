"""
Custom exceptions for the Linear SDK.
"""

class LinearError(Exception):
    """Base exception for Linear SDK errors."""
    pass


class AuthenticationError(LinearError):
    """Raised when authentication fails."""
    pass


class GraphQLError(LinearError):
    """Raised when a GraphQL query fails."""
    def __init__(self, message: str, errors: list = None):
        super().__init__(message)
        self.errors = errors or []


class RateLimitError(LinearError):
    """Raised when API rate limit is exceeded."""
    pass


class NetworkError(LinearError):
    """Raised when network requests fail."""
    pass 