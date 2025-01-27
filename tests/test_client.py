"""
Tests for the Linear client.
"""
import os
from unittest.mock import Mock, patch

import pytest
from requests import Session

from linear import LinearClient
from linear.config import LinearConfig
from linear.errors import AuthenticationError, LinearError


def test_client_init_with_key():
    """Test client initialization with API key."""
    client = LinearClient(api_key="test-key")
    assert client.config.api_key == "test-key"
    assert isinstance(client._session, Session)


def test_client_init_with_config():
    """Test client initialization with config object."""
    config = LinearConfig(api_key="test-key")
    client = LinearClient(config=config)
    assert client.config == config


def test_client_init_from_env():
    """Test client initialization from environment variables."""
    with patch.dict(os.environ, {"LINEAR_API_KEY": "env-key"}):
        client = LinearClient()
        assert client.config.api_key == "env-key"


def test_client_init_no_key():
    """Test client initialization with no API key raises error."""
    with patch.dict(os.environ, clear=True):
        with pytest.raises(ValueError):
            LinearClient()


@patch("linear.client.execute_query")
def test_client_query(mock_execute):
    """Test GraphQL query execution."""
    mock_execute.return_value = {"data": {"test": "value"}}
    
    client = LinearClient(api_key="test-key")
    result = client.query("query { test }")
    
    assert result == {"data": {"test": "value"}}
    mock_execute.assert_called_once()


@patch("linear.client.execute_query")
def test_client_query_error(mock_execute):
    """Test GraphQL query error handling."""
    mock_execute.side_effect = Exception("Test error")
    
    client = LinearClient(api_key="test-key")
    with pytest.raises(LinearError):
        client.query("query { test }")


@patch("linear.client.execute_query")
def test_client_me(mock_execute):
    """Test getting authenticated user."""
    mock_execute.return_value = {
        "viewer": {
            "id": "user-id",
            "name": "Test User",
            "email": "test@example.com"
        }
    }
    
    client = LinearClient(api_key="test-key")
    user = client.me
    
    assert user["id"] == "user-id"
    assert user["name"] == "Test User"
    assert user["email"] == "test@example.com" 