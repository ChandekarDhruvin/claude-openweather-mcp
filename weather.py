from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os
load_dotenv()
# Initialize FastMCP server
mcp = FastMCP("weather")

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")  # Replace with your real API key
OPENWEATHER_API_BASE = "https://api.openweathermap.org/data/2.5"

async def make_weather_request(url: str) -> dict[str, Any] | None:
    """Make a request to the OpenWeather API with proper error handling."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30.0)
            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.text[:500]}")  # Just the first 500 chars

            response.raise_for_status()

            # Check for correct content type before parsing
            if "application/json" not in response.headers.get("Content-Type", ""):
                print("⚠️ Unexpected content-type. Not JSON!")
                return None

            return response.json()

        except httpx.RequestError as e:
            print(f"Request error: {str(e)}")
            return None
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"API request error: {str(e)}")
            return None


@mcp.tool()
async def get_weather(city: str, country: str = "IN") -> str:
    """Get current weather data for a location."""
    print(f"Fetching weather data for {city}, {country}...")  # Log when the function is triggered
    url = f"{OPENWEATHER_API_BASE}/weather?q={city},{country}&units=metric&appid={OPENWEATHER_API_KEY}"
    data = await make_weather_request(url)

    if not data:
        return f"Unable to fetch weather for {city}, {country}."

    if data.get("cod") != 200:
        return f"Error: {data.get('message', 'Unknown error occurred')}"

    weather_main = data['weather'][0]['main']
    weather_desc = data['weather'][0]['description']
    temp = data['main']['temp']
    feels_like = data['main']['feels_like']
    humidity = data['main']['humidity']
    wind_speed = data['wind']['speed']

    return f"""
    Current weather in {city}, {country}:
    Condition: {weather_main} ({weather_desc})
    Temperature: {temp}°C (Feels like {feels_like}°C)
    Humidity: {humidity}%
    Wind Speed: {wind_speed} m/s
    """




@mcp.tool()
async def get_forecast(city: str, country: str = "IN") -> str:
    """Get 5-day forecast (1 per day between 11 AM and 3 PM) for a location."""
    print(f"Fetching forecast data for {city}, {country}...")  # Log when the function is triggered
    url = f"{OPENWEATHER_API_BASE}/forecast?q={city},{country}&units=metric&appid={OPENWEATHER_API_KEY}"
    data = await make_weather_request(url)

    if not data:
        return f"Unable to fetch forecast data for {city}, {country}."

    if data.get("cod") != "200":
        return f"Error: {data.get('message', 'Unknown error occurred')}"

    city_name = data['city']['name']
    forecasts = []
    days_added = set()

    for item in data["list"]:
        date = item["dt_txt"].split(" ")[0]
        time = item["dt_txt"].split(" ")[1]

        if date not in days_added and "11:00:00" < time < "15:00:00":
            days_added.add(date)
            weather = item["weather"][0]["main"]
            description = item["weather"][0]["description"]
            temp = item["main"]["temp"]
            feels_like = item["main"]["feels_like"]
            humidity = item["main"]["humidity"]

            forecast = f"""
            Date: {date}
            Time: {time}
            Condition: {weather} ({description})
            Temperature: {temp}°C (Feels like {feels_like}°C)
            Humidity: {humidity}%
            """
            forecasts.append(forecast)

        if len(forecasts) >= 5:
            break

    if not forecasts:
        return f"No forecast data available for {city_name}."

    return f"5-Day Forecast for {city_name}:\n" + "\n---\n".join(forecasts)


if __name__ == "__main__":
    print("Starting MCP server...")
    mcp.run(transport="stdio")
    print("MCP server started successfully!")
