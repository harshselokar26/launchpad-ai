
import httpx
import logging

logger = logging.getLogger(__name__)

async def fetch_lever_jobs(site_name: str):
    url = f"https://api.lever.co/v0/postings/{site_name}"

    params = {"mode": "json"}

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()

            data = response.json()

        jobs = []

        for item in data:
            categories = item.get("categories") or {}

            location = categories.get("location", "")

            jobs.append({
                "title": item.get("text", ""),
                "company": site_name,
                "description": (
                    item.get("descriptionPlain", "")
                    or item.get("description", "")
                ),
                "location": location,
                "source": "Lever",
                "source_url": item.get("hostedUrl", ""),
                "posted_at": item.get("createdAt")
            })

        return jobs

    except Exception as exc:
        logger.exception(
            "Lever failed for %s: %s",
            site_name,
            exc
        )
        return []