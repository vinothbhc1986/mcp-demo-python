"""
Weather tool implementation.
Fetches real-time weather information using the wttr.in service.
"""

import json
import logging
import urllib.error
import urllib.parse
import urllib.request

logging.basicConfig(
    level=logging.INFO,
    filename="mcp_server.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def get_weather(city: str) -> dict:
    """
    Get the current weather for a given city.
    """
    logging.info(f"Executing get_weather tool for city: {city}")
    encoded_city = urllib.parse.quote(city.strip())
    url = f"https://wttr.in/{encoded_city}?format=j1"

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "curl/8.0.0"},
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status != 200:
                return {"error": f"Failed to fetch weather: HTTP {response.status}"}

            data = json.loads(response.read().decode("utf-8"))
            current = data["current_condition"][0]
            nearest = data.get("nearest_area", [{}])[0]

            area_name = nearest.get("areaName", [{}])[0].get("value", city)
            country = nearest.get("country", [{}])[0].get("value", "")

            return {
                "city": area_name,
                "country": country,
                "temperature": f"{current['temp_C']}°C",
                "condition": current["weatherDesc"][0]["value"],
                "humidity": f"{current['humidity']}%",
                "wind_speed": f"{current['windspeedKmph']} km/h",
                "feels_like": f"{current['FeelsLikeC']}°C",
            }
    except urllib.error.HTTPError as e:
        error_msg = f"HTTP {e.code}: Could not fetch weather for '{city}'"
        logging.error(error_msg)
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"Failed to retrieve weather data: {str(e)}"
        logging.error(error_msg)
        return {"error": error_msg}


if __name__ == "__main__":
    from mcp.server.mcpserver import MCPServer

    standalone = MCPServer("Weather Server")
    standalone.add_tool(get_weather)
    standalone.run()
