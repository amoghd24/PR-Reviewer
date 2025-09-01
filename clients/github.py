"""GitHub API Client for MCP integration.

Provides OAuth authentication and API access utilities for GitHub integration.
Follows the same patterns as Asana and Slack clients.
"""

import os
from typing import Any, Dict, Optional
import httpx
from utils.logger import get_logger

logger = get_logger(__name__)


class GitHubClient:
    """GitHub API client with OAuth support."""
    
    def __init__(self):
        """Initialize GitHub client with credentials from environment."""
        self.access_token = os.getenv("GITHUB_ACCESS_TOKEN")
        self.client_id = os.getenv("GITHUB_CLIENT_ID")
        self.client_secret = os.getenv("GITHUB_CLIENT_SECRET")
        self.default_owner = os.getenv("GITHUB_OWNER")
        
        if not self.access_token:
            raise ValueError("GITHUB_ACCESS_TOKEN environment variable is required")
            
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "pr-reviewer-mcp/0.1.0"
        }
        
    async def get_pull_request(self, owner: str, repo: str, pull_number: int) -> Dict[str, Any]:
        """Get pull request details."""
        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pull_number}"
            logger.info(f"Fetching PR #{pull_number} from {owner}/{repo}")
            
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
            
    async def get_pull_request_files(self, owner: str, repo: str, pull_number: int) -> Dict[str, Any]:
        """Get files changed in a pull request."""
        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pull_number}/files"
            logger.info(f"Fetching files for PR #{pull_number} from {owner}/{repo}")
            
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
            
    async def get_pull_request_diff(self, owner: str, repo: str, pull_number: int) -> str:
        """Get pull request diff in unified format."""
        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pull_number}"
            headers = {**self.headers, "Accept": "application/vnd.github.v3.diff"}
            logger.info(f"Fetching diff for PR #{pull_number} from {owner}/{repo}")
            
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.text
            
    async def get_pull_request_comments(self, owner: str, repo: str, pull_number: int) -> Dict[str, Any]:
        """Get pull request review comments."""
        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pull_number}/comments"
            logger.info(f"Fetching comments for PR #{pull_number} from {owner}/{repo}")
            
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
            
    async def get_pull_request_reviews(self, owner: str, repo: str, pull_number: int) -> Dict[str, Any]:
        """Get pull request reviews."""
        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pull_number}/reviews"
            logger.info(f"Fetching reviews for PR #{pull_number} from {owner}/{repo}")
            
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
            
    async def get_pull_request_status(self, owner: str, repo: str, pull_number: int) -> Dict[str, Any]:
        """Get pull request status checks."""
        # First get the PR to get the head SHA
        pr_data = await self.get_pull_request(owner, repo, pull_number)
        head_sha = pr_data["head"]["sha"]
        
        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}/repos/{owner}/{repo}/commits/{head_sha}/status"
            logger.info(f"Fetching status for PR #{pull_number} commit {head_sha}")
            
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
            
    async def validate_credentials(self) -> bool:
        """Validate GitHub credentials by checking user access."""
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/user"
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                user_data = response.json()
                logger.info(f"GitHub credentials validated for user: {user_data.get('login')}")
                return True
        except Exception as e:
            logger.error(f"GitHub credential validation failed: {e}")
            return False