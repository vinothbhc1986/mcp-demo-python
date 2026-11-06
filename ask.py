"""
Interactive Question-Answering Client for MCP Server.
Accepts question prompts about weather and math operations,
selects the correct MCP tool, executes it (via live MCP server or direct mode),
and displays the formatted answer.
"""

import asyncio
import json
import re
import socket
import sys
from typing import Any, Dict, Optional, Tuple

# Local tool imports for direct execution fallback
from weather import get_weather
from math_tools import add, subtract, multiply

MCP_SERVER_HOST = "127.0.0.1"
MCP_SERVER_PORT = 8000
MCP_SERVER_URL = f"http://{MCP_SERVER_HOST}:{MCP_SERVER_PORT}/mcp"

# Available local tools mapping
LOCAL_TOOLS = {
    "get_weather": get_weather,
    "add": add,
    "subtract": subtract,
    "multiply": multiply,
}


def is_mcp_server_running(host: str = MCP_SERVER_HOST, port: int = MCP_SERVER_PORT) -> bool:
    """Fast check if the MCP Streamable-HTTP server is actively listening on port 8000."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.3)
            s.connect((host, port))
            return True
    except Exception:
        return False


def select_tool(question: str) -> Optional[Tuple[str, Dict[str, Any]]]:
    """
    Pattern-matches questions about weather and math to the right tool and parameters.
    Returns (tool_name, arguments) if matched, or None if no matching tool is found.
    """
    clean_q = question.strip().rstrip("?.!").lower()

    # 1. Weather Intent
    weather_keywords = ["weather", "temperature", "temp", "forecast", "climate", "condition"]
    if any(k in clean_q for k in weather_keywords):
        city = None
        # Pattern: weather in/of/for/at <city>
        m = re.search(
            r"(?:weather|temperature|temp|forecast|climate|condition)(?:\s+report)?\s+(?:in|of|for|at)\s+([a-zA-Z\s,]+)",
            clean_q,
        )
        if m:
            city = m.group(1).strip()
        else:
            # Pattern: how is/what is weather in/of <city>
            m = re.search(
                r"(?:how is|what is|tell me)\s+(?:the\s+)?(?:weather|temperature)\s+(?:in|of|for|at)\s+([a-zA-Z\s,]+)",
                clean_q,
            )
            if m:
                city = m.group(1).strip()
            else:
                # Pattern: <city> weather
                m = re.search(r"([a-zA-Z\s]+)\s+(?:weather|temperature)", clean_q)
                if m:
                    city = m.group(1).strip()

        if city:
            city = re.sub(r"^(the|current|today's|todays)\s+", "", city).strip()
            return "get_weather", {"city": city.title()}

    # 2. Math Intent - Subtraction (subtract X from Y -> Y - X)
    sub_from = re.search(r"subtract\s+(-?\d+)\s+from\s+(-?\d+)", clean_q)
    if sub_from:
        return "subtract", {"a": int(sub_from.group(2)), "b": int(sub_from.group(1))}

    # Math Intent - Subtraction (X - Y or subtract X and Y)
    sub_general = (
        re.search(r"(-?\d+)\s*-\s*(-?\d+)", clean_q)
        or re.search(r"(-?\d+)\s+minus\s+(-?\d+)", clean_q)
        or re.search(r"subtract\s+(-?\d+)\s+(?:and|by)\s+(-?\d+)", clean_q)
    )
    if sub_general:
        return "subtract", {"a": int(sub_general.group(1)), "b": int(sub_general.group(2))}

    # Math Intent - Addition (X + Y or add X and Y)
    add_match = (
        re.search(r"(-?\d+)\s*\+\s*(-?\d+)", clean_q)
        or re.search(r"(-?\d+)\s+plus\s+(-?\d+)", clean_q)
        or re.search(r"add\s+(-?\d+)\s+(?:and|to|\+)\s+(-?\d+)", clean_q)
        or re.search(r"sum\s+of\s+(-?\d+)\s+and\s+(-?\d+)", clean_q)
    )
    if add_match:
        return "add", {"a": int(add_match.group(1)), "b": int(add_match.group(2))}

    # Math Intent - Multiplication (X * Y or multiply X by Y)
    mul_match = (
        re.search(r"(-?\d+)\s*[\*x]\s*(-?\d+)", clean_q)
        or re.search(r"(-?\d+)\s+times\s+(-?\d+)", clean_q)
        or re.search(r"multiply\s+(-?\d+)\s+(?:by|and|\*)\s+(-?\d+)", clean_q)
        or re.search(r"product\s+of\s+(-?\d+)\s+and\s+(-?\d+)", clean_q)
    )
    if mul_match:
        return "multiply", {"a": int(mul_match.group(1)), "b": int(mul_match.group(2))}

    return None


# Backward-compatible alias
parse_intent_fallback = select_tool


def format_tool_result(tool_name: str, args: dict, result_data: Any) -> str:
    """Format tool execution output into a clean user answer."""
    data = result_data

    # Handle MCP result object if present
    if hasattr(result_data, "content"):
        content_items = result_data.content
        raw_text = ""
        for item in content_items:
            raw_text += getattr(item, "text", str(item))
        try:
            data = json.loads(raw_text)
        except Exception:
            data = raw_text

    # If data is a JSON string, decode it
    if isinstance(data, str) and (data.startswith("{") or data.startswith("[")):
        try:
            data = json.loads(data)
        except Exception:
            pass

    if tool_name == "get_weather":
        if isinstance(data, dict):
            if "error" in data:
                return (
                    f"❌ Weather Error: {data['error']}\n"
                    f"💡 Note: Ensure your system has active internet access to reach wttr.in."
                )
            city = data.get("city", args.get("city", "Unknown"))
            country = f", {data['country']}" if data.get("country") else ""
            temp = data.get("temperature", "N/A")
            feels = data.get("feels_like", "N/A")
            cond = data.get("condition", "N/A")
            humidity = data.get("humidity", "N/A")
            wind = data.get("wind_speed", "N/A")
            return (
                f"🌤️  Weather for {city}{country}:\n"
                f"   • Condition:    {cond}\n"
                f"   • Temperature:  {temp} (Feels like {feels})\n"
                f"   • Humidity:     {humidity}\n"
                f"   • Wind Speed:   {wind}"
            )
        return f"Weather Result: {data}"

    if tool_name == "add":
        return f"➕  Result: {args.get('a')} + {args.get('b')} = {data}"

    if tool_name == "subtract":
        return f"➖  Result: {args.get('a')} - {args.get('b')} = {data}"

    if tool_name == "multiply":
        return f"✖️  Result: {args.get('a')} × {args.get('b')} = {data}"

    return f"Result: {data}"


async def _call_mcp_session(tool_name: str, tool_args: dict) -> Any:
    """Async helper to execute a tool via Streamable-HTTP."""
    from mcp import ClientSession
    from mcp.client.streamable_http import streamable_http_client

    async with streamable_http_client(MCP_SERVER_URL) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            return await session.call_tool(tool_name, arguments=tool_args)


def execute_via_mcp(tool_name: str, tool_args: dict) -> Any:
    """Execute tool through the active MCP Streamable-HTTP server."""
    return asyncio.run(_call_mcp_session(tool_name, tool_args))


def execute_direct(tool_name: str, tool_args: dict) -> Any:
    """Execute tool directly in Python if MCP HTTP server is not running."""
    tool = LOCAL_TOOLS[tool_name]
    return tool(**tool_args)


def answer_question(question: str):
    """Selects the correct tool, executes it, and displays the answer."""
    matched = select_tool(question)
    if not matched:
        print("\n❓ Could not determine a matching tool for your question.")
        print("💡 Examples you can ask:")
        print("   - 'what is weather of hyderabad?'")
        print("   - 'how is the weather in Chennai?'")
        print("   - 'what is 15 + 27?'")
        print("   - 'multiply 8 and 12'")
        print("   - 'subtract 14 from 50'\n")
        return

    tool_name, tool_args = matched
    print(f"\n[Tool Selected] 🔧 `{tool_name}` with arguments: {json.dumps(tool_args)}")

    server_running = is_mcp_server_running()
    try:
        if server_running:
            print(f"[Transport] 🌐 Connected to MCP Streamable-HTTP ({MCP_SERVER_URL})")
            result = execute_via_mcp(tool_name, tool_args)
        else:
            print("[Transport] ⚡ Direct Mode (Start 'python server.py' to use live MCP HTTP server)")
            result = execute_direct(tool_name, tool_args)

        formatted = format_tool_result(tool_name, tool_args, result)
        print("\n" + "=" * 55)
        print(formatted)
        print("=" * 55 + "\n")

    except Exception as e:
        print(f"\n❌ Error during execution: {e}\n")


def main():
    print("=" * 60)
    print("       MCP Prompt Client (Weather & Math Tools)")
    print("=" * 60)

    server_status = "Online (http://127.0.0.1:8000/mcp)" if is_mcp_server_running() else "Offline (Using Direct Mode)"
    print(f"MCP Server Status: {server_status}")
    print("Tools Available:   get_weather, add, subtract, multiply")
    print("-" * 60)

    # If question passed via CLI argument
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        print(f"Prompt: {question}")
        answer_question(question)
        return

    # Interactive prompt loop
    print("Enter your question below (or type 'exit' to quit):\n")
    while True:
        try:
            prompt = input("Question > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not prompt:
            continue
        if prompt.lower() in ["exit", "quit", "q"]:
            print("Goodbye!")
            break

        answer_question(prompt)


if __name__ == "__main__":
    main()
