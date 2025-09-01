"""Global MCP Server - PR-6 Implementation.

Main entry point for the global MCP server that aggregates all individual
MCP servers into a unified system with centralized tool discovery, routing,
and advanced search capabilities.
"""

import os
import asyncio
from typing import Dict, Any

from dotenv import load_dotenv
from utils.logger import get_logger
from global_server.registry import McpServersRegistry
from global_server.api_tools.registry_api import register_api_tools

# Load environment variables
load_dotenv()

# Configure logging
logger = get_logger(__name__)

# Global registry instance
mcp_registry: McpServersRegistry = None


async def initialize_global_server() -> McpServersRegistry:
    """Initialize the global MCP server registry."""
    global mcp_registry
    
    logger.info("Initializing Global MCP Server...")
    
    # Create and initialize the registry
    mcp_registry = McpServersRegistry()
    await mcp_registry.initialize()
    
    # Register registry API tools
    app = mcp_registry.get_registry()
    await register_api_tools(app, mcp_registry)
    
    logger.info("Global MCP Server initialization complete")
    return mcp_registry


async def get_global_registry() -> McpServersRegistry:
    """Get the global MCP registry, initializing if necessary."""
    global mcp_registry
    
    if mcp_registry is None or (mcp_registry is not None and not mcp_registry.is_initialized()):
        await initialize_global_server()
    
    return mcp_registry


async def health_check() -> Dict[str, Any]:
    """Perform a comprehensive health check on the global server."""
    try:
        registry = await get_global_registry()
        health_data = await registry.health_check()
        health_data["global_server_status"] = "operational"
        return health_data
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "global_server_status": "error",
            "error": str(e),
            "initialized": False
        }


def validate_environment() -> bool:
    """Validate required environment variables for all servers."""
    logger.info("Validating environment variables...")
    
    # Collect all required environment variables from all servers
    required_vars = {
        "asana": ["ASANA_PERSONAL_ACCESS_TOKEN", "ASANA_WORKSPACE_ID"],
        "slack": ["SLACK_BOT_TOKEN"],
        "github": ["GITHUB_ACCESS_TOKEN", "GITHUB_OWNER"],
        "agent_scope": ["GITHUB_OWNER"]  # Uses GITHUB_OWNER for PR URL construction
    }
    
    missing_vars = {}
    all_valid = True
    
    for server, vars_list in required_vars.items():
        server_missing = [var for var in vars_list if not os.getenv(var)]
        if server_missing:
            missing_vars[server] = server_missing
            all_valid = False
    
    if not all_valid:
        logger.error("Missing required environment variables:")
        for server, vars_list in missing_vars.items():
            logger.error(f"  {server}: {', '.join(vars_list)}")
        return False
    
    logger.info("All environment variables validated successfully")
    return True


async def run_server():
    """Run the global MCP server."""
    logger.info("Starting Global MCP Server...")
    
    # Validate environment
    if not validate_environment():
        logger.error("Environment validation failed. Please set required variables.")
        return
    
    # Initialize the registry
    try:
        registry = await initialize_global_server()
        
        # Get the FastMCP instance
        app = registry.get_registry()
        
        # Log server status
        health_status = await health_check()
        logger.info(f"Global server health: {health_status}")
        
        # Run the server - just return the app so it can be run externally
        logger.info("Global MCP Server is ready to handle requests")
        return app
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


def main():
    """Main entry point for the global MCP server."""
    logger.info("Starting Global MCP Server...")
    
    # Validate environment
    if not validate_environment():
        logger.error("Environment validation failed. Please set required variables.")
        return
    
    try:
        # Initialize the registry synchronously for the app.run() call
        registry = McpServersRegistry()
        
        async def init_registry():
            await registry.initialize()
            health_status = await registry.health_check()
            logger.info(f"Global server health: {health_status}")
        
        # Run initialization
        asyncio.run(init_registry())
        
        # Register API tools
        app = registry.get_registry()
        asyncio.run(register_api_tools(app, registry))
        
        logger.info("Global MCP Server is ready to handle requests")
        app.run()
        
    except KeyboardInterrupt:
        logger.info("Global MCP Server shutdown complete")
    except Exception as e:
        logger.error(f"Failed to start Global MCP Server: {e}")
        exit(1)


if __name__ == "__main__":
    main()