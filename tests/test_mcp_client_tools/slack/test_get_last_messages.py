"""Test Slack get_last_messages tool."""

import asyncio
import pytest
from mcp_client import MCPClient


@pytest.mark.asyncio
async def test_slack_get_last_messages():
    """Test getting last messages from Slack."""
    async with MCPClient() as client:
        await client.connect("global", "uv", ["run", "python", "-m", "global_server.server"])
        
        result = await client.call_tool("global", "slack_slack_conversation_history", {
            "limit": 5
        })
        
        assert len(result) == 1
        assert result[0].type == "text"
        
        # Check JSON structure
        import json
        data = json.loads(result[0].text)
        assert data["success"] == True
        assert "messages" in data


def test_slack_get_last_messages_sync():
    """Synchronous wrapper for manual testing."""
    asyncio.run(test_slack_get_last_messages())