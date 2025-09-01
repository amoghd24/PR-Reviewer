"""MCP Servers Registry - PR-6 Implementation.

Central registry that aggregates all MCP servers in the PR reviewer system.
Provides unified tool discovery, routing, tag management, and advanced search capabilities.
"""

from typing import Set, Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from dotenv import load_dotenv

from fastmcp import FastMCP
from utils.logger import get_logger

# Load environment variables
load_dotenv()

# Configure logging
logger = get_logger(__name__)


@dataclass
class ToolMetadata:
    """Enhanced metadata for registered tools."""
    name: str
    description: str
    tags: Set[str]
    server_prefix: str
    parameters: Dict[str, Any]
    usage_count: int = 0
    last_used: Optional[datetime] = None
    is_deprecated: bool = False
    
    def matches_tag_filter(self, required_tags: Set[str]) -> bool:
        """Check if tool matches all required tags."""
        return required_tags.issubset(self.tags)
    
    def matches_search_query(self, query: str) -> bool:
        """Check if tool matches search query in name or description."""
        query_lower = query.lower()
        return (
            query_lower in self.name.lower() or
            query_lower in self.description.lower() or
            any(query_lower in tag.lower() for tag in self.tags)
        )


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
        self._tool_metadata: Dict[str, ToolMetadata] = {}
        self._tag_index: Dict[str, Set[str]] = {}  # tag -> set of tool names
        self._performance_cache: Dict[str, Any] = {}
    
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
            
            # Collect all tags and build metadata
            await self._collect_all_tags()
            await self._build_tool_metadata()
            await self._build_tag_index()
            
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
    
    async def _build_tool_metadata(self) -> None:
        """Build enhanced metadata for all tools."""
        try:
            all_tools = await self.registry.get_tools()
            
            for tool_name, tool in all_tools.items():
                # Extract server prefix from tool name
                server_prefix = tool_name.split('_')[0] if '_' in tool_name else 'unknown'
                
                # Get tool tags
                tags = set(tool.tags) if hasattr(tool, 'tags') and tool.tags else set()
                
                # Get tool description
                description = getattr(tool, 'description', '') or ''
                
                # Get tool parameters (schema)
                parameters = {}
                if hasattr(tool, '__annotations__'):
                    parameters = tool.__annotations__
                elif hasattr(tool, 'model_json_schema'):
                    parameters = tool.model_json_schema()
                elif hasattr(tool, 'schema'):
                    parameters = tool.schema
                
                metadata = ToolMetadata(
                    name=tool_name,
                    description=description,
                    tags=tags,
                    server_prefix=server_prefix,
                    parameters=parameters
                )
                
                self._tool_metadata[tool_name] = metadata
            
            logger.info(f"Built metadata for {len(self._tool_metadata)} tools")
            
        except Exception as e:
            logger.error(f"Failed to build tool metadata: {e}")
            raise
    
    async def _build_tag_index(self) -> None:
        """Build reverse index for fast tag-based lookups."""
        try:
            for tool_name, metadata in self._tool_metadata.items():
                for tag in metadata.tags:
                    if tag not in self._tag_index:
                        self._tag_index[tag] = set()
                    self._tag_index[tag].add(tool_name)
            
            logger.info(f"Built tag index with {len(self._tag_index)} tags")
            
        except Exception as e:
            logger.error(f"Failed to build tag index: {e}")
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
        
        # Use tag index for fast lookup
        if tag in self._tag_index:
            tool_names = self._tag_index[tag]
            all_tools = await self.registry.get_tools()
            matching_tools = {name: all_tools[name] for name in tool_names if name in all_tools}
            logger.info(f"Found {len(matching_tools)} tools with tag '{tag}'")
            return matching_tools
        
        logger.info(f"No tools found with tag '{tag}'")
        return {}
    
    async def search_tools(
        self, 
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        server_prefix: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[ToolMetadata]:
        """Advanced tool search with multiple filters."""
        if not self._is_initialized:
            await self.initialize()
        
        results = []
        required_tags = set(tags) if tags else set()
        
        for metadata in self._tool_metadata.values():
            # Filter by tags
            if required_tags and not metadata.matches_tag_filter(required_tags):
                continue
            
            # Filter by server prefix
            if server_prefix and metadata.server_prefix != server_prefix:
                continue
            
            # Filter by search query
            if query and not metadata.matches_search_query(query):
                continue
            
            results.append(metadata)
        
        # Sort by usage count (most used first)
        results.sort(key=lambda x: x.usage_count, reverse=True)
        
        # Apply limit
        if limit:
            results = results[:limit]
        
        logger.info(f"Search found {len(results)} tools (query: '{query}', tags: {tags}, prefix: '{server_prefix}')")
        return results
    
    async def get_tools_by_tags(self, tags: List[str], match_all: bool = True) -> Dict[str, Any]:
        """Get tools matching multiple tags."""
        if not self._is_initialized:
            await self.initialize()
        
        if not tags:
            return {}
        
        if match_all:
            # Find intersection of all tag sets
            matching_tool_names = None
            for tag in tags:
                if tag in self._tag_index:
                    tag_tools = self._tag_index[tag]
                    if matching_tool_names is None:
                        matching_tool_names = tag_tools.copy()
                    else:
                        matching_tool_names &= tag_tools
                else:
                    # Tag doesn't exist, no matches possible
                    matching_tool_names = set()
                    break
        else:
            # Find union of all tag sets
            matching_tool_names = set()
            for tag in tags:
                if tag in self._tag_index:
                    matching_tool_names |= self._tag_index[tag]
        
        if not matching_tool_names:
            logger.info(f"No tools found matching tags: {tags} (match_all: {match_all})")
            return {}
        
        all_tools = await self.registry.get_tools()
        matching_tools = {name: all_tools[name] for name in matching_tool_names if name in all_tools}
        
        logger.info(f"Found {len(matching_tools)} tools matching tags: {tags} (match_all: {match_all})")
        return matching_tools
    
    async def get_tool_metadata(self, tool_name: str) -> Optional[ToolMetadata]:
        """Get metadata for a specific tool."""
        if not self._is_initialized:
            await self.initialize()
        
        return self._tool_metadata.get(tool_name)
    
    def get_tools_by_server(self, server_prefix: str) -> List[ToolMetadata]:
        """Get all tools from a specific server."""
        return [
            metadata for metadata in self._tool_metadata.values() 
            if metadata.server_prefix == server_prefix
        ]
    
    def get_tag_statistics(self) -> Dict[str, int]:
        """Get usage statistics for all tags."""
        tag_stats = {}
        for tag, tool_names in self._tag_index.items():
            tag_stats[tag] = len(tool_names)
        return tag_stats
    
    def record_tool_usage(self, tool_name: str) -> None:
        """Record usage of a tool for analytics."""
        if tool_name in self._tool_metadata:
            self._tool_metadata[tool_name].usage_count += 1
            self._tool_metadata[tool_name].last_used = datetime.now()
            logger.debug(f"Recorded usage for tool: {tool_name}")
    
    def get_popular_tools(self, limit: int = 10) -> List[ToolMetadata]:
        """Get most frequently used tools."""
        sorted_tools = sorted(
            self._tool_metadata.values(), 
            key=lambda x: x.usage_count, 
            reverse=True
        )
        return sorted_tools[:limit]
    
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