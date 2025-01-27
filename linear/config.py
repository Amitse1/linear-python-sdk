"""
Configuration management for the Linear SDK.
"""
import os
from typing import Optional

from pydantic import BaseModel, Field


class LinearConfig(BaseModel):
    """Configuration settings for the Linear SDK."""
    api_key: str = Field(..., description="Linear API key")
    api_url: str = Field(
        default="https://api.linear.app/graphql",
        description="Linear API URL"
    )
    timeout: int = Field(
        default=30,
        description="Request timeout in seconds",
        ge=1
    )

    @classmethod
    def from_env(cls, env_prefix: str = "LINEAR_") -> "LinearConfig":
        """
        Create configuration from environment variables.
        
        Looks for:
        - LINEAR_API_KEY: Required
        - LINEAR_API_URL: Optional
        - LINEAR_TIMEOUT: Optional
        """
        api_key = os.environ.get(f"{env_prefix}API_KEY")
        if not api_key:
            raise ValueError(
                f"Missing {env_prefix}API_KEY environment variable"
            )
        
        return cls(
            api_key=api_key,
            api_url=os.environ.get(
                f"{env_prefix}API_URL",
                "https://api.linear.app/graphql"
            ),
            timeout=int(os.environ.get(f"{env_prefix}TIMEOUT", "30"))
        ) 