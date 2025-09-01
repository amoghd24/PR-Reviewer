"""Agent Scope MCP Server - PR-3 Implementation.

A FastMCP server providing prompt management for the PR reviewer system.
This server focuses on prompt serving following MCP protocol patterns.
"""

import os
from typing import Dict, Any

from dotenv import load_dotenv
from fastmcp import FastMCP

from utils.logger import get_logger
import opik
from .prompts.pr_review_prompt import PR_REVIEW_PROMPT

# Load environment variables
load_dotenv()

# Configure logging
logger = get_logger(__name__)

# Configure Opik
opik_client = opik.Opik()

# Initialize FastMCP server
app = FastMCP(
    name="agent-scope-mcp-server",
    version="0.1.0"
)


@app.prompt(
    name="pr_review_prompt",
    description="Prompt for reviewing pull requests with Asana task context"
)
@opik.track(name="agent_scope_pr_review_prompt")
def pr_review_prompt(pr_id: str, repo_id: str) -> str:
    """
    Format the PR review prompt using the provided arguments.
    
    Args:
        pr_id: The pull request ID
        repo_id: The repository name
        
    Returns:
        Formatted PR review prompt
    """
    try:
        # Get owner from environment
        owner = os.getenv("GITHUB_OWNER")
        if not owner:
            logger.error("GITHUB_OWNER not found in environment variables")
            owner = "unknown"
        
        # Construct the PR URL
        pr_url = f"https://github.com/{owner}/{repo_id}/pull/{pr_id}"
        
        # Format the prompt with constructed arguments
        formatted_prompt = PR_REVIEW_PROMPT.format(pr_id=pr_id, pr_url=pr_url)
        logger.info(f"Formatted PR review prompt for PR #{pr_id} in {owner}/{repo_id}")
        return formatted_prompt
    except Exception as e:
        logger.error(f"Error formatting PR review prompt: {e}")
        # Return the base template if formatting fails
        return PR_REVIEW_PROMPT.get()


if __name__ == "__main__":
    logger.info("Starting Agent Scope MCP Server")
    logger.info(f"Available prompts: pr_review_prompt")
    
    # Run the FastMCP server
    app.run()