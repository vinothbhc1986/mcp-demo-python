from mcp.server import MCPServer

# Initialize the MCP server
mcp = MCPServer("My Custom Prompt Server")

# Define a prompt template
@mcp.prompt()
def explain_code(code: str) -> str:
    """Explains a piece of code provided by the user."""
    return f"Please explain this code snippet in simple terms:\n\n{code}"

if __name__ == "__main__":
    mcp.run()