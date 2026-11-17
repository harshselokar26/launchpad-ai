
import httpx
from bs4 import BeautifulSoup


BASE_URL = "https://boards-api.greenhouse.io/v1/boards"


def clean_html(content: str | None) -> str:
    if not content:
        return ""

    return BeautifulSoup(content, "html.parser").get_text(
        separator=" ",
        strip=True
    )


async def scrape_greenhouse(board_token: str) -> list[dict]:
    """
    Fetch public jobs from a Greenhouse company board.
    board_token is the company's Greenhouse board identifier.
    """

    url = f"{BASE_URL}/{board_token}/jobs"

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            url,
            params={"content": "true"}
        )
        response.raise_for_status()
        data = response.json()

    jobs = []

    for item in data.get("jobs", []):
        location = item.get("location") or {}

        job = {
            "title": item.get("title", ""),
            "company": board_token,
            "location": location.get("name", "Not specified"),
            "description": clean_html(item.get("content")),
            "source": "greenhouse",
            "source_url": item.get("absolute_url", ""),
            "is_active": True
        }

        if job["title"] and job["source_url"]:
            jobs.append(job)

    return jobs
