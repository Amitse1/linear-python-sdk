"""
Linear API client implementation.
"""
from typing import Optional, Union

import requests
import logging

from linear.config import LinearConfig
from linear.errors import LinearError
from linear.utils.graphql import execute_query
from linear.api.issues import IssuesResource
from linear.api.teams import TeamsResource
from linear.api.users import UsersResource
from linear.api.comments import CommentsResource
from linear.api.attachments import AttachmentsResource
from linear.api.workflow_states import WorkflowStatesResource
from linear.models.user import User

logger = logging.getLogger(__name__)


class LinearClient:
    """
    Main client class for interacting with the Linear API.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        config: Optional[LinearConfig] = None,
    ):
        """
        Initialize a new Linear API client.

        Args:
            api_key: Your Linear API key (can also be set via LINEAR_API_KEY env var)
            config: Optional configuration object
        """
        if config is None:
            if api_key is None:
                config = LinearConfig.from_env()
            else:
                config = LinearConfig(api_key=api_key)
        
        self.config = config
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"{config.api_key}",
            "Content-Type": "application/json",
        })
        
        # Initialize API resources
        self.issues = IssuesResource(self)
        self.teams = TeamsResource(self)
        self.users = UsersResource(self)
        self.comments = CommentsResource(self)
        self.attachments = AttachmentsResource(self)
        self.workflow_states = WorkflowStatesResource(self)

    def query(self, query_string, variables=None):
        logger.debug(f"Sending GraphQL query: {query_string}")
        logger.debug(f"Variables: {variables}")
        try:
            response = requests.post(
                self.config.api_url,
                json={
                    'query': query_string,
                    'variables': variables
                },
                headers=self._session.headers
            )
            
            # Add better error handling
            if response.status_code != 200:
                error_data = response.json() if response.text else "No error details available"
                raise LinearError(
                    f"Query failed with status {response.status_code}. "
                    f"Error details: {error_data}"
                )
            
            result = response.json()
            
            # Check for GraphQL errors
            if 'errors' in result:
                raise LinearError(f"GraphQL errors: {result['errors']}")
            
            return result['data']
            
        except requests.exceptions.RequestException as e:
            raise LinearError(f"Request failed: {str(e)}") from e

    @property
    def me(self) -> User:
        """Get the authenticated user."""
        return self.users.me() 