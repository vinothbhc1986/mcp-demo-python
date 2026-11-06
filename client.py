import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def main():
    url = "http://127.0.0.1:8000/mcp"
    async with streamable_http_client(url) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # 1. Initialize the session
            await session.initialize()

            # 2. List tools
            tools = await session.list_tools()
            print("Available Tools:", [t.name for t in tools.tools])

            # 3. Call the weather tool
            weather_result = await session.call_tool(
                "get_weather", arguments={"city": "Hyderabad"}
            )
            print("Weather Tool Response:", weather_result.content)

            # 4. Call math tool from math_tools.py
            math_result = await session.call_tool(
                "add", arguments={"a": 15, "b": 27}
            )
            print("Add Tool Response:", math_result.content)


if __name__ == "__main__":
    asyncio.run(main())
