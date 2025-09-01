"""Slack Web API client for MCP server integration."""

from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field
from utils.logger import get_logger

logger = get_logger(__name__)


class SlackMessage(BaseModel):
    """Slack message model with essential fields."""
    
    ts: str
    text: str
    user: str
    channel: str
    type: str = "message"
    subtype: Optional[str] = None
    username: Optional[str] = None
    bot_id: Optional[str] = None
    attachments: List[Dict[str, Any]] = Field(default_factory=list)
    blocks: List[Dict[str, Any]] = Field(default_factory=list)
    thread_ts: Optional[str] = None
    reply_count: Optional[int] = None
    replies: List[Dict[str, Any]] = Field(default_factory=list)


class SlackChannel(BaseModel):
    """Slack channel model with essential fields."""
    
    id: str
    name: str
    is_channel: bool = True
    is_private: bool = False
    is_im: bool = False
    is_group: bool = False
    is_archived: bool = False
    num_members: Optional[int] = None
    purpose: Dict[str, Any] = Field(default_factory=dict)
    topic: Dict[str, Any] = Field(default_factory=dict)


class SlackClient:
    """Async HTTP client for Slack Web API operations."""
    
    BASE_URL = "https://slack.com/api"
    
    def __init__(self, bot_token: str):
        """Initialize Slack client.
        
        Args:
            bot_token: Slack bot token for authentication
        """
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {bot_token}",
                "Content-Type": "application/json; charset=utf-8",
            },
            timeout=30.0,
        )
    
    async def close(self):
        """Close HTTP client connection."""
        await self.client.aclose()
    
    async def chat_post_message(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Post message to Slack API with O(1) complexity."""
        try:
            response = await self.client.post("/chat.postMessage", json=payload)
            response.raise_for_status()
            
            result = response.json()
            if not result.get("ok"):
                error = result.get("error", "Unknown error")
                logger.error(f"Slack API error: {error}")
                raise httpx.HTTPError(f"Slack API error: {error}")
            
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error posting message: Status {e.response.status_code}")
            logger.error(f"Response: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error posting message: {e}")
            raise
    
    async def conversations_history(self, channel: str, **params) -> List[SlackMessage]:
        """Get conversation history from Slack API with O(1) complexity."""
        api_params = {"channel": channel, **params}
        
        try:
            response = await self.client.get("/conversations.history", params=api_params)
            response.raise_for_status()
            
            result = response.json()
            if not result.get("ok"):
                error = result.get("error", "Unknown error")
                logger.error(f"Slack API error: {error}")
                raise httpx.HTTPError(f"Slack API error: {error}")
            
            messages = []
            for msg_data in result.get("messages", []):
                if msg_data.get("type") == "message":
                    try:
                        msg_data["channel"] = channel
                        message = SlackMessage(**msg_data)
                        messages.append(message)
                    except Exception as e:
                        logger.warning(f"Skipping malformed message: {e}")
                        continue
            
            return messages
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Channel {channel} not found")
                return []
            logger.error(f"HTTP error getting messages: Status {e.response.status_code}")
            logger.error(f"Response: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            raise
    
    async def conversations_list(self, **params) -> List[SlackChannel]:
        """Get list of channels from Slack API with O(1) complexity."""
        try:
            response = await self.client.get("/conversations.list", params=params)
            response.raise_for_status()
            
            result = response.json()
            if not result.get("ok"):
                error = result.get("error", "Unknown error")
                logger.error(f"Slack API error: {error}")
                raise httpx.HTTPError(f"Slack API error: {error}")
            
            channels = []
            for channel_data in result.get("channels", []):
                try:
                    channel = SlackChannel(**channel_data)
                    channels.append(channel)
                except Exception as e:
                    logger.warning(f"Skipping malformed channel: {e}")
                    continue
            
            return channels
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting channels: Status {e.response.status_code}")
            logger.error(f"Response: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error getting channels: {e}")
            raise
    
    async def conversations_replies(self, channel: str, ts: str, **params) -> List[Dict[str, Any]]:
        """Get replies to a thread from Slack API with O(1) complexity."""
        api_params = {"channel": channel, "ts": ts, **params}
        
        try:
            response = await self.client.get("/conversations.replies", params=api_params)
            response.raise_for_status()
            
            result = response.json()
            if not result.get("ok"):
                error = result.get("error", "Unknown error")
                logger.error(f"Slack API error: {error}")
                raise httpx.HTTPError(f"Slack API error: {error}")
            
            replies = result.get("messages", [])
            return replies[1:] if replies else []  # Skip the parent message
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Thread {ts} not found in channel {channel}")
                return []
            logger.error(f"HTTP error getting replies: Status {e.response.status_code}")
            logger.error(f"Response: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error getting replies: {e}")
            raise