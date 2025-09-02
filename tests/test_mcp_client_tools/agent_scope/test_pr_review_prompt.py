"""Test Agent Scope PR review prompt."""

import asyncio
import pytest
from mcp_client import MCPClient


@pytest.mark.asyncio
async def test_list_prompts():
    """Test listing available prompts."""
    async with MCPClient() as client:
        await client.connect("global", "uv", ["run", "python", "-m", "global_server.server"])
        
        prompts = await client.list_prompts("global")
        
        assert len(prompts) >= 1
        # Check if PR review prompt exists
        prompt_names = [p.name for p in prompts]
        assert "scope_pr_review_prompt" in prompt_names


@pytest.mark.asyncio
async def test_get_pr_review_prompt():
    """Test getting PR review prompt with arguments."""
    async with MCPClient() as client:
        await client.connect("global", "uv", ["run", "python", "-m", "global_server.server"])
        
        messages = await client.get_prompt("global", "scope_pr_review_prompt", {
            "pr_id": "123",
            "repo_id": "test-repo"
        })
        
        assert len(messages) >= 1
        assert messages[0].role == "user"
        # Content could be string or list of content blocks
        assert hasattr(messages[0], 'content')


def test_list_prompts_sync():
    """Synchronous wrapper for manual testing."""
    asyncio.run(test_list_prompts())


def test_get_pr_review_prompt_sync():
    """Synchronous wrapper for manual testing."""
    asyncio.run(test_get_pr_review_prompt())