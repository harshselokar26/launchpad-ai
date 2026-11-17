import asyncio
import httpx


async def test():

    async with httpx.AsyncClient(
        timeout=120
    ) as client:

        response = await client.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3.2:3b",
                "messages": [
                    {
                        "role": "user",
                        "content": "Return JSON: {\"status\": \"working\"}"
                    }
                ],
                "stream": False,
                "format": "json"
            }
        )

        print(response.status_code)
        print(response.json())


asyncio.run(test())