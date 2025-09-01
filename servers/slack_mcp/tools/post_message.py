"""Post message tool for Slack MCP server."""

import os
from typing import Any, Dict, List, Optional

from clients.slack import SlackClient
from utils.logger import get_logger

logger = get_logger(__name__)


async def post_message(
    channel: str,
    text: Optional[str] = None,
    blocks: Optional[List[Dict[str, Any]]] = None,
    attachments: Optional[List[Dict[str, Any]]] = None,
    thread_ts: Optional[str] = None,
    username: Optional[str] = None,
    icon_emoji: Optional[str] = None,
    unfurl_links: bool = True,
) -> dict:
    """Post a message to a Slack channel.
    
    Args:
        channel: Channel ID or name to post to
        text: Message text (required if blocks not provided)
        blocks: Block kit blocks for rich formatting
        attachments: Message attachments
        thread_ts: Thread timestamp for replies
        username: Bot username override
        icon_emoji: Bot emoji override
        unfurl_links: Whether to unfurl links
        
    Returns:
        Dictionary with success status and message details
        
    Raises:
        ValueError: If required parameters are missing or invalid
        Exception: If API request fails
    """
    if not text and not blocks:
        return {
            "success": False,
            "error": "Either text or blocks must be provided"
        }
    
    if not channel or not channel.strip():
        return {
            "success": False,
            "error": "Channel is required and cannot be empty"
        }
    
    # Get Slack bot token from environment
    bot_token = os.getenv("SLACK_BOT_TOKEN")
    if not bot_token:
        return {
            "success": False,
            "error": "SLACK_BOT_TOKEN environment variable not set"
        }
    
    client = SlackClient(bot_token)
    
    try:
        # Build payload
        payload = {
            "channel": channel.strip(),
            "unfurl_links": unfurl_links,
        }
        
        if text:
            payload["text"] = text.strip()
        if blocks:
            payload["blocks"] = blocks
        if attachments:
            payload["attachments"] = attachments
        if thread_ts:
            payload["thread_ts"] = thread_ts
        if username:
            payload["username"] = username
        if icon_emoji:
            payload["icon_emoji"] = icon_emoji
        
        # Send message via client
        result = await client.chat_post_message(payload)
        
        message = result["message"]
        logger.info(f"Successfully posted message to {channel}: {message['ts']}")
        
        return {
            "success": True,
            "message": {
                "ts": message["ts"],
                "channel": message.get("channel", channel.strip()),
                "text": message.get("text", ""),
                "user": message.get("user"),
                "bot_id": message.get("bot_id"),
                "permalink": result.get("permalink")
            }
        }
        
    except Exception as e:
        logger.error(f"Error posting message to {channel}: {e}")
        return {
            "success": False,
            "error": str(e)
        }
    
    finally:
        await client.close()