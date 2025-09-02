"""Test GitHub get_pull_request_diff tool."""

import asyncio
import pytest
from mcp_client import MCPClient


@pytest.mark.asyncio
async def test_github_get_pull_request_diff():
    """Test getting GitHub pull request diff."""
    async with MCPClient() as client:
        await client.connect("global", "uv", ["run", "python", "-m", "global_server.server"])
        
        result = await client.call_tool("global", "github_get_pull_request_diff_tool", {
            "repo": "pr-reviewer",
            "pull_number": 1
        })
        
        assert len(result) == 1
        assert result[0].type == "text"
        
        # Check JSON structure
        import json
        data = json.loads(result[0].text)
        assert data["success"] == True
        assert "diff" in data


def test_github_get_pull_request_diff_sync():
    """Synchronous wrapper for manual testing."""
    asyncio.run(test_github_get_pull_request_diff())