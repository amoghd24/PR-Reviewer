"""End-to-end test for Gemini Agent with MCP Tools."""

import asyncio
import pytest
from dotenv import load_dotenv
from agent.gemini_agent import GeminiAgent
from utils.logger import get_logger

# Load environment variables
load_dotenv()

logger = get_logger(__name__)


@pytest.mark.asyncio
async def test_gemini_agent_basic_response():
    """Test that Gemini agent can process a simple message and respond."""
    
    # Initialize the agent
    agent = GeminiAgent()
    
    try:
        # Initialize agent (connects to MCP tools)
        await agent.initialize()
        
        # Send a simpler test message that doesn't require tool usage
        test_prompt = "Hello, can you help me with code reviews?"
        
        # Generate response
        response = await agent.generate(test_prompt)
        
        # Print the response for human reading
        print("\n" + "="*50)
        print("PROMPT:", test_prompt)
        print("="*50)
        print("RESPONSE:", response)
        print("="*50 + "\n")
        
    finally:
        # Clean up
        await agent.cleanup()


if __name__ == "__main__":
    # Run the test directly
    asyncio.run(test_gemini_agent_basic_response())