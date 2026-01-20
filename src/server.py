from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import StaticTokenVerifier
import logging
from .config import Config
from .tools import register_tools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_server():
    logger.info(f"Initializing Google Tasks MCP Server...")
    
    # Optional: Enable Auth if token provided
    auth = None
    if Config.MCP_SERVER_TOKEN:
         logger.info("Enabling Static Token Authentication")
         auth = StaticTokenVerifier(tokens={
            Config.MCP_SERVER_TOKEN: {
                "client_id": "google-tasks-mcp-client",
                "scopes": ["read", "write"]
            }
         })

    mcp = FastMCP("google-tasks", auth=auth) 
    
    # Register our tools
    register_tools(mcp)
    
    return mcp

mcp = create_server()

def main():
    # Run over HTTP by default for Docker compatibility
    # Stateless HTTP for simpler scaling/debugging usually, or SSE.
    # CanvasMCP used stateless_http=True
    mcp.run(transport="http", host=Config.HOST, port=Config.PORT, stateless_http=True)

if __name__ == "__main__":
    main()
