"""Test GitHub list_pull_requests tool."""

import asyncio
import pytest
from mcp_client import MCPClient


@pytest.mark.asyncio
async def test_github_list_pull_requests():
    """Test listing GitHub pull requests."""
    async with MCPClient() as client:
        await client.connect("global", "uv", ["run", "python", "-m", "global_server.server"])
        
        result = await client.call_tool("global", "github_list_pull_requests_tool", {
            "repo": "pr-reviewer",
            "state": "open"
        })
        
        assert len(result) == 1
        assert result[0].type == "text"
        
        # Check JSON structure
        import json
        data = json.loads(result[0].text)
        assert data["success"] == True
        assert "pull_requests" in data


def test_github_list_pull_requests_sync():
    """Synchronous wrapper for manual testing."""
    asyncio.run(test_github_list_pull_requests())