"""
Unified MCP Server runner using Streamable-HTTP transport.
Hosts all application tools (Weather & Math operations).
"""

from mcp.server.mcpserver import MCPServer
from weather import get_weather
from math_tools import add, subtract, multiply

HOST = "127.0.0.1"
PORT = 8000

# Unified MCP Server instance
mcp = MCPServer("App MCP Server")

# Explicit tool registration
mcp.add_tool(get_weather)
mcp.add_tool(add)
mcp.add_tool(subtract)
mcp.add_tool(multiply)

if __name__ == "__main__":
    print(f"Starting MCP Streamable-HTTP server on http://{HOST}:{PORT}/mcp ...")
    print("Registered tools: get_weather, add, subtract, multiply")
    print("Press Ctrl+C to stop the server.\n")
    mcp.run(transport="streamable-http", host=HOST, port=PORT)
