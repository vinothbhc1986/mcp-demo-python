from mcp.server import MCPServer

mcp = MCPServer("Prompt Server")

@mcp.prompt()
def explain_topic(topic: str) -> str:
    return f"""
        Explain {topic} in simple words,
        with suitable example, if needed give
        diagram or program code for explanation
    """

if __name__ == "__main__":
    mcp.run()