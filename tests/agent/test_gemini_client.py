"""Integration tests for GeminiClient."""

import pytest
import asyncio
import os
from dotenv import load_dotenv
from agent.gemini_client import GeminiClient

# Load environment variables
load_dotenv()


@pytest.mark.asyncio
async def test_gemini_client_real_completion():
    """Test real completion with Gemini API."""
    # Initialize client
    client = GeminiClient()
    
    # Ask a simple question
    response = await client.generate("Hi, who are you?")
    
    # Check we got a response
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0
    
    print(f"\nGemini Response: {response}")
    
    # Verify conversation was tracked
    assert len(client.conversation) == 2
    assert client.conversation[0]["content"] == "Hi, who are you?"
    assert client.conversation[1]["content"] == response


if __name__ == "__main__":
    # Run the test directly
    async def run_test():
        print("Testing Gemini Client with real API...")
        client = GeminiClient()
        response = await client.generate("Hi, who are you?")
        print(f"\nResponse: {response}")
        print(f"\nConversation tracked: {len(client.conversation)} messages")
        print("Test completed successfully!")
    
    asyncio.run(run_test())