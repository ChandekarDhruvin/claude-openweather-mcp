import httpx

OPENWEATHER_API_KEY = "d6d41d1fecabcc82f2cdc4bb2d23fa7a"
city = "Ahmedabad"
country = "IN"

async def get_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city},{country}&units=metric&appid={OPENWEATHER_API_KEY}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            print(f"Request error: {str(e)}")
            return None
        except Exception as e:
            print(f"Error: {str(e)}")
            return None

import asyncio

async def main():
    data = await get_weather()
    print(data)

asyncio.run(main())
