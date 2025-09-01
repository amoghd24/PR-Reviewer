"""Get last messages tool for Slack MCP server."""

import os
from typing import Optional

from clients.slack import SlackClient
from utils.logger import get_logger

logger = get_logger(__name__)


async def get_last_messages(
    channel: str,
    limit: int = 10,
    latest: Optional[str] = None,
    oldest: Optional[str] = None,
    include_replies: bool = True,
) -> dict:
    """Get the last messages from a Slack channel.
    
    Args:
        channel: Channel ID to get messages from
        limit: Number of messages to retrieve (max 1000)
        latest: Latest timestamp to include
        oldest: Oldest timestamp to include
        include_replies: Whether to fetch replies for threaded messages
        
    Returns:
        Dictionary with success status and messages list
        
    Raises:
        ValueError: If required parameters are missing or invalid
        Exception: If API request fails
    """
    if not channel or not channel.strip():
        return {
            "success": False,
            "error": "Channel is required and cannot be empty"
        }
    
    if limit <= 0 or limit > 1000:
        return {
            "success": False,
            "error": "Limit must be between 1 and 1000"
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
        # Build parameters
        params = {"limit": limit}
        if latest:
            params["latest"] = latest
        if oldest:
            params["oldest"] = oldest
        
        # Get messages via client
        messages = await client.conversations_history(channel.strip(), **params)
        
        logger.info(f"Successfully retrieved {len(messages)} messages from {channel}")
        
        # Convert to serializable format and fetch replies if needed
        message_list = []
        for msg in messages:
            message_dict = {
                "ts": msg.ts,
                "text": msg.text,
                "user": msg.user,
                "channel": msg.channel,
                "type": msg.type,
                "subtype": msg.subtype,
                "username": msg.username,
                "bot_id": msg.bot_id,
                "attachments": msg.attachments,
                "blocks": msg.blocks,
                "thread_ts": msg.thread_ts,
                "reply_count": msg.reply_count,
                "replies": [],
            }
            
            # Fetch replies if this message has a thread and include_replies is True
            if include_replies and msg.reply_count and msg.reply_count > 0:
                try:
                    replies = await client.conversations_replies(channel.strip(), msg.ts)
                    message_dict["replies"] = replies
                    logger.info(f"Fetched {len(replies)} replies for message {msg.ts}")
                except Exception as e:
                    logger.warning(f"Failed to fetch replies for message {msg.ts}: {e}")
                    message_dict["replies"] = []
            
            message_list.append(message_dict)
        
        return {
            "success": True,
            "messages": message_list,
            "count": len(message_list),
            "channel": channel.strip()
        }
        
    except Exception as e:
        logger.error(f"Error getting messages from {channel}: {e}")
        return {
            "success": False,
            "error": str(e)
        }
    
    finally:
        await client.close()