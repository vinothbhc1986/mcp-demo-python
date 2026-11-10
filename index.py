from mcp.server.mcpserver import MCPServer

mcp = MCPServer("MCP Server")

@mcp.tool()
def divide_number(a:int, b:int) -> str:
    "Divide two numbers"
    if b != 0:
        return str(a // b )
    return "Cannot divide by zero"

if __name__ == "__main__":
    mcp.run(transport="streamable-http",
    host="127.0.0.1",
    port=5000
)