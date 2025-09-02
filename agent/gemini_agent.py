"""Gemini Agent using LangChain with MCP Tools."""

import os
from typing import List, Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from agent.mcp_tool_wrapper import MCPToolWrapper
from utils.logger import get_logger
import opik

logger = get_logger(__name__)


class GeminiAgent:
    """LangChain agent using Gemini LLM with MCP tools."""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        """Initialize Gemini agent.
        
        Args:
            model_name: The Gemini model to use
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        # Initialize Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.7,
            convert_system_message_to_human=True
        )
        
        self.model_name = model_name
        self.mcp_wrapper = MCPToolWrapper()
        self.agent_executor = None
        self.conversation_history = []  # Simple list for conversation memory
        self.initialized = False
        
        logger.info(f"Initialized Gemini agent with model: {model_name}")
    
    async def initialize(self):
        """Initialize MCP tools and create the agent."""
        if self.initialized:
            return
            
        try:
            # Initialize MCP wrapper
            await self.mcp_wrapper.initialize()
            
            # Get LangChain tools from MCP
            tools = await self.mcp_wrapper.create_langchain_tools()
            
            # Create ReAct prompt template
            prompt = PromptTemplate.from_template("""
Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}
""")
            
            # Create the agent
            agent = create_react_agent(
                llm=self.llm,
                tools=tools,
                prompt=prompt
            )
            
            # Create agent executor
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=tools,
                verbose=True,
                handle_parsing_errors=True
            )
            
            self.initialized = True
            logger.info(f"Agent initialized with {len(tools)} MCP tools")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            raise
    
    @opik.track(name="gemini_generate")
    async def generate(self, prompt: str) -> str:
        """Generate response using the agent.
        
        Args:
            prompt: User message to process
            
        Returns:
            The agent's response
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": prompt})
            
            # Process with agent
            result = await self.agent_executor.ainvoke({"input": prompt})
            
            # Extract response
            response = result.get("output", "")
            
            # Add to conversation history
            self.conversation_history.append({"role": "assistant", "content": response})
            
            logger.debug(f"Generated response. History length: {len(self.conversation_history)}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    def clear_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []
        logger.debug("Cleared conversation history")
    
    async def list_available_tools(self) -> List[str]:
        """List all available MCP tools.
        
        Returns:
            List of tool names
        """
        if not self.initialized:
            await self.initialize()
        
        tools = await self.mcp_wrapper.get_available_tools()
        return [tool.get("name", "unknown") for tool in tools]
    
    async def cleanup(self):
        """Clean up resources."""
        if self.mcp_wrapper:
            await self.mcp_wrapper.cleanup()
        logger.info("Gemini agent cleaned up")