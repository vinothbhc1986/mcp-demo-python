from mcp.server import MCPServer

# Initialize MCP server
mcp = MCPServer("User Server")

# Sample user data
user = {
    "101": "Leo",
    "102": "Parthiban",
    "103": "Vijay"
}

@mcp.resource("user://{user_id}")
def get_user(user_id: str) -> str:
    """Get user information using user id."""
    name = user.get(user_id)

    if name is None:
        return "User not found!"

    return f"User Id: {user_id}\nName: {name}"

if __name__ == "__main__":
    mcp.run()