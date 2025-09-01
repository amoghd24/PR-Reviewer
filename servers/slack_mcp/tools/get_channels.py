"""Get channels tool for Slack MCP server."""

import os
from typing import Optional

from clients.slack import SlackClient
from utils.logger import get_logger

logger = get_logger(__name__)


async def get_channels(
    types: str = "public_channel,private_channel",
    exclude_archived: bool = True,
    limit: int = 100,
    cursor: Optional[str] = None,
) -> dict:
    """Get list of channels with their IDs and information.
    
    Args:
        types: Comma-separated list of channel types to include
               (public_channel, private_channel, mpim, im)
        exclude_archived: Whether to exclude archived channels
        limit: Number of channels to retrieve (max 1000)
        cursor: Pagination cursor for retrieving more results
        
    Returns:
        Dictionary with success status and channels list
        
    Raises:
        ValueError: If required parameters are missing or invalid
        Exception: If API request fails
    """
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
        params = {
            "types": types,
            "exclude_archived": exclude_archived,
            "limit": limit,
        }
        if cursor:
            params["cursor"] = cursor
        
        # Get channels via client
        channels = await client.conversations_list(**params)
        
        logger.info(f"Successfully retrieved {len(channels)} channels")
        
        # Convert to serializable format
        channel_list = []
        for channel in channels:
            channel_list.append({
                "id": channel.id,
                "name": channel.name,
                "is_channel": channel.is_channel,
                "is_private": channel.is_private,
                "is_im": channel.is_im,
                "is_group": channel.is_group,
                "is_archived": channel.is_archived,
                "num_members": channel.num_members,
                "purpose": channel.purpose,
                "topic": channel.topic,
            })
        
        return {
            "success": True,
            "channels": channel_list,
            "count": len(channel_list),
        }
        
    except Exception as e:
        logger.error(f"Error getting channels: {e}")
        return {
            "success": False,
            "error": str(e)
        }
    
    finally:
        await client.close()