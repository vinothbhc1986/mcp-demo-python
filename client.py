import anyio
import sys
from mcp import Client, StdioServerParameters

server = StdioServerParameters(
    command=sys.executable,
    args=['index.py']
)

async def main():
    async with Client(server) as client:
        print("Connected to Server")

        # 1. List tools inside the block
        result = await client.list_tools()
        for tool in result.tools:
            print(f"Tool found: {tool.name}")

        # 2. Call tool inside the block
        tool_result = await client.call_tool(
            "add",
            {"a": 10, "b": 20}
        )
        print("Tool result:", tool_result)

if __name__ == "__main__":
    anyio.run(main)