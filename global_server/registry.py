"""MCP Servers Registry - PR-5 Implementation.

Central registry that aggregates all MCP servers in the PR reviewer system.
Provides unified tool discovery, routing, and tag management.
"""

from typing import Set, Dict, Any
from dotenv import load_dotenv

from fastmcp import FastMCP
from utils.logger import get_logger

# Load environment variables
load_dotenv()

# Configure logging
logger = get_logger(__name__)


class McpServersRegistry:
    """Central registry for all MCP servers with tool discovery and routing."""
    
    def __init__(self):
        """Initialize the registry with a FastMCP instance."""
        self.registry = FastMCP(
            name="mcp-global-registry",
            version="0.1.0"
        )
        self.all_tags: Set[str] = set()
        self._is_initialized = False
        self._server_statuses: Dict[str, str] = {}
    
    async def initialize(self) -> None:
        """Initialize the registry by importing all MCP servers."""
        if self._is_initialized:
            logger.info("Registry already initialized, skipping...")
            return

        logger.info("Initializing McpServersRegistry...")
        
        try:
            # Import individual MCP servers with prefixes
            await self._import_asana_server()
            await self._import_slack_server() 
            await self._import_agent_scope_server()
            await self._import_github_server()
            
            # Collect all tags from imported tools
            await self._collect_all_tags()
            
            logger.info(f"Registry initialization complete. Found tags: {sorted(self.all_tags)}")
            logger.info(f"Server statuses: {self._server_statuses}")
            self._is_initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize registry: {e}")
            raise
    
    async def _import_asana_server(self) -> None:
        """Import the Asana MCP server with 'asana' prefix."""
        try:
            from servers.asana_mcp.main import app as asana_mcp
            await self.registry.import_server(asana_mcp, prefix="asana")
            self._server_statuses["asana"] = "imported"
            logger.info("Successfully imported Asana MCP server")
        except Exception as e:
            logger.error(f"Failed to import Asana MCP server: {e}")
            self._server_statuses["asana"] = f"error: {e}"
            raise
    
    async def _import_slack_server(self) -> None:
        """Import the Slack MCP server with 'slack' prefix."""
        try:
            from servers.slack_mcp.main import app as slack_mcp
            await self.registry.import_server(slack_mcp, prefix="slack")
            self._server_statuses["slack"] = "imported"
            logger.info("Successfully imported Slack MCP server")
        except Exception as e:
            logger.error(f"Failed to import Slack MCP server: {e}")
            self._server_statuses["slack"] = f"error: {e}"
            raise
    
    async def _import_agent_scope_server(self) -> None:
        """Import the Agent Scope MCP server with 'scope' prefix."""
        try:
            from servers.agent_scope_mcp.main import app as agent_scope_mcp
            await self.registry.import_server(agent_scope_mcp, prefix="scope")
            self._server_statuses["scope"] = "imported"
            logger.info("Successfully imported Agent Scope MCP server")
        except Exception as e:
            logger.error(f"Failed to import Agent Scope MCP server: {e}")
            self._server_statuses["scope"] = f"error: {e}"
            raise
    
    async def _import_github_server(self) -> None:
        """Import the GitHub MCP server with 'github' prefix."""
        try:
            from servers.github_mcp.main import app as github_mcp
            await self.registry.import_server(github_mcp, prefix="github")
            self._server_statuses["github"] = "imported"
            logger.info("Successfully imported GitHub MCP server")
        except Exception as e:
            logger.error(f"Failed to import GitHub MCP server: {e}")
            self._server_statuses["github"] = f"error: {e}"
            raise
    
    async def _collect_all_tags(self) -> None:
        """Collect tags from all imported tools for discovery and filtering."""
        try:
            all_tools = await self.registry.get_tools()
            logger.info(f"Found {len(all_tools)} total tools in registry")
            
            for tool_name, tool in all_tools.items():
                if hasattr(tool, 'tags') and tool.tags:
                    self.all_tags.update(tool.tags)
                    logger.debug(f"Tool '{tool_name}' has tags: {tool.tags}")
            
            logger.info(f"Collected {len(self.all_tags)} unique tags: {sorted(self.all_tags)}")
            
        except Exception as e:
            logger.error(f"Failed to collect tags: {e}")
            raise
    
    def get_registry(self) -> FastMCP:
        """Get the underlying FastMCP registry instance."""
        return self.registry
    
    def get_all_tags(self) -> Set[str]:
        """Get all collected tags from imported servers."""
        return self.all_tags.copy()
    
    def get_server_statuses(self) -> Dict[str, str]:
        """Get the status of all imported servers."""
        return self._server_statuses.copy()
    
    def is_initialized(self) -> bool:
        """Check if the registry has been initialized."""
        return self._is_initialized
    
    async def get_tools_by_tag(self, tag: str) -> Dict[str, Any]:
        """Get all tools that have the specified tag."""
        if not self._is_initialized:
            await self.initialize()
        
        all_tools = await self.registry.get_tools()
        matching_tools = {}
        
        for tool_name, tool in all_tools.items():
            if hasattr(tool, 'tags') and tool.tags and tag in tool.tags:
                matching_tools[tool_name] = tool
        
        logger.info(f"Found {len(matching_tools)} tools with tag '{tag}'")
        return matching_tools
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the registry."""
        health_status = {
            "status": "healthy" if self._is_initialized else "not_initialized",
            "initialized": self._is_initialized,
            "server_count": len([s for s in self._server_statuses.values() if s == "imported"]),
            "error_count": len([s for s in self._server_statuses.values() if s.startswith("error")]),
            "total_tags": len(self.all_tags),
            "server_statuses": self._server_statuses,
            "available_tags": sorted(self.all_tags)
        }
        
        if self._is_initialized:
            try:
                all_tools = await self.registry.get_tools()
                health_status["total_tools"] = len(all_tools)
                health_status["tool_names"] = list(all_tools.keys())
            except Exception as e:
                health_status["tools_error"] = str(e)
                health_status["status"] = "degraded"
        
        return health_status