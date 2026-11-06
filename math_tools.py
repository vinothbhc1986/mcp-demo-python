"""
Math tools implementation.
"""

import logging

logging.basicConfig(
    level=logging.INFO,
    filename="mcp_server.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def add(a: int, b: int) -> int:
    """Add two numbers"""
    logging.info(f"Executing add tool with {a} and {b}")
    return a + b


def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    logging.info(f"Executing subtract tool with {a} and {b}")
    return a - b


def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    logging.info(f"Executing multiply tool with {a} and {b}")
    return a * b


if __name__ == "__main__":
    from mcp.server.mcpserver import MCPServer

    standalone = MCPServer("Math Server")
    standalone.add_tool(add)
    standalone.add_tool(subtract)
    standalone.add_tool(multiply)
    standalone.run()
