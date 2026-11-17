
import httpx
from bs4 import BeautifulSoup


BASE_URL = "https://api.lever.co/v0/postings"


def clean_html(content: str | None) -> str:
    if not content:
        return ""

    return BeautifulSoup(content, "html.parser").get_text(
        separator=" ",
        strip=True
    )


async def scrape_lever(site: str) -> list[dict]:
    """
    Fetch public jobs from a Lever company career site.
    site is the company's Lever site identifier.
    """

    url = f"{BASE_URL}/{site}"

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            url,
            params={"mode": "json"}
        )
        response.raise_for_status()
        data = response.json()

    jobs = []

    for item in data:
        categories = item.get("categories") or {}

        location = categories.get("location") or "Not specified"

        description = item.get("descriptionPlain") or clean_html(
            item.get("description")
        )

        job = {
            "title": item.get("text", ""),
            "company": site,
            "location": location,
            "description": description,
            "source": "lever",
            "source_url": item.get("hostedUrl", ""),
            "is_active": True
        }

        if job["title"] and job["source_url"]:
            jobs.append(job)

    return jobs
