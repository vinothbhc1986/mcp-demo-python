from mcp.server import MCPServer

mcp = MCPServer("User Server")

@mcp.resource("user://details")
def get_user() -> str:
    """Get user Information"""

    return """
        Name: Nagarajan Vijay,
        Age: 20
    """

if __name__ == "__main__":
    mcp.run()