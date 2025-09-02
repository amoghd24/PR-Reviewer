"""Test Slack post_message tool."""

import asyncio
import pytest
from mcp_client import MCPClient


@pytest.mark.asyncio
async def test_slack_post_message():
    """Test posting a Slack message."""
    async with MCPClient() as client:
        await client.connect("global", "uv", ["run", "python", "-m", "global_server.server"])
        
        result = await client.call_tool("global", "slack_post_message_tool", {
            "text": "Test message from MCP Client integration test"
        })
        
        assert len(result) == 1
        assert result[0].type == "text"
        
        # Check JSON structure
        import json
        data = json.loads(result[0].text)
        assert data["success"] == True
        assert "message" in data


def test_slack_post_message_sync():
    """Synchronous wrapper for manual testing."""
    asyncio.run(test_slack_post_message())