"""GitHub MCP Server - PR-4 Implementation.

A FastMCP server providing GitHub integration tools for the PR reviewer system.
Implements PR-related tools with proper error handling, validation, and OAuth authentication.
"""

import os
from typing import Optional

from dotenv import load_dotenv
from fastmcp import FastMCP

from utils.logger import get_logger
import opik
from .tools.get_pull_request import get_pull_request
from .tools.get_pull_request_diff import get_pull_request_diff
from .tools.get_pull_request_files import get_pull_request_files
from .tools.get_pull_request_comments import get_pull_request_comments
from .tools.get_pull_request_reviews import get_pull_request_reviews
from .tools.get_pull_request_status import get_pull_request_status
from .tools.list_pull_requests import list_pull_requests

# Load environment variables
load_dotenv()

# Configure logging
logger = get_logger(__name__)

# Configure Opik
opik_client = opik.Opik()

# Initialize FastMCP server
app = FastMCP(
    name="github-mcp-server",
    version="0.1.0"
)


@app.tool(
    tags=["github", "pull_request", "details", "pr-reviewer"],
    description="Get comprehensive pull request information including metadata, author, and status"
)
@opik.track(name="github_get_pull_request")
async def get_pull_request_tool(
    repo: str,
    pull_number: int
) -> dict:
    """Get detailed information about a pull request."""
    owner = os.getenv("GITHUB_OWNER")
    if not owner:
        return {"status": "error", "error": "GITHUB_OWNER environment variable must be set"}
    return await get_pull_request(owner, repo, pull_number)


@app.tool(
    tags=["github", "pull_request", "diff", "pr-reviewer"],
    description="Get the unified diff for a pull request showing all code changes"
)
@opik.track(name="github_get_pull_request_diff")
async def get_pull_request_diff_tool(
    repo: str,
    pull_number: int
) -> dict:
    """Get the unified diff for a pull request."""
    owner = os.getenv("GITHUB_OWNER")
    if not owner:
        return {"status": "error", "error": "GITHUB_OWNER environment variable must be set"}
    return await get_pull_request_diff(owner, repo, pull_number)


@app.tool(
    tags=["github", "pull_request", "files", "pr-reviewer"],
    description="Get the list of files changed in a pull request with their modifications"
)
@opik.track(name="github_get_pull_request_files")
async def get_pull_request_files_tool(
    repo: str,
    pull_number: int
) -> dict:
    """Get the list of files changed in a pull request."""
    owner = os.getenv("GITHUB_OWNER")
    if not owner:
        return {"status": "error", "error": "GITHUB_OWNER environment variable must be set"}
    return await get_pull_request_files(owner, repo, pull_number)


@app.tool(
    tags=["github", "pull_request", "comments", "pr-reviewer"],
    description="Get review comments and discussion for a pull request"
)
@opik.track(name="github_get_pull_request_comments")
async def get_pull_request_comments_tool(
    repo: str,
    pull_number: int
) -> dict:
    """Get review comments for a pull request."""
    owner = os.getenv("GITHUB_OWNER")
    if not owner:
        return {"status": "error", "error": "GITHUB_OWNER environment variable must be set"}
    return await get_pull_request_comments(owner, repo, pull_number)


@app.tool(
    tags=["github", "pull_request", "reviews", "pr-reviewer"],
    description="Get formal reviews (approved, requested changes, comments) for a pull request"
)
@opik.track(name="github_get_pull_request_reviews")
async def get_pull_request_reviews_tool(
    repo: str,
    pull_number: int
) -> dict:
    """Get formal reviews for a pull request."""
    owner = os.getenv("GITHUB_OWNER")
    if not owner:
        return {"status": "error", "error": "GITHUB_OWNER environment variable must be set"}
    return await get_pull_request_reviews(owner, repo, pull_number)


@app.tool(
    tags=["github", "pull_request", "status", "ci", "pr-reviewer"],
    description="Get status checks and CI/CD information for a pull request"
)
@opik.track(name="github_get_pull_request_status")
async def get_pull_request_status_tool(
    repo: str,
    pull_number: int
) -> dict:
    """Get status checks for a pull request."""
    owner = os.getenv("GITHUB_OWNER")
    if not owner:
        return {"status": "error", "error": "GITHUB_OWNER environment variable must be set"}
    return await get_pull_request_status(owner, repo, pull_number)


@app.tool(
    tags=["github", "repository", "pull_requests", "list", "pr-reviewer"],
    description="List all pull requests for a repository with metadata including PR numbers and descriptions"
)
@opik.track(name="github_list_pull_requests")
async def list_pull_requests_tool(
    repo: str,
    state: str = "all",
    limit: int = 30,
    sort: str = "updated"
) -> dict:
    """List pull requests for a repository with their metadata."""
    owner = os.getenv("GITHUB_OWNER")
    if not owner:
        return {"status": "error", "error": "GITHUB_OWNER environment variable must be set"}
    return await list_pull_requests(owner, repo, state, limit, sort)


if __name__ == "__main__":
    # Validate environment variables on startup
    required_vars = ["GITHUB_ACCESS_TOKEN", "GITHUB_OWNER"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set the required environment variables and restart the server")
        exit(1)
    
    # Validate GitHub credentials
    from clients.github import GitHubClient
    import asyncio
    
    async def validate_startup():
        try:
            github_client = GitHubClient()
            is_valid = await github_client.validate_credentials()
            if not is_valid:
                logger.error("GitHub credentials validation failed")
                exit(1)
            logger.info("GitHub credentials validated successfully")
        except Exception as e:
            logger.error(f"Failed to validate GitHub credentials: {e}")
            exit(1)
    
    # Run credential validation
    asyncio.run(validate_startup())
    
    logger.info("Starting GitHub MCP Server")
    logger.info(f"Access Token configured: {'Yes' if os.getenv('GITHUB_ACCESS_TOKEN') else 'No'}")
    
    # Run the FastMCP server
    app.run()