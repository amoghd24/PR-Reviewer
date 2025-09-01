"""
VersionedPrompt class for managing prompt templates with local fallbacks.

This module provides a simple VersionedPrompt class for managing prompt templates
with basic versioning capabilities. Opik integration will be added in later phases.
"""

from typing import Optional
from utils.logger import get_logger

logger = get_logger(__name__)


class VersionedPrompt:
    """
    A prompt management class that supports versioned prompts with local templates.
    Future versions will integrate with Opik for advanced versioning.
    """

    def __init__(self, name: str, template: str, version: str = "1.0.0"):
        """
        Initialize a VersionedPrompt.

        Args:
            name: The name/identifier for this prompt
            template: The prompt template string
            version: The version of this prompt
        """
        self.name = name
        self.version = version
        self._template = template
        logger.info(f"Initialized prompt '{self.name}' version {self.version}")

    def get(self) -> str:
        """
        Get the current prompt template.

        Returns:
            The prompt template string.
        """
        return self._template

    def update_template(self, new_template: str, new_version: Optional[str] = None):
        """
        Update the template and optionally the version.
        
        Args:
            new_template: The new template string
            new_version: Optional new version number
        """
        old_version = self.version
        self._template = new_template
        
        if new_version:
            self.version = new_version
            
        logger.info(f"Updated prompt '{self.name}' from version {old_version} to {self.version}")

    def format(self, **kwargs) -> str:
        """
        Format the prompt template with provided arguments.
        
        Args:
            **kwargs: Arguments to format the template with
            
        Returns:
            Formatted prompt string
        """
        try:
            return self._template.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing template argument for prompt '{self.name}': {e}")
            raise
        except Exception as e:
            logger.error(f"Error formatting prompt '{self.name}': {e}")
            raise