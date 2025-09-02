"""Gemini client for LLM operations."""

import os
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from utils.logger import get_logger
import opik

logger = get_logger(__name__)


class GeminiClient:
    """Client for interacting with Google's Gemini API."""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        """Initialize Gemini client with API key from environment.
        
        Args:
            model_name: The Gemini model to use (default: gemini-2.0-flash-exp)
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.conversation = []  # Start with empty conversation history
        logger.info(f"Initialized Gemini client with model: {model_name}")
    
    @opik.track(name="gemini_generate")
    async def generate(self, prompt: Optional[str] = None) -> str:
        """Generate response, optionally adding a new user message.
        
        Args:
            prompt: Optional new user message to add to conversation
            
        Returns:
            The text response from Gemini
        """
        try:
            # Add user message if provided
            if prompt:
                self.conversation.append({
                    "role": "user",
                    "content": prompt
                })
            
            # Convert conversation to Gemini format
            contents = []
            for msg in self.conversation:
                role = "user" if msg["role"] == "user" else "model"
                contents.append(types.Content(
                    role=role,
                    parts=[types.Part(text=msg["content"])]
                ))
            
            # Generate response
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents
            )
            
            # Add model response to conversation
            self.conversation.append({
                "role": "model", 
                "content": response.text
            })
            
            logger.debug(f"Generated response. Conversation length: {len(self.conversation)}")
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    def clear_conversation(self):
        """Clear the conversation history."""
        self.conversation = []
        logger.debug("Cleared conversation history")