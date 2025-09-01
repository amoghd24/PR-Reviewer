"""Slack MCP Server - PR-2 Implementation.

A FastMCP server providing Slack messaging tools for the PR reviewer system.
Implements post_message() and get_last_messages() tools with proper error handling and validation.
"""

import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastmcp import FastMCP

from utils.logger import get_logger
import opik
from .tools.post_message import post_message
from .tools.get_last_messages import get_last_messages
from .tools.get_channels import get_channels

# Load environment variables
load_dotenv()

# Configure logging
logger = get_logger(__name__)

# Configure Opik
opik_client = opik.Opik()

# Initialize FastMCP server
app = FastMCP(
    name="slack-mcp-server",
    version="0.1.0"
)


@app.tool(
    tags=["slack", "message", "send", "pr-reviewer"],
    description="Post a message to a Slack channel with optional formatting and threading"
)
@opik.track(name="slack_post_message")
async def post_message_tool(
    channel: str,
    text: Optional[str] = None,
    blocks: Optional[List[Dict[str, Any]]] = None,
    attachments: Optional[List[Dict[str, Any]]] = None,
    thread_ts: Optional[str] = None,
    username: Optional[str] = None,
    icon_emoji: Optional[str] = None,
    unfurl_links: bool = True,
) -> dict:
    """Post a message to a Slack channel."""
    return await post_message(
        channel=channel,
        text=text,
        blocks=blocks,
        attachments=attachments,
        thread_ts=thread_ts,
        username=username,
        icon_emoji=icon_emoji,
        unfurl_links=unfurl_links,
    )


@app.tool(
    tags=["slack", "message", "retrieve", "pr-reviewer"],
    description="Get conversation history from a Slack channel with optional filtering and thread replies"
)
@opik.track(name="slack_get_messages")
async def slack_conversation_history(
    channel: str,
    limit: int = 10,
    latest: Optional[str] = None,
    oldest: Optional[str] = None,
    include_replies: bool = True,
) -> dict:
    """Get conversation history from a Slack channel."""
    return await get_last_messages(
        channel=channel,
        limit=limit,
        latest=latest,
        oldest=oldest,
        include_replies=include_replies,
    )


@app.tool(
    tags=["slack", "channel", "list", "pr-reviewer"],
    description="Get list of Slack channels with their IDs and information for message posting"
)
@opik.track(name="slack_get_channels")
async def get_channels_tool(
    types: str = "public_channel,private_channel",
    exclude_archived: bool = True,
    limit: int = 100,
    cursor: Optional[str] = None,
) -> dict:
    """Get list of Slack channels with their IDs and information."""
    return await get_channels(
        types=types,
        exclude_archived=exclude_archived,
        limit=limit,
        cursor=cursor,
    )


if __name__ == "__main__":
    # Validate environment variables on startup
    required_vars = ["SLACK_BOT_TOKEN"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set the required environment variables and restart the server")
        exit(1)
    
    logger.info("Starting Slack MCP Server")
    logger.info(f"Bot Token configured: {'Yes' if os.getenv('SLACK_BOT_TOKEN') else 'No'}")
    
    # Run the FastMCP server
    app.run()